from penguicontrax import constants
from flask import g, session, Response, render_template, request, redirect
from .. import app, db

rsvps = db.Table('rsvps',
                db.Column('submission_id', db.Integer, db.ForeignKey('submissions.id', ondelete='CASCADE', onupdate='CASCADE')),
                db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE')))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    account_name = db.Column(db.String())
    staff = db.Column(db.Boolean())
    email = db.Column(db.String())
    openid = db.Column(db.String())
    points = db.Column(db.Integer())
    oauth_token = db.Column(db.String())
    oauth_secret = db.Column(db.String())
    fbid = db.Column(db.Integer())
    image_small = db.Column(db.String())
    image_large = db.Column(db.String())
    rsvped_to = db.relationship('Submission', secondary=rsvps, backref=db.backref('rsvped_by', passive_deletes=True))
    special_tag = db.Column(db.String())
    
    def __init__(self):
        self.staff = False
        self.points = 5

    def __repr__(self):
        return self.name
    
class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    merged_to_user = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return self.name

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
        
def user_profile(view_user):
    return redirect('/') if view_user is None else render_template('user_profile.html', user=g.user, view_user=view_user)

@app.route('/userprofile', methods=['GET'])
def user_profile_by_id():
    return user_profile(User.query.filter_by(id=request.args['id']).first())

@app.route('/<user>', methods=['GET'])
def user_profile_by_account_name(user):
    return user_profile(User.query.filter_by(account_name=user).first())
