from pulp import *
from flask import Markup

def solve_convention(convention):
    from penguicontrax.user import User, Person
    from penguicontrax.event import Events, Timeslot
    
    #a finite set H of hours
    timeslots = Timeslot.query.filter_by(convention_id=convention.id)
    H = [timeslot.id for timeslot in timeslots]
    
    combined_presenters = []
    combined_presenters.extend([(0, user.id) for user in User.query.all()])
    combined_presenters.extend([(1, person.id) for person in Person.query.all()])
    
    #a collection {P_1, P_2, ..., P_n}, where P_i is a subset of H
    #there are n presenters and P_i is the set of hours during which the ith teacher is available for teaching
    P = [H for presenter in combined_presenters] #all presenters always available
    
    total_events = Events.query.filter_by(convention_id=convention.id)
    
    #a collection {T_1, T_2, ..., T_m}, where T_j is a subset of H
    #there are m talks and T_j is the set of hours during which the jth talk can be given
    T = [H for event in total_events] #all events always available
    
    event_presenters= []
    for event in total_events:
        user_ids = [user.id for user in event.userPresenters]
        person_ids = [person.id for person in event.personPresenters]
        event_presenters.append((user_ids, person_ids))
    
    #an n x m matrix G of nonnegative integers 
    #G_ij is the number of hours (times) which the ith presenter will give the jth talk
    G = []
    for presenter in combined_presenters:
        GP = []
        for event_num in range(len(event_presenters)):
            event_presenter_list = event_presenters[event_num]
            if presenter[0] == 0:
                GP.append(1 if presenter[1] in event_presenter_list[0] else 0)
            else:
                GP.append(1 if presenter[1] in event_presenter_list[1] else 0)
        G.append(GP)
    
    prob = LpProblem('Convention Time Table Optimization Problem', LpMinimize)
    
    f_range = []
    for i in range(len(P)):
        for j in range(len(T)):
            for h in range(len(H)):
                f_range.append((i, j, h))
                
    f = LpVariable.dicts("f", f_range, cat="Integer")
    for k in f.viewkeys():
        f[k].lowBound = 0
        f[k].upBound = 1
    f_range = None
        

    prob += lpSum([f[(i,j,h)] for i in range(len(P)) for j in range(len(T)) for h in range(len(H))])
    
    #the presenter and talk are both available to be scheduled at hour
    for i in range(len(P)):
        for j in range(len(T)):
            for h in range(len(H)):
                available = 1 if (H[h] in P[i] and H[h] in T[j]) else 0
                prob += (f[(i,j,h)] <= available)
    
    #the ith presenter was scheduled for the jth talk the required number of times
    for i in range(len(P)):
        for j in range(len(T)):
            prob += lpSum([f[(i,j,h)] for h in range(len(H))]) == G[i][j]
            
    #no talk has more than one presenter at a time
    for j in range(len(T)):
        for h in range(len(H)):
            prob += lpSum([f[(i,j,h)] for i in range(len(P))]) <= 1
            
    #no presenter is giving more than one talk simultaneously
    for i in range(len(P)):
        for h in range(len(H)):
            prob += lpSum([f[(i,j,h)] for j in range(len(T))]) <= 1
    
    filename = '%s.mps' % convention.name
    prob.writeMPS(filename)
    
    filename = '%s.lp' % convention.name
    prob.writeLP(filename)
    
    with open(filename,'r') as f:
        return Markup.escape(f.read())