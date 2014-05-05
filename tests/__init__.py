import os.path
import json

from penguicontrax import app, db


DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')


def load_data(name, model):
    """Load a named JSON data fixture into the given model"""
    out = dict()
    path = os.path.join(DATA_PATH, '%s.json' % name)
    data = json.load(open(path, 'r'))
    for item in data:
        out[item['id']] = o = model(**item)
        db.session.add(o)
    db.session.commit()
    return out
