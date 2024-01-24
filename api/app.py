#!/usr/bin/env python3
"""
Module for defining flask core Application
"""
from api import cache
from api.utils.config import Config
from api.utils.validate import (
    validate_email,
    validate_password,
    validate_uname,
    validate_notifications,
)
from api.utils.wraps import json_required, login_required
from api.users.endpoints import users_endpoints
from api.Auth.auth import auth
from api.channel import channels
from db.docs import Users, Queries, Notifications, Responses

from flask_mongoengine import MongoEngine
from flask import Flask, g, Response, jsonify, redirect, request, url_for
from flasgger import swag_from, Swagger


app = Flask(__name__)
app.config.from_object(Config)
app.register_blueprint(users_endpoints)
app.register_blueprint(auth)
app.register_blueprint(channels)

mongo = MongoEngine(app)
swagger = Swagger(app)


err_res = {"status": "error", "message": ""}
succ_res = {"status": "success", "message": ""}


@app.route('/', strict_slashes=False)
@swag_from("../YAML/base/index.yml")
def index() -> Response:
    """
    View for the route path
    """
    succ_res["message"] = 'Welcome to ConsultHub API'
    return jsonify(succ_res), 200


@app.route("/status", strict_slashes=False)
@swag_from("../YAML/base/status.yml")
def status() -> Response:
    """
    view for status
    """
    return jsonify({"status": "success"}), 200


@app.route("/register", methods=["POST"], strict_slashes=False)
@json_required
@swag_from("../YAML/base/register.yml")
def create_account() -> Response:
    """
    function to create a user account
    Returns: Response with correct message and string
    """
    data = request.get_json()

    missing = {}

    REQUIRED = ["username", "email", "password", "field"]

    # check for missing Field
    for _ in REQUIRED:
        if _ not in data.keys():
            missing.update({_: "Info required but missing"})

    if len(missing) > 0:
        err_res["message"] = missing
        return jsonify(err_res), 400

    username = data.get("username").lower()
    email = data.get("email").lower()
    password = data.get("password")
    field = data.get("field")
    notifications = data.get("notifications")

    # Validate fields
    if (
        not validate_uname(username)
        or not validate_password(password)
        or not validate_email(email)
    ):
        err_res["message"] = "Invalid username, password or email(only Gmail)"
        return jsonify(err_res), 400

    if len(field) == 0:
        err_res["message"] = "Field cannot be empty"
        return jsonify(err_res), 400

    if Users.find_user(username):
        err_res["message"] = "Account with username already exists"
        return jsonify(err_res), 409

    if Users.find_user_by_email(email):
        err_res["message"] = "Account with email already exists"
        return jsonify(err_res), 409

    if notifications and not validate_notifications(notifications):
        err_res["message"] = "Invalid notifications"
        return jsonify(err_res), 400
    else:
        if not notifications:
            notifications = {"own_channel": True, "general_channel": False}

    user = Users(
        username=username,
        password=password,
        email=email,
        field=field,
        notifications=notifications,
    )

    user.save()

    return jsonify({**user.to_dict(), "id": str(user.id)}), 201


@app.route("/api/general", strict_slashes=False)
@login_required
@swag_from("../YAML/base/api_general.yml")
def get_general_channel() -> Response:
    """
    view for general channel
    Redirected to the channel's route
    """
    return redirect(
        url_for("channel.handle_specific_channel", channel="general")
        )


@app.teardown_appcontext
def close_connection(response_or_error=None) -> None:
    """
    Function to close and teardown relevant connections
    """
    cache.close()
