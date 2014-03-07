from penguicontrax import app, db
from flask import redirect, g, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime

class Audit(db.Model):
    id = db.Column(db.Integer(), primary_key = True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    user = db.relationship('User')
    log = db.Column(db.String())
    time = db.Column(db.DateTime())
    
    def __init__(self):
        self.time = datetime.now()
        
def parse_audit_ref(ref):
    table_pos = ref.find(u':')
    bad_ret = u'{%s}' % ref
    if table_pos == -1:
        return bad_ret
    table_name = ref[0:table_pos]
    clause_strs = ref[table_pos+1:].split(',')
    clauses = []
    for clause in clause_strs:
        parts = clause.split('=')
        if len(parts) != 2:
            return bad_ret
        clauses.append([parts[0].strip(), parts[1].strip()]) 
    table = db.metadata.tables[table_name] if table_name in db.metadata.tables.keys() else None
    if table == None:
        return bad_ret
    for clause in clauses:
        try:
            column = table.columns[clause[0]]
            clause[0] = column
            clause[1] = column.type.python_type(clause[1])
        except Exception as e:
            clauses.remove(clause)
    try:
        args = [clause[0] == clause[1] for clause in clauses]
        return table, db.session.query(table).filter(*args).first()
    except:
        pass
    return bad_ret
        
def audit_change(table, user, before, after):
    audit = Audit()
    audit.user = user
    audit.log = u'In {%s: id=%s}: ' % (unicode(table.name), unicode(after.id))
    before_dict = dict((col, getattr(before, col)) for col in table.columns.keys())
    after_dict = dict((col, getattr(after, col)) for col in table.columns.keys())
    first = True
    for key in before_dict.keys():
        if before_dict[key] != after_dict[key]:
            if first:
                first = False
            else:
                audit.log += u', '
            audit.log += u'%s: %s -> %s' % (unicode(key), unicode(before_dict[key]), unicode(after_dict[key]))
    db.session.add(audit)
    db.session.commit()

def audit_user_creation(user):
    audit = Audit()
    audit.user = user
    audit.log = u'Created by %s' % user.creation_ip
    db.session.add(audit)
    db.session.commit()

@app.route('/logs')
def logs():
    from user import User  
    from submission import Submission
    if g.user is None or g.user.staff == False:
        return redirect('/')
    logs = Audit.query.order_by(Audit.time.desc()).all()
    rendered_logs = []
    for log in logs:
        rendered_log = {}
        rendered_log['user'] = log.user
        rendered_log['time'] = log.time
        open = 0
        log_text = log.log
        length = len(log_text)
        result = u''
        try:
            while open < length:
                next = log_text.find(u'{', open)
                if next == open:
                    close = log_text.find(u'}', open + 1, length)
                    if close == -1:
                        raise Exception('Error parsing %s' % log_text)
                    ref = log_text[open + 1 : close]
                    ref_table, ref_obj = parse_audit_ref(ref)
                    if ref_obj is None:
                        result += render_template('audit_refs/unknown.html', ref_obj = None)
                    elif ref_table == User.__table__:
                        result += render_template('audit_refs/user.html', user = ref_obj)
                    elif ref_table == Submission.__table__:
                        result += render_template('audit_refs/submission.html', submission = ref_obj)
                    else:
                        result += render_template('audit_refs/unknown.html', ref_obj = ref_obj)
                    open = close + 1 
                    continue
                elif next == -1:
                    next = length
                if next > open:
                    result += log_text[open:next]
                    open = next
        except Exception as e:
            pass
        result = result.replace('->', '<i class="fa fa-arrow-right"></i>')
        rendered_log['log'] = result
        rendered_logs.append(rendered_log)
    return render_template('logs.html', logs=rendered_logs, user=g.user)