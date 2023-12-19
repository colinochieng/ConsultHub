#!/usr/bin/env python3
"""
Modules for Channel Endpoints
"""
from flask import Blueprint


channels = Blueprint("channel", __name__, url_prefix="/api/channel/")


from api.channel.base import *
from api.channel.get import *
from api.channel.post import *
