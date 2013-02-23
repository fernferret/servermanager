activate_this = '/opt/venv/servermanager/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

import sys
sys.path.insert(0, '/opt/sw/servermanager')

from servermanager import app as application
