from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
app = Flask(__name__)
db =  SQLAlchemy(app);      

from flask import render_template, g
from submission import Submissions, Tags
from user import Login
import os, sqlite3, import2013schedule
from constants import constants


def init():
    app.secret_key = constants.SESSION_SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = constants.DATABASE_URL
    app.config.from_object(__name__)
    try:
        db.create_all()
    except:
        pass
    # GET RID OF THIS LATER
    if len(Submissions.query.all()) == 0:
        import2013schedule.import_old()
   
                
@app.route('/')
def index():
    submissions = Submissions.query.all() if g.user is not None and g.user.staff == True else Submissions.query.filter(Submissions.followUpState != 3)
    tags = [tag.name for tag in Tags.query.all()]
    return render_template('index.html', tags=tags, submissions=submissions, user=g.user)
       
    

    
