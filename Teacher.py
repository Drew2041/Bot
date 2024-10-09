from User import *
from Data import *
from datetime import *
from calendar import *

# def NewDay(dates):
#     for k in dates['date'][0]:
#         date_for_del=k
#     del (dates['date'][0])
#     date_to_append = date_for_del+timedelta(days=3)
#     time = datetime(2016,1,1,8)
#     new_day = {}
#     dates['date'].append({date_to_append:[]})
#     for j in range(3):
#         new_day[str(time.hour)+':'+str(time.minute).zfill(2)]=0
#         time+=timedelta(minutes=30)
#     dates['date'][-1][date_to_append].append(new_day)
class Teacher(User):
    def add_to_db(self):
        cursor.execute("INSERT INTO teachers VALUES (?,?,?)",(self.telegram_id, self.telegram_name,self.name))
        db.commit()
    def CreateTablesForTeacher(self):
        cursor.execute("""CREATE TABLE IF NOT EXISTS TeacherActivities{} (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            student_telegram_id text,
            student_name text,
            day integer,
            time text,
            duration integer,
            week integer,
            price integer
        ); """.format(self.telegram_id))
        db.commit()
        cursor.execute("""CREATE TABLE IF NOT EXISTS TeacherStudents{} (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                    student_telegram_id text,
                    student_name text
                ); """.format(self.telegram_id))
        db.commit()
    def CreateSheduleForTeacher(self):
        cursor.execute("""CREATE TABLE IF NOT EXISTS SHEDULE{} (
            date text PRIMARY KEY,
            day_of_week integer,
            "8:00" text DEFAULT NULL,
            "8:30" text DEFAULT NULL,
            "9:00" text DEFAULT NULL,
            "9:30" text DEFAULT NULL,
            "10:00" text DEFAULT NULL,
            "10:30" text DEFAULT NULL,
            "11:00" text DEFAULT NULL,
            "11:30" text DEFAULT NULL,
            "12:00" text DEFAULT NULL,
            "12:30" text DEFAULT NULL
        );""".format(self.telegram_id))
        db.commit()
        current_date = datetime.now().date()
        current_date.weekday()
        for i in range(30):
            cursor.execute('INSERT  INTO SHEDULE{} (date,day_of_week) VALUES(?,?)'.format(self.telegram_id), (str(current_date),current_date.weekday(),))
            current_date += timedelta(days=1)
        db.commit()
