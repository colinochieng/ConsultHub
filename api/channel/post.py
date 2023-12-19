#!/usr/bin/env python3
"""
Module for dealing with
posting of Question and Responses
"""
from bson import ObjectId, errors
from flask import g, request, Response, jsonify
from api.channel import channels
from api.utils.emailing import send_emails
from api.utils.validate import verify_query_data_and_send_mail
from db.docs import Queries, Responses, Users

res_err = {"status": "error", "message": ""}
res_suc = {"status": "success", "message": ""}


@channels.route("/", methods=["POST"], strict_slashes=False)
def post_question() -> Response:
    """
    function for posting user question
    Returns: Response
    Note: for general's channel the query parameter should be set to true
    """
    general = request.args.get("general", False)
    channel = g.user.field

    if general:
        if general.lower() != "true":
            res_err["message"] = "Invalid value for generals query parameter"
            return jsonify(res_err), 400
        else:
            channel = "general"

    verification = verify_query_data_and_send_mail(
        request.get_json(), channel, g.user)

    if not verification:
        res_err["message"] = "Invalid query input"
        return jsonify(res_err), 400

    if len(verification[1]) == 0:
        res_suc["message"] = "Query posted successfully"
        return jsonify(res_suc), 200
    else:
        query = verification[2]
        res_suc["message"] = "Query posted successfully"
        res_suc["data"] = {"id": query.id, "content": query.query_text}
        res_suc["more_info"] = verification[1]
        return jsonify(res_suc), 200


@channels.route(
    "/<channel>/<question_id>/response", strict_slashes=False, methods=["POST"]
)
def post_response(channel, question_id) -> Response:
    """
    Post question based on id
    Args:
        - channel (str): question channel
        - question_id: id of the question responsing to
    """
    try:
        question_id = ObjectId(question_id)
    except errors.InvalidId:
        res_err["message"] = "Invalid question Id"
        return jsonify(res_err), 400
    query = Queries.find_query_by_id(question_id, channel)

    if not query:
        res_err["message"] = "No question with that Id"
        return jsonify(res_err), 400

    data = request.get_json()
    content = data.get("content", False)

    if not content or len(content) < 0:
        res_err["message"] = "Invalid content"
        return jsonify(res_err), 400

    query_res = Responses(content=content, author=g.user)
    query.update(push__responses=query_res)
    query.save()

    questioner = Users.objects(_id=query.author)

    contexts = {
        "questioner": questioner.username,
        "channel": channel,
        "question": query.query_text,
        "response": content,
        "response_id": query_res._id,
    }

    email_info = (contexts, questioner.email)
    subject = "Your ConsultHub Question Has a New Answer!"

    send_emails(subject, "response", email_info)

    data = {
        "question_id": query._id,
        "response_id": query_res._id,
        "question": query.query_text,
        "response": content,
    }
    res_suc.update({"data": data})
    res_suc["message"] = "Response Posted successfully"
    return jsonify(res_suc), 200
