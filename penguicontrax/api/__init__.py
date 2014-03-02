from flask import Flask, request
from flask.ext.restful import Resource, Api
from penguicontrax import app

#api modules
import events
import users

api = Api(app)
#define routes

#events
api.add_resource(events.EventAPI,'/api/event/<string:event_id>')
api.add_resource(events.EventsAPI,'/api/events')

#users
api.add_resource(users.SearchUserAPI,'/api/search_users/<string:search_string>')
