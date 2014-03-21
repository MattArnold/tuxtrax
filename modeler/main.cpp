#include <stdlib.h>
#include <iostream>
#include <string>
#include <fstream>
#include <string.h>
#include "database.h"

using namespace std;

void process_args(int argc, char** argv, string& database, string& file, int& convention, int& mode)
{
    int arg = 0;
    while(++arg < argc)
    {
        if(strcmp(argv[arg], "-d") == 0)
        {
            if(++arg < argc)
                database = argv[arg];
        }
        else if(strcmp(argv[arg], "-f") == 0)
        {
            if(++arg < argc)
                file = argv[arg];
        }
        else if(strcmp(argv[arg], "-c") == 0)
        {
            if(++arg < argc)
                convention = atoi(argv[arg]);
        }
        else if(strcmp(argv[arg], "-m") == 0)
        {
            if(++arg < argc)
                mode = atoi(argv[arg]);
        }
    }
}

void generate_model(const string& dbstring, const string& file, int convention)
{
    database db(dbstring, convention);

    ofstream lp;
    lp.open(file.c_str());

    lp << "\\* Extended Convention Timetable Optimization *\\" << endl;
    lp << "Minimize" << endl;

    auto events = db.get_events();
    auto timeslots = db.get_timeslots();
    auto rooms = db.get_rooms();
    auto users = db.get_users();
    auto people = db.get_people();
    const int num_events = events.size();
    const int num_timeslots = timeslots.size();
    const int num_rooms = rooms.size();
    const int num_users = users.size();
    const int num_people = people.size();
    int constraint_count = 0;

    // Minimize "c" which will be matrix timeslot x talk x talk -> rsvp conflicts
    lp << "OBJ: ";
    for(int h = 0; h < num_timeslots ; ++h)
    {
        for(int t1 = 0; t1 < num_events ; ++t1)
        {
            for(int t2 = 0; t2 < num_events ; ++t2)
            {
                if(h !=0 || t1 !=0 || t2 != 0)
                    lp <<  " + ";
                lp << "c_" << h << "_" << t1 << "_" << t2;
            }
        }
    }
    lp << endl << "Subject To" << endl;

    // Build the master presenter list by merging users and presenters (pruning those that don't give any presentations)
    map<int, int> userid_to_index;
    map<int, int> personid_to_index;
    set< pair<int, int> > presenters_set;
    for(int i = 0; i < num_users ; ++i)
        userid_to_index[users[i].id] = i;
    for(int i = 0; i < num_people ; ++i)
        personid_to_index[people[i].id] = i;
    for(int j = 0; j < num_events ; ++j)
    {
        auto& event = events[j];
        for(auto it = event.user_presenters.begin() ; it != event.user_presenters.end() ; ++it)
            presenters_set.insert(pair<int,int>(0, *it));
        for(auto it = event.person_presenters.begin() ; it != event.person_presenters.end() ; ++it)
            presenters_set.insert(pair<int,int>(1, *it));
    }
    vector< pair<int,int> > presenters;
    for(auto it = presenters_set.begin() ; it != presenters_set.end() ; ++it)
    {
        if(it->first == 0)
            presenters.push_back(pair<int,int>(0, userid_to_index[it->second]));
        else
            presenters.push_back(pair<int,int>(1, personid_to_index[it->second]));
    }
    const int num_presenters = presenters.size();


    // The first constraint is to check that presenters and talks are available at
    // a given hour, but right now these aren't in the db, so this is a TODO

    // This matrix tells us how many times (0/1 for now) each presenter must give each talk
    vector< vector<int> > presenter_requirement_matrix;
    presenter_requirement_matrix.resize(num_presenters);
    for(int i = 0 ; i < num_presenters ; ++i)
    {
        auto& presenter = presenters[i];
        auto& event_requirement_vector = presenter_requirement_matrix[i];
        event_requirement_vector.resize(num_events);
        for(int j = 0; j < num_events ; ++j)
        {
            auto event = events[j];
            if(presenter.first == 0)
                event_requirement_vector[j] = event.user_presenters.find(presenter.second) != event.user_presenters.end() ? 1 : 0;
            else
                event_requirement_vector[j] = event.person_presenters.find(presenter.second) != event.person_presenters.end() ? 1 : 0;
        }
    }

    // Each presenter must be scheduled for all of their presentations
    for(int i = 0 ; i < num_presenters ; ++i)
    {
        for(int j = 0; j < num_events ; ++j)
        {
            lp << "_C" << constraint_count++ << ": ";
            for(int h = 0; h < num_timeslots ; ++h)
            {
                if(h != 0)
                    lp << " + ";
                lp << "f_" << i << "_" << j << "_" << h;
            }
            lp << " = " << presenter_requirement_matrix[i][j] << endl;
        }
    }

    lp.close();
}

int main(int argc, char** argv)
{
    string database, file;
    int convention = -1, mode = -1;

    process_args(argc, argv, database, file, convention, mode);
    if(database.empty())
    {
        cerr << "No database supplied" << endl;
        return 1;
    }
    if(file.empty())
    {
        cerr << "No file supplied" << endl;
        return 1;
    }
    if(convention == -1)
    {
        cerr << "No convention id supplied" << endl;
        return 1;
    }

    switch(mode)
    {
    case 0: generate_model(database, file, convention); break;
    default:
        cerr << "Unknown mode" << endl;
        return 1;
    }

    return 0;
}
