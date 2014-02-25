from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from contextlib import closing
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.openid import OpenID
import os

app = Flask(__name__)
app.secret_key = 'DEVELOPMENT_SECRET_KEY_CHANGE_ME_PLEASE' 
os.environ['DATABASE_URL'] = 'sqlite:///penguicontrax.db'
os.environ['OID_STORE'] = 'openid_store'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app);
app.config.from_object(__name__)
oid = OpenID(app, os.environ['OID_STORE'], safe_roots=[])

class Submissions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120))
    title = db.Column(db.String(120))
    description = db.Column(db.String(120))
    comments = db.Column(db.String(120))
    firstname = db.Column(db.String(120))
    lastname = db.Column(db.String(120))
    trackId = db.Column(db.Integer())
    duration = db.Column(db.Boolean()) 
    setupTime = db.Column(db.Boolean()) 
    repetition = db.Column(db.Boolean()) 
    followUpState = db.Column(db.Integer()) # 0 = submitted, 1 = followed up, 2 = accepted, 3 = rejected
        
    def __init(self):
        pass

    def __repr__(self):
        return '<email: %s, title: %s>' % self.name, self.email

class Tags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<name: %s>' % self.name

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(50))
    lastName = db.Column(db.String(50))
    staff = db.Column(db.Boolean())
    email = db.Column(db.String(120))
    openid = db.Column(db.String(200))
    points = db.Column(db.Integer())

    def __repr__(self):
        return '<name: %s %s, email: %s>' % self.firstName, self.lastName, self.email

class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    staffId = db.Column(db.Integer())

    def __init__(self, name, staffId):
        self.name = name
        self.staffId = staffId

    def __repr__(self):
        return '<name: %s, staffId: %d>' % self.name, self.staffId

@app.route('/')
def index():
    lookup_current_user()
    submissions = Submissions.query.all()
    tags = [tag.name for tag in Tags.query.all()]
    return render_template('index.html', tags=tags, submissions=submissions, user=g.user)

@app.route('/eventform')
def event_form():
    tags = [tag.name for tag in Tags.query.all()]
    return render_template('form.html', tags=tags)

@app.route('/submitevent', methods=['POST'])
def submitevent():
    submission = Submissions()
    submission.email = request.form['email']
    submission.title = request.form['title']
    submission.description = request.form['description']
    submission.duration = request.form['duration']
    submission.setupTime = request.form['setuptime'] if request.form['setuptime'] is not None else 1 
    submission.repetition = request.form['repetition']
    submission.comments = request.form['comments']
    submission.firstname = request.form['firstname']
    submission.lastname = request.form['lastname']
    db.session.add(submission)
    db.session.commit()
    return render_template('index.html')

@app.route('/createtag', methods=['POST'])
def createtag():
    tag = Tags(request.form['tagname'])
    db.session.add(tag)
    db.session.commit()
    return render_template('index.html')
    
@app.before_request
def lookup_current_user():
    g.user = None
    if 'openid' in session:
        openid = session['openid']
        g.user = User.query.filter_by(openid=openid).first()
        
@app.route('/login', methods=['GET'])
@oid.loginhandler
def login():
    if g.user is not None:
        return redirect(oid.get_next_url())
    provider = request.args.get('provider', '')
    if provider == 'google':
        api_url = 'https://www.google.com/accounts/o8/id'
    elif provider == 'yahoo':
        api_url = 'http://me.yahoo.com'
    else:
        return redirect(oid.get_next_url())
    return oid.try_login(api_url, ask_for=['email','fullname'])

@oid.after_login
def new_user(resp):
    session['openid'] = resp.identity_url
    lookup_current_user()
    if g.user is None:
        user = User()
        user.email = resp.email
        user.openid = resp.identity_url
        space = resp.fullname.rfind(' ')
        user.firstName = resp.fullname[:space]
        user.lastName = resp.fullname[space+1:]
        user.staff = False
        user.points = 5
        db.session.add(user)
        db.session.commit()
    return redirect(oid.get_next_url())

@app.route('/logout')
def logout():
    session.pop('openid', None)
    return redirect(oid.get_next_url())

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)