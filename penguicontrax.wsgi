import sys
sys.path.insert(0, '/var/www/penguicontrax/venv/penguicontrax')
activate_this = '/var/www/penguicontrax/venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))
from penguicontrax import app as application
