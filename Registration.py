import telebot
from telebot import types
times = ['8:00', '8:30', '9:00', '9:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30','13:00']
def Start(message,bot,db):
    #if CheckUser(message,bot,db,message.from_user.id)==False:
        welcome_text = 'Доброго времени суток!'
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton('Возможности бота', callback_data=str('/opportunities'))
        markup.add(btn)
        btn = types.InlineKeyboardButton('Зарегистрироваться', callback_data=str('/register'))
        markup.add(btn)
        btn = types.InlineKeyboardButton('Оплатить тариф', callback_data=str('/pay'))
        markup.add(btn)
        bot.send_message(message.chat.id, welcome_text, reply_markup=markup)
    #else:
     #   Menu(message,bot,db)
def Menu(message,bot,db):
    from Shedule import TeacherMenu
    id = message.from_user.id
    status = db.cursor().execute('SELECT user_status FROM Users WHERE telegram_id=?',(id,)).fetchone()[0]
    if status=='Student':
        StudentMenu(message,bot,db)
    elif status=='Parent':
        ParentMenu(message,bot,db)
    elif status=='Teacher':
        TeacherMenu(message,bot)
def RegisterUser(message, bot, db):
    name = message.text
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('Ученик')
    btn2 = types.KeyboardButton('Родитель')
    btn3 = types.KeyboardButton('Учитель')
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id, 'Вы ученик, родитель или учитель? Выберите из списка', reply_markup=markup)
    bot.register_next_step_handler(message, RegisterUserType, bot, db, name)
def RegisterUserType(message,bot,db,name):
    user_type = message.text
    if user_type=='Родитель':
        user_type= 'Parent'
    elif user_type=='Ученик':
        user_type='Student'
    elif user_type=='Учитель':
        user_type='Teacher'
    if CheckUser(message,bot,db,message.from_user.id)==False:
        RegiserUserByType(message,bot,db,name,user_type)
    else:
        Delite_user_maybe(message,bot,db,user_type,name)
def RegiserUserByType(message,bot,db,name,user_type):
    cursor = db.cursor()
    cursor.execute('INSERT INTO USERS (telegram_id, telegram_name, name, user_status) Values (?,?,?,?)', (message.from_user.id, message.from_user.username, name,user_type, ))
    if user_type=='Parent':
        RegisterParent(message,bot,db,name)
    elif user_type=='Teacher':
        RegisterTeacher(message,bot,db,name)
    elif user_type=='Student':
        RegisterStudent(message,bot,db,name)
def RegisterTeacher(message,bot,db,name):
    from Shedule import TeacherMenu
    from Teacher import Teacher
    teacher = Teacher(message.from_user.id,message.from_user.username,name)
    teacher.add_to_db()
    teacher.CreateTablesForTeacher()
    teacher.CreateSheduleForTeacher()
    bot.send_message(message.chat.id,'Вы успешно зарегистрированы как учитель',reply_markup=types.ReplyKeyboardRemove())
    TeacherMenu(message,bot)
def CheckUser(message,bot,db,id):
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Users WHERE telegram_id = ?',(message.from_user.id, ))
    users = cursor.fetchall()
    if len(users)>0:
        return True
    else:
        return False
def Delite_user_maybe(message,bot,db,status,name):
        cursor = db.cursor()
        cursor.execute('SELECT user_status FROM Users Where telegram_id = ?', (message.from_user.id, ))
        status_previous = cursor.fetchall()[0][0]
        if status_previous == 'Parent':
            mess = 'родитель'
        elif status_previous == 'Student':
            mess = 'ученик'
        elif status_previous == 'Teacher':
            mess = 'учитель'
        text = 'Вы уже зарегестрированы как '+str(mess)+', хотите удалить аккаунт? '
        markup = types.ReplyKeyboardMarkup()
        btn1 = types.KeyboardButton('Да')
        btn2 = types.KeyboardButton('Нет')
        markup.add(btn1,btn2)
        bot.send_message(message.chat.id, text,reply_markup=markup)
        bot.register_next_step_handler(message,Delite_user_check,bot,db,status_previous,name,status)
def Delite_user_check(message,bot,db,status_previous,name,status):
    if message.text=='Да':
        Delite_User(message,bot,db,status_previous,name,status)
    else:
        bot.send_message(message.chat.id,'Что-то должно произойти и выкинуть тебя на главный экран')
def Delite_User(message,bot,db,status_previous,name,status):
    cursor = db.cursor()

    if status_previous=='Parent':
        cursor.execute('UPDATE Students SET parent = {} WHERE parent = {}'.format('NULL', message.from_user.id))
        db.commit()
    elif status_previous =='Student':
        teacher = cursor.execute('SELECT teacher FROM STUDENTS WHERE telegram_id = ?',(message.chat.id,)).fetchone()
        if teacher!=[]:
            teacher=teacher[0]
            DeliteStudent(message,bot,db,teacher,message.chat.id)
    elif status_previous=='Teacher':
        cursor.execute('DROP TABLE TeacherActivities{}'.format(message.from_user.id))
        cursor.execute('DROP TABLE SHEDULE{}'.format(message.from_user.id))
        cursor.execute('DROP TABLE TeacherStudents{}'.format(message.from_user.id))
        cursor.execute('UPDATE Students SET teacher = {} WHERE teacher = {}'.format('NULL',message.from_user.id))
        db.commit()
    cursor.execute('DELETE FROM Users WHERE telegram_id = ?', (int(message.from_user.id),))
    cursor.execute('DELETE FROM Teachers WHERE telegram_id = ?', (int(message.from_user.id),))
    cursor.execute('DELETE FROM Parents WHERE telegram_id = ?', (int(message.from_user.id),))
    cursor.execute('DELETE FROM Students WHERE telegram_id = ?', (int(message.from_user.id),))
    db.commit()
    bot.send_message(message.chat.id, 'Старый аккаунт удален, продолжаем регистрацию')
    RegiserUserByType(message,bot,db,name,status)
def DeliteStudentChoose(message,bot,db):
    cursor = db.cursor()
    cursor.execute('SELECT student_name FROM TeacherStudents{}'.format(message.chat.id))
    result = cursor.fetchall()
    if result:
        markup = types.ReplyKeyboardMarkup()
        for i in result:
            btn = types.KeyboardButton(i[0])
            markup.add(btn)
        bot.send_message(message.chat.id, 'Выберите ученика', reply_markup=markup)
        bot.register_next_step_handler(message, DeliteStudentByTeacher, bot, db)
    else:
        bot.send_message(message.chat.id,'У вас нет учеников, курите бамбук')
def DeliteStudentByTeacher(message,bot,db):
    name = message.text
    teacher = message.chat.id
    cursor = db.cursor()
    student_id = cursor.execute('SELECT student_telegram_id FROM TeacherStudents{} WHERE student_name = ?'.format(teacher),(name,)).fetchone()[0]
    DeliteStudent(message,bot,db,teacher,student_id)
def DeliteStudent(message,bot,db,teacher,student_id):
    cursor = db.cursor()
    for i in range(len(times)-1):
        sql = f'UPDATE SHEDULE{teacher} SET "{times[i]}" = NULL WHERE "{times[i]}" = ?'
        cursor.execute(sql, (student_id,))
        db.commit()
    cursor.execute('DELETE FROM TeacherActivities{} WHERE student_telegram_id = ?'.format(teacher),(student_id,))
    cursor.execute('DELETE FROM TeacherStudents{} WHERE student_telegram_id = ?'.format(teacher), (student_id,))
    db.commit()
    bot.send_message(teacher,'Ученик успешно удален!',reply_markup=types.ReplyKeyboardRemove())
def RegisterParent(message,bot,db,name):
    from Parent import Parent
    parent = Parent(message.from_user.id,message.from_user.username,name)
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('11')
    btn2 = types.KeyboardButton('10')
    btn3 = types.KeyboardButton('9')
    btn4 = types.KeyboardButton('Другой')
    markup.row(btn1, btn2)
    markup.row(btn3, btn4)
    bot.send_message(message.chat.id, 'Выберите класс ученика', reply_markup=markup)
    bot.register_next_step_handler(message, ShowFreeStudents,bot,db,parent)
def ShowFreeStudents(message,bot,db,parent):
    cursor = db.cursor()
    markup = types.ReplyKeyboardMarkup()
    cursor.execute('SELECT name FROM Students WHERE clas = ? and parent IS NULL', (str(message.text),))
    result = cursor.fetchall()
    if result==[]:
        bot.send_message(message.chat.id,'Нет подходящих учеников, попробуйте немного позже',reply_markup=types.ReplyKeyboardRemove())
        StartMenu(message,bot)
    else:
        for i in result:
            btn = types.KeyboardButton(str(i[0]))
            markup.add(btn)
        bot.send_message(message.chat.id, 'Выберите ученика', reply_markup=markup)
        bot.register_next_step_handler(message, LinkStudentToParent,bot,db, parent)
def LinkStudentToParent(message,bot,db,parent):
    cursor = db.cursor()
    cursor.execute('SELECT telegram_id FROM Students WHERE name = ? ', (str(message.text),))
    result=cursor.fetchall()
    parent.set_student(result[0][0])
    parent.add_to_db(db)
    UpdateStudentParent(result[0][0],parent.telegram_id)
    end_of_registration = 'Вы успешно зарегистрировались! Ваше Имя: ' + str(parent.name) + ', ученик:' + str(message.text)
    bot.send_message(message.chat.id,end_of_registration,reply_markup=types.ReplyKeyboardRemove())
def RegisterStudent(message,bot,db,name):
    from Student import Student
    student = Student(message.from_user.id,message.from_user.username, name)
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('11')
    btn2 = types.KeyboardButton('10')
    btn3 = types.KeyboardButton('9')
    btn4 = types.KeyboardButton('Другой')
    markup.row(btn1, btn2)
    markup.row(btn3, btn4)
    bot.send_message(message.chat.id, 'В каком классе обучаетесь?', reply_markup=markup)
    bot.register_next_step_handler(message, RegisterStudentClass,bot,db,student)
def RegisterStudentClass(message,bot,db,student):
    if message.text=='Другой':
        clas = 0
    else:
        clas = int(message.text)
    student.set_clas(clas)
    student.add_to_db(db)
    end_of_registration = 'Вы успешно зарегистрировались! Ваше Имя: ' + str(student.name) + ', класс:' + str(student.clas)
    bot.send_message(message.chat.id, end_of_registration, reply_markup=types.ReplyKeyboardRemove())
    StudentMenu(message, bot,db,student)
def StudentMenu(message, bot,db,student):
    if student.teacher == None:
        bot.send_message(message.chat.id,'Ожидайте, когда учитель добавит вас в свои ученики')
    else:
        student_menu = 'Для быстрого ввода команды можете нажать на нее\n/add_lesson - добавить занятие\n'
        bot.send_message(message.chat.id,student_menu)
def StartMenu(message,bot):
    bot.send_message(message.chat.id,'ЭТО СТАРТОВОЕ МЕНЯ ТУТ ЧЕТО БУДЕТf')
