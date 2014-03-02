#flask libs
from flask import Flask, request
from flask.ext.restful import Resource, Api

#global libs
from sys import exit;

## Import Local Libs
from penguicontrax import dump_table
from penguicontrax.submission import Submission
from functions import return_null_if_not_logged_in

class SubmissionAPI(Resource):
    @return_null_if_not_logged_in
    def get(self,submission_id):
        ## Output only one element
        output = dump_table(Submission.query.filter_by(id=int(submission_id)), Submission.__table__).pop()
        return output

class SubmissionsAPI(Resource):
    @return_null_if_not_logged_in
    def get(self):
        output = dump_table(Submission.query.all(), Submission.__table__)
        return output
