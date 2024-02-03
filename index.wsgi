activate_this = '/home/c/cc68639/findimper/public_html/venv/bin/activate_this.py'
exec(open(activate_this).read())
 
import sys
sys.path.remove('/usr/lib/python3/dist-packages')
sys.path.insert(0, '/home/c/cc68639/findimper/public_html/web')
sys.path.insert(1, '/home/c/cc68639/findimper/public_html/venv/lib/python3.6/site-packages')

import os
os.chdir(os.path.dirname(__file__) + '/web')
 
from flaskapp import app as application