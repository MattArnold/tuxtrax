from flask import g, redirect, request, session, flash, url_for
from flask_openid import OpenID
from flask_oauth import OAuth
from penguicontrax import constants
from . import lookup_current_user, User
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
        return facebook.authorize(callback=constants.PUBLIC_URL + 'oauth-authorized-facebook')
    elif provider == 'twitter':
        return twitter.authorize(callback=constants.PUBLIC_URL + 'oauth-authorized-twitter')
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
        gravatar_image_update(user)
        db.session.add(user)
        db.session.commit()
    return redirect(oid.get_next_url())

@app.route('/logout')
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
        user.firstName = me.data['first_name']
        user.lastName = me.data['last_name']
        user.email = me.data['email']
        user.fbid = me.data['id']
        user.image_small = 'http://graph.facebook.com/' + user.fbid + '/picture?type=small'
        user.image_large = 'http://graph.facebook.com/' + user.fbid + '/picture?type=large'
        db.session.add(user)
        db.session.commit()

@app.route('/oauth-authorized-facebook')
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
        update_fb_info(user)
        db.session.add(user)
        db.session.commit()
    # Update name/email
    g.temp_oauth_token = None
    update_fb_info(g.user)
    return redirect(next_url)

@app.route('/oauth-authorized-twitter')
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
        user.firstName = resp['screen_name']
        gravatar_image_update(user)
        db.session.add(user)
        db.session.commit()
    return redirect(next_url)
       
    