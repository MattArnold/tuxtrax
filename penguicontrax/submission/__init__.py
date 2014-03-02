from flask import g, request, session, render_template, redirect, Response, Markup
from sqlalchemy.orm import relationship
from .. import app, db, dump_table_json
import string

# Associates multiple tags to a submission
SubmissionToTags = db.Table('submission_tags', db.Model.metadata,
    db.Column('submission_id', db.Integer(), db.ForeignKey('submissions.id', ondelete='CASCADE', onupdate='CASCADE')),
    db.Column('tag_id', db.Integer(), db.ForeignKey('tags.id', ondelete='CASCADE', onupdate='CASCADE'))
)
SubmissionToResources = db.Table('submission_resources', db.Model.metadata,
    db.Column('submission_id', db.Integer(), db.ForeignKey('submissions.id', ondelete='CASCADE', onupdate='CASCADE')),
    db.Column('resource_id', db.Integer(), db.ForeignKey('resources.id', ondelete='CASCADE', onupdate='CASCADE'))
)

class Submission(db.Model):
    __tablename__ = 'submissions'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String())
    title = db.Column(db.String())
    description = db.Column(db.String())
    comments = db.Column(db.String())
    submitter = db.Column(db.String())
    firstname = db.Column(db.String())
    lastname = db.Column(db.String())
    trackId = db.Column(db.Integer(), db.ForeignKey('tracks.id'))
    track = db.relationship('Track')
    tags = db.relationship('Tag', secondary=SubmissionToTags, backref=db.backref('submissions'), passive_deletes=True)
    duration = db.Column(db.Boolean())
    setupTime = db.Column(db.Integer())
    repetition = db.Column(db.Integer())
    timeRequest = db.Column(db.String())
    eventType = db.Column(db.String(20))
    resources = db.relationship('Resource', secondary=SubmissionToResources)
    players = db.Column(db.Integer())
    roundTables = db.Column(db.Integer())
    longTables = db.Column(db.Integer())
    facilityRequest = db.Column(db.String())
    followUpState = db.Column(db.Integer()) # 0 = submitted, 1 = followed up, 2 = accepted, 3 = rejected
        
    def __init__(self):
        pass

    def __repr__(self):
        return '<email: %s, title: %s>' % (self.email, self.title)

class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<name: %s>' % self.name
    
class Track(db.Model):
    __tablename__ = 'tracks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    staffId = db.Column(db.Integer())

    def __init__(self, name, staffId):
        self.name = name
        self.staffId = staffId

    def __repr__(self):
        return '<name: %s, staffId: %d>' % self.name, self.staffId

class Resource(db.Model):
    __tablename__ = 'resources'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<name: %s>' % self.name

def get_tag(name):
    tags = Tag.query.filter(Tag.name==name)
    if tags.count() < 1:
        tag = Tag(name=name)
        db.session.append(tag)
        db.session.commit()
    else:
        tag = tags[0]
    return tag

def normalize_tag_name(tag):
    tag = tag.lower().strip()
    tag = tag.translate(string.maketrans("",""), string.punctuation)
    tag = "-".join(tag.split())
    return tag

def get_track(name):
    tracks = Track.query.filter(Track.name==name)
    if tracks.count() == 1:
        return tracks.first()
    else:
        return None
def get_resource(id):
    resources = Resource.query.filter(Resource.id==id)
    if resources.count() == 1:
        return resources.first()
    else:
        return None

@app.route('/getevent', methods=['GET'])
def getevent():
    if 'id' in request.args:
        return Response(dump_table_json(Submission.query.filter_by(id=int(request.args['id'])), Submission.__table__), mimetype='application/json')
    return Response(dump_table_json(Submission.query.all(), Submission.__table__), mimetype='application/json')
    
@app.route('/eventform', methods=['GET', 'POST'])
def event_form():
    # probably need orders
    tags = [tag.name for tag in Tag.query.all()]
    tracks = [track.name for track in Track.query.all()]
    resources = Resource.query.all()

    if request.method == 'GET':
        eventid = request.args.get('id',None)
        event_tags = []
        if eventid is not None:
            event = Submission.query.filter_by(id=eventid).first()
        else:
            event = None
    return render_template('form.html', tags=tags, resources=resources, tracks=tracks,event=event, user=g.user)

@app.route('/submitevent', methods=['POST'])
def submitevent():
    print("Yay")
    eventid = request.form.get('eventid')
    if eventid is not None:
        submission = Submission.query.get(eventid)
    else:
        submission = Submission()

    fields = {'email':'email', 'title':'title', 'description':'description', 'submitter':'submitter',
              'firstname':'firstname', 'lastname':'lastname',
              'duration':'duration', 'setuptime':'setupTime', 'repetition':'repetition', 'timerequest':'timeRequest',
              'eventtype':'eventType','players':'players', 'roundtables':'roundTables', 'longtables':'longTables', 'facilityrequest':'facilityRequest',
              'comments':'comments',
              'person0':'person0', 'person1':'person1', 'person2':'person2', 'person3':'person3'}
    for field,dbfield in fields.items():
       if field in request.form:
           setattr(submission, dbfield, request.form[field])
    submission.followUpState = request.form['followupstate'] if 'followupstate' in request.form and request.form['followupstate'] is not None else 0

    tags = [t[4:] for t,v in request.form.items() if len(t)>4 and t[:4]=='tag_' and v]
    del submission.tags[:]
    for tag in tags:
        submission.tags.append(get_tag(tag))

    resources = [r[9:] for r,v in request.form.items() if len(r)>9 and r[:9]=='resource_' and v]
    del submission.resources[:]
    for resource_id in resources:
        matched_resource = get_resource(resource_id)
        if matched_resource:
            submission.resources.append(matched_resource)

    submission.track = get_track(request.form.get('track'))

    db.session.add(submission)
    db.session.commit()
    return redirect('/')

@app.route('/createtag', methods=['POST'])
def createtag():
    tag = get_tag(request.form['tagname'])
    db.session.add(tag)
    db.session.commit()
    return render_template('index.html')

@app.route('/rsvp', methods=['POST'])
def rsvp():
    if g.user is None or (g.user.points <= 0 and g.user.staff != 1):
        return redirect('/')
    submission = None
    value = None
    for field in request.form:
        if field.find('submit_') == 0: 
            submission = Submission.query.filter_by(id=int(field[7:])).first()
            value = request.form[field]
            break
    if submission is None:
        return redirect('/')
    if value == 'un-RSVP':
        g.user.rsvped_to.remove(submission)
        g.user.points += 1
    else:
        g.user.rsvped_to.append(submission)
        g.user.points -= 1
    db.session.add(g.user)
    db.session.commit()
    return redirect('/#submission_' + str(submission.id))

@app.template_filter()
def is_selected(value, needs_to_be):
    if value == needs_to_be:
        return Markup('selected="selected"')
    return ''
@app.template_filter()
def is_checked(value, needs_to_be):
    if value == needs_to_be:
        return Markup('checked')
    return ''
@app.template_filter()
def checked_if_resourced(submission, resource):
    if resource in submission.resources:
        return Markup('checked')
    return ''
@app.template_filter()
def checked_if_tagged(submission, tag):
    if tag in [tag.name for tag in submission.tags]:
        return Markup('checked')
    return ''
