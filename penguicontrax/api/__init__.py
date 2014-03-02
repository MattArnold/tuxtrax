from flask import Flask, request
from flask.ext.restful import Resource, Api
from penguicontrax import app

#api modules
import submissions
import users

api = Api(app)
#define routes

#submissions
api.add_resource(submissions.SubmissionAPI,'/api/submission/<string:submission_id>')
api.add_resource(submissions.SubmissionsAPI,'/api/submissions')

#users
api.add_resource(users.SearchUserAPI,'/api/search_users/<string:search_string>')
