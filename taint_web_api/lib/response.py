#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from flask import make_response
import json
import flask



def success(msg):
    res = flask.make_response(msg)
    res.headers['Access-Control-Allow-Origin'] = '*'
    res.headers['Access-Control-Allow-Methods'] = 'POST，GET,OPTIONS'
    res.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return res

def fail(msg):
    res = flask.make_response(msg)
    res.headers['Access-Control-Allow-Origin'] = '*'
    res.headers['Access-Control-Allow-Methods'] = 'POST，GET,OPTIONS'
    res.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'

    return res
