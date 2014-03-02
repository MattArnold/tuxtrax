#flask libs
from flask import Flask, request
from flask.ext.restful import Resource, Api
from flask import g

#global libs
from sys import exit;

## Import Local Libs
from penguicontrax import dump_table, db
from penguicontrax.submission import Submission
from penguicontrax.user import User, rsvps
from functions import return_null_if_not_logged_in

class SubmissionAPI(Resource):
    @return_null_if_not_logged_in
    def get(self,submission_id,noun):
        ## Output only one element
        output = dump_table(Submission.query.filter_by(id=int(submission_id)), Submission.__table__).pop()
        return output
    @return_null_if_not_logged_in
    def post(self,submission_id,noun):
        nouns = {
            'rsvp':self.__rsvp_post
        }
        if nouns.has_key(noun.lower()):
            return nouns[noun.lower()](submission_id)
        return 'Noun not found', 404
    def __rsvp_post(self,submission_id):
        #first check that the id exists
        submission = Submission.query.filter_by(id=int(submission_id)) 
        if g.user != None and submission.count() > 0:
            # getthe user id
            id = g.user.id
            g.user.rsvped_to.append(submission.first())
            db.session.add(g.user)
            db.session.commit()
            return None,'200'
        return None,'404'

class SubmissionsAPI(Resource):
    @return_null_if_not_logged_in
    def get(self):
        output = dump_table(Submission.query.all(), Submission.__table__)
        return output
