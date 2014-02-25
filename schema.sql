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
  lastname VARCHAR not null,
  followupstate INTEGER DEFAULT 0
);
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
DROP TABLE if EXISTS user;
CREATE TABLE user (
  id INTEGER primary key autoincrement,
  firstname VARCHAR,
  lastname VARCHAR not null,
  email VARCHAR not null,
  openid VARCHAR,
  staff INTEGER DEFAULT 0,
  points INTEGER DEFAULT 5
);
DROP TABLE if EXISTS track;
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
