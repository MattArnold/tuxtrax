#flask libs
from flask.ext.restful import Resource, reqparse
from flask import g
from sqlalchemy import or_

#global libs
from penguicontrax import dump_table, db
from penguicontrax.submission import Submission
from functions import return_null_if_not_logged_in


class SubmissionAPI(Resource):
    def get(self, submission_id, noun=None):
        submission = Submission.query.filter_by(id=int(submission_id)).all()
        ## Output only one element
        output = dump_table(submission, Submission.__table__).pop()
        output['tags'] = [_.name for _ in submission[0].tags]
        output['personPresenters'] = [_.name for _ in submission[0].personPresenters]
        user_map = ['name', 'email', 'id']
        output['userPresenters'] = [dict([(field, getattr(_, field)) for field in user_map]) for _ in
                                    submission[0].userPresenters]
        output['rsvped_by'] = [dict([(field, getattr(_, field)) for field in user_map]) for _ in
                               submission[0].rsvped_by]
        return output, 200

    @return_null_if_not_logged_in
    def post(self, submission_id, noun):
        nouns = {
            'rsvp': self.__rsvp_post
        }
        if nouns.has_key(noun.lower()):
            return nouns[noun.lower()](submission_id)
        return 'Noun not found', 404

    def __rsvp_post(self, submission_id):
        #first check that the id exists
        submission = Submission.query.filter_by(id=int(submission_id))
        if g.user is not None and submission.count() > 0:
            # get the user id
            id = g.user.id
            g.user.rsvped_to.append(submission.first())
            db.session.add(g.user)
            db.session.commit()
            return None, 200
        return None, 404

    @return_null_if_not_logged_in
    def delete(self, submission_id, noun):
        nouns = {
            'rsvp': self.__rsvp_delete
        }
        if noun.lower() in nouns:
            return nouns[noun.lower()](submission_id)
        return 'Delete Noun not found', 404

    def __rsvp_delete(self, submission_id):
        #first check that the id exists x
        submission = Submission.query.filter_by(id=int(submission_id))
        if g.user is not None and submission.count() > 0:
            # get the user id
            id = g.user.id
            g.user.rsvped_to.remove(submission.first())
            db.session.delete(g.user)
            db.session.commit()
            return None, 200
        return None, 404


class SubmissionsAPI(Resource):
    @staticmethod
    def get():
        """ Returns a list of objects to represent users in the database
            Pass a ?q=query to conduct a search by name and email
        """
        parser = reqparse.RequestParser()
        parser.add_argument('state', type=str)
        args = parser.parse_args()

        query = Submission.query
        if args['state']:
            parts = args['state'].split(',')
            orbits = [Submission.followUpState == i for i in parts]
            query = query.filter(or_(*orbits))
        else:
            query = query.filter(Submission.followUpState != 3)
        submissions = query.all()
        output = dump_table(submissions, Submission.__table__)
        for index, element in enumerate(output):
            element['tags'] = [_.name for _ in submissions[index].tags]
            element['personPresenters'] = [_.name for _ in submissions[index].personPresenters]
            user_map = ['name', 'email', 'id']
            element['userPresenters'] = [dict([(field, getattr(_, field)) for field in user_map]) for _ in
                                         submissions[index].userPresenters]
            element['rsvped_by'] = [dict([(field, getattr(_, field)) for field in user_map]) for _ in
                                    submissions[index].rsvped_by]
        return output
