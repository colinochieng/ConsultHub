#!/usr/bin/env python3
"""
Module for Authentications
"""
import uuid
from flasgger import swag_from
from flask import Blueprint, g, jsonify, request, Response
from api.utils.wraps import login_required
from db.docs import Users
from api import cache

auth = Blueprint("auth", __name__, url_prefix="/api/auth/")

err_res = {"status": "error", "message": ""}
succ_res = {"status": "success", "message": ""}


@auth.route("/login/", methods=["POST"], strict_slashes=False)
@swag_from("../../YAML/Auth/login.yml")
def login_user() -> Response:
    """
    view to login user
    User: user is logged in Only for 24 hours
    """
    data = request.get_json()
    for _ in ["username", "password"]:
        if _ not in data.keys():
            err_res["message"] = "username or password missing for login"
            return jsonify(err_res), 400

    username = data.get("username").lower()
    password = data.get("password")

    user = Users.find_user(username)

    if not user:
        err_res["message"] = "Invalid username"
        return jsonify(err_res), 400
    else:
        if not user.check_pwd(password):
            err_res["message"] = "Invalid password"
            return jsonify(err_res), 400

    api_token = str(uuid.uuid4())

    # save to cache
    if cache.set(api_token, username):
        succ_res["message"] = "Token created"
        succ_res["data"] = {"token": api_token}
        return jsonify(succ_res), 200

    err_res["message"] = "Failed to create token"
    return jsonify(err_res), 400


@auth.route("/logout/", methods=["POST"], strict_slashes=False)
@login_required
@swag_from("../../YAML/Auth/logout.yml")
def logout() -> Response:
    """
    logs out logged in user
    """
    cache.delete(g.token)  # if exists

    res = jsonify()
    res.status_code = 200

    return res
