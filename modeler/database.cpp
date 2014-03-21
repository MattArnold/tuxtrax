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
    rowset<row> rs = (db.prepare << "select id,name from convention where id=:convention", use(convention));
    for(auto it = rs.begin() ; it != rs.end() ; ++it)
    {
        event e;
        e.id = it->get<int>(0);
        e.name = it->get<string>(1);
        events.push_back(e);
    }
    return events;
}
