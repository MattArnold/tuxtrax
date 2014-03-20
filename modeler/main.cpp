#include <stdlib.h>
#include <iostream>
#include <string>
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
    auto events = db.get_events();
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
