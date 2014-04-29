#flask libs
from flask.ext.restful import Resource, reqparse
from sqlalchemy import or_

## Import Local Libs
from penguicontrax import dump_table
from functions import return_null_if_not_logged_in
from penguicontrax.user import Presenter


class PresentersAPI(Resource):
    @return_null_if_not_logged_in
    def get(self):
        """ Returns a list of objects to represent users in the database
            Pass a ?q=query to conduct a search by name and email
        """
        parser = reqparse.RequestParser()
        parser.add_argument('q', type=str)
        args = parser.parse_args()
        output = Presenter.query
        if args['q']:
            search_string = '%' + args['q'] + '%'
            output = output.filter(
                or_(
                    Presenter.name.like(search_string),
                    Presenter.email.like(search_string),
                    Presenter.phone.like(search_string)
                )
            )
        output = dump_table(output, Presenter.__table__)
        # fields to show in search results
        fields = ['name', 'id', 'email', 'phone']
        return [
            dict([(name, element[name]) for name in fields])
            for element in output
        ]
