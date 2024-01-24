#!/usr/bin/env python3
"""
Module for user verifications
"""
from flask import Blueprint, Response, jsonify, request, g
from api.utils.validate import validate_notifications
from api.utils.wraps import json_required, login_required
from flasgger import swag_from

from db.docs import Users


users_endpoints = Blueprint("users", __name__, url_prefix="/api/users/")

invalid_notifications = {"status": "error", "message": "Invalid notifications"}
invalid_field = {"status": "error", "message": "Invalid field"}


@users_endpoints.route("/<username>", strict_slashes=False)
@login_required
@swag_from("../../YAML/users/get.yaml")
def get_user(username) -> Response:
    """
    function to retrives user info
    Args:
        username(str): username to use in fetching db
    """
    if username == "me":
        return jsonify(g.user.to_dict()), 200
    user = Users.find_user(username)

    if not user:
        return jsonify({"status": "error", "message": "Invalid username"}), 400
    return jsonify(user.to_dict()), 200


@users_endpoints.route("/", strict_slashes=False,
                       endpoint="with_field", methods=["PUT"])
@users_endpoints.route(
    "/notifications", endpoint="without_field",
    strict_slashes=False, methods=["PUT"]
)
@json_required
@login_required
@swag_from("../../YAML/users/put_user.yml")
@swag_from("../../YAML/users/put_notifications.yml")
def handle_user() -> Response:
    """
    function to updates and retrive user info
    Note: can only update field and notifications
        other updates (including unknown fields) are discarded
    """
    user = user = g.user

    data = request.get_json()
    field = data.get("field")
    notifications = data.get("notifications")

    if request.path.find("/notifications") != -1:  # notications path
        field = None

    if not field and not notifications:
        return jsonify({"status": "success", "message": "empty update"}), 200

    if field and type(field) is not str:
        return jsonify(invalid_field), 400
    elif field.isspace() or not field.isalpha():
        return jsonify(invalid_field), 400

    if notifications and not validate_notifications(notifications):
        return jsonify(invalid_notifications), 400

    update = {}

    if field:
        update["field"] = field
    if notifications:
        update["notifications"] = notifications

    user.update_user(**update)

    return jsonify(user.to_dict()), 200
