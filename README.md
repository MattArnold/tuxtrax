penguicon-trax
==============

## Description

Penguicon Scheduling Web App

First, an event submission/feedback website. Later there will be a site to assign rooms and times to the events. These sites will interact but will be two different sites.

## Installation

### Basic prerequisites

```sh
$ sudo apt-get install git python python-dev libpq-dev python-pip
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

## Design Notes

An important schema design element is the distinction between actual events and merely requests for events. See the milestone "Site Moves Event Requests Through Statuses" for more details.

## User Stories

### *Epic 0: The Basics*

*001*: A form to submit an event suggestion. A message at the top reads “this form doesn’t work yet”. -DONE

*002*: Now the form saves to a database. The message now reads “we’re going to make these form results publicly visible soon.” - DONE

*003*: A public-facing webpage lists every entry in the database. At the top of the page is the headline “Penguicon Events Suggested So Far!” Next to that is “Suggest An Event” with a link to the form. For now, just manually put the database on the page. -DONE
 
*004*: When the form is filled out, add the new entry immediately and automatically to the public-facing page. -DONE

### *Epic 1: User Logins*

*005*: Create a database of users that uses OpenID. -DONE

*006*: Add OpenID login buttons to the top of the page through Google and Facebook. -DONE

*007*: Add a third OpenID provider that is not evil. -DONE

*008*: in the database of users, make a field for "User Type". Each user is either "staff" or "nonstaff". Manually confirm which specific OpenIDs are staff and add that status. - DONE

### *Epic 2: Stages*

*009*: Add a "followed up" button on each entry that the concom can see. When they follow up, they should go to this page and click that button. -DONE (for ease of implementation the different states are just a drop down on the event form)

*010*: When a concom clicks "followed up" on an event, it now shows up as yellow. Put a line at the top of the page saying "If an event is yellow, the programming team has contacted the presenter."  -DONE

*011*: Add a "confirmed" button on each entry that the concom can see. The "confirmed" button is only there if the "followed up" button was already clicked. -DONE

*012*: When a concom clicks "confirmed" on an event, it now shows up as purple. Put a line at the top of the page saying "Purple events are confirmed." -DONE

*013*: To reject an event, when the concom clicks "hide" on an event, it is no longer displayed on the page. -DONE

*014*: Hidden events are now displayed on a separate page with a link from the main page. Their color changes to red when hidden. This page starts with "We regret that for various reasons, we can’t use these event suggestions this year. Maybe next year! Also, some of them may be here in error, in which case bear with us while we fix it." -DONE (Rejected events show on main page, but only for staff.)

*015*: Add a "Oops, unhide" button on each entry on the page of rejected events. Only the concom can see the button. It puts the event back on the main page.  -DONE (Change status away from Rejected on event page)

### *Epic 3: RSVPs*

*016*: Give each OpenID user five RSVP "points". -DONE

*017*: Create an RSVP button on each event, visible to all users. When they click it, the event index number is added to their user entry in the user database, and their points are reduced by 1. A message at the top of the page reads "Choose up to 5 events. Click RSVP to indicate your interest in attending." -DONE

*018*: Display a number on each event showing how many people are interested in attending. (Yes, events on the rejected page also show this number.) -DONE, each user RSVPed is actually displayed!

### *Epic 4: Proofreading*

*019*: Create a tiny pencil icon button on each field in each individual event suggestion. This transforms it into a textarea containing all the content of that field. Prepend this span to the event div: "" Pressing the button only saves a new field to that entry, called a proofread, showing the suggested edit.

*020*: When a user clicks on an event (anywhere but a button or editable field), it expands to show all the suggested proofreads. This view of an event is called a "Details" pane. If you click anywhere on a Details pane (other than a button or editable field), it collapses to its previous state. Later user stories will give Details more features, and apply it to listings on more pages.

*021*: In that list of proofreads, each proofread shows which user made it.

*022*: Each proofread has a button visible to concom members, which when pushed, causes it to switch places with the original contents of that field. For instance, if there was a mis-spelled event title, and someone made a proofread correcting the mis-spelling, the proofreader’s text is now the official title, and the misspelling is now just another one of the proofreads. The reason this does not just delete the mis-spelled original is that people make mistakes and may want to reverse the mistake.

*023*: On each proofread, where it lists the name of the user who made it, you can click the name and it will take you to a profile page. This lists all the events this user has RSVP’ed to and all the proofreads they have made.

*024*: For each proofread of theirs which was accepted, the user gets one more RSVP point. 

### *Epic 5: Associate Event Submitters With Users*

*028*: On the event submission form, next to the Suggester Name field, offer the login buttons to users who are not logged in. (Please leave the field there regardless of login state. This is because staff will often fill in event requests for other people who do not want to use our site.) Logging in hides the login buttons but does not clear the work done on the form.

*025*: When the event submission form is filled out by someone who is not logged in, if the email address exists in the system for an existing user, that event is associated to that user.

*026*: On the event submission form, if the user is logged in with Google's OpenID or Mozilla Persona, the Suggester name and email fields are pre-populated from their account. (The fields may still be edited.)

*027*: If a user is logged in through a non-email method, filling out the the event submission form associates their user account to the name and email they provide. This will be pre-populated if they use the form again while logged in.

### *Epic 6: Associate Program Participants With Users*

*027*: There is a new page called Person List, visible only to staff, with a list of every user, and a list of every unique person0, person1, person2, etc from the program participants (speakers/game masters/panelists/etc) from every submitted event. There will be massive duplication from variations and mis-spellings of the same name. Each value in each list will have a checkbox.

*028*: When one User checkbox and one or more Program Participant checkboxes are checked by staff, a "Merge" button appears. The buttons do not do yet do anything.

*029*: There is a linking table that associates ```submissions``` entries with ```users```. Pressing the "Merge" button associates all the checked Program Participant names with the selected user, into one identity. Example: Someone suggested "Ann Grey" be on a panel, but mis-spelled her name. "Anne Gray" offered to give a talk, but did not create a user account until later, as "Anne K Gray". After discussing it with the OpenID user "Anne K Gray", Staff associates those event suggestions with her user account.

*030*: The bottom of the Person List page lists a complete log of all merges that have ever been done.

### *Epic 7: Personal Pages*

*031*: Each user has a personal page visible to the public: domaingoeshere.com/usernamegoeshere At first the page displays only their user id and a link back to the homepage.

*032*: A personal page now also displays their user type (nonstaff or staff, see user story #8), number of stars, and login method.

*033*: A personal page now also displays a list of event suggestions for which they are the suggester or a suggested program participant.

*034*: Each event listed on a personal page is clickable to expand its div to show its Details.

*035*: That list is now ordered by its progress status (at the top of the list, "Request opened", followed by "Followed up", "Accepted", "Scheduled", "Confirmed", "Rejected", in that order).

*036*: A personal page now also displays a list of proofreads they have made, grouped by event suggestion. When clicked, this expands to display the entire event suggestion's Details.

### *Epic 8: Staff Queue*

*037*: There is exactly one user who will have elevated privileges and responsibilities over the staff, to be defined in later user stories. That user is the ```headofprogramming```.

*038*: Each track may now be associated with exactly one Staff user accounts responsible for the track, called the ```trackhead```. Remember the difference between "track" and "topic": "Tracks" determine exactly one staffer who is responsible. "Topics" are tags seen by the public. ```trackhead``` is not allowed to have a null value. Each track defaults to ```headofprogramming``` as its ```trackhead```. (It is still possible to be a Staff user without being ```headofprogramming``` or ```trackhead```.)

*039*: A new page visible only to logged-in Staff users called "Staff Queue" is the same as the homepage, except it lists event requests grouped by track. I.E. Which staffer is in charge of it? Each track group on the "Task List" page has the name of the track at the top of it, left-justified.

*040*: On the same line as each Track name, right-justified, there is the username of the track's ```trackhead```.

*042*: There is a link from the homepage to the Task List page, visible only to logged-in Staff users.

*043*: When a Staff user is logged in, and surfs to the Task List page, the track order is changed so the Track associated with that Staff user (if any) is at the top of the page.

### *Epic 9: Associate Your Own Duplicate Accounts*

*044*: The footer of personal pages now display a "Merge Accounts" button. Outside the button is the label text "This user account is me, using a different login method. I would like to request to merge that account with the one I'm using now." This button does not do anything yet.

*045*: When a "Merge Accounts" button is clicked, the label changes to read "Next, log in using your other login method, and accept the merge request you just sent to yourself." The button now reads "Cancel this merge request." Clicking it will reverse the button and label to their previous state.

*046*: If the "Merge Accounts" button was clicked, that page will now show a new message and two buttons to its own logged-in user. The username of the account that clicked the Merge button "has indicated you are them and they are you. This will merge these two accounts." Two buttons read "Accept" and "Deny". This message and these buttons will go away if the original account clicks "Cancel this merge request" or this account clicks "Deny".

*047*: The "Accept" button also causes the message and buttons to go away. It also associates all the events from the account that sent the Merge request, into the account that received the Merge request. The user will have the same permissions when logging in through either method.

*048*: All currently merged login methods are listed on the user page instead of just one.
