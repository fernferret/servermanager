===================
Sexy Server Manager
===================

.. image:: http://i.minus.com/i7npm9vP7QCnt.png

Installing
==========

To install the Sexy Server Manager, simply type::

    $ hg clone ssh://hg@bitbucket.org/fernferret/servermanager
    
    $ cd servermanager
    
    $ pip install -r requirements.txt

Note
----
You may need `sudo` to install the server manager::

    $ sudo pip install -r requirements.txt

Running
=======

Right now, the SSM is in development and does not yet have the hooks to run as a service (WSGI).

You can start it up in a screen session by running the bash script in the tools folder


First Run
=========

Copy the provided ``servermanager/settings.cfg.example`` to 
``servermanager/settings.cfg`` and edit the values inside it. The big one is 
the ``STEAM_API_KEY``. You can get one from here: http://steamcommunity.com/dev/apikey.

To run it quickly::

    $ ./runservermanager.py

Once you've started it up, simply login with steam.
The first user who logs in will become an administrator
and can add other users.

After this, you're on your own for now, until I feel
like writing more documentation...
