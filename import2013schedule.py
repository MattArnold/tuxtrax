import sqlite3, os
import xml.etree.ElementTree as ET

app_directory = os.path.split(os.path.realpath(__file__))[0]
DATABASE = os.path.join(app_directory, 'penguicontrax.db')
db = sqlite3.connect(DATABASE)
tree = ET.parse(os.path.join(app_directory, 'schedule2013.html'))
events = tree.find('document')
for section in events:
    if section.tag == 'div' and section.attrib['class'] == 'section':
        name = section[0].text
        tag = section[1].text # Tag doesn't seem to be in the DB yet
        person = section[3][0].text
        # Only one presenter is supported so far
        firstPerson = person.split(',')[0].split(' ')
        description = section[3][0].tail
        db.execute('''INSERT INTO submissions (email, title, description,
                 duration, setuptime, repetition, comments, firstname,
                 lastname) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                 ['none@none.com', name, description, 1, 0, 1, '', firstPerson[0], firstPerson[1] if len(firstPerson) > 1 else ''])
db.commit()
db.close()