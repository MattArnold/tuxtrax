#from flask import Flask, request
from flask.ext.restful import Api
from penguicontrax import app

#api modules
import submissions
import users

#import json for date encoder
import json


#override for json encoder to handle datetime objects
class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        else:
            return json.JSONEncoder.default(self, obj)


api = Api(app)
#define routes


@api.representation('application/json')
def json_date(data, code, headers=None):
    resp = app.make_response(json.dumps(data, cls=DateEncoder))
    resp.headers.extend(headers or {})
    resp.status_code = code
    return resp

#submissions
##api.add_resource(submissions.SubmissionAPI,
##                 '/api/submission/<string:submission_id>/rsvp')
api.add_resource(submissions.SubmissionAPI,
                 '/api/submission/<string:submission_id>',
                 '/api/submission/<string:submission_id>/<string:noun>')
api.add_resource(submissions.SubmissionsAPI,
                 '/api/submissions')

#users
api.add_resource(users.UsersAPI,
                 '/api/users')
api.add_resource(users.UserAPI,
                 '/api/user/<int:id>')
api.add_resource(users.UserSubmissionsAPI,
                 '/api/user/<int:id>/submissions')
api.add_resource(users.UserPresentationsAPI,
                 '/api/user/<int:id>/presentations')
