from penguicontrax import constants
from flask import g, session
from .. import app, db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String())
    lastName = db.Column(db.String())
    staff = db.Column(db.Boolean())
    email = db.Column(db.String())
    openid = db.Column(db.String())
    points = db.Column(db.Integer())
    oauth_token = db.Column(db.String())
    oauth_secret = db.Column(db.String())
    fbid = db.Column(db.Integer())
    
    def __init__(self):
        self.staff = False
        self.points = 5

    def __repr__(self):
        return 'User: ' + (self.firstName if self.firstName is not None else '') + ' ' + (self.lastName if self.firstName is not None else '')

@app.before_request
def lookup_current_user():
    g.user = None
    if 'openid' in session:
        openid = session['openid']
        g.user = User.query.filter_by(openid=openid).first()
    elif 'fbid' in session: #This needs to come first -- Facebook sends back different oauth_tokens for each login
        id = session['fbid']
        g.user = User.query.filter_by(fbid=id).first()
    elif 'oauth_token' in session:
        oa = session['oauth_token']
        g.user = User.query.filter_by(oauth_token=oa[0]).first()