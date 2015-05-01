#!venv/bin/python
import sys 
sys.path.append('/Users/chris/Projects/lol/lib/')
sys.path.append("/Users/chris/Projects/lol/projects/winprob/wpmodel/")

from app import app
app.run(host="0.0.0.0", debug=True)
