import sqlite3, os
import xml.etree.ElementTree as ET
import penguicontrax as penguicontrax
from submission import Submission, Tag, Track, Resource, normalize_tag_name
from user import Person, User
from event import Convention, Rooms, Events
import datetime, random
from user.Login import generate_account_name, gravatar_image_update
import sys

def import_old(as_convention, random_rsvp_users = 0, submission_limit = sys.maxint, timeslot_limit = sys.maxint):
    
    if as_convention == True:
        convention = Convention()
        convention.name = 'Penguicon 2013'
        convention.url = '2013'
        convention.description = 'Penguicon 2013 schedule imported from schedule2013.html'
        convention.start_dt = datetime.datetime(year=2013, month=4, day=26, hour=16)
        convention.end_dt = datetime.datetime(year=2013, month=4, day=28, hour=16)
        convention.timeslot_duration = datetime.timedelta(hours=1)
        penguicontrax.db.session.add(convention)
        current_day = convention.start_dt.date()
        current_time = None
        
    existing_tags = {}
    for tag in Tag.query.all():
        existing_tags[tag.name] = tag
        
    existing_people = {}
    for person in Person.query.all():
        existing_people[person.name] = person
        
    existing_rooms = {}
    existing_submissions = []

    if as_convention == False:
        for resource in ['Projector', 'Microphone', 'Sound system', 'Drinking water', 'Quiet (no airwalls)']:
            penguicontrax.db.session.add(Resource(resource))
        for track in ['literature', 'tech', 'music', 'food', 'science']:
            penguicontrax.db.session.add(Track(track,None))
            
    submission_count = 0
    with penguicontrax.app.open_resource('schedule2013.html', mode='r') as f:
        tree = ET.fromstring(f.read())
        events = tree.find('document')
        for section in events:
            if submission_count == submission_limit:
                break
            if as_convention == True and section.tag == 'time':
                time_text= section.text.split(' ')
                hour = int(time_text[0])
                if time_text[1] == 'PM' and hour != 12:
                    hour += 12
                elif time_text[1] == 'AM' and hour == 12:
                    hour = 0
                new_time = datetime.time(hour = hour)
                if not current_time is None and new_time.hour < current_time.hour:
                    current_day = current_day + datetime.timedelta(days=1)
                current_time = new_time                 
            elif section.tag == 'div' and section.attrib['class'] == 'section':
                name = section[0].text
                tag_list = section[1].text # Tag doesn't seem to be in the DB yet
                room = section[2].text
                person = section[3][0].text
                description = section[3][0].tail
                submission = Submission() if as_convention == False else Events()
                submission.title = name
                submission.description = description
                submission.duration = 1
                submission.setupTime = 0
                submission.repetition = 0
                submission.followUpState = 0
                submission.eventType = 'talk'
                #Load presenters
                submission.personPresenters= []
                for presenter in [presenter.strip() for presenter in person.split(',')]:
                    if presenter == 'Open':
                        continue #"Open" person will cause the schedule to become infesible
                    person = None
                    if not presenter in existing_people:
                        person = Person(presenter)
                        penguicontrax.db.session.add(person)
                        existing_people[presenter] = person
                    else:
                        person = existing_people[presenter]
                    submission.personPresenters.append(person)
                #Load Tags
                submission.tags = []
                for tag in tag_list.split(','):
                    tag = normalize_tag_name(tag)
                    db_tag = None
                    if not tag in existing_tags:
                        db_tag = Tag(tag)
                        penguicontrax.db.session.add(db_tag)
                        existing_tags[tag] = db_tag
                    else:
                        db_tag = existing_tags[tag]
                    submission.tags.append(db_tag)
                #Load rooms
                if as_convention == True:
                    submission.convention = convention
                    db_room = None
                    if not room in existing_rooms:
                        db_room = Rooms()
                        db_room.room_name = room
                        db_room.convention = convention
                        penguicontrax.db.session.add(db_room)
                        existing_rooms[room] = db_room
                    else:
                        db_room = existing_rooms[room]
                    if not current_day is None and not current_time is None:
                        submission.rooms.append(db_room)
                        submission.start_dt = datetime.datetime(year=current_day.year, month=current_day.month, day=current_day.day,\
                            hour = current_time.hour, minute=current_time.minute)
                        submission.duration = 4 #1 hour
                existing_submissions.append(submission)
                penguicontrax.db.session.add(submission)
                submission_count = submission_count + 1
        penguicontrax.db.session.commit()

    if random_rsvp_users > 0:
        for user_index in range(random_rsvp_users):
            user = User()
            user.name = 'Random User %d' % user_index
            user.email = '%d@randomtraxuser.com' % user_index
            user.public_rsvps = True
            user.staff = False
            user.special_tag = None
            user.superuser = False
            generate_account_name(user)
            gravatar_image_update(user)
            for rsvp_index in range(user.points):
                rand = random.randint(0, len(existing_submissions) - 1)
                while user in existing_submissions[rand].rsvped_by:
                    rand = random.randint(0, len(existing_submissions) - 1)
                existing_submissions[rand].rsvped_by.append(user)
            user.points = 0
            penguicontrax.db.session.add(user)
        penguicontrax.db.session.commit()
        
    if as_convention == True:
        from event import generate_schedule, generate_timeslots
        generate_timeslots(convention, timeslot_limit)
        all_rooms = [room for room in existing_rooms.viewvalues()]
        hackerspace = [existing_rooms['Hackerspace A'], existing_rooms['Hackerspace B']]
        food = [existing_rooms['Food']]
        from copy import copy
        general_rooms = copy(all_rooms)
        general_rooms.remove(hackerspace[0])
        general_rooms.remove(hackerspace[1])
        general_rooms.remove(food[0])
        timeslots = [timeslot for timeslot in convention.timeslots]
        for submission in existing_submissions:
            if food[0] in submission.rooms:
                submission.suitable_rooms = food
            elif hackerspace[0] in submission.rooms or hackerspace[1] in submission.rooms:
                submission.suitable_rooms = hackerspace
            else:
                submission.suitable_rooms = general_rooms
        for room in all_rooms:
            room.available_timeslots = timeslots
        generate_schedule(convention)
            