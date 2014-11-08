from flask import g, redirect, request, session, flash, url_for, render_template
from flask_openid import OpenID
from flask_oauth import OAuth
from penguicontrax import constants, uncacheable_response
from . import lookup_current_user, User, UserLoginIP
from .. import app, db
from ..constants import constants
import urllib, hashlib

oid = OpenID(app, constants.OPENID_STORE, safe_roots=[])
oauth = OAuth()
twitter = oauth.remote_app('twitter',
    base_url='https://api.twitter.com/1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authorize',
    consumer_key=constants.TWITTER_KEY,
    consumer_secret=constants.TWITTER_SECRET_KEY
)
facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=constants.FACEBOOK_APP_ID,
    consumer_secret=constants.FACEBOOK_SECRET,
    request_token_params={'scope': 'email'}
)

def gravatar_image_update(user):
    default_small = constants.PUBLIC_URL + 'static/penguinhead_small.png'
    default_large = constants.PUBLIC_URL + 'static/penguinhead.png'
    if user.email is None or user.email == '':
        user.image_small = default_small
        user.image_large = default_large
        return
    user.image_small = 'http://www.gravatar.com/avatar/' + hashlib.md5(user.email.lower()).hexdigest() + '?' + urllib.urlencode({'d':default_small, 's':'32'})
    user.image_large = 'http://www.gravatar.com/avatar/' + hashlib.md5(user.email.lower()).hexdigest() + '?' + urllib.urlencode({'d':default_large, 's':'200'})

def generate_account_name(user):
    dedupe=0
    base = "".join(user.name.split())
    proposed = base
    while not User.query.filter_by(account_name=proposed).first() is None:
        dedupe += 1
        proposed = base + str(dedupe)
    user.account_name = proposed
        
@app.route('/login', methods=['GET'])
@uncacheable_response
@oid.loginhandler
def login():
    if g.user is not None:
        next_override = request.args.get('next', None)
        return redirect(next_override if not next_override is None else oid.get_next_url())
    provider = request.args.get('provider', '')
    session['ip'] = request.remote_addr
    if provider == 'google':
        return oid.try_login('https://www.google.com/accounts/o8/id', ask_for=['email','fullname'])
    elif provider == 'yahoo':
        return oid.try_login('http://me.yahoo.com', ask_for=['email','fullname'])
    elif provider == 'facebook':
        return facebook.authorize(callback=constants.PUBLIC_URL + 'oauth-authorized-facebook')
    elif provider == 'twitter':
        return twitter.authorize(callback=constants.PUBLIC_URL + 'oauth-authorized-twitter')
    return render_template('login.html', user=g.user)


def update_user_login_ip(user, ip):
    if UserLoginIP.query.filter_by(user_id=user.id, ip=ip).first() is None:
        login_record = UserLoginIP()
        login_record.user_id = user.id
        login_record.ip = ip
        db.session.add(login_record)
        db.session.commit()

from penguicontrax.audit import audit_user_creation

@oid.after_login
def new_openid_user(resp):
    session['openid'] = resp.identity_url
    lookup_current_user()
    if g.user is None:
        user = User()
        user.email = resp.email
        user.openid = resp.identity_url
        user.name = resp.fullname
        user.creation_ip = session['ip']
        gravatar_image_update(user)
        generate_account_name(user)
        db.session.add(user)
        db.session.commit()
        g.user = user
        audit_user_creation(user)
    update_user_login_ip(g.user, session['ip'])
    return redirect(oid.get_next_url())

@app.route('/logout')
@uncacheable_response
def logout():
    session.pop('openid', None)
    session.pop('oauth_token', None)
    session.pop('oauth_token_secret', None)
    session.pop('fbid', None)
    return redirect(oid.get_next_url())

@twitter.tokengetter
def get_oauth_token_twitter(token=None):
    lookup_current_user()
    if g.user is None:
        return None
    return (g.user.oauth_token, g.user.oauth_secret)

@facebook.tokengetter
def get_oauth_token_facebook(token=None):
    if g.temp_oauth_token is not None:
        return (g.temp_oauth_token, '')
    lookup_current_user()
    if g.user is None:
        return None
    return (g.user.oauth_token, '')

def update_fb_info(user):
    if user is not None:
        me = facebook.get('/me')
        user.name = me.data['first_name'] + ' ' + me.data['last_name']
        user.email = me.data['email']
        user.fbid = me.data['id']
        user.image_small = 'http://graph.facebook.com/' + user.fbid + '/picture?type=small'
        user.image_large = 'http://graph.facebook.com/' + user.fbid + '/picture?type=large'
        db.session.add(user)
        db.session.commit()

@app.route('/oauth-authorized-facebook')
@uncacheable_response
@facebook.authorized_handler
def oauth_authorized_facebook(resp):
    next_url = request.args.get('next') or url_for('index')
    if resp is None:
        flash('You denied the request to sign in.')
        return redirect(next_url)
    session['oauth_token'] = (resp['access_token'], '')
    g.temp_oauth_token = resp['access_token']
    session['fbid'] = facebook.get('/me').data['id']
    lookup_current_user()
    if g.user is None:
        user = User()
        user.oauth_token = resp['access_token']
        user.creation_ip = session['ip']
        update_fb_info(user)
        generate_account_name(user)
        db.session.add(user)
        db.session.commit()
        g.user = user
        audit_user_creation(user)
    # Update name/email
    g.temp_oauth_token = None
    update_fb_info(g.user)
    update_user_login_ip(g.user, session['ip'])
    return redirect(next_url)

@app.route('/oauth-authorized-twitter')
@uncacheable_response
@twitter.authorized_handler
def oauth_authorized_twitter(resp):
    next_url = request.args.get('next') or url_for('index')
    if resp is None:
        flash('You denied the request to sign in.')
        return redirect(next_url)
    session['oauth_token'] = (resp['oauth_token'], resp['oauth_token_secret'])
    lookup_current_user()
    if g.user is None:
        user = User()
        user.oauth_token = resp['oauth_token']
        user.oauth_secret = resp['oauth_token_secret']
        user.name = resp['screen_name']
        user.creation_ip = session['ip']
        gravatar_image_update(user)
        generate_account_name(user)
        db.session.add(user)
        db.session.commit()
        g.user = user
        audit_user_creation(user)
    update_user_login_ip(g.user, session['ip'])
    return redirect(next_url)
       
    
