#!/usr/bin/env python

from flask import Flask, render_template, session, redirect, url_for, escape, request, g, flash
from flask_sqlalchemy import SQLAlchemy
from flaskext.openid import OpenID

app = Flask(__name__)
app.config.from_pyfile('settings.cfg')
db = SQLAlchemy(app)
oid = OpenID(app)
my_globals = {}

import servermanager.models
import servermanager.routes
import servermanager.helpers
