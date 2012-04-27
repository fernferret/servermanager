from servermanager import db

import os, socket
from srcdslib.SourceQuery import SourceQuery
from srcdslib.SourceRcon import SourceRcon
import time
from threading import Timer

class Ad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    steam_id = db.Column(db.String(40))
    # this is so we know whos steam id is whos
    name = db.Column(db.String(40))
    nickname = db.String(80)
    admin = db.Column(db.Boolean)

    def make_admin(self, admin):
        self.admin = admin
        db.session.commit()

    @staticmethod
    def get(steam_id):
        # Always create the first user that logs in.
        if not User.query.count():
            user = User()
            user.steam_id = steam_id
            user.name = 'FernFerret'
            user.admin = True
            db.session.add(user)
            print "Creating initial user - %s" % steam_id
            return user 
        user = User.query.filter_by(steam_id=steam_id).first()
        if not user:
            return False
        return user

    @staticmethod
    def get_from_id(id):
        return User.query.filter_by(id=id).first()

    @staticmethod
    def get_all():
        return User.query.all()

    @staticmethod
    def create(name, steamid, admin):
        # Make sure the user isn't already registered.
        user = User.query.filter_by(steam_id=steamid).first()
        if user:
            return (False, "Error, user already exists!")
        new_user = User()
        new_user.steam_id = steamid
        new_user.name = name
        new_user.admin = admin
        db.session.add(new_user)
        return (True, "Success! User '%s' was created!" % name)

    @staticmethod
    def delete(id):
        user = User.query.filter_by(id=id).first()
        if not user:
            return False
        db.session.delete(user)
        db.session.commit()
        return True

class Server(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    type = db.Column(db.String(40))
    ip = db.Column(db.String(40))
    port = db.Column(db.Integer)
    game_type = db.Column(db.String(40))
    rcon = db.Column(db.String(80))
    location = db.Column(db.String(256))
    _server = None
    is_restarting = db.Column(db.Boolean)
    def __init__(self, name, ip, port, rcon, location, game_type):
        '''Creates a new server object.
        
        Params:
          name     - Friendly name of server.
          type     - Type of server, TF2 as an example.
          ip       - Ip of the server.
          port     - Port this server is running on.
          location - Location on disk, absolute path.
          '''
        self.name = name
        self.ip = ip
        self.port = port
        self.location = location
        self.rcon = rcon
        self.game_type = game_type
        self._get_source_binding()
        self._server = None

    def get_players(self):
        '''Return the number of players on the server.'''
        try:
            if not self._server:
                self._get_source_binding()
            return self._server.info()['numplayers']
        except socket.error:
            return "??"

    def _get_source_binding(self):
        self._server = SourceQuery(self.ip, self.port)

    def get_all_players(self):
        try:
            if not self._server:
                self._get_source_binding()
            return self._server.player()
        except socket.error:
            return "??"

    def get_mode(self):
        if not self.location:
            return "Error - Unknown Server Location"
        if not os.path.exists(location):
            return "Error - Server Location (%s) was not found." % location

    def restart(self, message=None):
        if not message:
            message = "Server is restarting in 10 seconds..."
        self._send_rcon('say sm_csay "%s"' % message)
        self.is_restarting = True
        db.session.commit()
        self._send_rcon('quit')
        # Derp. The server already waits 10 seconds...
        #Timer(10, self._send_rcon, ['quit']).start()
        return True

    def _send_rcon(self, cmd):
        print "Sending RCON!"  
        server = SourceRcon(self.ip, self.port, self.rcon)
        return server.rcon(cmd)

    @staticmethod
    def get(id):
        server = Server.query.filter_by(id=id).first()
        if not server:
            return False
        server._get_source_binding()
        # Verify that this server didn't come back online
        if server.is_restarting and not server.get_players() == "??":
            server.is_restarting = False
            db.session.commit()
        return server

    @staticmethod
    def create(name, address, port, rcon, servertype, path):
        server = Server.query.filter_by(name=name).first()
        if server:
            return (False, "Error: A server named '%s' already exists." % name)
        new_server = Server(name, address, port, rcon, path, servertype)
        db.session.add(new_server)
        return (True, "Success! A server named '%s' was created!" % name)
        
    @staticmethod
    def get_all():
        allservers = Server.query.all()
        for server in allservers:
            if server.is_restarting and not server.get_players() == "??":
                server.is_restarting = False
                db.session.commit()
        return allservers

    @staticmethod
    def delete(id):
        server = Server.query.filter_by(id=id).first()
        if not server:
            return False
        db.session.delete(server)
        db.session.commit()
        return True

