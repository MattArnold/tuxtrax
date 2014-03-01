#flask libs
from flask import Flask, request
from flask.ext.restful import Resource, Api

#global libs
from sys import exit;

## Import Local Libs
from .. import Submission, dump_table

events = {}
class EventsAPI(Resource):
    def get(self,event_id):
        ## Output only one element
        output = dump_table(Submission.query.filter_by(id=int(event_id)), Submission.__table__).pop()
        return output
