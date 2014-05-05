#!/usr/bin/env python
import logging
import unittest
from contextlib import contextmanager

from nose.tools import (ok_, eq_, raises, nottest)

from flask import g, session, appcontext_pushed

from . import load_data

import penguicontrax
from penguicontrax import app, db
from penguicontrax.user import User
from penguicontrax.tag import Tag
from penguicontrax.submission import Submission


class SimpleTest(unittest.TestCase):
    """Super simple unit tests to verify the app is functioning"""

    def setUp(self):
        penguicontrax.constants.DATABASE_URL = 'sqlite:////tmp/tuxtrax-test.db'
        penguicontrax.init()

        self.users = load_data('users', User)
        self.user1 = self.users[1001]

        self.client = app.test_client(self)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_index_anonymous(self):
        """Ensure home page exists"""
        with app.test_client() as c:
            resp = c.get('/', content_type='html/text')
            eq_(resp.status_code, 200)
            ok_('Log in using' in resp.data)
            ok_('Logged in as' not in resp.data)

    def test_index_logged_in(self):
        """Ensure home page reflects logged in user"""
        with app.test_client() as c:
            with c.session_transaction() as s:
                s['oauth_token'] = (self.user1.oauth_token,
                                    self.user1.oauth_secret)

            resp = c.get('/', content_type='html/text')
            eq_(resp.status_code, 200)
            ok_('Log in using' not in resp.data)
            ok_('Logged in as' in resp.data)

    def test_create_event(self):
        """Create an event."""
        with app.test_client() as c:
            with c.session_transaction() as s:
                s['oauth_token'] = (self.user1.oauth_token,
                                    self.user1.oauth_secret)

            args = {
                'eventtype': 'talk',
                'resources' : '4', # drinking water
                'players':    '2', # default val?
                'roundtables': '0', 
                'longtables':  '1',
                'facilityrequest': 'Linen table clothes',
                'duration': '1',
                'setuptime': '1',
                'repetition': '2',
                'timerequest': '',
                'submitter_id': '1001',
                'firstname': 'Unit',
                'lastname':  'Tester',
                'email': 'user@example.com',
                'person0': 'Unit Tester',
                'tag':['action-adventure'],
                'track': 'literature',
                'title': 'Hunger Games. Literature or not?',
                'description': 'Lorem ipsum dolor amet',
                'comments': 'Best lecture on Hunger Games ever?'
            }

            r = c.post('/submitevent', data=args )
            self.assertEqual(r.status_code, 302)

            # Ensure the event landed in the database
            result = Submission.query.filter_by(title=args['title']).first()
            ok_(result is not None)
            eq_(result.description, args['description'])

            # Ensure the event landed on the /logs page
            r = c.get('/logs', content_type='html/text')
            self.assertEqual(r.status_code, 200)
            self.assertTrue(args['title'] in r.data)
        

if __name__ == "__main__":
    unittest.main()
