#!/usr/bin/env python3
"""
Module for route/index and specific(channel)
under the channel blueprint
"""
from api.channel import channels
from flask import g, jsonify, redirect, request, Response, url_for
from db.docs import Queries
from api.utils.wraps import login_required, parse_pagination_params
from flasgger import swag_from

res = {
    "status": "success",
    "message": "User questions and responses retrieved successfully",
}


@channels.route("/<channel>/", strict_slashes=False)
@parse_pagination_params
@login_required
@swag_from("../../YAML/channels/get_channel.yml")
def handle_specific_channel(channel) -> Response:
    """
    function to handle request to a particular channel
    Args:
            channel(str): channel/field to check daat
    Return (Response): a JSON representation of questions
            posted to the channel with their responses (paginated).
    """
    queries, paginations_data = Queries.get_queries(
        channel, g.page, g.page_size)

    return jsonify({**res, "data": queries, **paginations_data}), 200


@channels.route("/", strict_slashes=False)
@parse_pagination_params
@login_required
@swag_from("../../YAML/channels/get_channels.yml")
def root_channel() -> Response:
    """
    function to compute the response for the base
            route under channel's blueprint
    Returns (Response): a JSON representation of questions
            posted to all channels with their responses (paginated)
            if query parameter all is true else defaults to general
            channel or else you need to specify the channel name
            as a query parameter.
    """
    err_res = {"status": "error", "message": "Invalid all parameter"}
    data = request.get_json()
    all_query = request.args.get("all", False) or data.get("all", False)
    channel = request.args.get("channel", "developer") or data.get(
        "channel", "developer"
    )

    if not all_query:
        return redirect(
            url_for("channel.handle_specific_channel", channel=channel)
            )

    if type(all) is str and all.lower() is True:
        queries, pagination_data = Queries.get_queries(
            channel, g.page, g.page_size
            )
        return jsonify({**res, "data": queries, **pagination_data}), 200

    return jsonify(err_res), 400
