#!/usr/bin/env python3
"""
Module for defining flask core Application
"""
from flask_mongoengine import MongoEngine
from api import cache
from api.utils.config import Config
from flask import Flask, g, Response, jsonify, redirect, request, url_for
from db.docs import Users, Queries, Notifications, Responses
from api.utils.validate import (
    validate_email,
    validate_password,
    validate_uname,
    validate_notifications,
)
from api.users.endpoints import users_endpoints
from api.Auth.auth import auth
from api.channel import channels


app = Flask(__name__)
app.config.from_object(Config)
app.register_blueprint(users_endpoints)
app.register_blueprint(auth)
app.register_blueprint(channels)

mongo = MongoEngine(app)

err_res = {"status": "error", "message": ""}
succ_res = {"status": "success", "message": ""}


@app.route("/status", strict_slashes=False)
def status() -> Response:
    """
    view for status
    """
    return jsonify({"status": "success"}), 200


@app.route("/register", methods=["POST"], strict_slashes=False)
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
        err_res["message"] = "Invalid username, password or email"
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
def get_general_channel() -> Response:
    """
    view for general channel
    Redirected to the channel's route
    """
    return redirect(
        url_for("channel.handle_specific_channel", channel="general")
        )


@app.before_request
def before_request() -> Response | None:
    """
    Function to execute before any request
    """
    non_token_paths = [
        "/status",
        "/status/",
        "/register/",
        "/register",
        "/api/auth/login",
        "/api/auth/login/",
    ]

    if request.path not in non_token_paths:
        token = request.headers.get("X-Api-Token")

        if not token:
            token = request.args.get("api_key")

        if not token:
            err_res["message"] = "No API Authentication Token"
            return jsonify(err_res), 400

        username = cache.get(token)

        if not username:
            err_res["message"] = "Invalid API Authentication Token"
            return jsonify(err_res), 401

        user = Users.find_user(username)
        if not user:
            err_res["message"] = "No account with the username"
            return jsonify(err_res), 400

        g.user = user
        g.token = token


@app.teardown_appcontext
def close_connection(response_or_error=None) -> None:
    """
    Function to close and teardown relevant connections
    """
    cache.close()
