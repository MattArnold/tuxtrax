import sqlite3, os
import xml.etree.ElementTree as ET
import penguicontrax as penguicontrax
from submission import Submissions, Tags

def import_old():
    with penguicontrax.app.open_resource('schedule2013.html', mode='r') as f:
        tree = ET.fromstring(f.read())
        events = tree.find('document')
        for section in events:
            if section.tag == 'div' and section.attrib['class'] == 'section':
                name = section[0].text
                tags = section[1].text # Tag doesn't seem to be in the DB yet
                person = section[3][0].text
                # Only one presenter is supported so far
                firstPerson = person.split(',')[0].split(' ')
                description = section[3][0].tail
                submission = Submissions()
                submission.email = 'none@none.com'
                submission.title = name
                submission.description = description
                submission.duration = 1
                submission.setupTime = 0
                submission.repetition = 1
                submission.firstname = firstPerson[0]
                submission.lastname = firstPerson[1] if len(firstPerson) > 1 else ''  
                submission.followUpState = 0
                for tag in tags.split(','):
                    tag = tag.strip()
                    if Tags.query.filter_by(name=tag).first() is None:
                        penguicontrax.db.session.add(Tags(tag))
                penguicontrax.db.session.add(submission)
                penguicontrax.db.session.commit()
                