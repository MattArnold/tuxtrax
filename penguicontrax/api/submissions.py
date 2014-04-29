#flask libs
import datetime, json

from flask.ext.restful import Resource, reqparse
from flask import g
from sqlalchemy import or_
from redis import WatchError


#global libs
from penguicontrax import dump_table, db, audit, conn
from penguicontrax.submission import Submission, submission_dataset_ver, submission_dataset_changed
from functions import return_null_if_not_logged_in


class SubmissionAPI(Resource):
    def get(self, submission_id, noun=None):
        submission = Submission.query.filter_by(id=int(submission_id)).all()
        ## Output only one element
        output = dump_table(submission, Submission.__table__).pop()
        output['tags'] = [_.name for _ in submission[0].tags]
        user_map = ['name', 'email', 'id']
        output['submitter'] = dict([(field, getattr(submission[0].submitter, field)) for field in user_map])
        output['presenters'] = [dict([(field, getattr(_, field)) for field in user_map]) for _ in
                                    submission[0].presenters]
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
                    submission_dataset_changed()
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
                submission_dataset_changed()
                db.session.add(g.user)
                db.session.commit()
                return None, 200
            return None, 400
        return None, 404


class SubmissionsAPI(Resource):

    @staticmethod
    def expand_presenter(presenter):
        presenter_map = ['name', 'email', 'id', 'special_tag', 'account_name', 'image_small']
        ret = {}
        for key in presenter_map:
            if hasattr(presenter, key):
                ret[key] = getattr(presenter, key)
            elif presenter.user is not None and \
                 hasattr(presenter.user, key):
                ret[key] = getattr(presenter.user, key)
            else:
                ret[key] = None
        return ret

    @staticmethod
    def query_db(parts):
        orbits = [Submission.followUpState == i for i in parts]
        query = Submission.query.filter(or_(*orbits))
        submissions = query.all()
        output = dump_table(submissions, Submission.__table__)
        for index, element in enumerate(output):
            element['tags'] = [_.name for _ in submissions[index].tags]
            user_map = ['name', 'email', 'id', 'special_tag', 'account_name', 'image_small']
            element['presenters'] = [SubmissionsAPI.expand_presenter(_) for _ in
                                         submissions[index].presenters]
            element['rsvped_by'] = [dict([(field, getattr(_, field)) for field in user_map]) for _ in
                                    submissions[index].rsvped_by]
            element['overdue'] = (datetime.datetime.now() - submissions[index].submitted_dt).days > 13
            element['followUpDays'] = (datetime.datetime.now() - submissions[index].submitted_dt).days
            if not submissions[index].submitter is None:
                element['submitter'] = dict([(field, getattr(submissions[index].submitter, field)) for field in user_map])
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
        
        try:
            with conn.pipeline() as pipe:
                cache_key = 'SUBMISSION_DATASET_CACHE_' + str(parts)
                cache_version_key = cache_key + '_VERSION'
                while 1:
                    try:
                        pipe.watch(cache_version_key)
                        current_cache_value = pipe.get(cache_version_key)
                        current_version = submission_dataset_ver()
                        if current_cache_value == current_version and not current_cache_value is None:
                            output = pipe.get(cache_key)
                        else:
                            pipe.multi()
                            output = SubmissionsAPI.query_db(parts)
                            from penguicontrax.api import DateEncoder
                            pipe.set(cache_key, json.dumps(output, cls=DateEncoder))
                            pipe.set(cache_version_key, current_version)
                            pipe.execute()
                        break
                    except WatchError:
                        continue
        except Exception as e:
            output = SubmissionsAPI.query_db(parts)

        expires = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        return output, 200, {
            "Expires": expires.strftime("%a, %d %b %Y %H:%M:%S GMT"),
            "Cache-Control": "public, max-age=86400"
        }
