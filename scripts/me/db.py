from datetime import datetime

import duckdb
import fire


con = duckdb.connect(database = "./data/my-db.db", read_only = False)

def AddState(dateID):
    while True:
        
        if dateID == '':
            date = datetime.strptime(input("Date: "), "%m/%d/%Y") 
            event = input("Event: ")
            dateID = con.execute("INSERT INTO events VALUES (DEFAULT, ?, ?) RETURNING id", [date, event]).fetchone()[0]
        else:
            dateID = dateID
            event = con.execute("SELECT * FROM events WHERE id = ?", [dateID]).df()
            print(event)
        
        creativity = float(input("Creativity: "))
        physical = float(input("Physical: "))
        focus = float(input("Focus: "))
        drive = float(input("Drive: "))
        resilience = float(input("Resilience: "))
        rage = float(input("Rage: "))

        con.execute("""
                    INSERT INTO attributes VALUES (DEFAULT, ?, ?, ?, ?, ?, ?, ?)
                    """, [creativity, physical, focus, drive, resilience, rage, dateID])

        repeat = input("Type anything other than blank to repeat this scenario: ")

        if not repeat:
            break
        
        dateID = int(input("Enter date ID or leave blank: "))


def AddEvent():
    while True:
        date = datetime.strptime(input("Date: "), "%m/%d/%Y") 
        description = input("Enter description: ")
        con.execute("INSERT INTO events VALUES (DEFAULT, ?, ?)", [date, description])

        repeat = input("Enter anything if you want to keep adding dates: ")

        if repeat == '':
            break

def ListEvents():
    eventLists = con.execute("SELECT * FROM events").df()
    print(eventLists)

def AddSkill(dateID):
     while True:
        
        if dateID == '':
            date = datetime.strptime(input("Date: "), "%m/%d/%Y") 
            event = input("Event: ")
            dateID = con.execute("INSERT INTO events VALUES (DEFAULT, ?, ?) RETURNING id", [date, event]).fetchone()[0]
        else:
            dateID = dateID
            event = con.execute("SELECT * FROM events WHERE id = ?", [dateID]).df()
            print(event)
        
        name = input("Name: ")
        level = input("Level: ")
        field = input("Field: ")
        category = input("Category: ")


        con.execute("""
                    INSERT INTO skills VALUES (DEFAULT, ?, ?, ?, ?, ?)
                    """, [name, level, field, category, dateID])

        repeat = input("Type anything other than blank to repeat this scenario: ")

        if repeat == '':
            break
        
        dateID = int(input("Enter date ID or leave blank: "))

if __name__ == '__main__':
    fire.Fire()