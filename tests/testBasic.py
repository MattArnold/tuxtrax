#!/usr/bin/env python

import penguicontrax
import unittest

penguicontrax.init()
app = penguicontrax.app

"""
The best way to run this and other tests is to run:
  nosetests

The unit tests do not require the web app to be running. It interacts with the Flask
application directly.

Should you want to see the stdout from these tests, set a unix shell variable like this:

export NOSE_NOCAPTURE=1
"""

class SimpleTest(unittest.TestCase):
    """Super simple unit tests to verify the app is functioning"""

    def setUp(self):
        pass
    
    #def test_bad(self):
    #    self.assertEqual(1,0)

    def login(self):
        """Fake a social login by inserting data into the database and setting a session."""
        t = penguicontrax.app.test_client(self)
        
        r = t.get('/fakelogin', content_type='html/text')

    def test_index(self):

        m="test_index"
        #print "Go time."
        t = penguicontrax.app.test_client(self)

        r = t.get('/', content_type='html/text')

        #print "Testing baby!"
        #print r

        self.assertEqual(r.status_code, 200, "test_eventform GET failed with %s" % r.status_code)
        self.assertTrue(b'penguicon-trax' in r.data, "%s: Page didn't contain 'penguicon-trax'" % m)
        self.assertTrue(b'Zombie Tag' in r.data, "%s: Page didn't contain 'Zombie Tag'" % m)

    def testZombieEventForm(self):
        """Pull the Zombie Tag event down."""

        m="testZombiEventForm"
        t = penguicontrax.app.test_client(self)

        r = t.get('/eventform?id=1', content_type='html/text')

        self.assertEqual(r.status_code, 200, "%s: GET failed with %s" % (m, r.status_code))
        self.assertTrue(b'Zombie Tag' in r.data, "%s: Page didn't contain 'Zombie Tag' event" % m)

    def testCreateEvent(self):
        """Create an event."""

        m="testCreateEvent"
        t = penguicontrax.app.test_client(self)

        args={ 'eventtype': 'talk',
               'resources' : '4', # drinking water
               'players':    '2', # default val?
               'roundtables': '0', 
               'longtables':  '1',
               'facilityrequest': 'Linen table clothes',
               'duration': '1',
               'setuptime': '1',
               'repetition': '2',
               'timerequest': '',
               'submitter': 'unit test',
               'firstname': 'Unit',
               'lastname':  'Tester',
               'email': 'rseward@bluestone-consulting.com', # 'unittest@penguicamp.com',
               'person0': 'Unit Tester',
               'tag_actionadventure':'actionadventure',
               'track': 'literature',
               'title': 'Hunger Games. Literature or not?',
               'comments': 'Best lecture on Hunger Games ever?',
               'submitevent':  'submitevent'
            }

        print "Posting a new event to /eventform"
        r = t.post('/submitevent', data=args )
        print r
        self.assertEqual(r.status_code, 302, "%s: POST failed with %s" % (m, r.status_code))

        # Check to see if the new event landed on the index page
        r = t.get('/', content_type='html/text')

        self.assertEqual(r.status_code, 200, "%s: GET failed with %s" % (m, r.status_code))
        self.assertTrue(b'Hunger Games' in r.data, "%s: Page didn't contain 'Hunger Games' event" % m)
        

if __name__ == "__main__":
    unittest.main()









