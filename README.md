penguicon-trax
==============

## Description

Penguicon Scheduling Web App

First, an event submission/feedback website. Later there will be a site to assign rooms and times to the events. These sites will interact but will be two different sites.

## Installation

### Basic prerequisites

```sh
$ sudo apt-get install git python python-dev libpq-dev python-pip curl
$ sudo pip install virtualenv
```

Clone the repository and create/activate a new virtualenv.

```sh
$ git clone https://github.com/MattArnold/penguicontrax
$ cd penguicontrax
$ virtualenv venv --distribute
$ source venv/bin/activate
```

Then, install the dependencies using pip:

```sh
$ pip install -r requirements.txt
```

Now you can run the app locally with:

```sh
$ python runserver.py
```

### Optional: Deploy to Heroku

You will need to be added as a collaborator on the Heroku app to be able to push public changes. 

Install the Heroku toolbelt

```sh
$ wget -qO- https://toolbelt.heroku.com/install-ubuntu.sh | sh
```

You will need to add your SSH key to the Heroku website. Copy the contents of ~/.ssh/id_rsa.pub to the SSH Keys section of https://dashboard.heroku.com/account. If you don't have an SSH key, you can generate one with:

```sh
$ ssh-keygen -t rsa
```

Log in to Heroku

```sh
$ heroku login
```

Add Heroku as a remote to your repo

```sh
$ heroku git:remote -a gentle-tor-1515
````

To deploy, pull and push to Heroku

```sh
$ git pull heroku master
$ git push heroku master
```

If you've changed the database schema you will need to empty the databse and reset the web app.

```sh
$ heroku pg:reset DATABASE
$ heroku restart
```

### Optional: Use PostgreSQL instead of SQLite

penguicon-trax is deployed on Heroku, a cloud application platform. Heroku uses PostgreSQL as its database engine. By default, penguicon-trax uses SQLite as its database engine when running locally. For the most part this is all well and good but there are some subtle differences between the two engines. If you're having problems when deployed to Heroku, you can run a local PostgreSQL server and have penguicon-trax connect to it to better simulate the production environment.

First, install PostgreSQL:

```sh
$ sudo apt-get install postgresql postgresql-contrib
```

Set the password for the postgres database role
```sh
$ sudo -u postgres psql postgres
postgres=# \password postgres
Enter new password:
Enter it again:
postgres=# \q
```

Create a database for penguicon-trax

```sh
$ sudo -u postgres createdb penguicontrax
```

penguicon-trax relies on the DATABASE_URL environment variable to tell it what database engine to use. Heroku supplies this to the app; if it is empty the app switches to SQLite. We can write a script to provide the app with a DATABASE_URL that will point to our local PostgreSQL database. Create a file named psql_runserver.sh with the following contents:

```sh
#!/bin/bash
export DATABASE_URL=postgresql://postgres:<password>@localhost/penguicontrax
python runserver.py
```

You will need to replace <password> with the PostgreSQL password you previously set. Now, make the script executable and run it to use penguicon-trax with PostgreSQL!

```sh
$ chmod +x psql_runserver.sh
$ ./psql_runserver.sh
```

### Optional: Set up auto scheduler

One feature of penguicontrax is an auto scheduler for conventions: the app will automatically schedule presenations in rooms so that presenters don't conflict, and it also will minimize the number of RSVP conflicts. This optimization is [NP-Hard](http://en.wikipedia.org/wiki/NP-hard), and to solve it the app generates a [linear programming](http://en.wikipedia.org/wiki/Linear_programming) model and then uses one of the freely available linear programming solvers such as [clp](http://www.coin-or.org/projects/Clp.xml), [cbc](http://www.coin-or.org/projects/Cbc.xml), or [glpk](http://www.gnu.org/software/glpk/) to solve it. Depending on the size of the convention this may a computationally intensive task. To make the scheduler faster, the app uses highly optimized C++ to create the model file. Also, the solvers themselves are native applications. Both must be built on the target machine.

The native code to be built has two portions: modeler, the C++ program that reads the app's SQL database and generates a .lp file, and the actual solver. modeler relies on [soci](http://soci.sourceforge.net/) for database access. Building soci requires [cmake](http://www.cmake.org/) and [sqlite3](https://sqlite.org/), and since we cannot be sure that these packages will be available on the target machine (they are not on Heroku, for example) we will need to build everything from source. However, this is accomplished easily. From the root of the project:

```sh
$ modeler/makemodeler.sh
```

The `makemodeler.sh` script will download the source for the prerequisite packages and build everything. Once the build is finished you can confirm that the modeler works by running the following script:

```sh
$ modeler/runmodeler.sh
```
If you see a message along the lines `No database supplied` then the build succeeded.
