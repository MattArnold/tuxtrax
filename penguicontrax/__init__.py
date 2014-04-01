from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.cache import Cache
import xml.etree.ElementTree as ET
import json
app = Flask(__name__)
db =  SQLAlchemy(app)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

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

from flask import render_template, g, url_for, redirect, Response
from submission import Submission, Tag
from user import Login
import os, sqlite3, import2013schedule
from constants import constants
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
    # GET RID OF THIS LATER
    if len(Submission.query.all()) == 0:
        import2013schedule.import_old()


@app.route('/')
def index():
    submissions = Submission.query.order_by('id').all() if g.user is not None and g.user.staff == True else Submission.query.filter(Submission.followUpState != 3, Submission.private != True).order_by('id')
    tags = [tag.name for tag in Tag.query.all()]
    return render_template('index.html', tags=tags, submissions=submissions, user=g.user, showhidden=False)
    
@app.route('/hidden')
def hidden():
    return render_template('index.html', user=g.user, showhidden=True)


@app.route('/report')
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
@cache.cached(timeout=900)
def reportcsv():
	out = ''.join([u'\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",%s\r\n' % \
		(s.submitter.name if not s.submitter is None else u'',\
		 '' if (s.submitter is None or s.submitter.email is None) else s.submitter.email,\
		 s.title.replace('\"','\'') if not s.title is None else u'',
		 s.description.replace('\"','\'') if not s.description is None else u'',
		 s.comments.replace('\"','\'') if not s.comments is None else u'',
		 s.track.name if not s.track is None else '',
		 str(s.duration),
		 str(s.setupTime),
		 str(s.repetition),
		 s.timeRequest.replace('\"','\'') if not s.timeRequest is None else u'',
		 s.facilityRequest.replace('\"','\'') if not s.facilityRequest is None else u'',
		 u'%s%s' % (''.join([p.name.replace('\"','\'')  + u',' for p in s.personPresenters]), ''.join([p.name.replace('\"','\'') + u',' for u in s.userPresenters]))
		) for s in Submission.query.all()])
	out = u'Submitter,Submitter e-mail,Title,Description,Comments,Track,Duration,Setup time,Repetition,Time request,Facility request,Presenters\r\n' + out
	return Response(out.encode('utf-8'), mimetype='text/csv')

# TODO: this fake URL is used to run unittests. It should be disabled on a deploy
@app.route('/fakelogin')
def fake_login():
    import os
    from flask import session
    if 'PC_FAKE_OID' in os.environ:
        session['openid']=os.environ['PC_FAKE_OID']









