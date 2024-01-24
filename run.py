#!/usr/bin/env python3
"""
Module for starting the API
"""
from api.app import app

app.run("127.0.0.1", 5000)
