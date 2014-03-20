#ifndef DATABASE_H
#define DATABASE_H

#include "soci.h"
#include <string>
#include <vector>

class database
{
public:
    database(const std::string& dburl, int convention);
    ~database();

    struct event
    {
        int id;
        std::string name;
    };

    std::vector<event> get_events();

private:


    std::string path;
    int convention;
    soci::session db;

};

#endif // DATABASE_H
