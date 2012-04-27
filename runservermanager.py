#!/usr/bin/env python

from servermanager import app, db
#db.drop_all()
db.create_all()
# Uncomment to enable debug.
app.debug = True

# This is required.
app.secret_key = 'A0Z&(*&B)(&)B(*b987b9n08&r98j/3yX R~XHH!jmN]LWX/,?RT'

# TODO: Unhardcode this.
app.run(host='74.91.113.244')

