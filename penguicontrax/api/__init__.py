from flask import Flask, request
from flask.ext.restful import Resource, Api
from .. import app

#api modules
import events

api = Api(app)
#define routes
api.add_resource(events.EventAPI,'/api/event/<string:event_id>')
api.add_resource(events.EventsAPI,'/api/events')


