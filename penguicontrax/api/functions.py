from flask import g

def return_null_if_not_logged_in(func):
    def returnNone(*args,**kwargs):
        if g.user == None:
            return None 
        return func(*args,**kwargs)
    return returnNone
