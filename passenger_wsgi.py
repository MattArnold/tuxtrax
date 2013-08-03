import sys, os
INTERP = os.path.join(os.environ['HOME'], 'flask_env', 'bin', 'python')
if sys.executable != INTERP:
	os.execl(INTERP, INTERP, *sys.argv)
sys.path.append(os.getcwd())

from flask import Flask
application = Flask(__name__)
 
sys.path.append('penguicontrax')
from penguicontrax.penguicontrax import app as application
