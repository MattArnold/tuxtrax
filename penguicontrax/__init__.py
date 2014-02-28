from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
app = Flask(__name__)
db =  SQLAlchemy(app);      

from flask import render_template, g
from submission import Submission, Tag
from user import Login
import os, sqlite3, import2013schedule
from constants import constants


def init():
    app.secret_key = constants.SESSION_SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = constants.DATABASE_URL
    app.config.from_object(__name__)
    try:
        db.create_all()
    except Exception as e:
        print e
        pass
    # GET RID OF THIS LATER
    if len(Submission.query.all()) == 0:
        import2013schedule.import_old()
   
                
@app.route('/')
def index():
    submissions = Submission.query.all() if g.user is not None and g.user.staff == True else Submission.query.filter(Submission.followUpState != 3)
    tags = [tag.name for tag in Tag.query.all()]
    return render_template('index.html', tags=tags, submissions=submissions, user=g.user)
       
    

    
