#flask libs
import datetime, json

from flask.ext.restful import Resource, reqparse
from flask import g
from sqlalchemy import or_
from redis import WatchError


#global libs
from penguicontrax import dump_table, db, audit, conn
from penguicontrax.tag import Tag, create_tag, get_tag, get_user_tag
from functions import return_null_if_not_logged_in, return_null_if_not_staff


class TagsAPI(Resource):
    def get(self):
        tags = Tag.query.filter(Tag.system==True).all()
        output = [{'id': t.name, 'desc': t.desc} for t in tags]
        return output, 200


class UserTagsAPI(Resource):
    def get(self):
        tags = Tag.query.filter(Tag.system==False).all()
        output = [t.name for t in tags]
        return output, 200

    @return_null_if_not_logged_in
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=str, required=True)
        parser.add_argument('desc', type=str, default='')
        args = parser.parse_args()
        tag = create_tag(args['id'], args['desc'])
        output = {'id': tag.name, 'desc': tag.desc}
        return output


class UserTagAPI(Resource):
    def get(self, name):
        tag = get_user_tag(name)
        if tag is None:
            return 'Invalid id', 404
        output = {'id': tag.name, 'desc': tag.desc}
        return output

    @return_null_if_not_logged_in
    def put(self, name):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=str)
        parser.add_argument('desc', type=str)
        args = parser.parse_args()
        tag = get_user_tag(name)
        if tag is None:
            return 'Invalid id', 404
        dest_tag = get_user_tag(name)
        if dest_tag is not None:
            return 'Duplicate id', 400
        tag.name = args['id']
        if args['desc'] is not None:
            tag.desc = args['desc']
        db.session.add(tag)
        db.session.commit()
        output = {'id': tag.name, 'desc': tag.desc}
        return output

    @return_null_if_not_staff
    def delete(self, name):
        tag = get_user_tag(name)
        if tag is None:
            return 'Invalid id', 404
        db.session.delete(tag)
        db.session.commit()
        return 'Deleted', 200
