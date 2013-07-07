DROP TABLE if EXISTS submissions;
CREATE TABLE submissions (
  id INTEGER primary key autoincrement,
  email VARCHAR not null,
  title VARCHAR not null,
  description VARCHAR not null,
  duration TINYINT not null,
  setuptime TINYINT not null,
  repetition TINYINT not null,
  comments VARCHAR not null,
  firstname VARCHAR not null,
  lastname VARCHAR not null
);
INSERT INTO submissions ('id', 'email', 'title', 'description', 'duration', 'setuptime', 'repetition', 'comments', 'firstname', 'lastname') VALUES (0, 'example@sample.com', 'An Example Of A Requested Event', 'This will be great! This example has boilerplate text for now. I have blood pumping straight to my brain. Topics covered will include excitement and discovery.', '1', '0', '0', 'Some comments.', 'Matt', 'Arnold');
INSERT INTO submissions ('id', 'email', 'title', 'description', 'duration', 'setuptime', 'repetition', 'comments', 'firstname', 'lastname') VALUES (1, 'example@sample.com', 'An Event Being Requested', 'Here is boilerplate text for an example event being requested to run at Penguicon. This may lead to excellence. Topics covered will be: awesomeness, fantasticality, and verbosity.', '1', '0', '0', 'Some comments.', 'Matt', 'Arnold');
INSERT INTO submissions ('id', 'email', 'title', 'description', 'duration', 'setuptime', 'repetition', 'comments', 'firstname', 'lastname') VALUES (2, 'example@sample.com', 'Identifying and Addressing the Flask Python Framework With SQLite3', 'Unified efficient archetypes have led to many key advances, including active networks and red-black trees. In fact, few leading analysts would disagree with the development of multi-processors. This finding at first glance seems perverse but fell in line with our expectations. Tenth, our new application for architecture, is the solution to all of these issues.', '1', '0', '0', 'Some comments.', 'Matt', 'Arnold');
INSERT INTO submissions ('id', 'email', 'title', 'description', 'duration', 'setuptime', 'repetition', 'comments', 'firstname', 'lastname') VALUES (3, 'example@sample.com', 'Deconstructing Write-Back Caches Using Dunt', 'To our knowledge, our work in our research marks the first algorithm explored specifically for object-oriented languages. Unfortunately, 8 bit architectures might not be the panacea that cyberinformaticians expected. This is an important point to understand. of course, this is not always the case. As a result, we probe how symmetric encryption can be applied to the emulation of 802.11 mesh networks.', '1', '0', '0', 'Some comments.', 'Matt', 'Arnold');
INSERT INTO submissions ('id', 'email', 'title', 'description', 'duration', 'setuptime', 'repetition', 'comments', 'firstname', 'lastname') VALUES (4, 'example@sample.com', 'Investigating Digital-to-Analog Converters and Write-Back Caches', 'Authenticated algorithms and superpages have garnered great interest from both scholars and cryptographers in the last several years. After years of significant research into hash tables, we show the visualization of courseware, which embodies the compelling principles of operating systems. We propose a real-time tool for architecting RAID, which we use to disprove that the much-touted lossless algorithm for the understanding of von Neumann machines by Kobayashi and Suzuki runs in 0(n!) time.', '1', '0', '0', 'Some comments.', 'Matt', 'Arnold');
DROP TABLE if EXISTS tags;
CREATE TABLE tags (
  id INTEGER primary key autoincrement,
  name VARCHAR not null
);
INSERT INTO tags ('id', 'name') VALUES (0, 'art');
INSERT INTO tags ('id', 'name') VALUES (1, 'boardgame'); 
INSERT INTO tags ('id', 'name') VALUES (2, 'computer'); 
INSERT INTO tags ('id', 'name') VALUES (3, 'costuming'); 
INSERT INTO tags ('id', 'name') VALUES (4, 'career'); 
INSERT INTO tags ('id', 'name') VALUES (5, 'crafts'); 
INSERT INTO tags ('id', 'name') VALUES (6, 'debauchery'); 
INSERT INTO tags ('id', 'name') VALUES (7, 'diy'); 
INSERT INTO tags ('id', 'name') VALUES (8, 'eco'); 
INSERT INTO tags ('id', 'name') VALUES (9, 'food'); 
INSERT INTO tags ('id', 'name') VALUES (10, 'game'); 
INSERT INTO tags ('id', 'name') VALUES (11, 'gaming'); 
INSERT INTO tags ('id', 'name') VALUES (12, 'hardware'); 
INSERT INTO tags ('id', 'name') VALUES (13, 'law'); 
INSERT INTO tags ('id', 'name') VALUES (14, 'literature'); 
INSERT INTO tags ('id', 'name') VALUES (15, 'media'); 
INSERT INTO tags ('id', 'name') VALUES (16, 'music'); 
INSERT INTO tags ('id', 'name') VALUES (17, 'penguicon'); 
INSERT INTO tags ('id', 'name') VALUES (18, 'quest'); 
INSERT INTO tags ('id', 'name') VALUES (19, 'relationships'); 
INSERT INTO tags ('id', 'name') VALUES (20, 'software'); 
INSERT INTO tags ('id', 'name') VALUES (21, 'science'); 
INSERT INTO tags ('id', 'name') VALUES (22, 'tech'); 
INSERT INTO tags ('id', 'name') VALUES (23, 'videogame'); 
INSERT INTO tags ('id', 'name') VALUES (24, 'violence');
