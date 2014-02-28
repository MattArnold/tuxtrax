import sqlite3, os
import xml.etree.ElementTree as ET
import penguicontrax as penguicontrax
from submission import Submission, Tag

def import_old():
    existing_tags = {}
    for tag in Tag.query.all():
        exisiting_tags[tag.name] = tag
    with penguicontrax.app.open_resource('schedule2013.html', mode='r') as f:
        tree = ET.fromstring(f.read())
        events = tree.find('document')
        for section in events:
            if section.tag == 'div' and section.attrib['class'] == 'section':
                name = section[0].text
                tag_list = section[1].text # Tag doesn't seem to be in the DB yet
                person = section[3][0].text
                # Only one presenter is supported so far
                firstPerson = person.split(',')[0].split(' ')
                description = section[3][0].tail
                submission = Submission()
                submission.email = 'none@none.com'
                submission.title = name
                submission.description = description
                submission.duration = True
                submission.setupTime = False
                submission.repetition = True
                submission.firstname = firstPerson[0]
                submission.lastname = firstPerson[1] if len(firstPerson) > 1 else ''  
                submission.followUpState = 0
                submission.tags = []
                for tag in tag_list.split(','):
                    tag = tag.strip()
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
                
