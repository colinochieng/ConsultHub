#!/usr/bin/env python3
"""
Module for the channels get endpoints
"""
from bson import ObjectId, errors
from api.utils.validate import verify_query_id
from flask import Response, g, jsonify, request
from api.channel import channels
from api.utils.wraps import login_required
from db.docs import Queries, Users
from flasgger import swag_from

res = {
    "status": "success",
    "message": "User questions and responses retrieved successfully",
}
res_err = {"status": "error", "message": ""}


@channels.route("/<channel>/<username>/", strict_slashes=False)
@login_required
@swag_from("../../YAML/channels/get_users_channel.yml")
def get_users_channel_data(channel: str, username: str) -> Response:
    """
    Args:
        channel (str): channel to query from
        username (str): specified username for querying
    Return: a JSON representation of the questions
        the user posted and their responses,
        together with the questions they responded
        to with their responses
    """
    user = None
    if username == "me":
        user = g.user
    else:
        user = Users.find_user(username.lower())

    if not user:
        return jsonify({"status": "error", "message": "Invalid Username"}), 400

    db_data = Queries.get_user_questions_and_responses(user._id, channel)

    res["data"] = {
        "user_questions": db_data[0],
        "responded_questions": db_data[1]
        }

    return jsonify(res), 200


@channels.route("/<channel>/multi", strict_slashes=False)
@login_required
@swag_from("../../YAML/channels/fetch_multi.yml")
def fetch_multi_users_channels_query_response(channel: str) -> Response:
    """
    fetches multi users data
    Args:
        channel (str): channel to query from
    Return: a JSON representation of the questions the named users
        posted and their responses, together with the questions
        they responded to with their responses
    """
    names = request.args.getlist("name")
    res["data"] = {}

    for username in names:
        if username.lower() != "me":
            user = Users.find_user(username.lower())
        else:
            user = g.user

        if not user:
            res_err["message"] = f"Invalid username {username}"
            return jsonify(res_err), 400

        db_data = Queries.get_user_questions_and_responses(user._id, channel)

        res["data"][username] = {
            "user_questions": db_data[0],
            "responded_questions": db_data[1],
        }
    return jsonify(res), 200


@channels.route("/<channel>/<username>/<question_title>", strict_slashes=False)
@login_required
def get_query_by_channel_uname_qtitle(
    channel: str, username: str, question_title_or_id: str
) -> Response:
    """
    Args:
        channel (str): channel to query from
        username (str): specified username for querying
        question_title_or_id: title or id to the questions

    Return: Returns a JSON representation of the question
        with the specified title if it is valid and associated
        with the user. If it is the user who posted the question,
        it shows the responses from others. Otherwise, it shows the
        response made by the user to the question.
    """
    user = None
    if username == "me":
        user = g.user
    else:
        user = Users.find_user(username.lower())

    if not user:
        return jsonify({"status": "error", "message": "Invalid Username"}), 400

    db_data = None
    question_title = question_title_or_id.replace("_", " ")

    if verify_query_id(question_title_or_id):
        q_id = question_title_or_id
        db_data = Queries.get_user_questions_and_responses(
            user._id, channel, _id=q_id)

        if len(db_data) == 0:  # incase the info was title and not id
            db_data = Queries.get_user_questions_and_responses(
                user._id, channel, question_title=question_title
            )
    else:
        db_data = Queries.get_user_questions_and_responses(
            user._id, channel, question_title=question_title
        )

    res["data"] = {
        "user_questions": db_data[0],
        "responded_questions": db_data[1]
        }

    return jsonify(res), 200


@channels.route("/<channel>/questions/<question_id_or_title>",
                strict_slashes=False)
@login_required
def get_question(channel, question_id_or_title) -> Response:
    """
    Args:
        channel (str): channel to query from
        username (str): specified username for querying
        question_id_or_title: title or id to the questions

    Return: a JSON representation of the question with the specified
        ID and its responses, if it is associated with the channel
    """
    query = None
    question_title = question_id_or_title.replace("_", " ")

    if verify_query_id(question_id_or_title):
        q_id = question_id_or_title
        query = Queries.find_query_by_id(channel=channel, _id=q_id)

        if len(query) == 0:  # incase the info was title and not id
            query = Queries.find_query_by_title(
                channel=channel, question_title=question_title
            )
    else:
        query = Queries.find_query_by_title(
            channel=channel, question_title=question_title
        )

    if not query:
        res["message"] = "Invalid channel, question title or id"
        return (
            jsonify(res),
            400,
        )

    res["data"] = query.to_dict()

    return jsonify(res), 200


@channels.route("/channel/response/<response_id>", strict_slashes=False)
@login_required
def get_response(response_id) -> Response:
    """
    computes the response
    Args:
        response_id (str): response id
    Return (response): json based on user info
    """
    res_err["message"] = "Invalid response id"
    id = ""
    try:
        id = ObjectId(response_id)
    except errors.InvalidId:
        return jsonify(res_err), 400

    query = Queries.object.filter(responses___id=id)
    response = None

    for res in query.responses:
        if res._id == id:
            response = res
            break

    if not query:
        return jsonify(res_err), 400

    data = {
        "question_id": query.id,
        "question": query.query_text,
        "response_id": str(id),
        "response": response.content,
        "responder": response.author,
        "created_at": response.created_at,
        "updated_at": response.updated_at,
    }
    res_suc = {
        "status": "success",
        "message": "Responses retrieved successfully",
        **data,
    }

    return jsonify(res_suc), 200
