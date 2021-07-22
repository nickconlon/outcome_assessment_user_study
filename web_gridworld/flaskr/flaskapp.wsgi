activate_this = '/var/www/html/flaskapp/flask/bin/activate_this.py'
exec(open(activate_this).read(), dict(__file__=activate_this))
import sys
sys.path.insert(0, '/var/www/html/flaskapp/flaskr')
from flaskapp import app as application
