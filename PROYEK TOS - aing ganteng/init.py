import sqlite3

conn = sqlite3.connect('database.db')
print "Opened database successfully";

conn.execute('CREATE TABLE posts (id INTEGER PRIMARY KEY AUTOINCREMENT, caption varchar(500) NOT NULL, image varchar(200) NOT NULL, owner varchar(50) NOT NULL, submitdate date NOT NULL, points int(11) NOT NULL)')
conn.execute('CREATE TABLE comments (id INTEGER PRIMARY KEY AUTOINCREMENT, content varchar(200) NOT NULL, post_id int(11) NOT NULL, username varchar(512) NOT NULL, commentdate date NOT NULL)')
conn.execute('CREATE TABLE user (username varchar(15) NOT NULL, password varchar(20) NOT NULL, fullname varchar(50) NOT NULL, email varchar(50) NOT NULL, image varchar(200) NOT NULL)')
print "Tables created successfully";
conn.close()

