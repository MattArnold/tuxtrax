import xml.etree.ElementTree as ET
import json
from flask import Flask, Response
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.cache import Cache
from flask.ext.mail import Mail
import xml.etree.ElementTree as ET
import json, redis
from constants import constants
from flask.ext.assets import Environment, Bundle
import os
import functools
import csv
import collections


app = Flask(__name__)
db = SQLAlchemy(app)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
app.config.update(dict(
    MAIL_SERVER = constants.MAIL_SERVER,
    MAIL_PORT = constants.MAIL_PORT,
    MAIL_USE_TLS = constants.MAIL_USE_TLS,
    MAIL_USE_SSL = constants.MAIL_USE_SSL,
    MAIL_USERNAME = constants.MAIL_USERNAME,
    MAIL_PASSWORD = constants.MAIL_PASSWORD,
    DEFAULT_MAIL_SENDER = constants.DEFAULT_MAIL_SENDER
))
mail = Mail(app)
debug = os.environ.get("DEBUG")

if not debug:

    try:
        conn = redis.from_url(constants.REDIS_URL)
        conn.incr('REDIS_CONNECTION_COUNT')
        if conn.get('SUBMISSION_DATASET_VERSION') is None:
            conn.set('SUBMISSION_DATASET_VERSION', 0)
    except Exception as e:
        conn = None
        pass
else:
    conn = None

# decorator to add uncaching headers
def uncacheable_response(fun):
    uncache_headers = {
       'Cache-Control': 'no-cache, no-store, must-revalidate',
       'Pragma': 'no-cache', 'Expires': '0'
    }
    @functools.wraps(fun)
    def wrapped(*args, **kwargs):
        ret = fun(*args, **kwargs)
        # figure out what type of response it was
        if hasattr(ret, 'headers'):   # is a response object
            response = ret
        else:
            # create real response
            if hasattr(ret, 'strip') or \
               not hasattr(ret, '__getitem__'):
                response = make_response(ret)    # handle string
            else:
                response = make_response(*ret)   # handle tuple
        # adds uncacheable headers to response
        for key,val in uncache_headers.items():
            response.headers[key] = val
        return response
    return wrapped

def dump_table_xml(elements, table, parent_node, collection_name, element_name):
    collection = ET.SubElement(parent_node, collection_name)
    for element in elements:
        element_node = ET.SubElement(collection, element_name)
        element_dict = dict((col, getattr(element, col)) for col in table.columns.keys())
        for key, value in element_dict.iteritems():
            ET.SubElement(element_node, str(key)).text = unicode(value)
    return collection

"""
    @elements is a result set from sqlalchemy
    @table is the table name used for the result set
    returns a list of dicts
"""
def dump_table(elements, table):
    all = [ dict( (col, getattr(element, col)) for col in table.columns.keys()) for element in elements ]
    return all

"""
    @elements is a result set from sqlalchemy
    @table is the table name used for the result set
    @returns a string of serialized list of dicts
"""
def dump_table_json(elements, table):
    return json.dumps(dump_table(elements,table))

from flask import render_template, g, url_for, redirect, Response, make_response
from submission import Submission, submission_dataset_ver, Track
from tag import Tag
from user import Login
import import2013schedule
import datetime, audit
from event import Events, Rooms, RoomGroups, Convention
import api

def init():
    app.secret_key = constants.SESSION_SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = constants.DATABASE_URL
    app.config.from_object(__name__)
    try:
        db.create_all()
    except Exception as e:
        print e
        pass

    if len(Track.query.all()) == 0:
        import2013schedule.setup_predefined()

    if len(Submission.query.all()) == 0 and len(Events.query.all()) == 0:
        print 'Importing 2015 schedule into submissions'
        import2013schedule.import_old('schedule2015.html')
        print 'Importing 2013 schedule into convention'
        import2013schedule.import_old('schedule2013.html', True, random_rsvp_users = 1000, submission_limit = 500, timeslot_limit = 500)

@app.route('/')
@uncacheable_response
def index():
    tags = [tag.name for tag in Tag.query.all()]
    resp = make_response(render_template('index.html', user=g.user, showhidden=False, tags=tags))
    resp.set_cookie('submission_ver', str(submission_dataset_ver()))
    return resp

@app.route('/hidden')
@uncacheable_response
def hidden():
    return render_template('index.html', user=g.user, showhidden=True)


@app.route('/report')
@uncacheable_response
@cache.cached(timeout=900)
def report():
    root = ET.Element('penguicontrax')
    ET.SubElement(root, 'generated').text = str(datetime.datetime.now())
    dump_table_xml(Submission.query.all(), Submission.__table__, root, 'submissions', 'submission')
    dump_table_xml(Tag.query.all(), Tag.__table__, root, 'tags', 'tag')
    from submission import SubmissionToTags
    dump_table_xml(db.session.query(SubmissionToTags).all(), SubmissionToTags, root, 'SubmissionToTags', 'SubmissionToTag')
    return Response(ET.tostring(root, encoding='utf-8'), mimetype='text/xml')


@app.route('/report.csv')
@uncacheable_response
@cache.cached(timeout=900)
def reportcsv():
    # helper to format csv lines
    class Echo(object):
        """ An object that implements a writable file object
            It returns the data that was written
            to help implement a streaming csv writer
        """
        def write(self, value):
            return value
    writer = csv.writer(Echo())   # writer.writerow will now return the formatted line

    # helpers to fetch data from the object
    def default(data, default=u''):
        """ Replicates that jinja2 default filter
            Returns the default object if the data is None
        """
        return data if data is not None else default
    def get_obj(obj, key, default=u''):
        """ Returns the default object if the obj is None """
        return getattr(obj, key, default) if obj is not None else default
    # list of columns, and how to get the data for them
    schema = collections.OrderedDict()
    schema['Submitter'] = lambda s: get_obj(s.submitter, 'name')
    schema['Submitter e-mail'] = lambda s: get_obj(s.submitter, 'email')
    schema['Title'] = lambda s: default(s.title)
    schema['Description'] = lambda s: default(s.description)
    schema['Comments'] = lambda s: default(s.comments)
    schema['Track'] = lambda s: get_obj(s.track, 'name')
    schema['Duration'] = lambda s: unicode(s.duration)
    schema['Setup time'] = lambda s: unicode(s.setupTime)
    schema['Repetition'] = lambda s: unicode(s.repetition)
    schema['Time request'] = lambda s: default(s.timeRequest)
    schema['Facility request'] = lambda s: default(s.facilityRequest)
    schema['Presenting submitter'] = lambda s: unicode(s.submitter in [p.user for p in s.presenters])
    schema['Presenters'] = lambda s: ','.join([p.name for p in s.presenters])
    # generate the table
    def generate_data_rows(data):
        yield list(schema.keys())
        for s in data:
            yield [column(s).encode('utf-8') for column in schema.values()]
    # convert the table to csv
    rows_iterator = (writer.writerow(row) for row in generate_data_rows(Submission.query))
    output = list(rows_iterator)  # iterators break the cache middleware
    return Response(output, mimetype='text/csv')


# TODO: this fake URL is used to run unittests. It should be disabled on a deploy
@app.route('/fakelogin')
def fake_login():
    import os
    from flask import session

    if 'PC_FAKE_OID' in os.environ:
        session['openid'] = os.environ['PC_FAKE_OID']

# static asset versioning and packaging
assets = Environment(app)

js = Bundle('jquery-1.11.0.js',
            'bootstrap-3.1.1/dist/js/bootstrap.js',
            'bootstrap-selectpicker/bootstrap-select.js',
            'typeahead.bundle.js',
            'lodash.min.js',
            'can.jquery.js',
            filters='rjsmin', output='build/tuxtrax-%(version)s.js')

css = Bundle('ptrax.css', output='build/tuxtrax-%(version)s.css')

try:
    os.environ["DEBUG"]
except KeyError:
    debug = False
else:
    debug = True

assets.debug = debug

assets.versions = "hash"
assets.register('js_base', js)
assets.register('css_base', css)











