import datetime

import duckdb

con = duckdb.connect(database = "./data/my-db.db", read_only = False)

con.execute("CREATE SEQUENCE event_id START 1")

con.execute("CREATE TABLE events (id INTEGER PRIMARY KEY DEFAULT nextval('event_id'), date DATE, description VARCHAR)")

con.execute("CREATE SEQUENCE attr_id START 1")

con.execute("CREATE TABLE attributes (id INTEGER PRIMARY KEY DEFAULT nextval('attr_id'),\
             creativity FLOAT, physical FLOAT, focus FLOAT, drive FLOAT, resilience FLOAT, rage FLOAT, event_id INTEGER,\
             FOREIGN KEY (event_id) REFERENCES events (id))")

con.execute("CREATE SEQUENCE skill_id START 1")

con.execute("CREATE TABLE skills (id INTEGER PRIMARY KEY DEFAULT nextval('skill_id'),\
             name VARCHAR, level VARCHAR, field VARCHAR, category VARCHAR, event_id INTEGER,\
             FOREIGN KEY (event_id) REFERENCES events (id))")
