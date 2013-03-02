from servermanager import app, oid, db, my_globals
from servermanager.models import User, Server
from flask import render_template, session, redirect, url_for, request, g, flash, get_flashed_messages
from functools import wraps
import time
import re
import random
import json
from pyfile import write_pyfile

from servermanager.helpers import get_steam_userinfo, get_my_ip

_steam_id_re = re.compile('steamcommunity.com/openid/id/(.*?)$')

## Route Helpers ##
def admin_required(function):
    @wraps(function)
    def decorated(*args, **kwargs):
        if not g.user.admin:
            flash('Error, please login through Steam to view this page.', category='error')
            return redirect(url_for('index'))
        return function(*args, **kwargs)
    return decorated

def login_required(function):
    @wraps(function)
    def decorated(*args, **kwargs):
        if not g.user:
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
        flash("Error, Could not log in. You don't have an account.", category='error')
        return redirect(url_for('index'))
    steamdata = get_steam_userinfo(g.user.steam_id, app.config['STEAM_API_KEY'])
    g.user.nickname = steamdata['personaname']
    db.session.commit()
    session['user_id'] = g.user.id
    session['user_admin'] = g.user.admin
    session['user_nick'] = g.user.nickname
    session['avatar'] = steamdata['avatar']
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
@login_required
def servers():
    return render_template('servers.html', servers=Server.get_all(), lock=app.config.get('LOCKSERVERS', True))

@app.route('/server/view/<server>/<viewtab>/', methods=['GET', 'POST'])
@app.route('/server/view/<server>/', methods=['GET', 'POST'])
@login_required
def view_server(server=None, viewtab=None):
    if viewtab not in ['info', 'settings', 'rcon', 'edit']:
        return redirect(url_for('view_server', server=server, viewtab='info'))
    if not g.user.admin and viewtab in ['rcon', 'edit']:
        return redirect(url_for('view_server', server=server, viewtab='info'))
    if request.method == 'POST':
        if viewtab == 'settings':
            if request.form['action'] == 'sendmsg' and request.form['saytext']:
                server_obj = Server.get(server)
                server_obj._send_rcon("sm_csay '%s: %s'" % (session['user_nick'], request.form['saytext']))
                flash("Message sent!", category='success')
            elif request.form['action'] == 'alltalk':
                server_obj = Server.get(server)
                if 'enable' in request.form:
                    flash("Alltalk temporarily Enabled!", category='success')
                    server_obj._send_rcon("sv_alltalk 1")
                else:
                    flash("Alltalk temporarily Disabled!", category='success')
                    server_obj._send_rcon("sv_alltalk 0")
            elif request.form['action'] == 'changepass':
                server_obj = Server.get(server)
                if len(request.form['srvpass']) == 0:
                    server_obj._send_rcon('sv_password ""')
                else:
                    server_obj._send_rcon("sv_password "+request.form['srvpass'])
                flash("Password set!", category='success')
            else:
                flash(request.form, category='success')
    return render_template('view_server.html', server=Server.get(server), servers=Server.get_all(), viewtab=viewtab, lock=app.config.get('LOCKSERVERS', True))

@app.route('/servers/add/', methods=['GET', 'POST'])
@admin_required
def add_server():
    errors = []
    values = {}
    required = ['name', 'address', 'rcon', 'servertype', 'port', 'path']
    if request.method == 'POST':
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
    return render_template('users.html', users=User.get_all())

@app.route('/settings/', methods=['GET', 'POST'])
@admin_required
def settings():
    values = {}
    if request.method == 'POST':
        values['STEAM_API_KEY'] = str(app.config['STEAM_API_KEY'])
        values['SECRET_KEY'] = str(app.config['SECRET_KEY'])
        values['ADDRESS'] = str(app.config['ADDRESS'])
        values['SQLALCHEMY_DATABASE_URI'] = str(app.config['SQLALCHEMY_DATABASE_URI'])
        values['TITLE'] = str(request.form['title'])
        values['LOCKSERVERS'] = request.form.get('lockservers', None) is not None
        values['DEBUG'] = request.form.get('debug', None) is not None
        values['TEST'] = request.form.get('test', None) is not None
        values['ALLOW_LOCAL'] = request.form.get('allowlocal', None) is not None
        write_pyfile(app.config['CFG_FILE'], values)
        # Now set our config values properly
        for key, value in values.iteritems():
            app.config[key] = value
        flash('Success! Your settings were updated.', category='success')
    return render_template('settings.html')

@app.route('/users/add/', methods=['GET', 'POST'])
@admin_required
def add_user():
    errors = []
    values = {}
    if request.method == 'POST':
        values['name'] = request.form['name']
        values['steamid'] = request.form['steamid']
        values['admin'] = request.form.get('admin', None) is not None
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
        if int(request.form['delete']) == g.user.id:
            return "You cannot delete yourself!", 403
    except ValueError:
        return "Fail.", 403
    if User.delete(int(request.form['delete'])):
        return "Success."
    return "Fail.", 403

@app.route('/users/makeadmin/', methods=['POST', 'GET'])
@admin_required
def make_admin():
    print "Making Admin"
    try:
        if int(request.form['userid']) == g.user.id:
            return "You cannot modify your own admin privs.", 403
    except ValueError:
        return "Fail.", 403
    user = User.get_from_id(int(request.form['userid']))
    admin = request.form['admin'].lower() == 'true'
    if user:
        user.make_admin(admin)
        session['user_admin'] = user.admin
        session.modified = True
        print "Session is MOdded"
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

@app.route('/rcon', methods=['POST', 'GET'])
@admin_required
def issue_rcon():
    try:
        server = Server.get(int(request.form['serverid']))
        return server._send_rcon(request.form['cmd'])
    except ValueError:
        return "Fail.", 403
    return "Whoops! Something bad happened..."

@app.route('/rcon/<serverid>', methods=['POST'])
@admin_required
def issue_rcon_better(serverid=None):
    try:
        server = Server.get(int(serverid))
        return server._send_rcon(request.form['cmd'])
    except ValueError:
        return "Fail.", 403
    return "Whoops! Something bad happened..."

@app.route('/data/maps/<serverid>', methods=['GET', 'POST'])
@login_required
def list_maps(serverid=None):
    try:
        server = Server.get(int(serverid))
        map_list = [a.split(" ")[-1][0:-4] for a in server._send_rcon("maps *").split("\n")]
        # Pop off the first element, it's always going to be '-------------'
        map_list.pop(0)
        map_list.pop(-1)
        return json.dumps(map_list)
    except Exception:
        # Probably an RCON failure
        return "Fail.", 403
    return "Yep!"

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

