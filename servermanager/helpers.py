import json
import urllib2
import urllib
import re
import socket

## Functions ##
def get_my_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("google.com", 80))
    return s.getsockname()[0]
    
def get_steam_userinfo(steam_id, api_key=None):
    if api_key is None:
        return {}
    options = {
        'key': api_key,
        'steamids': steam_id
    }
    url = 'http://api.steampowered.com/ISteamUser/' \
          'GetPlayerSummaries/v0001/?%s' % urllib.urlencode(options)
    rv = json.load(urllib2.urlopen(url))
    return rv['response']['players']['player'][0] or {}

def convert_id_to_community(steam_id):
    match = re.match("^.*([01]):(\d+)$", steam_id)
    if not match:
        return None
    if len(match.groups()) != 2:
        return None
    return (int(match.group(2) * 2)) + 76561197960265728 + int(match.group(1))
