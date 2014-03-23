#flask libs
from flask import Flask, request
from flask.ext.restful import Resource, Api, reqparse
from sqlalchemy import or_

#global libs
from sys import exit
import sys
import os

## Import Local Libs
from penguicontrax import dump_table
from functions import return_null_if_not_logged_in
##from .. import user
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


class SearchUserAPI(Resource):
    @return_null_if_not_logged_in
    def get(self, search_string):
        search_string = '%' + search_string + '%'
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
