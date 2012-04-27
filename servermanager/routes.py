from servermanager import app, oid, db, my_globals
from servermanager.models import User, Server
from flask import render_template, session, redirect, url_for, request, g, flash, get_flashed_messages
from functools import wraps
import time
import re
import random

from servermanager.helpers import get_steam_userinfo, get_my_ip

_steam_id_re = re.compile('steamcommunity.com/openid/id/(.*?)$')

if app.config.get('TEST', False):
    session['user_admin'] = True
    session['user_id'] = 'TEST_ID'
## Route Helpers ##
def admin_required(function):
    @wraps(function)
    def decorated(*args, **kwargs):
        if not 'user_admin' in session or not session['user_admin']:
            flash('Error, please login through Steam to view this page.', category='error')
            return redirect(url_for('index'))
        return function(*args, **kwargs)
    return decorated

def login_required(function):
    @wraps(function)
    def decorated(*args, **kwargs):
        print session
        if not 'user_id' in session:
            flash('Error, please login through Steam to view this page.', category='error')
            return redirect(url_for('index'))
        return function(*args, **kwargs)
    return decorated

## Routes ## 

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login/')
@oid.loginhandler
def login():
    if g.user is not None:
        return redirect(oid.get_next_url())
    return oid.try_login('http://steamcommunity.com/openid')

@oid.after_login
def check_login(resp):
    match = _steam_id_re.search(resp.identity_url)
    g.user = User.get(match.group(1))
    if not g.user:
        flash('Error, Could not log in. You don\'t have an account.', category='error')
        return redirect(url_for('index'))
    steamdata = get_steam_userinfo(g.user.steam_id)
    g.user.nickname = steamdata['personaname']
    db.session.commit()
    session['user_id'] = g.user.id
    session['user_admin'] = g.user.admin
    session['user_nick'] = g.user.nickname
    flash('You are logged in as %s' % g.user.nickname, category='success')
    return redirect(oid.get_next_url())

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_nick', None)
    session.pop('user_admin', None)
    flash('You\'ve been logged out.', category='info')
    return redirect(url_for('index'))

@app.route('/servers/')
@app.route('/servers/view/<server>/')
@login_required
def servers():
    return render_template('servers.html', servers=Server.get_all(), lock=app.config.get('LOCKSERVERS', True))

@app.route('/servers/add/', methods=['GET', 'POST'])
@admin_required
def add_server():
    errors = []
    values = {}
    required = ['name', 'address', 'rcon', 'servertype', 'port', 'path']
    if request.method == 'POST':
        print request.form
        values['name'] = request.form['name']
        values['address'] = request.form['address']
        values['rcon'] = request.form['rcon']
        values['servertype'] = request.form['servertype']
        values['port'] = request.form['port']
        values['path'] = request.form['path']
        for key, value in values.items():
            if not value:
                errors.append(key)
        if not errors:
            success, msg = Server.create(values['name'], values['address'], values['port'], values['rcon'], values['servertype'], values['path'])
            if success:
                flash(msg, category='success')
                db.session.commit()
            else:
                flash(msg, category='error')
            return redirect(url_for('servers'))
    return render_template('add_server.html', values=values, errors=errors)

@app.route('/users/')
@admin_required
def users():
    for user in User.query.all():
        print user.name
    return render_template('users.html', users=User.get_all())

@app.route('/users/add/', methods=['GET', 'POST'])
@admin_required
def add_user():
    errors = []
    values = {}
    if request.method == 'POST':
        values['name'] = request.form['name']
        values['steamid'] = request.form['steamid']
        values['admin'] = request.form.get('admin', None) != None
        for key, value in values.items():
            if value == '':
                errors.append(key)
        if not errors:
            success, msg = User.create(values['name'], values['steamid'], values['admin'])
            if success:
                flash(msg, category='success')
                db.session.commit()
            else:
                flash(msg, category='error')
            return redirect(url_for('add_user'))
    return render_template('add_user.html', errors=errors, values=values)

@app.route('/users/delete/', methods=['POST'])
@admin_required
def delete_user():
    try:
        if int(request.form['delete']) == session['user_id']:
            return "You cannot delete yourself!", 403
    except ValueError:
        return "Fail.", 403
    if User.delete(int(request.form['delete'])):
        return "Success."
    return "Fail.", 403
        
@app.route('/users/makeadmin/', methods=['POST'])
@admin_required
def make_admin():
    print "Fish"
    print request.form
    try:
        if int(request.form['userid']) == session['user_id']:
            return "You cannot modify your own admin privs.", 403
    except ValueError:
        return "Fail.", 403
    user = User.get_from_id(int(request.form['userid']))
    admin = request.form['admin'].lower() == 'true'
    print "here", user
    if user:
        user.make_admin(admin)
        return "Success"
    return "Fail.", 403

@app.route('/servers/restart/', methods=['POST'])
@login_required
def restart_server():
    if not hasattr(g, 'wait_time'):
        g.wait_time = {}
    try:
        server = Server.get(int(request.form['serverid']))
        # TODO: Put other logic here.
        if not server.is_restarting:
            status = server.restart()
            my_globals['wait_time%s' % server.id] = time.time() + 11
            return "Success"
    except ValueError:
        return "Fail.", 403
    return "Success."

@app.route('/servers/restart/status/', methods=['POST'])
@login_required
def restart_status():
    '''Returns success if the server is done restarting.'''
    try:
        server = Server.get(int(request.form['serverid']))
        if time.time() < my_globals['wait_time%s' % server.id]:
            return "Fail", 403
        if server.is_restarting:
            return "Fail.", 403
    except ValueError:
        return "Fail.", 403
    return "Success"

@app.route('/servers/delete/', methods=['POST'])
@admin_required
def delete_server():
    try:
        if Server.delete(int(request.form['serverid'])):
            return "Success."
    except ValueError:
        return "Fail.", 403
    return "Fail.", 403


