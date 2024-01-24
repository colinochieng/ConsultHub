#!/usr/bin/env python3
"""
Module for Authentications
"""
from functools import wraps
from flask import g, jsonify, request, Response
from typing import Any, Callable
from db.docs import Users
from api import cache


err_res = {"status": "error", "message": ""}


def login_required(view_func) -> Callable[[str], Response]:
    """
    Custom decorator to check if the user is logged in
    Args:
        view_func (function): decorated view
    return: function
    """
    @wraps(view_func)
    def wrapper(*args, **kwargs) -> Callable[..., Response] | None:
        """
        describe: function for Authenticating user
        """
        auth_token = request.headers.get('X-API-Token')

        if not auth_token:
            auth_token = request.args.get("api_key")

        if not auth_token:
            err_res["message"] = "No API Authentication Token"
            return jsonify(err_res), 401

        username = cache.get(auth_token)

        if not username:
            err_res["message"] = "Invalid Token"
            return jsonify(err_res), 401

        g.user = Users.find_user(username)
        g.token = auth_token

        return view_func(*args, **kwargs)

    return wrapper


def json_required(func: Callable[..., Response]) -> Callable[..., Response]:
    """
    function to check whether the request contains JSON data
    Args:
        func: view function
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        """
        wrapper function
        """
        if not request.is_json:
            err_res = {"status": "error", "message": "Invalid or no JSON data"}
            return jsonify(err_res), 415
        return func(*args, **kwargs)

    return wrapper


def parse_pagination_params(func) -> Callable[..., Response]:
    """
    function to extracts the pagination parameters from the request
    on route functions that require similar pagination parameter parsing
    Args:
        func (Function): view function
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        data = request.get_json()
        page = data.get("page") or request.args.get("page")
        page_size = data.get("page_size") or request.args.get("page_size")

        try:
            if page:
                page = int(page)
            else:
                page = 0
            if page_size:
                page_size = int(page_size)
            else:
                page_size = 10
        except ValueError:
            err_res["message"] = "page or page_size must be numerals"
            return jsonify(err_res), 400

        g.page = page
        g.page_size = page_size

        return func(*args, **kwargs)

    return wrapper
