#include "database.h"
#include <soci-postgresql.h>
#include <soci-sqlite3.h>
#include <iostream>

using namespace std;
using namespace soci;

database::database(const std::string& dburl, int _convention) : convention(_convention)
{
    if(dburl.find("sqlite3:///") == 0)
    {
        auto file = dburl.substr(11);
        db.open(sqlite3, file);
    }

    //TODO: POSTGRES
}

database::~database()
{
}

std::vector<database::event> database::get_events()
{
    std::vector<event> events;
    rowset<row> rs = (db.prepare << "select id,title from events where convention_id=:convention;", use(convention));
    for(auto it = rs.begin() ; it != rs.end() ; ++it)
    {
        event e;
        e.id = it->get<int>(0);
        e.name = it->get<string>(1);

        rowset<row> us = (db.prepare << "select user_id from user_event where event_id=:id;", use(e.id));
        for(auto user_it = us.begin() ; user_it != us.end() ; ++user_it)
            e.user_presenters.insert(user_it->get<int>(0));

        rowset<row> ps = (db.prepare << "select person_id from person_event where events_id=:id;", use(e.id));
        for(auto person_it = ps.begin() ; person_it != ps.end() ; ++person_it)
            e.person_presenters.insert(person_it->get<int>(0));


        events.push_back(e);
    }
    return events;
}

std::vector<database::timeslot> database::get_timeslots()
{
    std::vector<timeslot> timeslots;
    rowset<row> rs = (db.prepare << "select id from timeslot where convention_id=:convention;", use(convention));
    for(auto it = rs.begin() ; it != rs.end() ; ++it)
    {
        timeslot t;
        t.id = it->get<int>(0);
        timeslots.push_back(t);
    }
    return timeslots;
}

std::vector<database::room> database::get_rooms()
{
    std::vector<room> rooms;
    rowset<row> rs = (db.prepare << "select id,room_name from rooms where convention_id=:convention;", use(convention));
    for(auto it = rs.begin() ; it != rs.end() ; ++it)
    {
        room r;
        r.id = it->get<int>(0);
        r.name = it->get<string>(1);
        rooms.push_back(r);
    }
    return rooms;
}

std::vector<database::person> database::get_people()
{
    std::vector<person> people;
    rowset<row> rs = (db.prepare << "select id,name from person;");
    for(auto it = rs.begin() ; it != rs.end() ; ++it)
    {
        person p;
        p.id = it->get<int>(0);
        p.name = it->get<string>(1);
        people.push_back(p);
    }
    return people;
}

std::vector<database::user> database::get_users()
{
    std::vector<user> users;
    rowset<row> rs = (db.prepare << "select id,name from user;");
    for(auto it = rs.begin() ; it != rs.end() ; ++it)
    {
        user u;
        u.id = it->get<int>(0);
        u.name = it->get<string>(1);
        users.push_back(u);
     }
    return users;
}
