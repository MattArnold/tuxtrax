from penguicontrax import constants
from flask import g, session, Response, render_template, request, redirect
from .. import app, db

rsvps = db.Table('rsvps',
                db.Column('submission_id', db.Integer, db.ForeignKey('submissions.id', ondelete='CASCADE', onupdate='CASCADE')),
                db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE')))

event_rsvps = db.Table('event_rsvps',
                db.Column('event_id', db.Integer, db.ForeignKey('events.id', ondelete='CASCADE', onupdate='CASCADE')),
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
    event_rsvped_to = db.relationship('Events', secondary=event_rsvps, backref=db.backref('rsvped_by', passive_deletes=True))
    presentations = db.relationship('Submission', secondary='user_presenting_in', backref=db.backref('presented_by', passive_deletes=True))
    special_tag = db.Column(db.String())
    public_rsvps = db.Column(db.Boolean())
    superuser = db.Column(db.Boolean())
    creation_ip = db.Column(db.String())
    phone = db.Column(db.String())
    
    def __init__(self):
        self.points = 5
        self.public_rsvps = False
        if User.query.count() == 0:
            self.staff = True
            self.superuser = True
            self.special_tag = "root"
        else:
            self.staff = True # TODO: Make people not be staff by default
            self.superuser = False

    def __repr__(self):
        return self.name
    
class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    email = db.Column(db.String())
    phone = db.Column(db.String())
    merged_to_user = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return self.name
    
class UserLoginIP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String())
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    logged_in_as = db.relationship('User', backref=db.backref('logged_in_from_ip', passive_deletes=True))
    
    def __repr__(self):
        return self.ip

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

from penguicontrax import audit
from copy import copy

@app.route('/updateuser', methods=['POST'])
def update_user():
    if g.user is None:
        return redirect('/')
    view_user = User.query.filter_by(id=int(request.form['user_id'])).first()
    old_view_user = copy(view_user)
    if view_user is None:
        return redirect('/')
    if view_user == g.user or g.user.staff == True or g.user.superuser == True:
        view_user.public_rsvps = 'public_rsvps' in request.form
        view_user.email = request.form['email']
        view_user.phone = request.form['phone']
        if g.user.staff == True:
            view_user.special_tag = request.form['special_tag']
        if g.user.superuser == True:
            view_user.staff = 'staff' in request.form
        if view_user.special_tag.strip() == '':
            view_user.special_tag = None
        db.session.add(view_user)
        db.session.commit()
        audit.audit_change(User.__table__, g.user, old_view_user, view_user)
        return redirect('/' + view_user.account_name)
    return redirect('/')

@app.route('/users')
def user_list():
    if g.user is None or not g.user.staff:
        return redirect('/')
    return render_template('user_list.html', user=g.user, users=User.query.all())

def find_user(name, phone=None, email=None):
    query = User.query.filter_by(name=name)
    if phone:
        query = query.filter_by(phone=phone)
    if email:
        query = query.filter_by(email=email)
    return query.first()
def find_person(name, phone=None, email=None):
    query = Person.query.filter_by(name=name)
    if phone:
        query = query.filter_by(phone=phone)
    if email:
        query = query.filter_by(email=email)
    return query.first()
