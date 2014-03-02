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
    def get(self,submission_id,noun=None):
        submission = Submission.query.filter_by(id=int(submission_id)).all()
        ## Output only one element
        output = dump_table(submission, Submission.__table__).pop()
        output['tags'] = [_.name for _ in submission[0].tags]
        output['personPresenters'] = [_.name for _ in submission[0].personPresenters]
        user_map = ['name','email','id']
        output['userPresenters'] = [dict(field,getattr(_,field)) for _ in submission[0].userPresenters]
        return output,200

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

    @return_null_if_not_logged_in
    def delete(self,submission_id,noun):
        nouns = {
            'rsvp':self.__rsvp_delete
        }
        if nouns.has_key(noun.lower()):
            return nouns[noun.lower()](submission_id)
        return 'Delete Noun not found', 404
    def __rsvp_delete(self,submission_id):
        #first check that the id exists x
        submission = Submission.query.filter_by(id=int(submission_id)) 
        if g.user != None and submission.count() > 0:
            # getthe user id
            id = g.user.id
            g.user.rsvped_to.remove(submission.first())
            db.session.delete(g.user)
            db.session.commit()
            return None,'200'
        return None,'404'
        

class SubmissionsAPI(Resource):
    @return_null_if_not_logged_in
    def get(self):
        submissions = Submission.query.all()
        output = dump_table(submissions, Submission.__table__)
        for index,element in enumerate(output):
            element['tags'] = [_.name for _ in submissions[index].tags]
            element['personPresenters'] = [_.name for _ in submissions[index].personPresenters]
            user_map = ['name','email','id']
            element['userPresenters'] = [dict(field,getattr(_,field)) for _ in submissions[index].userPresenters]
        return output
