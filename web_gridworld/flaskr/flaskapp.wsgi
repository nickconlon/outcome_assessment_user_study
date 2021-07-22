activate_this = '/var/www/html/web_gridworld/venv/bin/activate_this.py'
exec(open(activate_this).read(), dict(__file__=activate_this))
import sys
sys.path.insert(0, '/var/www/html/web_gridworld/web_gridworld/flaskr')
from flaskapp import app as application
