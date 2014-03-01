#flask libs
from flask import Flask, request
from flask.ext.restful import Resource, Api

#global libs
from sys import exit;

## Import Local Libs
from .. import Submission, dump_table

events = {}
class EventAPI(Resource):
    def get(self,event_id):
        ## Output only one element
        output = dump_table(Submission.query.filter_by(id=int(event_id)), Submission.__table__).pop()
        return output
class EventsAPI(Resource):
    def get(self):
        output = dump_table(Submission.query.all(), Submission.__table__)
        return output
