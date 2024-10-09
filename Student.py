from User import *
class Student(User):
    teacher = None
    parent = None
    def set_teacher(self,teacher):
        self.teacher = teacher
    def set_clas(self,clas):
        self.clas = clas
    def set_parent(self,parent):
        self.parent = parent
    def add_to_db(self,db):
        c = db.cursor()
        c.execute("INSERT INTO students VALUES (?,?,?,NULL,?,NULL)",(self.telegram_id,self.telegram_name,self.name,self.clas))
        db.commit()