#flask libs
import datetime, json

from flask.ext.restful import Resource, reqparse
from flask import g
from sqlalchemy import or_
from redis import WatchError


#global libs
from penguicontrax import dump_table, db, audit, conn
from penguicontrax.submission import Track, get_track
from functions import return_null_if_not_logged_in, return_null_if_not_staff


class TracksAPI(Resource):
    def get(self):
        tracks = Track.query
        output = [{'name': t.name, 'staffId': t.staffId} for t in tracks]
        return output, 200
