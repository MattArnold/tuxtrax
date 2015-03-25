#include <stdlib.h>
#include <iostream>
#include <iomanip>
#include <string>
#include <fstream>
#include <string.h>
#include <time.h>
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
    if(lp.bad())
        throw runtime_error("Unable to open output file");

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


    #define C(h,t1,t2) (lp << "c_" << h << "_" << t1 << "_" << t2)
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
                C(h,t1,t2);
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

    #define NEW_CON() (lp << "_C" << constraint_count++ << ": ")
    #define F(i,j,h) (lp << "f_" << i << "_" << j << "_" << h)
    // Each presenter must be scheduled for all of their presentations
    for(int i = 0 ; i < num_presenters ; ++i)
    {
        for(int j = 0; j < num_events ; ++j)
        {
            NEW_CON();
            for(int h = 0; h < num_timeslots ; ++h)
            {
                if(h != 0)
                    lp << " + ";
                F(i,j,h);
            }
            lp << " = " << presenter_requirement_matrix[i][j] << endl;
        }
    }

    // If two presenters give the same talk they must have the same schedule for that talk
    for(int i1 = 0; i1 < num_presenters ; ++i1)
    {
        for(int i2 = i1 + 1 ; i2 < num_presenters ; ++i2)
        {
            for(int j = 0 ; j < num_events ; ++j)
            {
                for(int h = 0; h < num_timeslots ; ++h)
                {
                    if(presenter_requirement_matrix[i1][j] > 0 && presenter_requirement_matrix[i2][j] > 0)
                    {
                        NEW_CON();
                        F(i1,j,h);
                        lp << " - ";
                        F(i2,j,h);
                        lp << " = 0" << endl;
                    }
                }
            }
        }
    }

    // No presenter can have multiple bookings in a timeslot
    for(int i = 0; i < num_presenters ; ++i)
    {
        for(int h = 0; h < num_timeslots ; ++h)
        {
            NEW_CON();
            for(int j = 0; j < num_events ; ++j)
            {
                if(j != 0)
                    lp << " + ";
                F(i,j,h);
            }
            lp << " <= 1" << endl;
        }
    }

    // No room has more than one event per timeslot
    // We first use a bool cast/implication trick to make z : talk x hour -> 0,1 == 1 <=> the jth talk is being given at hour h
    #define Z(j,h) (lp << "z_" << j << "_" << h)
    const int presenters_upper_bound = num_presenters * 2;
    for(int j = 0; j < num_events ; ++j)
    {
        for(int h = 0; h < num_timeslots ; ++h)
        {
            NEW_CON();
            for(int i = 0 ; i < num_presenters ; ++i)
            {
                if(i != 0)
                    lp << " + ";
                F(i,j,h);
            }
            lp << " - " << presenters_upper_bound << " ";
            Z(j,h);
            lp << " <= 0" << endl;
        }
    }
    #define G(j,h,r) (lp << "g_" << j << "_" << h << "_" << r)
    for(int h = 0 ; h < num_timeslots ; ++h)
    {
        // We also make the matrix g : talk x hour x room -> 0,1 == 1 <=> the jth talk is given at hour h in room r
        // Clearly, z(j,h) == sum(g(j,h,r) for a fixed j,h and all r
        for(int j = 0; j < num_events ; ++j)
        {
            NEW_CON();
            for(int r = 0 ; r < num_rooms ; ++r)
            {
                if(r != 0)
                    lp << " + ";
                G(j,h,r);
            }
            lp << " - ";
            Z(j,h);
            lp << " = 0" << endl;
        }

        // For each timeslot, we also need to make sure we don't put the same event in multiple rooms
        for(int r = 0; r < num_rooms ; ++r)
        {
            NEW_CON();
            for(int j = 0; j < num_events ; ++j)
            {
                if(j != 0)
                    lp << " + ";
                G(j,h,r);
            }
            lp << " <= 1" << endl;
        }
    }

    // Each room must be available for scheduling
    for(int r = 0 ; r < num_rooms ; ++r)
    {
        auto& available = rooms[r].available_timeslots;
        for(int h = 0 ; h < num_timeslots ; ++h)
        {
            if(available.find(timeslots[h].id) == available.end())
            {
                NEW_CON();
                for(int j = 0 ; j < num_events ; ++j)
                {
                    if(j != 0)
                        lp << " + ";
                    G(j,h,r);
                }
                lp << " = 0" << endl;
            }
        }
    }

    // A talk can only be given in a room for which it is suitable
    for(int j = 0 ; j < num_events ; ++j)
    {
        auto& suitable = events[j].suitable_rooms;
        for(int r = 0 ; r < num_rooms ; ++r)
        {
            if(suitable.find(rooms[r].id) == suitable.end())
            {
                NEW_CON();
                for(int h = 0; h < num_timeslots ; ++h)
                {
                    if(h != 0)
                        lp << " + ";
                    G(j,h,r);
                }
                lp << " = 0" << endl;
            }
        }
    }

    // The f matrix has the requirement that at talk is given the required number
    // of times by the fact that all of the presenters have to be scheduled for it G(i,h)
    // times, but g doesn't have this constraint yet, it needs to have it as well.
    // Since currently each talk can only be given once, the sum of the g(j,h,r) for a fixed j and all h,r is just 1
    // However, we dont schedule events with no presenters, so those should be zero
    for(int j = 0 ; j < num_events ; ++j)
    {
        auto& event = events[j];
        const int required_times = event.user_presenters.size() + event.person_presenters.size() == 0 ? 0 : 1;
        NEW_CON();
        for(int h = 0 ; h < num_timeslots ; ++h)
        {
            for(int r = 0; r < num_rooms ; ++r)
            {
                if(h != 0 || r != 0)
                    lp << " + ";
                G(j,h,r);
            }
        }
        lp << " = " << required_times << endl;
    }

    // Each pair of talks in each hour gives rise to a certain number of rsvp conflicts
    // We're minimized the sum of all elements of the c matrix, which we'd like to be the total number of conflicts
    // So, we create a constraint for each element of c that it is equal to the number of conflicts IF that booking were
    // made times the indicator variable z which tells us if the booking was actually made
    for(int h = 0; h < num_timeslots ; ++h)
    {
        for(int t1 = 0; t1 < num_events ; ++t1)
        {
            for(int t2 = t1 + 1 ; t2 < num_events; ++t2 )
            {
                set<int> intersection;
                auto& event1 = events[t1];
                auto& event2 = events[t2];

                intersection.insert(event1.rsvps.begin(), event1.rsvps.end());
                intersection.insert(event2.rsvps.begin(), event2.rsvps.end());

                const int intersection_size = intersection.size();
                const int event1_size = event1.rsvps.size();
                const int event2_size = event2.rsvps.size();
                const int conflicts =  event1_size + event2_size - intersection_size;

                // Since we're minimizing the sum of c we don't need to explicitly set the zero entries
                if(conflicts > 0)
                {
                    NEW_CON();
                    C(h,t1,t2);
                    lp << " - " << conflicts << " ";
                    Z(t1,h);
                    lp << " - " << conflicts << " ";
                    Z(t2,h);
                    lp << " = 0" << endl;
                }
            }
        }
    }

    lp << "Bounds" << endl;
    for(int h = 0; h < num_timeslots ; ++h)
    {
        for(int t1 = 0; t1 < num_events ; ++t1)
        {
            for(int t2 = t1 + 1 ; t2 < num_events; ++t2 )
            {
                lp << "0 <= ";
                C(h,t1,t2);
                lp << endl;
            }

        }
    }

    lp << "Generals" << endl;
    for(int h = 0; h < num_timeslots ; ++h)
    {
        for(int t1 = 0; t1 < num_events ; ++t1)
        {
            for(int t2 = t1 + 1 ; t2 < num_events; ++t2 )
            {
                C(h,t1,t2);
                lp << endl;
            }

        }
    }

    lp << "Binaries" << endl;
    for(int i = 0 ; i < num_presenters ; ++i)
    {
        for(int j = 0; j < num_events ; ++j)
        {
            for(int h = 0; h < num_timeslots ; ++h)
            {
                F(i,j,h);
                lp << endl;
            }
        }
    }
    for(int j = 0 ; j < num_events ; ++j)
    {
        for(int h = 0 ; h < num_timeslots ; ++h)
        {
            for(int r = 0; r < num_rooms ; ++r)
            {
                G(j,h,r);
                lp << endl;
            }
        }
    }

    lp << "End" << endl;
    lp.close();
}

#define FLOAT_TO_BOOL(X) (X >= 0.5f ? true : false)

void load_schedule(const string& dbstring, const string& file, int convention)
{
    database db(dbstring, convention);

    auto events = db.get_events();
    auto timeslots = db.get_timeslots();
    auto rooms = db.get_rooms();
    auto users = db.get_users();
    auto people = db.get_people();

    ifstream sol;
    sol.open(file);
    if(sol.bad())
        throw runtime_error("Unable to open input file");

    char input[1024];
    sol.getline(input, 1024);

    string first(input);
    if(first.find("Optimal") != 0 && first.find("optimal") != 0)
        throw runtime_error("Non-optimal solution");

    for(auto it = events.begin() ; it != events.end() ; ++it)
        db.clear_event_time(it->id);

    if(input[0] == 'o') //clp has extra line and lowercase o
        sol.getline(input, 1024); //Read header

    const char* delim = "_\r\n";
    while(!sol.eof())
    {
        float line, value, other;
        sol >> line;
        if(sol.eof())
            break;
        sol >> input;
        sol >> value;
        sol >> other;

        if(input[0] != 'g')
            continue;

        if(!FLOAT_TO_BOOL(value))
            continue;

        strtok(input, delim);
        int j = atoi(strtok(NULL, delim));
        int h = atoi(strtok(NULL, delim));
        int r = atoi(strtok(NULL, delim));

        db.set_event_time(events[j].id, timeslots[h].start_dt);
        db.set_event_room(events[j].id, rooms[r].id);

        string time_str(asctime(&timeslots[h].start_dt));
        time_str = time_str.substr(0,time_str.size()-1);
        cout << events[j].name << " is scheduled at " << time_str << " in " << rooms[r].name << endl;

    }

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

    try
    {
        switch(mode)
        {
        case 0:
            {
                clock_t start = clock();
                generate_model(database, file, convention);
                clock_t stop = clock();
                float total = ((float)stop - start) / CLOCKS_PER_SEC;

                cout << setprecision(2);
                cout << "Generated model in " << total << " seconds" << endl;
            }
            break;
        case 1:
            load_schedule(database, file, convention);
            break;
        default:
            cerr << "Unknown mode" << endl;
            return 1;
        }
    }
    catch(exception& e)
    {
        cerr << e.what();
        return 1;
    }

    return 0;
}
