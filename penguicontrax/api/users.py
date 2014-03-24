#flask libs
from flask import Flask, request, g
from flask.ext.restful import Resource, Api, reqparse
from sqlalchemy import or_

#global libs
from sys import exit
import sys
import os

## Import Local Libs
from penguicontrax import dump_table
from functions import return_null_if_not_logged_in
from .. import db
##User = user.User
from penguicontrax.user import User


class UsersAPI(Resource):
    @return_null_if_not_logged_in
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('q', type=str)
        args = parser.parse_args()

        output = User.query
        if args['q']:
            search_string = '%' + args['q'] + '%'
            output = User.query.filter(
                or_(
                    User.name.like(search_string),
                    User.email.like(search_string),
                    User.account_name.like(search_string)
                    )
                )
        output = dump_table(output, User.__table__)
        fields = ['id', 'name', 'email']
        return [
            dict([(name, element[name]) for name in fields])
            for element in output
        ]


class UserAPI(Resource):
    def get(self, id):
        found = User.query.get(id)
        if found:
            self_fields = ['id', 'name', 'staff', 'email', 'points', 'image_large', 'image_small', 'public_rsvps', 'rsvped_to', 'superuser', 'creation_ip']
            loggedin_fields = ['id', 'name', 'points', 'image_large', 'image_small', 'public_rsvps', 'rsvped_to']
            anon_fields = ['id', 'name', 'image_large', 'image_small']
            if g.user == None:
                fields = anon_fields
            elif g.user.id == id:
                fields = self_fields
            else:
                fields = loggedin_fields
                if not found.public_rsvps:
                    fields.remove('rsvped_to')
            return dict([(name, getattr(found, name)) for name in fields])
    def put(self, id):
        found = User.query.get(id)
        if g.user:
            if found:
                if g.user.id == id:
                    fields = ['name', 'email']
                    parser = reqparse.RequestParser()
                    for field in fields:
                        parser.add_argument(field, type=str)
                    args = parser.parse_args()
                    for field in fields:
                        if args[field]:
                            setattr(found, field, args[field])
                    if any(args):
                        db.session.commit()
                    return "Success"
                else:
                    return "Unauthorized", 403
            else:
                return "Invalid ID", 404
        else:
            return "Unauthenticated", 401
