penguicon-trax
==============

## Description

Penguicon Scheduling Web App

First, an event submission/feedback website. Later there will be a site to assign rooms and times to the events. These sites will interact but will be two different sites.

## Installation

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
$ python penguicontrax.py
```

## Design Notes

An important schema design element is the distinction between actual events and merely requests for events. See the milestone "Site Moves Event Requests Through Statuses" for more details.

## User Stories

*001*: A form to submit an event suggestion. A message at the top reads “this form doesn’t work yet”. -DONE

*002*: Now the form saves to a database. The message now reads “we’re going to make these form results publicly visible soon.” - DONE (Although it's just hacked together with a PHP script.)

*003*: A public-facing webpage lists every entry in the database. At the top of the page is the headline “Penguicon Events Suggested So Far!” Next to that is “Suggest An Event” with a link to the form. For now, just manually put the database on the page. -DONE
 
*004*: When the form is filled out, add the new entry immediately and automatically to the public-facing page. 

*005*: Create a database of users that uses OpenID. 

*006*: Add OpenID login buttons to the top of the page through Google and Facebook.

*007*: Add a third OpenID provider that is not evil.

*008*: in the database of users, make a field for "User Type". Each user is either "staff" or "attendee". Manually confirm which specific OpenIDs are staff and add that status.

*009*: Add a "followed up" button on each entry that the concom can see. When they follow up, they should go to this page and click that button.

*010*: When a concom clicks "followed up" on an event, it now shows up as yellow. Put a line at the top of the page saying "If an event is yellow, the programming team has contacted the presenter." 

*011*: Add a "confirmed" button on each entry that the concom can see. The "confirmed" button is only there if the "followed up" button was already clicked. 

*012*: When a concom clicks "confirmed" on an event, it now shows up as purple. Put a line at the top of the page saying "Purple events are confirmed." 

*013*: To reject an event, when the concom clicks "hide" on an event, it is no longer displayed on the page.

*014*: Hidden events are now displayed on a separate page with a link from the main page. Their color changes to red when hidden. This page starts with "We regret that for various reasons, we can’t use these event suggestions this year. Maybe next year! Also, some of them may be here in error, in which case bear with us while we fix it."

*015*: Add a "Oops, unhide" button on each entry on the page of rejected events. Only the concom can see the button. It puts the event back on the main page. 

*016*: Give each OpenID user five RSVP "points".

*017*: Create an RSVP button on each event, visible to all users. When they click it, the event index number is added to their user entry in the user database, and their points are reduced by 1. A message at the top of the page reads "Choose up to 5 events. Click RSVP to indicate your interest in attending."

*018*: Display a number on each event showing how many people are interested in attending. (Yes, events on the rejected page also show this number.)

*019*: Create a tiny pencil icon button on each individual field event. This transforms it into a textarea containing all the content of that field. However, this only saves a new field to that entry, called a proofread, showing the suggested edit.

*020*: When a user clicks on an event, it expands to show all the suggested proofreads.

*021*: In that list of proofreads, each proofread shows which user made it.

*022*: Each proofread has a button visible to concom members, which when pushed, causes it to switch places with the original contents of that field. For instance, if there was a mis-spelled event title, and someone made a proofread correcting the mis-spelling, the proofreader’s text is now the official title, and the misspelling is now just another one of the proofreads. The reason this does not just delete the mis-spelled original is that people make mistakes and may want to reverse the mistake.

*023*: On each proofread, where it lists the name of the user who made it, you can click the name and it will take you to a profile page. This lists all the events this user has RSVP’ed to and all the proofreads they have made.

*024*: For each proofread of theirs which was accepted, the user gets one more RSVP point. 
