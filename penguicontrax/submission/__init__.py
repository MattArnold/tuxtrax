from copy import copy
import datetime
import json
import os

from flask import g, request, session, render_template, redirect, Response, Markup, url_for
from sqlalchemy.orm import relationship
from .. import app, db, dump_table_json
from penguicontrax.tag import Tag, get_tag, create_tag
from penguicontrax.user import User, Person, find_user, find_person


# Associates multiple tags to a submission
SubmissionToTags = db.Table('submission_tags', db.Model.metadata,
                            db.Column('submission_id', db.Integer(),
                                      db.ForeignKey('submissions.id', ondelete='CASCADE', onupdate='CASCADE')),
                            db.Column('tag_id', db.Integer(),
                                      db.ForeignKey('tags.id', ondelete='CASCADE', onupdate='CASCADE'))
)
SubmissionToResources = db.Table('submission_resources', db.Model.metadata,
                                 db.Column('submission_id', db.Integer(),
                                           db.ForeignKey('submissions.id', ondelete='CASCADE', onupdate='CASCADE')),
                                 db.Column('resource_id', db.Integer(),
                                           db.ForeignKey('resources.id', ondelete='CASCADE', onupdate='CASCADE'))
)

user_presenting_in = db.Table('user_presenting_in',
                              db.Column('submission_id', db.Integer,
                                        db.ForeignKey('submissions.id', ondelete='CASCADE', onupdate='CASCADE')),
                              db.Column('user_id', db.Integer,
                                        db.ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE')))

person_presenting_in = db.Table('person_presenting_in',
                                db.Column('submission_id', db.Integer,
                                          db.ForeignKey('submissions.id', ondelete='CASCADE', onupdate='CASCADE')),
                                db.Column('person_id', db.Integer,
                                          db.ForeignKey('person.id', ondelete='CASCADE', onupdate='CASCADE')))


class Submission(db.Model):
    __tablename__ = 'submissions'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    description = db.Column(db.String())
    comments = db.Column(db.String())
    submitter_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    submitter = db.relationship('User', backref='submissions')
    trackId = db.Column(db.Integer(), db.ForeignKey('tracks.id'))
    track = db.relationship('Track')
    tags = db.relationship('Tag', secondary=SubmissionToTags, backref=db.backref('submissions'), passive_deletes=True)
    duration = db.Column(db.Integer())
    setupTime = db.Column(db.Integer())
    repetition = db.Column(db.Integer())
    timeRequest = db.Column(db.String())
    eventType = db.Column(db.String())
    resources = db.relationship('Resource', secondary=SubmissionToResources)
    players = db.Column(db.Integer())
    roundTables = db.Column(db.Integer())
    longTables = db.Column(db.Integer())
    facilityRequest = db.Column(db.String())
    followUpState = db.Column(db.Integer())  # 0 = submitted, 1 = followed up, 2 = accepted, 3 = rejected
    userPresenters = db.relationship('User', secondary=user_presenting_in, backref=db.backref('presenting_in'),
                                     passive_deletes=True)
    personPresenters = db.relationship('Person', secondary=person_presenting_in, backref=db.backref('presenting_in'),
                                       passive_deletes=True)
    private = db.Column(db.Boolean())
    event_created = db.Column(db.Boolean())
    submitted_dt = db.Column(db.DateTime())

    def __init__(self):
        self.private = False
        self.submitted_dt = datetime.datetime.now()

    def __repr__(self):
        return '<email: %s, title: %s>' % (self.email, self.title)

    def presenter_list_str(self):
        first = False
        ret = ''
        for person in self.personPresenters:
            if not first:
                first = True
            else:
                ret = ret + ', '
            ret = ret + person.name
        for user in self.userPresenters:
            if not first:
                first = True
            else:
                ret = ret + ', '
            ret = ret + user.name
        if ret != '':
            ret += '.'
        return ret

    def duration_str(self):
        if self.duration == 1:
            return '50 minutes'
        elif self.duration == 2:
            return '1 hour and 50 minutes'
        elif self.duration == 3:
            return '2 hours and 50 minutes'
        elif self.duration == 4:
            return 'More than 2 hours and 50 minutes'
        elif self.duration == 5:
            return 'All weekend'
        return 'Unknown'

    def setupTime_str(self):
        if self.setupTime == 0:
            return 'None'
        elif self.setupTime == 1:
            return '1 hour'
        elif self.setupTime == 2:
            return '2 hours'
        elif self.setupTime == 3:
            return 'More than 2 hours'
        return 'Unknown'

    def repetition_str(self):
        if self.repetition == 0:
            return 'No'
        elif self.repetition == 1:
            return 'Twice'
        elif self.repetition == 2:
            return 'Thrice'
        elif self.repetition == 3:
            return  'More than thrice'
        return 'Unknown'



class Track(db.Model):
    __tablename__ = 'tracks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True)
    staffId = db.Column(db.Integer())

    def __init__(self, name, staffId):
        self.name = name
        self.staffId = staffId

    def __repr__(self):
        return '<name: %s, staffId: %d>' % self.name, self.staffId


class Resource(db.Model):
    __tablename__ = 'resources'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True)
    request_form_label = db.Column(db.String())
    displayed_on_requst_form = db.Column(db.Boolean())

    def __init__(self, name, request_form_label, displayed_on_requst_form):
        self.name = name
        self.request_form_label = request_form_label
        self.displayed_on_requst_form = displayed_on_requst_form

    def __repr__(self):
        return '<name: %s>' % self.name


from penguicontrax import audit

def submission_dataset_changed():
    from penguicontrax import conn
    if not conn is None:
        try:
            conn.incr('SUBMISSION_DATASET_VERSION')
        except:
            pass

def submission_dataset_ver():
    from penguicontrax import conn
    if not conn is None:
        try:
            return conn.get('SUBMISSION_DATASET_VERSION')
        except:
            pass
    return '0'

def get_track(name):
    tracks = Track.query.filter(Track.name == name)
    if tracks.count() == 1:
        return tracks.first()
    else:
        return None


def get_resource(id):
    resources = Resource.query.filter(Resource.id == id)
    if resources.count() == 1:
        return resources.first()
    else:
        return None


@app.route('/getevent', methods=['GET'])
def getevent():
    if 'id' in request.args:
        return Response(dump_table_json(Submission.query.filter_by(id=int(request.args['id'])), Submission.__table__),
                        mimetype='application/json')
    return Response(dump_table_json(Submission.query.all(), Submission.__table__), mimetype='application/json')


@app.route('/eventform', methods=['GET', 'POST'])
def event_form():
    eventid = request.args.get('id', None)
    if g.user is None:
        if eventid is None:
            nextpage = url_for('event_form')
        else:
            nextpage = url_for('event_form', id=eventid)
        return redirect(url_for('login', next=nextpage))
    # probably need orders
    tags = [tag.name for tag in Tag.query.all()]
    tracks = [track.name for track in Track.query.all()]
    resources = Resource.query.filter_by(displayed_on_requst_form=True)
    if request.method == 'GET':
        event_tags = []
        if eventid is not None:
            event = Submission.query.filter_by(id=eventid).first()
            if (not event is None) and (event.private) and (not g.user.staff):
                return redirect('/')
        else:
            event = None
    return render_template('form.html', tags=tags, resources=resources, tracks=tracks, event=event, user=g.user)


@app.route('/submitevent', methods=['POST'])
def submitevent():
    eventid = request.form.get('eventid')
    if eventid is not None:
        submission = Submission.query.get(eventid)
        old_submission = copy(submission)
    else:
        submission = Submission()
        old_submission = Submission()

    fields = {'email': 'email', 'title': 'title', 'description': 'description',
              'firstname': 'firstname', 'lastname': 'lastname',
              'duration': 'duration', 'setuptime': 'setupTime', 'repetition': 'repetition',
              'timerequest': 'timeRequest',
              'eventtype': 'eventType', 'players': 'players', 'roundtables': 'roundTables', 'longtables': 'longTables',
              'facilityrequest': 'facilityRequest',
              'comments': 'comments'}
    for field, dbfield in fields.items():
        if field in request.form:
            setattr(submission, dbfield, request.form[field])
    if 'submitter_id' in request.form:
        submission.submitter = User.query.filter_by(id=request.form['submitter_id']).first()
    submission.private = 'private' in request.form
    submission.followUpState = request.form['followupstate'] if 'followupstate' in request.form and request.form[
        'followupstate'] is not None else 0

    # presenter handling
    presenters_id = request.form.getlist('presenter_id')
    presenters_idtype = request.form.getlist('presenter_idtype')
    presenters_name = request.form.getlist('presenter')
    presenters_phone = request.form.getlist('phone')
    presenters_email = request.form.getlist('email')
    presenters = zip(presenters_id, presenters_idtype, presenters_name, presenters_phone, presenters_email)
    del submission.userPresenters[:]
    del submission.personPresenters[:]
    for presenter in presenters:
        found_user = None
        found_person = None
        (id, idtype, name, phone, email) = presenter
        if id:
            if idtype == 'user':
                found_user = User.query.get(id)
            elif idtype == 'person':
                found_person = Person.query.get(id)
        else:
            found_user = find_user(name, phone, email)
            if not found_user:
                found_person = find_person(name, phone, email)
        if found_user:
            if found_user not in submission.userPresenters:
                submission.userPresenters.append(found_user)
            continue
        if found_person:
            if found_person not in submission.personPresenters:
                submission.personPresenters.append(found_person)
            continue
        new_person = Person(name)
        new_person.phone = phone
        new_person.email = email
        db.session.add(new_person)
        submission.personPresenters.append(new_person)

    tags = request.form.getlist('tag')
    del submission.tags[:]
    for tag in tags:
        submission.tags.append(get_tag(tag))

    resources = request.form.getlist('resource')
    del submission.resources[:]
    for resource_id in resources:
        matched_resource = get_resource(resource_id)
        if matched_resource:
            submission.resources.append(matched_resource)

    submission.track = get_track(request.form.get('track'))
    db.session.add(submission)
    db.session.commit()
    audit.audit_change(Submission.__table__, g.user, old_submission,
                       submission)  #We'd like submission.id to actually be real so commit the creation first
    submission_dataset_changed()
    sendEmail(submission,old_submission);
    return redirect('/')

def sendEmail(submission,old_submission):
    if submission.followUpState != old_submission.followUpState:
        from penguicontrax import mail, constants
        from flask.ext.mail import Message
        if (submission.followUpState == 2 or submission.followUpState == 3) and not submission.submitter is None:
            if not submission.submitter.email is None:
                msg = Message( )
                msg.sender = constants.DEFAULT_MAIL_SENDER
                msg.recipients = [submission.submitter.email]
                msg.reply_to = constants.MAIL_REPLY_TO
                if submission.followUpState == 2:
                    msg.body = 'Thank you for submitting an event to %s. %s was approved. '\
                                'Type: %s. Program participants: %s. Description: '\
                                '%s. Duration: %s. Setup time: %s. Reptition: %s.' \
                                    % (constants.ORGANIZATION, submission.title, submission.eventType, \
                                       submission.presenter_list_str(), submission.description, submission.duration_str(), \
                                       submission.setupTime_str(), submission.repetition_str())
                    msg.subject = 'Your event titled %s has been approved for %s' % (submission.title, constants.ORGANIZATION)
                    missing = ''
                    for person in submission.personPresenters:
                        if person.email is None or person.phone is None:
                            if missing != '':
                                missing += ', '
                            missing = missing + person.name
                    for user in submission.userPresenters:
                        if user.email is None or user.phone is None:
                            if missing != '':
                                missing += ', '
                            missing = missing + user.name
                    if missing != '':
                        msg.body = msg.body + os.linesep + os.linesep + \
                            'We are missing contact info for %s. Would you help us get '\
                            'that and email it to %s? Thanks!' % (missing, constants.DEFAULT_MAIL_SENDER)
                else:
                    msg.body = 'Sorry, but your event titled %s was declined this year. If you think this message is an error, '\
                                'please contact %s.' % (submission.title, constants.MAIL_REPLY_TO)
                    msg.subject = 'Your event titled %s was not approved for %s' % (submission.title, constants.ORGANIZATION)
                mail.send(msg)


@app.route('/rsvp', methods=['POST'])
def rsvp():
    if g.user is not None:
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
            if g.user.points <= 0 and g.user.staff != 1:
                return redirect('/')
            else:
                g.user.rsvped_to.append(submission)
                g.user.points -= 1
        db.session.add(g.user)
        db.session.commit()
        return redirect('/#submission_' + str(submission.id))
    else:
        return redirect('/')


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
    if submission and resource in submission.resources:
        return Markup('checked')
    return ''


@app.template_filter()
def checked_if_tagged(submission, tag):
    if submission and tag in [tag.name for tag in submission.tags]:
        return Markup('checked')
    return ''


@app.template_filter()
def checked_if_tracked(submission, trackname):
    if submission and submission.track and submission.track.name == trackname:
        return Markup('checked')
    return ''


@app.template_filter()
def number_total_rsvps(submission):
    return len(submission.rsvped_by)


@app.template_filter()
def get_js_template(name):
    tpl = app.open_resource("templates/"+name, 'r')
    return json.dumps(str(tpl.read()))


@app.template_filter()
def days_since_now(dt):
    return
