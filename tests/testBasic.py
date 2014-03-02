#!/usr/bin/env python

import penguicontrax
import unittest

penguicontrax.init()
app = penguicontrax.app

class SimpleTest(unittest.TestCase):

    def setUp(self):
        pass
    
    #def test_bad(self):
    #    self.assertEqual(1,0)

    def test_index(self):
        print "Go time."
        t = penguicontrax.app.test_client(self)

        r = t.get('/', content_type='html/text')

        print "Testing baby!"
        print r

        self.assertEqual(r.status_code, 200)
        assert b'penguicon-trax' in r.data


if __name__ == "__main__":
    unittest.main()
