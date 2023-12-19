#!/usr/bin/env python3
"""
module for config object
"""
from os import getenv


class Config:
    """
    Class for flask app configuration
    """

    SECRET_KEY = getenv("SECRET_KEY", "33bfbd31c16d76519e6bae8f0ac569c7")
    DEBUG = getenv("DEBUG", None) == "True"
    MONGODB_SETTINGS = {
        "db": getenv("MONGO_DB", "consultdb"),
        "host": getenv("MONGO_HOST", "127.0.0.1"),
        'port': int(getenv('MONGO_PORT', '27017')),
        "alias": "default"
    }
