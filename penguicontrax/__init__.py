import logging

import collections
import csv
import datetime
import json
import os
import redis
import xml.etree.ElementTree as ET

from flask.ext.assets import Environment, Bundle
from flask.ext.cache import Cache
from flask.ext.mail import Mail
from flask.ext.sqlalchemy import SQLAlchemy
from flask import (Flask, Response, render_template, g, session, url_for,
                    redirect, Response, make_response)

from constants import constants
from .utils import (uncacheable_response, dump_table, dump_table_xml,
                    dump_table_json)

app = Flask(__name__)
db = SQLAlchemy(app)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
mail = Mail(app)

from event import Events, Rooms, RoomGroups, Convention
from submission import (Submission, submission_dataset_ver, Track,
                        SubmissionToTags)
from tag import Tag
from user import Login

if constants.DEBUG is True:
    conn = None
else:
    try:
        conn = redis.from_url(constants.REDIS_URL)
        conn.incr('REDIS_CONNECTION_COUNT')
        dataset_ver = conn.get('SUBMISSION_DATASET_VERSION')
        conn.flushall()
        if dataset_ver is None:
            conn.set('SUBMISSION_DATASET_VERSION', 0)
        else:
            conn.set('SUBMISSION_DATASET_VERSION', int(dataset_ver) + 1)
    except Exception as e:
        conn = None
        pass

import api


def init():
    app.config.update(dict(
        MAIL_SERVER=constants.MAIL_SERVER,
        MAIL_PORT=constants.MAIL_PORT,
        MAIL_USE_TLS=constants.MAIL_USE_TLS,
        MAIL_USE_SSL=constants.MAIL_USE_SSL,
        MAIL_USERNAME=constants.MAIL_USERNAME,
        MAIL_PASSWORD=constants.MAIL_PASSWORD,
        DEFAULT_MAIL_SENDER=constants.DEFAULT_MAIL_SENDER
    ))
    app.secret_key = constants.SESSION_SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = constants.DATABASE_URL
    app.config.from_object(__name__)
    db.create_all()

    import import2013schedule
    if len(Track.query.all()) == 0:
        import2013schedule.setup_predefined()
    """
    if len(Submission.query.all()) == 0 and len(Events.query.all()) == 0:
        print 'Importing 2015 schedule into submissions'
        import2013schedule.import_old('schedule2015.html')
        print 'Importing 2013 schedule into convention'
        import2013schedule.import_old('schedule2013.html', True,
                                      random_rsvp_users = 1000,
                                      submission_limit = 500,
                                      timeslot_limit = 500)
    """


@app.route('/')
@uncacheable_response
def index():
    tags = [tag.name for tag in Tag.query.all()]
    out = render_template('index.html', user=g.user,
                          showhidden=False, tags=tags)
    resp = make_response(out)
    resp.set_cookie('submission_ver', str(submission_dataset_ver()))
    return resp


@app.route('/hidden')
@uncacheable_response
def hidden():
    return render_template('index.html', user=g.user, showhidden=True)

@app.route('/help')
def help():
    return render_template('help.html', user=g.user)

@app.route('/report')
@uncacheable_response
@cache.cached(timeout=900)
def report():
    root = ET.Element('penguicontrax')
    ET.SubElement(root, 'generated').text = str(datetime.datetime.now())
    dump_table_xml(Submission.query.all(), Submission.__table__,
                   root, 'submissions', 'submission')
    dump_table_xml(Tag.query.all(), Tag.__table__, root, 'tags', 'tag')
    dump_table_xml(db.session.query(SubmissionToTags).all(), SubmissionToTags,
                   root, 'SubmissionToTags', 'SubmissionToTag')
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
    writer = csv.writer(Echo())

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
    schema['Presenting submitter'] = \
        lambda s: unicode(s.submitter in [p.user for p in s.presenters])
    schema['Presenters'] = lambda s: ','.join([p.name for p in s.presenters])

    # generate the table
    def generate_data_rows(data):
        yield list(schema.keys())
        for s in data:
            yield [column(s).encode('utf-8') for column in schema.values()]

    # convert the table to csv
    rows_iterator = (writer.writerow(row)
                     for row in generate_data_rows(Submission.query))
    output = list(rows_iterator)  # iterators break the cache middleware
    return Response(output, mimetype='text/csv')


# static asset versioning and packaging
assets = Environment(app)

js = Bundle('jquery-1.11.0.js',
            'bootstrap-3.1.1/dist/js/bootstrap.js',
            'bootstrap-selectpicker/bootstrap-select.js',
            'typeahead.bundle.js',
            'lodash.min.js',
            'can.jquery.js',
            'modal.js',
            filters='rjsmin', output='build/tuxtrax-%(version)s.js')

css = Bundle('ptrax.css', output='build/tuxtrax-%(version)s.css')
assets.debug = constants.DEBUG

assets.versions = "hash"
assets.register('js_base', js)
assets.register('css_base', css)
