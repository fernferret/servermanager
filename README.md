# Sexy Server Manager
![Server Manager in action](http://i.minus.com/i7npm9vP7QCnt.png)

## Installing
If I were you, I'd use [virtualenv](https://pypi.python.org/pypi/virtualenv).
Install that first:
```console
$ sudo pip install virtualenv
```

### Make a new Virtual Env
```console
$ virtualenv /opt/venv/ssm

$ source /opt/venv/ssm/bin/activate
```

**Note: The name of your virtual env will appear inside parenthesis: ``(ssm)`` in this example. 
If you don't see that, maybe you didn't source the proper [activate](http://www.virtualenv.org/#activate-script) script!**

### Install the Sexy Server Manager
```console
(ssm)$ cd /opt/sw

(ssm)$ git clone git://github.com/FernFerret/servermanager.git

(ssm)$ cd servermanager

(ssm)$ pip install -r requirements.txt
```

## First Run
Copy the provided ``servermanager/settings.cfg.example`` to
``servermanager/settings.cfg`` and edit the values inside it. The big one is
the ``STEAM_API_KEY``. You can get one from here:
[http://steamcommunity.com/dev/apikey](http://steamcommunity.com/dev/apikey).

Once you've started it up, simply login with steam.
The first user who logs in will become an administrator
and can add other users.

After this, you're on your own for now, until I feel
like writing more documentation...

### Quick Run
You can either use the provided wsgi script, or to get going quickly, just run:
To get going ASAP, just run:
```console
(ssm)$ python runservermanager.py
```

**Don't forget to [source your virtualenv](#make-a-new-virtual-env) script first!**

### Run with mod_wsgi
When you've given it all of your tweaks, use the provided [wsgi script](https://github.com/FernFerret/servermanager/blob/master/servermanager.wsgi)
to add to Apache!

TODO: Show my apache config!
