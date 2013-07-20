DROP TABLE if EXISTS submissions;
CREATE TABLE submissions (
  id INTEGER primary key autoincrement,
  email VARCHAR not null,
  title VARCHAR not null,
  description VARCHAR not null,
  trackid INT,
  duration TINYINT not null,
  setuptime TINYINT not null,
  repetition TINYINT not null,
  comments VARCHAR not null,
  firstname VARCHAR not null,
  lastname VARCHAR not null
);
INSERT INTO submissions ('id', 'email', 'title', 'description', 'trackid', 'duration', 'setuptime', 'repetition', 'comments', 'firstname', 'lastname') VALUES (0, 'example@sample.com', 'An Example Of A Requested Event', 'This will be great! This example has boilerplate text for now. I have blood pumping straight to my brain. Topics covered will include excitement and discovery.', '3', '1', '0', '0', 'Some comments.', 'Matt', 'Arnold');
INSERT INTO submissions ('id', 'email', 'title', 'description', 'trackid', 'duration', 'setuptime', 'repetition', 'comments', 'firstname', 'lastname') VALUES (1, 'example@sample.com', 'An Event Being Requested', 'Here is boilerplate text for an example event being requested to run at Penguicon. This may lead to excellence. Topics covered will be: awesomeness, fantasticality, and verbosity.', '3', '1', '0', '0', 'Some comments.', 'Matt', 'Arnold');
INSERT INTO submissions ('id', 'email', 'title', 'description', 'trackid', 'duration', 'setuptime', 'repetition', 'comments', 'firstname', 'lastname') VALUES (2, 'example@sample.com', 'Identifying and Addressing the Flask Python Framework With SQLite3', 'Unified efficient archetypes have led to many key advances, including active networks and red-black trees. In fact, few leading analysts would disagree with the development of multi-processors. This finding at first glance seems perverse but fell in line with our expectations. Tenth, our new application for architecture, is the solution to all of these issues.', '1', '1', '0', '0', 'Some comments.', 'Matt', 'Arnold');
INSERT INTO submissions ('id', 'email', 'title', 'description', 'trackid', 'duration', 'setuptime', 'repetition', 'comments', 'firstname', 'lastname') VALUES (3, 'example@sample.com', 'Deconstructing Write-Back Caches Using Dunt', 'To our knowledge, our work in our research marks the first algorithm explored specifically for object-oriented languages. Unfortunately, 8 bit architectures might not be the panacea that cyberinformaticians expected. This is an important point to understand. of course, this is not always the case. As a result, we probe how symmetric encryption can be applied to the emulation of 802.11 mesh networks.', '1', '1', '0', '0', 'Some comments.', 'Matt', 'Arnold');
INSERT INTO submissions ('id', 'email', 'title', 'description', 'trackid', 'duration', 'setuptime', 'repetition', 'comments', 'firstname', 'lastname') VALUES (4, 'example@sample.com', 'Investigating Digital-to-Analog Converters and Write-Back Caches', 'Authenticated algorithms and superpages have garnered great interest from both scholars and cryptographers in the last several years. After years of significant research into hash tables, we show the visualization of courseware, which embodies the compelling principles of operating systems. We propose a real-time tool for architecting RAID, which we use to disprove that the much-touted lossless algorithm for the understanding of von Neumann machines by Kobayashi and Suzuki runs in 0(n!) time.', '1', '1', '0', '0', 'Some comments.', 'Matt', 'Arnold');
DROP TABLE if EXISTS tags;
CREATE TABLE tags (
  id INTEGER primary key autoincrement,
  name VARCHAR not null
);
INSERT INTO tags ('name') VALUES ('art');
INSERT INTO tags ('name') VALUES ('boardgame'); 
INSERT INTO tags ('name') VALUES ('computer'); 
INSERT INTO tags ('name') VALUES ('costuming'); 
INSERT INTO tags ('name') VALUES ('career'); 
INSERT INTO tags ('name') VALUES ('crafts'); 
INSERT INTO tags ('name') VALUES ('debauchery'); 
INSERT INTO tags ('name') VALUES ('diy'); 
INSERT INTO tags ('name') VALUES ('eco'); 
INSERT INTO tags ('name') VALUES ('food'); 
INSERT INTO tags ('name') VALUES ('game'); 
INSERT INTO tags ('name') VALUES ('gaming'); 
INSERT INTO tags ('name') VALUES ('hardware'); 
INSERT INTO tags ('name') VALUES ('law'); 
INSERT INTO tags ('name') VALUES ('literature'); 
INSERT INTO tags ('name') VALUES ('media'); 
INSERT INTO tags ('name') VALUES ('music'); 
INSERT INTO tags ('name') VALUES ('penguicon'); 
INSERT INTO tags ('name') VALUES ('quest'); 
INSERT INTO tags ('name') VALUES ('relationships'); 
INSERT INTO tags ('name') VALUES ('software'); 
INSERT INTO tags ('name') VALUES ('science'); 
INSERT INTO tags ('name') VALUES ('tech'); 
INSERT INTO tags ('name') VALUES ('videogame'); 
INSERT INTO tags ('name') VALUES ('violence');
CREATE TABLE user (
  id INTEGER primary key autoincrement,
  firstname VARCHAR,
  lastname VARCHAR not null,
  email VARCHAR not null
);
INSERT INTO user ('firstname', 'lastname', 'email') VALUES ('Krunal', 'Desai', 'test@example.com');
INSERT INTO user ('firstname', 'lastname', 'email') VALUES ('Matt', 'Arnold', 'mytest@example.com');
INSERT INTO user ('firstname', 'lastname', 'email') VALUES ('Janet', 'Gocay', 'test@example2.com');
CREATE TABLE track (
  id INTEGER primary key autoincrement,
  name VARCHAR not null,
  staffid INTEGER
);
INSERT INTO track ('name', 'staff') VALUES ('Tech', '1');
INSERT INTO track ('name', 'staff') VALUES ('Science', '2');
INSERT INTO track ('name', 'staff') VALUES ('Life', '3');
INSERT INTO track ('name', 'staff') VALUES ('Literature', '2');
INSERT INTO track ('name', 'staff') VALUES ('Costuming', '2');
INSERT INTO track ('name', 'staff') VALUES ('Food', '3');
INSERT INTO track ('name', 'staff') VALUES ('Gaming', '3');
INSERT INTO track ('name', 'staff') VALUES ('Mayhem', '3');
INSERT INTO track ('name', 'staff') VALUES ('Action Adventure', '3');
INSERT INTO track ('name', 'staff') VALUES ('After Dark', '2');
INSERT INTO track ('name', 'staff') VALUES ('Music', '3');
INSERT INTO track ('name', 'staff') VALUES ('Film', '2');
