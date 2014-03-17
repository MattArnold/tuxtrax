from pulp import *
from flask import Markup, Response

class SolveTypes:
    TTD = 1
    CTTD = 2
    ECTTD = 3

def solve_convention(convention, type = SolveTypes.TTD, write_files = False):
    from penguicontrax.user import User, Person
    from penguicontrax.event import Events, Timeslot, Rooms, generate_schedule, Convention
    from penguicontrax import db
    def solve():
        
        yield 'Querying databse for timeslots and events</br>'
        timeslots = Timeslot.query.filter_by(convention_id=convention.id).all()
        total_events = Events.query.filter_by(convention_id=convention.id).all()
        rooms = Rooms.query.filter_by(convention_id=convention.id).all()
        
        yield 'Creating lists of presenters</br>'
        event_presenters= []
        presenters_upperbound = 0
        for event in total_events:
            user_ids = [user.id for user in event.userPresenters]
            person_ids = [person.id for person in event.personPresenters]
            presenters_upperbound += len(user_ids) + len(person_ids)
            event_presenters.append((user_ids, person_ids))
        combined_presenters_set = set()
        for event_presenter_lists in event_presenters:
            for user in event_presenter_lists[0]:
                combined_presenters_set.add((0, user))
            for person in event_presenter_lists[1]:
                combined_presenters_set.add((1, person))
        
        yield 'Creating hour, presenter, and presentation sets<br/>'
        #a finite set H of hours
        H = [timeslot.id for timeslot in timeslots]
        
        #a collection {P_1, P_2, ..., P_n}, where P_i is a subset of H
        #there are n presenters and P_i is the set of hours during which the ith teacher is available for teaching
        P = [H for presenter in combined_presenters_set] #all presenters always available 
        
        #a collection {T_1, T_2, ..., T_m}, where T_j is a subset of H
        #there are m talks and T_j is the set of hours during which the jth talk can be given
        T = [H for event in total_events] #all events always available
        
        R = [room.id for room in rooms]
        
        yield 'Creating presentation requirement matrix<br/>'
        #an n x m matrix G of nonnegative integers 
        #G_ij is the number of hours (times) which the ith presenter will give the jth talk
        G = []
        for presenter in combined_presenters_set:
            GP = []
            for event_num in range(len(event_presenters)):
                event_presenter_list = event_presenters[event_num]
                if presenter[0] == 0:
                    GP.append(1 if presenter[1] in event_presenter_list[0] else 0)
                else:
                    GP.append(1 if presenter[1] in event_presenter_list[1] else 0)
            G.append(GP)
        
        prob = LpProblem('Convention Time Table Optimization Problem', LpMinimize)
        
        num_vars_f = len(P)*len(T)*len(H)
        num_vars_g = len(T)*len(H)*len(R) if type == SolveTypes.ECTTD else 0
        yield 'Creating %d scheduling variables<br/>' % (num_vars_f + num_vars_g)
        f = LpVariable.dicts('f', range(num_vars_f), cat='Integer')
        for k in f.viewkeys():
            f[k].lowBound = 0
            f[k].upBound = 1
        index = lambda i,j,h: (i*len(T)*len(H) + j*len(H) + h)
        if type == SolveTypes.ECTTD:
            g = LpVariable.dicts('g', range(num_vars_g), cat='Integer')
            for k in g.viewkeys():
                g[k].lowBound = 0
                g[k].upBound = 1
            indexg = lambda j,h,r: (j*len(H)*len(R) + h*len(R) + r)
    
        yield 'Creating objective function<br/>'
        prob += lpSum(([f[x] for x in range(num_vars_f)].extend([g[x] for x in range(num_vars_g)])) if type == SolveTypes.ECTTD else ([f[x] for x in range(num_vars_f)]))
        
        yield 'Creating constraint that each presenter and presentation must be available<br/>'
        #the presenter and talk are both available to be scheduled at hour
        for i in range(len(P)):
            for j in range(len(T)):
                for h in range(len(H)):
                    if not (H[h] in P[i] and H[h] in T[j]):
                        prob += (f[index(i,j,h)] == 0)
                            
        
        yield 'Creating constraint that each presenter is scheduled for all their presentations<br/>'
        #the ith presenter was scheduled for the jth talk the required number of times
        for i in range(len(P)):
            for j in range(len(T)):
                presenter_talk_sum = [f[index(i,j,h)] for h in range(len(H))]
                presenter_talk_requirement = G[i][j]
                prob += lpSum(presenter_talk_sum) == presenter_talk_requirement
        
        if type == SolveTypes.TTD:
            yield 'Creating constraint no talk has more than one presenter at a time<br/>'
            #no talk has more than one presenter at a time
            for j in range(len(T)):
                for h in range(len(H)):
                    prob += lpSum([f[index(i,j,h)] for i in range(len(P))]) <= 1
        elif type == SolveTypes.CTTD or type == SolveTypes.ECTTD:
            yield 'Creating constraint that all talks have all presenters scheduled for them<br/>'
            for i in range(len(P)):
                for i_ in range(len(P)):
                    if i == i_:
                        continue
                    for j in range(len(T)):
                        for h in range(len(H)):
                            if G[i][j] > 0 and G[i_][j] > 0:
                                prob += f[index(i,j,h)] == f[index(i_,j,h)]
                          
                
        yield 'Creating constraint that no presenter has multiple bookings in a timeslot</br>'
        #no presenter is giving more than one talk simultaneously
        for i in range(len(P)):
            for h in range(len(H)):
                    prob += lpSum([f[index(i,j,h)] for j in range(len(T))]) <= 1
                    
        if type == SolveTypes.ECTTD:
            yield 'Creating constraint that no room has more than one event per timeslot<br/>'
            for j in range(len(T)):
                for h in range(len(H)):
                    room_sum = lpSum([g[indexg(j,h,r)] for r in range(len(R))])
                    presenter_sum = lpSum([f[index(i,j,h)] for i in range(len(P))])
                    prob += room_sum <= presenter_sum 
                    prob += presenter_sum <= presenters_upperbound*room_sum
                    prob += room_sum <= 1
                        
                
        if write_files == True:
            yield 'Writing linear programming files<br/>'    
            filename = '%s.mps' % convention.name
            prob.writeMPS(filename)
            filename = '%s.lp' % convention.name
            prob.writeLP(filename)
        
        yield 'Solving...<br/>'
        result = prob.solve()
        
        yield 'Solution: %s<br/>' % LpStatus[result]
        
        if result == constants.LpStatusOptimal:
            yield 'Creating schedule from solution<br/>'
            for event in total_events:
                event.start_dt = None
                del event.rooms[:]
            for h in range(len(H)):
                for j in range(len(T)):
                    scheduled = False
                    room = None
                    event = total_events[j]
                    if type != SolveTypes.ECTTD:
                        for i in range(len(P)):
                            if f[index(i,j,h)].varValue == 1:
                                scheduled = True
                                break
                    else:
                        for r in range(len(R)):
                            if g[indexg(j,h,r)].varValue == 1:
                                scheduled = True
                                room = R[r]
                                break
                    if scheduled == True:
                        timeslot = Timeslot.query.filter_by(id=H[h]).first()
                        event.start_dt = timeslot.start_dt
                        if room == None:
                            yield unicode(Markup.escape(u'%s is scheduled at %s' % (event.title, unicode(timeslot.start_dt)))) + u'<br/>'
                        else:
                            db_room = Rooms.query.filter_by(id=room).first()
                            yield unicode(Markup.escape(u'%s is scheduled at %s in %s' % (event.title, unicode(timeslot.start_dt), db_room.room_name))) + u'<br/>'
                            event.rooms.append(db_room)
                        db.session.add(event)
            yield 'Applying schedule to database...<br/>'
            db.session.commit()
            generate_schedule(Convention.query.filter_by(id=convention.id).first())
        
    return Response(solve())
