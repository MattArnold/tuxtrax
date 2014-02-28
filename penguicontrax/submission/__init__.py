from flask import g, request, session, render_template, redirect
from .. import app, db

tags = db.Table('tags', 
                db.Column('submission_id', db.Integer, db.ForeignKey('submission.id', ondelete='CASCADE', onupdate='CASCADE')), 
                db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')))
    
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<name: %s>' % self.name

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String())
    title = db.Column(db.String())
    description = db.Column(db.String())
    comments = db.Column(db.String())
    firstname = db.Column(db.String())
    lastname = db.Column(db.String())
    trackId = db.Column(db.Integer())
    duration = db.Column(db.Integer()) 
    setupTime = db.Column(db.Integer()) 
    repetition = db.Column(db.Integer()) 
    followUpState = db.Column(db.Integer()) # 0 = submitted, 1 = followed up, 2 = accepted, 3 = rejected
    tags = db.relationship('Tag', secondary=tags, backref=db.backref('submissions', passive_deletes=True))
        
    def __init(self):
        pass

    def __repr__(self):
        return '<email: %s, title: %s>' % self.name, self.email
    
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
    tags = [tag.name for tag in Tag.query.all()]
    if request.method == 'GET':
        eventid = request.args.get('id',None)
        event_tags = []
        if eventid is not None:
            event = Submission.query.filter_by(id=eventid).first()
            event_tags = [tag.name for tag in event.tags]
        else:
            event = None
    return render_template('form.html', tags=tags, event=event, user=g.user, event_tags=event_tags)

@app.route('/submitevent', methods=['POST'])
def submitevent():
    eventid = request.form['eventid'] if 'eventid' in request.form else None
    if eventid is not None:
        submission = Submission.query.filter_by(id=eventid).first()
    else:
        submission = Submission()
        submission.followUpState = 0
    submission.email = request.form['email']
    submission.title = request.form['title']
    submission.description = request.form['description']
    submission.duration = request.form['duration']
    submission.setupTime = request.form['setuptime'] if 'setuptime' in request.form else 1 
    submission.repetition = request.form['repetition']
    submission.comments = request.form['comments']
    submission.firstname = request.form['firstname']
    submission.lastname = request.form['lastname']
    if 'followupstate' in request.form:
        submission.followUpState = request.form['followupstate']
    submission.tags = []
    for tag in request.form.getlist('tagbtn'):
        submission.tags.append(Tag.query.filter_by(name=tag).first())
    db.session.add(submission)
    db.session.commit()
    return redirect('/')

@app.route('/createtag', methods=['POST'])
def createtag():
    tag = Tag(request.form['tagname'])
    db.session.add(tag)
    db.session.commit()
    return render_template('index.html')