from User import *
class Parent(User):
    def set_student(self,student):
        self.student = student
    def add_to_db(self,db):
        c = db.cursor()
        c.execute("INSERT INTO Parents VALUES (?,?,?,?)",(self.telegram_id,self.telegram_name,self.name,self.student))
        db.commit()