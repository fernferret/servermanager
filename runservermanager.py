#!/usr/bin/env python

from servermanager import app, db
#db.drop_all()
db.create_all()
app.debug = app.config.get('DEBUG', False)

# This is required.
app.secret_key = app.config.get('SECRET_KEY', 'I\'m a secret!11!!1')

# TODO: Unhardcode this.
app.run(host=app.config.get('ADDRESS', '127.0.0.1'))

