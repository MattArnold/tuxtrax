from flask import g, request, session, render_template, redirect, Response, Markup
from .. import app, db
import xml.etree.ElementTree as ET
import datetime, sys

# Associate multiple rooms to multiple events.
room_events = db.Table('room_events',
    db.Column('event_id', db.Integer, db.ForeignKey('events.id')),
    db.Column('room_id', db.Integer, db.ForeignKey('rooms.id'))
)

# Associates multiple tags to multiple events.
event_tags = db.Table('event_tags', db.Model.metadata,
    db.Column('event_id', db.Integer(), db.ForeignKey('events.id', ondelete='CASCADE', onupdate='CASCADE')),
    db.Column('tag_id', db.Integer(), db.ForeignKey('tags.id', ondelete='CASCADE', onupdate='CASCADE'))
)

# Associates multiple resources to multiple events.
event_resources = db.Table('event_resources', db.Model.metadata,
    db.Column('event_id', db.Integer(), db.ForeignKey('events.id', ondelete='CASCADE', onupdate='CASCADE')),
    db.Column('resource_id', db.Integer(), db.ForeignKey('resources.id', ondelete='CASCADE', onupdate='CASCADE'))
)

# Associates multiple users to multiple events.
user_event = db.Table('user_event',
    db.Column('event_id', db.Integer, db.ForeignKey('events.id', ondelete='CASCADE', onupdate='CASCADE')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE')))

# Associates multiple persons to multiple events.
person_event = db.Table('person_event',
    db.Column('events_id', db.Integer, db.ForeignKey('events.id', ondelete='CASCADE', onupdate='CASCADE')),
    db.Column('person_id', db.Integer, db.ForeignKey('person.id', ondelete='CASCADE', onupdate='CASCADE')))

room_suitability = db.Table('room_suitability',
    db.Column('event_id', db.Integer, db.ForeignKey('events.id', ondelete='CASCADE', onupdate='CASCADE')),
    db.Column('room_id', db.Integer, db.ForeignKey('rooms.id', ondelete='CASCADE', onupdate='CASCADE'))
)

room_availability = db.Table('room_availability',
    db.Column('timeslot_id', db.Integer, db.ForeignKey('timeslot.id', ondelete='CASCADE', onupdate='CASCADE')),
    db.Column('room_id', db.Integer, db.ForeignKey('rooms.id', ondelete='CASCADE', onupdate='CASCADE'))
)

class Events(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    description = db.Column(db.String())
    comments = db.Column(db.String())
    submitter_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    submitter = db.relationship('User')
    track_id = db.Column(db.Integer(), db.ForeignKey('tracks.id'))
    track = db.relationship('Track')
    tags = db.relationship('Tag', secondary=event_tags, backref=db.backref('events_tagged'), passive_deletes=True)
    rooms = db.relationship('Rooms', secondary='room_events', backref=db.backref('used_for_event'))
    eventType = db.Column(db.String(20))
    resources = db.relationship('Resource', secondary=event_resources, backref=db.backref('at_event'))
    players = db.Column(db.Integer())
    roundTables = db.Column(db.Integer())
    longTables = db.Column(db.Integer())
    facilityRequest = db.Column(db.String())
    userPresenters = db.relationship('User', secondary=user_event, backref=db.backref('at_event'), passive_deletes=True)
    personPresenters = db.relationship('Person', secondary=person_event, backref=db.backref('at_event'), passive_deletes=True)
    start_dt = db.Column(db.DateTime)
    duration = db.Column(db.Integer)    # The number of intervals.
    convention_id = db.Column(db.Integer, db.ForeignKey('convention.id'))
    convention = db.relationship('Convention')
    fixed = db.Column(db.Boolean())

    def __repr__(self):
        return 'Event: %' % self.event_name


class Rooms(db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, primary_key=True)
    room_name = db.Column(db.String(50))
    room_groups_id = db.Column(db.Integer, db.ForeignKey('room_groups.id'))
    rooms_groups = db.relationship('RoomGroups', backref='rooms')
    convention_id = db.Column(db.Integer, db.ForeignKey('convention.id'))
    convention = db.relationship('Convention', backref='rooms')
    suitable_events = db.relationship('Events', secondary=room_suitability, backref=db.backref('suitable_rooms'), passive_deletes=True)
    available_timeslots = db.relationship('Timeslot', secondary=room_availability, backref=db.backref('available_rooms'), passive_deletes=True)

    def __repr__(self):
        return 'Room: %' % self.room_name


class RoomGroups(db.Model):
    __tablename__ = 'room_groups'
    id = db.Column(db.Integer, primary_key=True)
    room_group_name = db.Column(db.String(50))

    def __init__(self, room_group_name):
        self.room_group_name = room_group_name

    def __repr__(self):
        return 'Room Group: %' % self.room_group_name

class Convention(db.Model):
    __tablename__ = 'convention'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50))
    description = db.Column(db.Text)
    start_dt = db.Column(db.DateTime)
    end_dt = db.Column(db.DateTime)
    url = db.Column(db.String())
    timeslot_duration = db.Column(db.Interval())

    def __repr__(self):
        return self.name
    
class Timeslot(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String())
    convention_id = db.Column(db.Integer(), db.ForeignKey('convention.id', ondelete='CASCADE', onupdate='CASCADE'))
    convention = db.relationship('Convention', backref=db.backref('timeslots'))
    start_dt = db.Column(db.DateTime())
    rsvp_conflicts = db.Column(db.Integer())
    
    def __init__(self):
        self.rsvp_conflicts = 0
    
    def __repr__(self):
        return self.name
    
class Presenterconflict(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    timeslot_id = db.Column(db.Integer(), db.ForeignKey('timeslot.id', ondelete='CASCADE', onupdate='CASCADE'))
    timeslot = db.relationship('Timeslot', backref=db.backref('presenter_conflicts'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'))
    user = db.relationship('User')
    person_id = db.Column(db.Integer, db.ForeignKey('person.id', ondelete='CASCADE', onupdate='CASCADE'))
    person = db.relationship('Person')
    convention_id = db.Column(db.Integer(), db.ForeignKey('convention.id', ondelete='CASCADE', onupdate='CASCADE'))
    convention = db.relationship('Convention', backref=db.backref('presenter_conflicts'))

class Timeslotbooking(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    timeslot_id = db.Column(db.Integer(), db.ForeignKey('timeslot.id', ondelete='CASCADE', onupdate='CASCADE'))
    timeslot = db.relationship('Timeslot', backref=db.backref('bookings'))
    room_id = db.Column(db.Integer(), db.ForeignKey('rooms.id', ondelete='CASCADE', onupdate='CASCADE'))
    room = db.relationship('Rooms')
    convention_id = db.Column(db.Integer(), db.ForeignKey('convention.id', ondelete='CASCADE', onupdate='CASCADE'))
    convention = db.relationship('Convention', backref=db.backref('timeslot_bookings'))
    
class Timeslotentry(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    booking_id = db.Column(db.Integer(), db.ForeignKey('timeslotbooking.id', ondelete='CASCADE', onupdate='CASCADE'))
    booking = db.relationship('Timeslotbooking', backref=db.backref('timeslot_entries'))
    event_id = db.Column(db.Integer(), db.ForeignKey('events.id', ondelete='CASCADE', onupdate='CASCADE'))
    event = db.relationship('Events')
    time_elapsed = db.Column(db.Interval())
    convention_id = db.Column(db.Integer(), db.ForeignKey('convention.id', ondelete='CASCADE', onupdate='CASCADE'))
    convention = db.relationship('Convention', backref=db.backref('timeslot_entries'))

def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def create_schedule_XML(convention_id):
    """
    Exports the events in XML format for the schedule book.

    TODO: expand this to match the format of 2013.penguicon.schedule.xml.
    """
    root = ET.Element('events')
    root.attrib['xmlns:xsi'] = 'http://www.w3.org/2001/XMLSchema-instance'
    document_elem = ET.SubElement(root, 'document')
    for event in Events.query.filter_by(convention_id=convention_id).all():
        event_elem = ET.SubElement(document_elem, 'event')
        title_elem = ET.SubElement(event_elem, 'title')
        title_elem.text = event.title
    indent(root)
    return ET.tostring(root, encoding='utf-8')

def get_schedule(convention):
    schedule_text = create_schedule_XML(convention.id)

    # Return XML prolog and XML schedule.
    return Response(
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' +
        schedule_text,
        mimetype='text/xml',
        headers={'Content-Disposition':
                 'attachment;filename=penguicon.schedule.xml'}
    )

@app.route('/convention/<convention_url>/schedulexml', methods=['GET'])
def get_schedule_url(convention_url):
    convention = Convention.query.fitler_by(url=convention_url).first()
    if convention is None:
        return redirect('/')
    return get_schedule(convention)

@app.route('/conventionschedulexml', methods=['GET'])
def get_schedule_args():
    convention = Convention.query.filter_by(id=request.args['id']).first
    if convention is None:
        return redirect('/')
    return get_schedule(convention)

def edit_convention_properties(convention):
    if (g.user is None) or (not g.user.staff):
        return redirect('/')
    if not convention is None:
        d = dict(convention.__dict__)
        d['start_date'] = u'{:%Y-%m-%d}'.format(convention.start_dt)
        d['start_time'] = u'{:%H:%M}'.format(convention.start_dt)
        d['end_date'] = u'{:%Y-%m-%d}'.format(convention.end_dt)
        d['end_time'] = u'{:%H:%M:%S}'.format(convention.end_dt)
        convention = d
    return render_template('/convention_properties.html', user=g.user, convention=convention)

@app.route('/conventionproperties')
def convention_properties_args():
    return edit_convention_properties(Convention.query.filter_by(id=request.args['id']).first() if 'id' in request.args else None) 

@app.route('/convention/<convention_url>/properties', methods=['GET'])
def convention_properties_url(convention_url):
    return edit_convention_properties(Convention.query.filter_by(url=convention_url).first())

from penguicontrax import audit
import copy

@app.route('/conventionupdate', methods=['POST'])
def convention_update():
    if g.user is None or not g.user.staff:
        return redirect('/')
    if 'id' in request.form:
        convention = Convention.query.filter_by(id=request.form['id'])
        old_convention = copy.copy(convention)
    else:
        convention = Convention()
        old_convention = Convention()
    if convention is None:
        return redirect('/')
    convention.name = request.form['name']
    convention.url = request.form['url']
    convention.description = request.form['description']
    start_date = request.form['start_date'].split('-')
    start_time = request.form['start_time'].split(':')
    end_date = request.form['end_date'].split('-')
    end_time = request.form['end_time'].split(':')
    convention.start_dt = datetime.datetime(year=int(start_date[0]), month=int(start_date[1]), day=int(start_date[2]), hour=int(start_time[0]), minute=int(start_time[1]))
    convention.end_dt = datetime.datetime(year=int(end_date[0]), month=int(end_date[1]), day=int(end_date[2]), hour=int(end_time[0]), minute=int(end_time[1]))
    db.session.add(convention)
    db.session.commit()
    audit.audit_change(Convention.__table__, g.user, old_convention, convention)
    return redirect('/convention/%s/' % convention.url)

def generate_timeslots(convention, timeslot_limit=sys.maxint):
    for timeslot in convention.timeslots:
        db.session.delete(timeslot)
    current = convention.start_dt
    end = convention.end_dt
    dow = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    first = True
    count = 0
    while (current < end) and (count < timeslot_limit):
        timeslot = Timeslot()
        timeslot.convention = convention
        timeslot.start_dt = current
        timeslot.name = '%s, %s' % (dow[current.weekday()], ('{:%I %p}'.format(current).lstrip('0'))) if (current.hour == 0 or first == True) else ('{:%I %p}'.format(current).lstrip('0'))
        db.session.add(timeslot)
        current += convention.timeslot_duration
        first = False
        count = count + 1
    db.session.commit()

def generate_schedule(convention):
    all_scheduled_events = Events.query.filter(Events.convention_id == convention.id, Events.start_dt != None).all()
    from operator import attrgetter
    all_scheduled_events.sort(key = attrgetter('start_dt'))
    scheduled_events = []
    cutoff_dt = None
    this_hour = None
    unassigned_room = 'unassigned_room'
    for event in all_scheduled_events:
        if cutoff_dt == None:
            this_hour = {}
            cutoff_dt = convention.start_dt + convention.timeslot_duration
            this_hour['time'] = convention.start_dt
            this_hour['rooms'] = dict()
            scheduled_events.append(this_hour)
        elif event.start_dt >= cutoff_dt:
            this_hour = {}
            this_hour['time'] = cutoff_dt
            this_hour['rooms'] = {}
            cutoff_dt = cutoff_dt + convention.timeslot_duration
            scheduled_events.append(this_hour)
        if len(event.rooms) > 0:
            room = event.rooms[0]
        else:
            room = unassigned_room
        if not (room in this_hour['rooms']):
            this_hour['rooms'][room] = []
        this_hour['rooms'][room].append({'event':event, 'time_left': datetime.timedelta(minutes = 15 * event.duration)})
        
    # Deal with events longer than timeslot_duration
    for hour_iter in range(len(scheduled_events)):
        for room, event_list in scheduled_events[hour_iter]['rooms'].iteritems():
            for event in event_list:
                overflow_left = datetime.timedelta(minutes = 15 * event['event'].duration) - convention.timeslot_duration
                next_hour = hour_iter
                while overflow_left > datetime.timedelta():
                    next_hour += 1
                    if next_hour < len(scheduled_events):
                        if scheduled_events[hour_iter]['rooms'][room] is None:
                            scheduled_events[hour_iter]['rooms'][room] = []
                        scheduled_events[hour_iter]['rooms'][room].append({'event':event, 'time_left':overflow_left})
                        overflow_left -= convention.timeslot_duration
                        
    # Evaluate conflicts
    for hour in scheduled_events:
        presenters = {}
        rsvps = {}
        for room, event_list in hour['rooms'].iteritems():
            for event_dict in event_list:
                event = event_dict['event']
                for userPresenter in event.userPresenters:
                    if not userPresenter in presenters:
                        presenters[userPresenter] = 0
                    presenters[userPresenter] += 1
                for personPresenter in event.personPresenters:
                    if not personPresenter in presenters:
                        presenters[personPresenter] = 0
                    presenters[personPresenter] += 1
                for user in event.rsvped_by:
                    if not user in rsvps:
                        rsvps[user] = 0
                    rsvps[user] += 1
        presenter_conflicts = []
        for presenter, commitments in presenters.iteritems():
            if commitments > 1:
                presenter_conflicts.append(presenter)
        rsvp_conflicts = 0
        for user, commitments in rsvps.iteritems():
            if commitments > 1:
                rsvp_conflicts += 1
        hour['presenter_conflicts'] = presenter_conflicts
        hour['rsvp_conflicts'] = rsvp_conflicts
        
                
    # Move everything over to the database
    for timeslot_entry in convention.timeslot_entries:
        db.session.delete(timeslot_entry)
    for timeslot_booking in convention.timeslot_bookings:
        db.session.delete(timeslot_booking)
    for presenter_conflict in convention.presenter_conflicts:
        db.session.delete(presenter_conflict)
    timeslots = {}
    for timeslot in convention.timeslots:
        timeslots[timeslot.start_dt] = timeslot
    for hour in scheduled_events:
        timeslot = timeslots[hour['time']]
        timeslot.rsvp_conflicts = hour['rsvp_conflicts']
        for presenter in hour['presenter_conflicts']:
            presenter_conflict = Presenterconflict()
            presenter_conflict.timeslot = timeslot
            from penguicontrax.user import Person, User
            if type(presenter) is Person:
                presenter_conflict.person = presenter
            elif type(presenter) is User:
                presenter_conflict.user = presenter
            db.session.add(presenter_conflict)
        for room, event_list in hour['rooms'].iteritems():
            booking = Timeslotbooking()
            booking.timeslot = timeslot
            booking.convention = convention
            if room != unassigned_room:
                booking.room = room
            for event in event_list:
                entry = Timeslotentry()
                entry.booking = booking
                entry.convention = convention
                entry.event = event['event']
                entry.time_elapsed = datetime.timedelta(minutes = 15 * event['event'].duration) - event['time_left']
                db.session.add(entry)
            db.session.add(booking)
        db.session.add(timeslot)
    db.session.commit()

def convention_schedule(convention):
    if convention is None:
        return redirect('/')
    unscheduled_events = Events.query.filter(Events.convention_id == convention.id, Events.start_dt == None).all()
    scheduled_events = convention.timeslots
    return render_template('convention_schedule.html', user=g.user, convention=convention, scheduled_events = scheduled_events, unscheduled_events = unscheduled_events, empty_timedelta = datetime.timedelta())

@app.route('/convention/<convention_url>/schedule')
def convention_schedule_url(convention_url):
    convention = Convention.query.filter_by(url=convention_url).first()
    return convention_schedule(convention) if not convention is None else redirect('/')

@app.route('/conventionschedule')
def convention_schedule_args():
    convention = Convention.query.filter_by(id=request.args['id']).first() if 'id' in request.args else None
    return convention_schedule(convention) if not convention is None else redirect('/')

@app.route('/convention/<convention_url>/')
def convention_index_url(convention_url):
   return convention_schedule_url(convention_url)
@app.route('/convention')
def convention_index_args():
    return convention_schedule_args()

def convention_rooms(convention):
    if g.user is None or not g.user.staff or convention is None:
        return redirect('/')
    return render_template('convention_rooms.html', user=g.user, convention=convention)

@app.route('/convention/<convention_url>/rooms')
def convention_rooms_url(convention_url):
    return convention_rooms(Convention.query.filter_by(url=convention_url).first())

def convention_editroom(convention, room):
    if g.user is None or not g.user.staff or convention is None:
        return redirect('/')
    return render_template('convention_editroom.html', user=g.user, convention=convention, room = room)

@app.route('/convention/<convention_url>/editroom')
def convention_editroom_url(convention_url):
    return convention_editroom(Convention.query.filter_by(url=convention_url).first(),\
        Rooms.query.filter_by(id=request.args['id']).first() if 'id' in request.args else None)
    
@app.route('/conventions', methods=['GET'])
def convention_list():
    if g.user is None or not g.user.staff:
        return redirect('/')
    return render_template('conventions.html', user=g.user, conventions=Convention.query.all())

def convention_solve(convention):
    if convention is None:
        return redirect('/')
    import solve
    return solve.solve_convention(convention, type = solve.SolveTypes.ECTTD, write_files = False)

@app.route('/convention/<convention_url>/solve')
def convention_solve_url(convention_url):
    return convention_solve(Convention.query.filter_by(url=convention_url).first())

@app.template_filter()
def get_date(dt):
    return Markup(u'{:%Y-%m-%d}'.format(dt)) if not dt is None else Markup(u'')

@app.template_filter()
def get_time(dt):
    return Markup(u'{:%H:%M}'.format(dt)) if not dt is None else Markup(u'')