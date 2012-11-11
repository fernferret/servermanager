#!/usr/bin/env python

import os, sys
from flask import Flask, render_template, session, redirect, url_for, escape, request, g, flash
from flask_sqlalchemy import SQLAlchemy
from flask_openid import OpenID

app = Flask(__name__)
try:
    app.config.from_pyfile('settings.cfg')
    app.config['CFG_FILE'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.cfg')
except IOError:
    my_path = os.path.dirname(os.path.abspath(__file__))
    print "ERROR: No 'settings.cfg' file found!"
    print "Did you forget to copy %s/settings.cfg.example " \
          "to %s/settings.cfg?" % (my_path, my_path)
    sys.exit(1)
db = SQLAlchemy(app)
oid = OpenID(app)
my_globals = {}

import servermanager.models
import servermanager.routes
import servermanager.helpers
