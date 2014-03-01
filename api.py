from flask import Flask, request
from flask.ext import restful
from flask.ext.restful import Resource, Api 
from icalendar import Calendar, Event
from datetime import datetime
from icalendar import LocalTimezone

app = Flask(__name__)
api = restful.Api(app)

class Events(Resource):
	def get(self):

		lt = LocalTimezone()
		dtstart = datetime(2014, 12, 1, 13, 0)
		dtend = datetime(2014, 12, 1, 14, 0)

		event = Event()
		event.add('summary', 'some summary')
		event.add('dtstart', dtstart) 

		return event.to_ical().splitlines()

api.add_resource(Events, '/')

if __name__ == '__main__':
	app.run(port=5050, debug=True)
