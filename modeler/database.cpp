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
    else if(dburl.find("sqlite:///") == 0)
    {
        auto file = dburl.substr(10);
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

        rowset<row> rooms = (db.prepare << "select room_id from room_suitability where event_id=:id;", use(e.id));
        for(auto room_it = rooms.begin() ; room_it != rooms.end() ; ++room_it)
            e.suitable_rooms.insert(room_it->get<int>(0));

        rowset<row> rsvps = (db.prepare << "select user_id from event_rsvps where event_id=:id;", use(e.id));
        for(auto rsvp_it = rsvps.begin() ; rsvp_it != rsvps.end() ; ++rsvp_it)
            e.rsvps.insert(rsvp_it->get<int>(0));

        events.push_back(e);
    }
    return events;
}

std::vector<database::timeslot> database::get_timeslots()
{
    std::vector<timeslot> timeslots;
    rowset<row> rs = (db.prepare << "select id,start_dt from timeslot where convention_id=:convention;", use(convention));
    for(auto it = rs.begin() ; it != rs.end() ; ++it)
    {
        timeslot t;
        t.id = it->get<int>(0);
        t.start_dt = it->get<tm>(1);

        rowset<row> rooms = (db.prepare << "select room_id from room_availability where timeslot_id=:id;", use(t.id));
        for(auto room_it = rooms.begin() ; room_it != rooms.end() ; ++room_it)
            t.available_rooms.insert(room_it->get<int>(0));

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

        rowset<row> timeslots = (db.prepare << "select timeslot_id from room_availability where room_id=:id;", use(r.id));
        for(auto timeslot_it = timeslots.begin() ; timeslot_it != timeslots.end() ; ++timeslot_it)
            r.available_timeslots.insert(timeslot_it->get<int>(0));

        rowset<row> events = (db.prepare << "select event_id from room_suitability where room_id=:id", use(r.id));
        for(auto event_it = events.begin() ; event_it != events.end() ; ++event_it)
            r.available_events.insert(event_it->get<int>(0));

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

void database::clear_event_time(int id)
{
    db << "update events set start_dt = NULL where id = :id;", use(id);
}

void database::set_event_time(int id, const std::tm& start_dt)
{
    db << "update events set start_dt = :start_dt where id = :id;", use(start_dt, "start_dt"), use(id, "id");
}

void database::set_event_room(int id, int room_id)
{
    db << "delete from room_events where event_id=:id;", use(id);
    db << "insert into room_events(event_id, room_id) values(:event_id, :room_id)", use(id, "event_id"), use(room_id, "room_id");
}
