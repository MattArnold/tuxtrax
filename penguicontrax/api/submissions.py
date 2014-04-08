#flask libs
import datetime

from flask.ext.restful import Resource, reqparse
from flask import g
from sqlalchemy import or_


#global libs
from penguicontrax import dump_table, db, audit, conn
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
            if g.user.points > 0:
                if not submission.first() in g.user.rsvped_to:
                    g.user.rsvped_to.append(submission.first())
                    g.user.points = g.user.points - 1
                    audit.audit_rsvp(g.user, submission.first())
                    db.session.add(g.user)
                    db.session.commit()
                    return None, 200
            return None, 400
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
        #first check that the id exists
        submission = Submission.query.filter_by(id=int(submission_id))
        if g.user is not None and submission.count() > 0:
            if submission.first() in g.user.rsvped_to:
                g.user.rsvped_to.remove(submission.first())
                g.user.points = g.user.points + 1
                audit.audit_rsvp(g.user, submission.first(), False)
                db.session.add(g.user)
                db.session.commit()
                return None, 200
            return None, 400
        return None, 404


class SubmissionsAPI(Resource):

    @staticmethod
    def query_db(parts):
        orbits = [Submission.followUpState == i for i in parts]
        query = Submission.query.filter(or_(*orbits))
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
            element['overdue'] = (datetime.datetime.now() - submissions[index].submitted_dt).days > 13
            element['followUpDays'] = (datetime.datetime.now() - submissions[index].submitted_dt).days
        import random
        random.shuffle(output)
        return output


    @staticmethod
    def get():
        """ Returns a list of objects to represent users in the database
            Pass a ?q=query to conduct a search by name and email
        """
        parser = reqparse.RequestParser()
        parser.add_argument('state', type=str)
        args = parser.parse_args()

        
        if args['state']:
            parts = args['state'].split(',')
        else:
            parts = ['0','1','2']

        
        output = SubmissionsAPI.query_db(parts)
        expires = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        return output, 200, {
            "Expires": expires.strftime("%a, %d %b %Y %H:%M:%S GMT"),
            "Cache-Control": "public, max-age=86400"
        }
