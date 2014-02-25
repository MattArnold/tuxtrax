from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from contextlib import closing
from flask.ext.sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
os.environ['DATABASE_URL'] = 'sqlite:///penguicontrax.db'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app);
app.config.from_object(__name__)

class Submissions(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(120))
	title = db.Column(db.String(120))
	description = db.Column(db.String(120))
	comments = db.Column(db.String(120))
	firstname = db.Column(db.String(120))
	lastname = db.Column(db.String(120))
	trackId = db.Column(db.Integer())
	duration = db.Column(db.Boolean()) 
	setupTime = db.Column(db.Boolean()) 
	repetition = db.Column(db.Boolean()) 

	def __init__(self, email, title, description, comments, firstname, lastname):
		self.email = email 
		self.title = title 
		self.description = description 
		self.comments = comments 
		self.firstname = firstname 
		self.lastname = lastname 
		self.trackId = trackId 
		self.duration = duration 
		self.setupTime = setupTime 
		self.repetition = repetition 

	def __repr__(self):
		return '<email: %s, title: %s>' % self.name, self.email

class Tags(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50))

	def __init__(self, name):
		self.name = name

	def __repr__(self):
		return '<name: %s>' % self.name

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	firstName = db.Column(db.String(50))
	lastName = db.Column(db.String(50))
	email = db.Column(db.String(120))

	def __init__(self, firstName, lastName, email):
		self.firstName = firstName
		self.lastName = lastName 
		self.email = email

	def __repr__(self):
		return '<name: %s %s, email: >' % self.firstName, self.lastName, self.email

class Track(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50))
	staffId = db.Column(db.Integer())

	def __init__(self, name, staffId):
		self.name = name
		self.staffId = staffId

	def __repr__(self):
		return '<name: %s, staffId: %d>' % self.name, self.staffId

@app.route('/')
def index():
	submissions = Submissions.query.all()
	tags = [tag.name for tag in Tags.query.all()]
	return render_template('index.html', tags=tags, submissions=submissions)

@app.route('/eventform')
def event_form():
	tags = [tag.name for tag in Tags.query.all()]
	return render_template('form.html', tags=tags)

@app.route('/submitevent', methods=['POST'])
def submitevent():
	user = User()
	user.email = request.form['email']
	user.title = request.form['title']
	user.description = request.form['description']
	user.duration = request.form['duration']
	user.setuptime = request.form['setuptime']
	user.repetition = request.form['repetition']
	user.comments = request.form['comments']
	user.firstname = request.form['firstname']
	user.lastname = request.form['lastname']
	db.session.add(user)
	db.session.commit()
	return render_template('index.html')

@app.route('/createtag', methods=['POST'])
def createtag():
	tag = Tags(request.form['tagname'])
	db.session.add(tag)
	db.session.commit()
	return render_template('index.html')

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)