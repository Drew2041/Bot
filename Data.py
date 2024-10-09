import sqlite3
db = sqlite3.connect('C:/Users/roshe/PycharmProjects/pythonProject3/data_base_test.db',check_same_thread=False)
cursor = db.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS Students (
    telegram_id integer PRIMARY KEY,
    telegram_name text,
    name text,
    teacher integer DEFAULT NULL,
    clas integer,
    parent integer DEFAULT NULL
); """)
cursor.execute("""CREATE TABLE IF NOT EXISTS Users (
    telegram_id integer PRIMARY KEY,
    telegram_name text,
    name text,
    user_status text
); """)
cursor.execute("""CREATE TABLE IF NOT EXISTS Requests (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    teacher integer,
    student integer,
    duration integer,
    day integer,
    time text,
    week integer
); """)
cursor.execute("""CREATE TABLE IF NOT EXISTS Teachers (
    telegram_id integer PRIMARY KEY,
    telegram_name text,
    name text
); """)
cursor.execute("""CREATE TABLE IF NOT EXISTS Parents (
    telegram_id integer PRIMARY KEY,
    telegram_name text,
    name text,
    student
); """)

db.commit()
def GetCursor():
    return cursor
def GetDB():
    return db
def UpdateStudentParent(name,parent_id):
    cursor.execute('UPDATE Students SET parent = {} WHERE telegram_id = {}'.format(parent_id,name))
    db.commit()
