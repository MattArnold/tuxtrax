from flask import g

def return_null_if_not_logged_in(func):
    def return_none(*args, **kwargs):
        if g.user is None:
            return "You must be logged in to perform this action.", 401
        return func(*args, **kwargs)
    return return_none
