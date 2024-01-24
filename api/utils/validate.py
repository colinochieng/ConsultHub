#!/usr/bin/python3
"""
Module for utility functions
"""
import re
from typing import Dict, Tuple
from db.docs import Queries, Users
from api.utils.emailing import send_emails


def validate_email(email: str) -> bool:
    """
    describe: checks if email is valid
    Args:
        email (str): mail to validate
    return: True or false
    Note: Checks only for Gmail Accounts
    """
    pattern = r"\b[A-Za-z0-9._%+-]+@gmail\.com\b"

    return bool(re.fullmatch(pattern, email))


def validate_uname(username: str) -> bool:
    """
    describe: checks if username is valid
    Args:
        username (str): uname to validate
    return: True or false
    """
    if len(username) < 8:
        return False

    pattern = r"^\S+$"

    return bool(re.fullmatch(pattern, username))


def validate_password(passcode: str) -> bool:
    """
    describe: checks if passcode is valid
    Args:
        passcode (str): password to validate
    return: True or false
    """
    if len(passcode) < 4:
        return False

    pattern = r"^\S+$"

    return bool(re.fullmatch(pattern, passcode))


def validate_notifications(notification: Dict) -> bool:
    """
    function to validate the given notification data
    Args:
        notification(str): data to verify
    Return(bool): if valid or not
    """
    notifications_set = {"own_channel", "general_channel"}

    try:
        for _ in notification.keys():
            if _ not in notifications_set:
                return False
        for _ in notification.values():
            if type(_) is not bool:
                return False
    except AttributeError:
        return False

    return True


def verify_query_id(id) -> bool:
    """
     checks for a valid query id
     Args:
        id: string to check for
    return (bool): true or false
    """

    def is_hexadecimal() -> bool:
        """
        verify for hexadecimals only
        """
        return all(
            c.isalnum() and
            (c.isdigit() or c.isalpha() and c.lower() in "abcdef")
            for c in id
        )

    if is_hexadecimal() and len(id) == 24:
        return True
    return False


def verify_query_data_and_send_mail(
    data: Dict, channel: str, questioner: Users
) -> bool | Tuple:
    """
    verify if sent data is correct, saves the data and
        send email if the data includes all necessary queries
    Args:
        data (dict): query data
        channel (str): field to query users
        questioner (Users): current user
    """
    def filter_by_uname(user) -> bool:
        """
        Args:
            user: user to use data from filtering
        """
        return user.username != questioner.username

    if (
        len(data) == 0
        or "title" not in data
        or "query_text" not in data
        or len(data["title"]) < 10
        or len(data["query_text"]) < 10
    ):
        return False
    title = data.get("title")
    query_text = data.get("query_text")

    users = Users.find_user_by_channel(channel)

    more_info = ""
    # assuming general channel will always be open (have users)
    # + assuming you are the only person in you channel
    # + the query will be generalized
    if not users or len(users) == 1:
        users = Users.find_user_by_channel("general")
        channel = "general"
        more_info = "Your are the only user in the channel\
            thus you query as been generalized"

    users = list(filter(filter_by_uname, users))

    subject = "Exploring Together: Check Out the Latest Query"
    contexts = {
        "channel": channel.capitalize(),
        "query_text": query_text,
        "query_title": title.capitalize(),
    }

    query = Queries(title=title, query_text=query_text, author=questioner)
    query.save()

    def generate_email_info(user_info: Users) -> Tuple:
        contexts["channel_user"] = user_info.username
        contexts["query_id"] = str(query._id)
        return (contexts, user_info.email)

    email_info = list(map(generate_email_info, users))

    send_emails(subject, "question", email_info)

    return True, more_info, query
