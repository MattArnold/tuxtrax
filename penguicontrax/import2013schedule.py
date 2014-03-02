import sqlite3, os
import xml.etree.ElementTree as ET
import penguicontrax as penguicontrax
from submission import Submission, Tag, Track, Resource, normalize_tag_name
from user import Person

def import_old():
    existing_tags = {}
    for tag in Tag.query.all():
        exisiting_tags[tag.name] = tag
    existing_people = {}
    for person in Person.query.all():
        existing_people[person.name] = person
    for resource in ['Projector', 'Microphone', 'Sound system', 'Drinking water', 'Quiet (no airwalls)']:
        penguicontrax.db.session.add(Resource(resource))
    for track in ['literature', 'tech', 'music', 'food', 'science']:
        penguicontrax.db.session.add(Track(track,None))
    with penguicontrax.app.open_resource('schedule2013.html', mode='r') as f:
        tree = ET.fromstring(f.read())
        events = tree.find('document')
        for section in events:
            if section.tag == 'div' and section.attrib['class'] == 'section':
                name = section[0].text
                tag_list = section[1].text # Tag doesn't seem to be in the DB yet
                person = section[3][0].text
                description = section[3][0].tail
                submission = Submission()
                submission.email = 'none@none.com'
                submission.title = name
                submission.description = description
                submission.duration = 1
                submission.setupTime = 0
                submission.repetition = 0
                submission.followUpState = 0
                #Load presenters
                submission.personPresenters= []
                for presenter in [presenter.strip() for presenter in person.split(',')]:
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
                penguicontrax.db.session.add(submission)
        penguicontrax.db.session.commit()

