from flask import g, request, session, render_template, redirect
from .. import app, db

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
    followUpState = db.Column(db.Integer()) # 0 = submitted, 1 = followed up, 2 = accepted, 3 = rejected
        
    def __init(self):
        pass

    def __repr__(self):
        return '<email: %s, title: %s>' % self.name, self.email
    
class Tags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<name: %s>' % self.name
    
class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    staffId = db.Column(db.Integer())

    def __init__(self, name, staffId):
        self.name = name
        self.staffId = staffId

    def __repr__(self):
        return '<name: %s, staffId: %d>' % self.name, self.staffId
    
@app.route('/eventform', methods=['GET', 'POST'])
def event_form():
    tags = [tag.name for tag in Tags.query.all()]
    if request.method == 'GET':
        eventid = request.args.get('id',None)
        if eventid is not None:
            event = Submissions.query.filter_by(id=eventid).first()
        else:
            event = None
    return render_template('form.html', tags=tags, event=event, user=g.user)

@app.route('/submitevent', methods=['POST'])
def submitevent():
    eventid = request.form['eventid']
    if eventid is not None:
        submission = Submissions.query.filter_by(id=eventid).first()
    if submission is None:
        submission = Submissions()
    submission.email = request.form['email']
    submission.title = request.form['title']
    submission.description = request.form['description']
    submission.duration = request.form['duration']
    submission.setupTime = request.form['setuptime'] if request.form['setuptime'] is not None else 1 
    submission.repetition = request.form['repetition']
    submission.comments = request.form['comments']
    submission.firstname = request.form['firstname']
    submission.lastname = request.form['lastname']
    submission.followUpState = request.form['followupstate'] if request.form['followupstate'] is not None else 0
    db.session.add(submission)
    db.session.commit()
    return redirect('/')

@app.route('/createtag', methods=['POST'])
def createtag():
    tag = Tags(request.form['tagname'])
    db.session.add(tag)
    db.session.commit()
    return render_template('index.html')