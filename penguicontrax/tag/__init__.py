import string
from .. import db
from sqlalchemy.exc import IntegrityError
import re

class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True)
    desc = db.Column(db.String())
    system = db.Column(db.Boolean())

    def __init__(self, name, desc, system):
        self.name = name
        self.desc = desc
        self.system = system

    def __repr__(self):
        return self.name


def get_tag(name):
    # returns the tag by this name, or None if it doesn't exist
    name = normalize_tag_name(name)
    tag = Tag.query.filter(Tag.name == name).first()
    return tag


def get_user_tag(name):
    # returns the tag by this name, or None if it doesn't exist
    name = normalize_tag_name(name)
    tag = Tag.query.filter(Tag.name == name).filter(Tag.system==False).first()
    return tag


def create_tag(name, desc=None, system=False):
    name = normalize_tag_name(name)
    if desc is None:
        desc = name
    tag = Tag.query.filter(Tag.name == name).first()
    if not tag:
        try:
            tag = Tag(name, desc, system)
            db.session.add(tag)
            db.session.commit()
        except IntegrityError:
            # managed to get created by someone else
            tag = Tag.query.filter(Tag.name == name).first()
    return tag

def normalize_tag_name(name):
    """ Takes a possible name and changes it to only have
        lowercase and - characters
    """
    removables = re.compile('[^ a-zA-Z0-9]')
    name = name.lower().strip()
    name = removables.sub('', name)
    name = "-".join(name.split())
    return name


