#!/usr/bin/env python3
"""
Module denoting the structure of mongoDB collections
"""
import bcrypt
from datetime import datetime
from bson import ObjectId

from mongoengine import (
    BooleanField,
    DateTimeField,
    Document,
    EmailField,
    EmbeddedDocument,
    EmbeddedDocumentField,
    EmbeddedDocumentListField,
    ObjectIdField,
    ReferenceField,
    StringField,
    Q,
)
from mongoengine.base.datastructures import EmbeddedDocumentList

from typing import Dict, List, Tuple
STRFTIME = "%Y-%m-%d %H:%M:%S"


class Base:
    """
    Base class with common methods
    """

    def to_dict(self) -> Dict:
        """
        method that method to convert objects to dict
        """
        attrs = getattr(self, f"_{self.__class__.__name__}__attributes", None)
        if not attrs:
            raise AttributeError("Child class must have attributes attribute")
        obj_dict = {}

        for key in attrs:
            if type(key) is str:  # for Users and general Queries
                value = getattr(self, key)

                if key in ["updated_at", "created_at"]:
                    value = value.strftime(STRFTIME)

                obj_dict.update({key: value})
            elif type(key) is dict:
                for k, v in key.items():
                    embedded = getattr(self, k)

                    # for queries responses
                    if type(embedded) is EmbeddedDocumentList:
                        obj_dict[k] = []
                        for res in embedded:
                            responses = {}
                            for _ in v:
                                value = getattr(res, _)

                                if _ in ["updated_at", "created_at"]:
                                    value = value.strftime(STRFTIME)

                                responses.update({_: value})
                            obj_dict[k].append(responses)
                    else:  # for notications
                        obj_dict[k] = {}
                        for _ in v:
                            value = getattr(embedded, _)
                            obj_dict[k].update({_: value})

        return obj_dict


class Notifications(EmbeddedDocument):
    """
    class defining notication status users
    """

    own_channel = BooleanField(default=True)
    general_channel = BooleanField(default=False)


class Responses(EmbeddedDocument):
    """
    Represents responses to queries.

    Attributes:
    - content (StringField): Content of the response.
    - author (StringField): Author of the response.
    - created_at (DateTimeField): Date and time of response creation.
    """

    _id = ObjectIdField(default=ObjectId)
    content = StringField(required=True)
    author = ReferenceField("users", required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)


class Users(Document, Base):
    """
    Defines basic schema for Documents in Users collection
    Note: is_hashed as been used due to mongo engine use of
        the class to instantiation which result to rehashing of the
        data (password) read from the database
    """

    username = StringField(min_length=8, unique=True, required=True)
    email = EmailField(domain_whitelist=["gmail"], unique=True, required=True)
    password = StringField(required=True)
    field = StringField(required=True)
    notifications = EmbeddedDocumentField(Notifications)

    __attributes = [
        "username",
        "email",
        "field",
        {"notifications": ["own_channel", "general_channel"]},
    ]

    def __init__(self, **kwargs) -> None:
        password = kwargs.pop("password", None)
        super().__init__(**kwargs)

        if password and not self.password and not self.is_hashed(password):
            self.set_password(password)
        else:
            self.password = password

    def set_password(self, password: str) -> None:
        """
        method that sets bcrypted passcode
        Arg:
            password (string): password to hash
        """
        salt = bcrypt.gensalt()
        hashed_passwd = bcrypt.hashpw(password.encode("utf-8"), salt)
        self.password = hashed_passwd.decode("utf-8")

    def is_hashed(self, password) -> bool:
        """
        Check if the password is already hashed.
        @weak, not strong
        """
        # Assuming that bcrypt hashes start with "$2b$"
        return password.startswith("$2b$") and len(password) == 60

    def check_pwd(self, password: str, db_pwd: str = None) -> bool:
        """
        method that check passcode passcode
        Arg:
            password (string): password to assert
            db_pwd (string): password from database
        Returns (bool): True if equal otherwise false
        """
        if not db_pwd:
            db_pwd = self.password
        return bcrypt.checkpw(password.encode("utf-8"), db_pwd.encode("utf-8"))

    @classmethod
    def find_user(cls, username) -> "Users":
        """
        method that method to retrive user by username
        params:
            username: username to use for filtering
        Return: First User or None
        """
        user = cls.objects(username=username).first()

        return user

    @classmethod
    def find_user_by_email(cls, email) -> "Users":
        """
        method that method to retrive user by email
        params:
            email: email to use for filtering
        Return: First User or None
        """
        user = cls.objects(email=email).first()

        return user

    @classmethod
    def find_user_by_channel(cls, channel: str) -> "Users":
        """
        method that method to retrive user by channel
        params:
            channel (str): channel/field to use for filtering
        Return: First User or None
        """
        user = None

        if channel == "general":
            user = cls.objects().filter(
                Q(notification__general_channel=True), field=channel
            )
        else:
            user = cls.objects().filter(
                Q(notification__own_channel=True), field=channel
            )

        return user

    def update_user(self, **kwargs):
        """
        method to update user
        Params:
            kwargs(dict): data to use for update
        """
        field = kwargs.get("field")
        notifications = kwargs.get("notifications")
        print(field)
        if field:
            self.field = field

        if notifications:
            for key in notifications.keys():
                setattr(self.notifications, key, notifications[key])

        self.save()


class Queries(Document, Base):
    """
    Represents queries posted by users.
    Attributes:
    - title (StringField): Title of the query.
    - author (ReferenceField): Reference to the User who posted the query.
    - channel (StringField): Channel associated with the query.
    - query_text (StringField): Text of the query.
    - created_at (DateTimeField): Date and time of query creation.
    - responses (ListField): List of embedded documents for query responses.
        - EmbeddedDocumentField: Represents each response to the query.
    """

    title = StringField(required=True)
    author = ReferenceField(Users)
    channel = StringField(required=True)
    query_text = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    responses = EmbeddedDocumentListField(Responses)

    __attributes = [
        "title",
        "channel",
        "query_text",
        "created_at",
        "updated_at",
        {"responses": ["content", "author", "created_at", "updated_at"]},
    ]

    # saves title in lower case
    query_title = StringField(required=True)

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.query_title = self.title.lower()

    @classmethod
    def find_query_by_title(cls, title: str, channel: str = None) -> "Queries":
        """
        method that finds query based on title
        params:
            title (str): title to use for querying
            channel (str): channel to build upon
        Returns: class instance
        """
        if channel:
            return cls.objects(
                channel=channel, query_title=title.lower()
                ).first()
        return cls.objects(query_title=title.lower()).first()

    @classmethod
    def find_query_by_id(cls, id: ObjectId, channel: str = None) -> "Queries":
        """
        method that finds query based on id
        params:
            id (ObjectId): id to use for querying
            channel (str): channel to build upon
        Returns: class instance
        """
        if channel:
            return cls.objects(channel=channel, _id=ObjectId(id)).first()
        return cls.objects(_id=ObjectId(id)).first()

    @classmethod
    def get_queries(
        cls, channel: str = "developer", page: int = 0, page_size: int = 10
    ) -> Tuple[List["Queries"], Dict[str, str]]:
        """
        Retrieve queries with pagination.
        Args:
            - channel (str): field to focus on
            - page (int): Page number (default: 1).
            - page_size (int): Number of items per page (default: 10).

        Returns: A Tuple of list of queries objects and paginations data
        """
        # Calculate skip value based on page number and page size
        skip_value = (page - 1) * page_size

        queries = None

        if channel == "all":
            queries = cls.objects().skip(skip_value).limit(page_size + 1)
        else:
            queries = cls.objects(
                channel=channel).skip(skip_value).limit(page_size + 1)

        queries_list = []

        if queries:
            for prompt in queries:
                queries_list.append(prompt.to_dict())

        pagination = {
            "page": page, "prev_page": page - 1 if page > 1 else None
            }
        # next page is valid
        if len(queries_list) == page_size + 1:
            queries_list = queries_list[:-1]
            pagination["next_page"] = page + 1
        else:
            pagination["next_page"] = None

        return (queries_list, pagination)

    @classmethod
    def get_user_questions_and_responses(
        cls,
        user_id: ObjectId,
        channel: str,
        question_title: str = None,
        _id: ObjectId = None,
    ) -> Tuple[list, list]:
        """
        Retrieve questions posted by the user and their responses,
        and questions they responded to with their respective responses.

        Args:
        - user_id (ObjectId): ID of the user.
        - channel (str): channel to target
        - question_title (str) : title to base on
        - _id (ObjectId): question id

        Returns:
        - Tuple containing user's questions with responses
            and questions responded to.
        """
        user_questions = None
        question_title = question_title.lower()
        if question_title:
            user_questions = cls.objects(
                author=user_id, channel=channel, query_title=question_title
            )
        elif _id:
            user_questions = cls.objects(
                author=user_id, channel=channel, _id=ObjectId(_id)
            )
        else:
            user_questions = cls.objects(author=user_id, channel=channel)

        # Questions posted by the user
        user_questions_with_responses = []
        for question in user_questions:
            question_data = question.to_dict()

            user_questions_with_responses.append(question_data)

        # Questions the user responded to with their responses
        responded_questions = None
        if question_title:
            responded_questions = cls.objects(
                responses__author=user_id,
                channel=channel,
                query_title=question_title
            )
        elif _id:
            responded_questions = cls.objects(
                responses__author=user_id, channel=channel, _id=ObjectId(_id)
            )
        else:
            responded_questions = cls.objects(
                responses__author=user_id, channel=channel
            )

        responded_questions_with_responses = []
        for question in responded_questions:
            responses = []
            for response in question.responses:
                if response.author == user_id:
                    response_data = {
                        "response_id": str(response._id),
                        "content": response.content,
                        "author": response.author,
                        "created_at": response.created_at.strftime(STRFTIME),
                        "updated_at": response.updated_at.strftime(STRFTIME),
                    }
                    responses.append(response_data)

            question_data = {
                "question_id": str(question.id),
                "title": question.title,
                "query_text": question.query_text,
                "responses": responses,
                "created_at": question.created_at.strftime(STRFTIME),
                "updated_at": question.updated_at.strftime(STRFTIME),
            }
            responded_questions_with_responses.append(question_data)

        return (user_questions_with_responses,
                responded_questions_with_responses)
