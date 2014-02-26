from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from contextlib import closing
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.openid import OpenID
from flask_oauth import OAuth
from penguicontrax_constants import penguicontrax_constants
import os, sqlite3, import2013schedule

app = Flask(__name__)
if not os.path.isfile(penguicontrax_constants.DATABASE_FILE):
    with app.open_resource('schema.sql', mode='r') as f:
        with sqlite3.connect(penguicontrax_constants.DATABASE_FILE) as sqlitedb:
            try:
                sqlitedb.cursor().executescript(f.read())
                sqlitedb.commit()
            except:
                pass
            # GET RID OF THIS LATER
            import2013schedule.import_old()
            
app.secret_key = penguicontrax_constants.SESSION_SECRET_KEY
os.environ['DATABASE_URL'] = penguicontrax_constants.DATABASE_URL
os.environ['OID_STORE'] = penguicontrax_constants.OPENID_STORE
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app);
app.config.from_object(__name__)
oid = OpenID(app, os.environ['OID_STORE'], safe_roots=[])
oauth = OAuth()
twitter = oauth.remote_app('twitter',
    base_url='https://api.twitter.com/1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authorize',
    consumer_key=penguicontrax_constants.TWITTER_KEY,
    consumer_secret=penguicontrax_constants.TWITTER_SECRET_KEY
)
facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=penguicontrax_constants.FACEBOOK_APP_ID,
    consumer_secret=penguicontrax_constants.FACEBOOK_SECRET,
    request_token_params={'scope': 'email'}
)

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
    oauth_token = db.Column(db.String(200))
    oauth_secret = db.Column(db.String(200))

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
    submissions = Submissions.query.all() if g.user is not None and g.user.staff == True else Submissions.query.filter(Submissions.followUpState != 3)
    tags = [tag.name for tag in Tags.query.all()]
    return render_template('index.html', tags=tags, submissions=submissions, user=g.user)

@app.route('/eventform', methods=['GET', 'POST'])
def event_form():
    lookup_current_user()
    tags = [tag.name for tag in Tags.query.all()]
    if request.method == 'GET':
        eventid = request.args.get('id',None)
        if eventid is not None:
            event = Submissions.query.filter_by(id=eventid).first()
        else:
            event = None
    return render_template('form.html', tags=tags, event=event, user=g.user)

@app.route('/submitevent', methods=['POST'])
def submitevent():
    eventid = request.form['eventid']
    if eventid is not None:
        submission = Submissions.query.filter_by(id=eventid).first()
    if submission is None:
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
    submission.followUpState = request.form['followupstate'] if request.form['followupstate'] is not None else 0
    db.session.add(submission)
    db.session.commit()
    return redirect('/')

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
    elif 'oauth_token' in session:
        oa = session['oauth_token']
        g.user = User.query.filter_by(oauth_token=oa[0], oauth_secret=oa[1]).first()
        
@app.route('/login', methods=['GET'])
@oid.loginhandler
def login():
    if g.user is not None:
        return redirect(oid.get_next_url())
    provider = request.args.get('provider', '')
    if provider == 'google':
        return oid.try_login('https://www.google.com/accounts/o8/id', ask_for=['email','fullname'])
    elif provider == 'yahoo':
        return oid.try_login('http://me.yahoo.com', ask_for=['email','fullname'])
    elif provider == 'facebook':
        return facebook.authorize(callback=url_for('oauth_authorized',next=request.args.get('next') or request.referrer or None))
    elif provider == 'twitter':
        return twitter.authorize(callback=url_for('oauth_authorized',next=request.args.get('next') or request.referrer or None))
    return redirect(oid.get_next_url())


@oid.after_login
def new_openid_user(resp):
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

@twitter.tokengetter
@facebook.tokengetter
def get_oauth_token(token=None):
    lookup_current_user()
    if g.user is None:
        return None
    return (g.user.oauth_token, g.user.oauth_secret)

@app.route('/oauth-authorized')
@twitter.authorized_handler
@facebook.authorized_handler
def oauth_authorized(resp):
    next_url = request.args.get('next') or url_for('/')
    if resp is None:
        flash('You denied the request to sign in.')
        return redirect(next_url)
    session['oauth_token'] = (resp['oauth_token'], resp['oauth_token_secret'])
    lookup_current_user()
    if g.user is None:
        user = User()
        user.oauth_token = resp['oauth_token']
        user.oauth_secret = resp['oauth_token_secret']
        user.staff = False
        user.points = 5
    return redirect(next_url)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)