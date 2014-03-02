from flask import g, request, session, render_template, redirect, Response, Markup
from .. import app, db
import xml.etree.ElementTree as ET


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

    def __init__(self, event_name):
        self.event_name = event_name

    def __repr__(self):
        return 'Event: %' % self.event_name


class Rooms(db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, primary_key=True)
    room_name = db.Column(db.String(50))
    room_groups_id = db.Column(db.Integer, db.ForeignKey('room_groups.id'))
    rooms_groups = db.relationship('RoomGroups', backref='room')

    def __init__(self, room_name):
        self.room_name = room_name

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
    id = db.Column(db.Integer, primary_key=True)
    convention_name = db.Column(db.String(50))
    description = db.Column(db.Text)
    start_dt = db.Column(db.DateTime)
    end_dt = db.Column(db.DateTime)
    default_duration = db.Column(db.Integer)

    def __init__(self, convention_name):
        self.convention_name = convention_name

    def __repr__(self):
        return 'Convention: %' % self.convention_name


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


def create_schedule_XML():
    """
    Exports the events in XML format for the schedule book.

    TODO: expand this to match the format of 2013.penguicon.schedule.xml.
    """
    root = ET.Element('events')
    root.attrib['xmlns:xsi'] = 'http://www.w3.org/2001/XMLSchema-instance'
    document_elem = ET.SubElement(root, 'document')
    for event in Events.query.all():
        event_elem = ET.SubElement(document_elem, 'event')
        title_elem = ET.SubElement(event_elem, 'title')
        title_elem.text = event.title
    indent(root)
    return ET.tostring(root, encoding='utf-8')


@app.route('/getschedule', methods=['GET'])
def get_schedule():
    schedule_text = create_schedule_XML()

    # Return XML prolog and XML schedule.
    return Response(
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' +
        schedule_text,
        mimetype='text/xml',
        headers={'Content-Disposition':
                 'attachment;filename=penguicon.schedule.xml'}
    )
