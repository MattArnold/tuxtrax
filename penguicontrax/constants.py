import os

class constants:
    DATABASE_FILE = 'penguicontrax.db'
    SESSION_SECRET_KEY = 'SESSION_SECRET_KEY' if not 'SESSION_SECRET_KEY' in os.environ else os.environ['SESSION_SECRET_KEY']
    DATABASE_URL = 'sqlite:///' + DATABASE_FILE if not 'DATABASE_URL' in os.environ else os.environ['DATABASE_URL']
    OPENID_STORE = 'openid_store'
    TWITTER_KEY = 'TWITTER_KEY' if not 'TWITTER_KEY' in os.environ else os.environ['TWITTER_KEY']
    TWITTER_SECRET_KEY = 'TWITTER_SECRET_KEY' if not 'TWITTER_SECRET_KEY' in os.environ else os.environ['TWITTER_SECRET_KEY']
    FACEBOOK_APP_ID = 'FACEBOOK_APP_ID' if not 'FACEBOOK_APP_ID' in os.environ else os.environ['FACEBOOK_APP_ID']
    FACEBOOK_SECRET = 'FACEBOOK_SECRET' if not 'FACEBOOK_SECRET' in os.environ else os.environ['FACEBOOK_SECRET']
    PUBLIC_URL = 'http://gentle-tor-1515.herokuapp.com/'
