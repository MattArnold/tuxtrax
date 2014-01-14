import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from contextlib import closing

DATABASE = 'penguicontrax.db'

app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    eventrqdb = g.db.execute('''SELECT email, title, description, duration,
                       setuptime, repetition, comments, firstname,
                       lastname FROM submissions''')
    tagdb = g.db.execute('SELECT name FROM tags')
    tags = [row[0] for row in tagdb.fetchall()]
    submissions = [dict(title=row[1], description=row[2], duration=row[3], firstname=row[7],
                   lastname=row[8]) for row in eventrqdb.fetchall()]
    return render_template('index.html', tags=tags, submissions=submissions)

@app.route('/eventform')
def event_form():
    tagdb = g.db.execute('SELECT name FROM tags')
    tags = [row[0] for row in tagdb.fetchall()]
    return render_template('form.html', tags=tags)

@app.route('/submitevent', methods=['POST'])
def submitevent():
    g.db.execute('''INSERT INTO submissions (email, title, description,
                 duration, setuptime, repetition, comments, firstname,
                 lastname) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                 [request.form['email'],
                 request.form['title'],
                 request.form['description'],
                 request.form['duration'],
                 request.form['setuptime'],
                 request.form['repetition'],
                 request.form['comments'],
                 request.form['firstname'],
                 request.form['lastname']])
    g.db.commit()
    return render_template('index.html')

@app.route('/createtag', methods=['POST'])
def createtag():
    g.db.execute("INSERT INTO tags (name) VALUES (?)", [request.form['tagname']])
    g.db.commit()
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
