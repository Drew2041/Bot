import telebot
from telebot import types
from datetime import *
times = ['8:00', '8:30', '9:00', '9:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30','13:00']
days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
# Меню учителя
def TeacherMenu(message,bot):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn = types.InlineKeyboardButton('Добавить ученика',callback_data=str('/add_student'))
    markup.add(btn)
    btn = types.InlineKeyboardButton('Показать расписание', callback_data=str('/show_teacher_shedule'))
    markup.add(btn)
    btn = types.InlineKeyboardButton('Добавить занятие', callback_data=str('/add_lesson'))
    markup.add(btn)
    btn = types.InlineKeyboardButton('Удалить занятие', callback_data=str('/delete_lesson'))
    markup.add(btn)
    btn = types.InlineKeyboardButton('Удалить ученика', callback_data=str('/delete_student'),)
    markup.add(btn)
    btn = types.InlineKeyboardButton('Показать запросы', callback_data=str('/show_requests'))
    markup.add(btn)
    mess_for_teacher = 'Что этот бот может сделать полезного для вас?'
    #'\n/add_student - добавить ученика\n/show_teacher_shedule - показать расписание занятий\n/add_lesson - добавить занятие\n/delete_lesson - отменить занятие\n/show_requests - показать запросы\n/delete_student - удалить ученика'
    bot.send_message(message.chat.id,mess_for_teacher,reply_markup=markup)
# Расписание учителя (возвращает массив)
def GetSheduleByTeacher(message,bot,db,teacher,week):
    cursor = db.cursor()
    shedule=[]
    current_date = datetime.now().date()
    current_day_of_week = current_date.weekday()
    if week == 1:
        cursor.execute('SELECT * FROM Shedule{} where ? <= date and date < ?'.format(teacher), (str(current_date + timedelta(days=7 - current_day_of_week)),str(current_date + timedelta(days=14 - current_day_of_week), )))
    elif week == 0:
        cursor.execute('SELECT * FROM Shedule{} where date <= ? and day_of_week >= ?'.format(teacher),
                       (str(current_date + timedelta(days=7 - current_day_of_week)), current_day_of_week,))
    elif week == -1:
        GetConstantlyLessons(message,bot,db,teacher,week)
    result = cursor.fetchall()
    for i in result:
        tmp=[]
        len_lesson = 1
        IsFree = True
        for j in range(2, len(i)):
            if i[j] != None:
                IsFree = False
        if IsFree == False:
            tmp.append(i[1])
            tmp.append(str(i[0]))
            #shedule.append([i,str(i[0])[5:]])
            #shedule += days[i[1]] + ' (' + str(i[0])[5:] + '):' + '\n'
            len_lesson=1
            for j in range(2, len(i)-1):
                if i[j]!=None and i[j]==i[j+1]:
                    len_lesson+=1
                elif i[j]!=None and i[j]!=i[j+1]:
                            cursor.execute('SELECT name FROM STUDENTS WHERE telegram_id = ? and teacher = ?',(i[j], teacher,))
                            name = cursor.fetchone()[0]
                            tmp.append(str(times[j - len_lesson - 1]))
                            tmp.append(str(times[j - 1]))
                            tmp.append(name)
                            shedule.append(tmp)
                            tmp=[]
                            tmp.append(i[1])
                            tmp.append(str(i[0]))
                            len_lesson=1
                            #shedule += str(times[j - len_lesson - 2]) + ' - ' + str(times[j - 2]) + ' ' + name + '\
            if len_lesson>1:
                cursor.execute('SELECT name FROM STUDENTS WHERE telegram_id = ? and teacher = ?', (i[j], teacher,))
                name = cursor.fetchone()[0]
                tmp.append(str(times[len(i)-1 - len_lesson - 1]))
                tmp.append(str(times[len(i)-1 - 1]))
                tmp.append(name)
                shedule.append(tmp)
                tmp = []
                tmp.append(i[1])
                tmp.append(str(i[0]))
    return shedule
# Удаление занятия, выбор недели
def DeliteLessonChooseWeek(message,bot,db):
    markup = types.ReplyKeyboardMarkup()
    btn = 'На этой неделе'
    markup.add(btn)
    btn = 'На следующей неделе'
    markup.add(btn)
    btn = 'Навсегда'
    markup.add(btn)
    bot.send_message(message.chat.id, 'Выберите неделю', reply_markup=markup)
    bot.register_next_step_handler(message, DeliteChooseLesson,bot,db)
# Удаление занятия, выбор урока
def DeliteChooseLesson(message,bot,db):
    user_status = db.cursor().execute('SELECT user_status FROM Users WHERE telegram_id = ?',(message.from_user.id, )).fetchone()[0]
    week = WeekToInt(message.text)
    if user_status=='Teacher':
        teacher = message.from_user.id
    elif user_status=='Student':
        teacher = db.cursor().execute('SELECT teacher FROM Students WHERE telegram_id = ?',(message.from_user.id, )).fetchone()[0]
        name = db.cursor().execute('SELECT name FROM Students WHERE telegram_id = ?', (message.from_user.id,)).fetchone()[0]
    if week==-1:
        shedule = GetConstantlyLessons(message,bot,db,teacher,week)
    else:
        shedule = GetSheduleByTeacher(message,bot,db,teacher,week)
    print(shedule)
    markup = types.ReplyKeyboardMarkup()
    if shedule:
        if week!=-1:
            for i in shedule:
                if user_status=='Teacher' or (user_status=='Student' and name == i[4]):
                    btn = types.KeyboardButton(days[i[0]]+' '+i[1]+' '+i[2]+' - '+i[3]+' '+i[4])
                    markup.add(btn)
            bot.send_message(message.chat.id, 'Выберите занятие, которое хотите удалить', reply_markup=markup)
            bot.register_next_step_handler(message, DeliteLesson,bot,db,teacher)
        else:
            for i in shedule:
                if user_status == 'Teacher' or (user_status == 'Student' and name == i[1]):
                    btn = types.KeyboardButton(days[i[0]] + ' ' + i[1] + ' ' + i[2] + ' - ' + i[3])
                    markup.add(btn)
            bot.send_message(message.chat.id, 'Выберите занятие, которое хотите удалить', reply_markup=markup)
            bot.register_next_step_handler(message, DeliteConstantlyLesson, bot, db, teacher)
    else:
            bot.send_message(message.chat.id,'На этой неделе нет занятий',reply_markup=None)
            ShowMenu(message,bot,db)
# Удаление занятия, message - строка с датой, временем именем и т.д
def DeliteLesson(message,bot,db,teacher):
    cursor = db.cursor()
    lesson = message.text.split()
    print(lesson)
    data = lesson[1]
    time = str((datetime.strptime(lesson[2], '%H:%M')).time())
    time = time[:len(time)-3]
    time_end = str((datetime.strptime(lesson[4], '%H:%M')).time())
    time_end = time_end[:len(time_end) - 3]
    while time<lesson[4]:
        if time < '1':
            time = time[1:]
        sql = 'UPDATE SHEDULE'+str(teacher)+' SET '+'"'+time+'" = NULL WHERE date = ?'
        cursor.execute(sql,(data, ))
        time = datetime.strptime(time, '%H:%M')
        time = str((time + timedelta(minutes=30)).time())[:-3]
        db.commit()
        if time < '1':
            time = time[1:]
    student = cursor.execute('SELECT telegram_id FROM Students WHERE name = ? and teacher = ?',(lesson[-1], teacher,)).fetchone()[0]
    bot.send_message(student,'Занятие отменено: '+message.text)
    bot.send_message(message.chat.id,'Занятие успешно удалено',reply_markup=types.ReplyKeyboardRemove())
    ShowMenu(message,bot,db)
def DeliteConstantlyLesson(message,bot,db,teacher):
    cursor = db.cursor()
    lesson = message.text.split()
    cursor.execute('SELECT date FROM SHEDULE{}'.format(teacher))
    result = cursor.fetchall()
    dates=[]
    for i in result:
        if (datetime.strptime(i[0],'%Y-%M-%d').weekday()-1)==days.index(lesson[0]):
            dates.append(i[0])
    for i in dates:
        time = str((datetime.strptime(lesson[2], '%H:%M')).time())
        time = time[:len(time) - 3]
        time_end = str((datetime.strptime(lesson[4], '%H:%M')).time())
        time_end = time_end[:len(time_end) - 3]
        while time < lesson[4]:
            if time < '1':
                time = time[1:]
            sql = 'UPDATE SHEDULE' + str(teacher) + ' SET ' + '"' + time + '" = NULL WHERE date = ?'
            cursor.execute(sql, (i,))
            time = datetime.strptime(time, '%H:%M')
            time = str((time + timedelta(minutes=30)).time())[:-3]
            db.commit()
            if time < '1':
                time = time[1:]
    db.commit()
    student = cursor.execute('SELECT telegram_id FROM Students WHERE name = ? and teacher = ?',
                             (lesson[1], teacher,)).fetchone()[0]
    bot.send_message(student, 'Занятие отменено: ' + message.text)
    bot.send_message(message.chat.id, 'Занятие успешно удалено', reply_markup=types.ReplyKeyboardRemove())
    cursor.execute('DELETE FROM TeacherActivities{} Where student_name = ? and day = ? and time =?'.format(teacher),(lesson[1],days.index(lesson[0]),lesson[2],))
    db.commit()
    ShowMenu(message, bot, db)
# Выбирает неделю и вызывает функцию, показа расписания
def ShowTeacherSheduleChooseWeek(message,bot,db,teacher_id):
    markup = types.ReplyKeyboardMarkup()
    btn = 'На этой неделе'
    markup.add(btn)
    btn = 'На следующей неделе'
    markup.add(btn)
    bot.send_message(message.chat.id,'Выберите неделю',reply_markup=markup)
    bot.register_next_step_handler(message,ShowTeacherShedule,bot,db,teacher_id)
# Написать расписание учителя
def ShowTeacherShedule(message,bot,db,teacher_id):
    if CheckingData(message.text,['На этой неделе','На следующей неделе']):
        week=0
        if message.text =='На этой неделе':
            week=0
        elif message.text == 'На следующей неделе':
            week=1
        shedule = GetSheduleByTeacher(message,bot,db,teacher_id,week)
        if shedule:
            message_shedule=''
            for i in range(len(shedule)):
                if i==0:
                    message_shedule+=days[shedule[i][0]]+' ('+shedule[i][1]+'):'+'\n'
                elif  shedule[i][1]!=shedule[i-1][1]:
                    message_shedule += '\n'+days[shedule[i][0]] + ' (' + shedule[i][1] + '):' + '\n'
                message_shedule+=shedule[i][2]+' - '+ shedule[i][3]+' '+shedule[i][4]+'\n'
            bot.send_message(message.chat.id,message_shedule,reply_markup=types.ReplyKeyboardRemove())
        else:
            bot.send_message(message.chat.id,'Занятий на этой неделе нет',reply_markup=types.ReplyKeyboardRemove())
            TeacherMenu(message,bot)
    else:
        bot.send_message(message.chat.id,'Неверно введенные данные')
        ShowTeacherSheduleChooseWeek(message,bot,db,teacher_id)
# Узнать продолжительность занятия
def GetLessonDuration(message,bot,db):
    cursor = db.cursor()
    status_user = FindStatus(message.chat.id, db)
    if status_user == 'Student':
        cursor.execute('SELECT teacher FROM Students Where telegram_id = ?', (message.from_user.id,))
        teacher = cursor.fetchone()[0]
    elif status_user == 'Teacher':
        teacher = message.chat.id
    btn1 = types.KeyboardButton('30 минут')
    btn2 = types.KeyboardButton('60 минут')
    btn3 = types.KeyboardButton('90 минут')
    markup = types.ReplyKeyboardMarkup()
    markup.add(btn1,btn2,btn3)
    bot.send_message(message.chat.id, 'Введите продолжительность занятия',reply_markup=markup)
    bot.register_next_step_handler(message, AddLessonChooseWeek,bot,db,teacher,status_user)
# Узнать на какой неделе занятие
def AddLessonChooseWeek(message,bot,db,teacher,status_user):
    duration=message.text
    if CheckingData(duration,['30 минут','60 минут','90 минут']):
        duration = TimeToDuration(duration)
        markup = types.ReplyKeyboardMarkup()
        btn = 'На этой неделе'
        markup.add(btn)
        btn = 'На следующей неделе'
        markup.add(btn)
        btn = 'Навсегда'
        markup.add(btn)
        bot.send_message(message.chat.id, 'Выберите неделю', reply_markup=markup)
        bot.register_next_step_handler(message, ShowFreeLessons,bot,db,duration,teacher,status_user)
    else:
        bot.send_message(message.chat.id,'Неверно введенные данные',reply_markup=types.ReplyKeyboardRemove())
        GetLessonDuration(message,bot,db)
# Печатает свободные окна учителя
def ShowFreeLessons(message,bot,db,duration,teacher,status_user):
    week = message.text
    week = WeekToInt(week)
    if CheckingData(week,[0,1,-1]):
        cursor = db.cursor()
        current_date = datetime.now().date()
        if week==0:
            cursor.execute('SELECT * FROM SHEDULE{} WHERE date <= ?'.format(teacher),(str(current_date+timedelta(days=(6-current_date.weekday()))), ))
        elif week ==1:
            cursor.execute('SELECT * FROM SHEDULE{} WHERE ? < date and date <= ?'.format(teacher),(str(current_date+timedelta(days=(6-current_date.weekday()))),str(current_date+timedelta(days=(13-current_date.weekday()))), ))
        elif week==-1:
            cursor.execute('SELECT * FROM SHEDULE{}'.format(teacher))
            result = cursor.fetchall()
            free_times=[]
            for i in range(7):
                tmp=[]
                for j in range(len(times)):
                    tmp.append(0)
                free_times.append(tmp)
            for i in range(len(result)):
                for j in range(2,len(result[i])):
                    if result[i][j]!=None:
                        free_times[result[i][1]][j-2]=-1
            for i in free_times:
                print(i)
            shedule = []
            for z in range(len(days)):
                tmp = [z]
                for i in result:
                    lesson_duration = 0
                    if i[1]==z:
                        for j in range(2, len(i)):
                            if i[j] != None or free_times[i[1]][j-2]==-1:
                                lesson_duration = 0
                            elif i[j] == None:
                                lesson_duration += 1
                            # print(f'i = {i}, j = {j}, lesson_duration = {lesson_duration}, duration = {duration}, i[j] = {i[j]}, free_times[i[1]][j-2] = {free_times[i[1]][j - 2]}')
                            if lesson_duration == duration:
                                # shedule+=times[j-lesson_duration+1-2]+' - '+times[j+1-2]+'\n'
                                if (times[j - lesson_duration + 1 - 2] + ' - ' + times[j + 1 - 2]) not in tmp:
                                    tmp.append(times[j - lesson_duration + 1 - 2] + ' - ' + times[j + 1 - 2])
                                    # print(times[j - lesson_duration + 1 - 2] + ' - ' + times[j + 1 - 2])
                                if duration > 1:
                                    lesson_duration = 0
                                    for k in range(j - (duration - 2), j + 1):
                                        if i[j] != None or free_times[i[1]][j-2]==-1:
                                            lesson_duration = 0
                                        elif i[z] == None:
                                            lesson_duration += 1
                    if len(tmp)>1 and tmp not in shedule:
                        shedule.append(tmp)
            mess_shedule = ''
            markup = types.ReplyKeyboardMarkup()
            for i in shedule:
                    mess_shedule += days[i[0]] + '\n'
                    btn = types.KeyboardButton(days[i[0]])
                    markup.add(btn)
                    for j in range(1, len(i)):
                        mess_shedule += i[j] + '\n'
            bot.send_message(message.chat.id, mess_shedule, reply_markup=markup)
            bot.register_next_step_handler(message, ShowFreeLessonsChooseDay, bot, db, duration, shedule, teacher,
                                           status_user, week)
        if week==1 or week==0:
            result = cursor.fetchall()
            # shedule = ''
            shedule=[]
            for i in result:
                # shedule+=days[i[1]]+'\n'
                tmp=[i[0],i[1]]
                lesson_duration=0
                for j in range(2,len(i)):
                        if i[j]!=None:
                            lesson_duration=0
                        elif i[j]==None:
                            lesson_duration+=1
                        if lesson_duration==duration:
                            # shedule+=times[j-lesson_duration+1-2]+' - '+times[j+1-2]+'\n'
                            tmp.append(times[j-lesson_duration+1-2]+' - '+times[j+1-2])
                            if duration>1:
                                lesson_duration=0
                                for z in range(j-(duration-2),j+1):
                                    if i[z] != None:
                                        lesson_duration = 0
                                    elif i[z] == None:
                                        lesson_duration += 1
                if tmp:
                    shedule.append(tmp)
                else:
                    shedule.append([])
            mess_shedule=''
            markup = types.ReplyKeyboardMarkup()
            for i in shedule:
                if len(i)>2:
                    mess_shedule+=days[i[1]]+'\n'
                    btn = types.KeyboardButton(days[i[1]])
                    markup.add(btn)
                    for j in range(2,len(i)):
                        mess_shedule += i[j] + '\n'
            bot.send_message(message.chat.id,mess_shedule,reply_markup=markup)
            bot.register_next_step_handler(message, ShowFreeLessonsChooseDay,bot,db,duration,shedule,teacher,status_user,week)
    else:
        bot.send_message(message.chat.id,'Неверно введенные данные')
        GetLessonDuration(message,bot,db)

# Создает кнопки со свободным временем в определенный день
def ShowFreeLessonsChooseDay(message,bot,db,duration,shedule,teacher,status_user,week):
    day = message.text
    data_to_checking=[]
    if CheckingData(day, days):
        for i in range(len(days)):
            if day==days[i]:
                day=i
                break
        markup=types.ReplyKeyboardMarkup()
        for i in shedule:
            if week!=-1:
                if len(i)>2:
                    if i[1]==day:
                        for j in range(2,len(i)):
                            btn = types.KeyboardButton(i[j])
                            data_to_checking.append(i[j])
                            markup.add(btn)
            elif week==-1:
                if i[0] == day:
                    for j in range(1, len(i)):
                        btn = types.KeyboardButton(i[j])
                        data_to_checking.append(i[j])
                        markup.add(btn)
        bot.send_message(message.chat.id,'Выберите время занятия',reply_markup=markup)
        if status_user=='Student':
            bot.register_next_step_handler(message,MakeRequest,bot,db,duration,teacher,day,week,data_to_checking)
        elif status_user=='Teacher':
            bot.register_next_step_handler(message, AddLessonByTeacher, bot, db, duration, teacher, day,week,data_to_checking)
    else:
        bot.send_message(message.chat.id,'Неверно введенные данные')
        GetLessonDuration(message, bot, db)
def AddLessonByTeacher(message,bot, db, duration, teacher, day,week,data_to_checking):
    time = message.text
    if CheckingData(time,data_to_checking):
        data_to_checking=[]
        cursor = db.cursor()
        cursor.execute('SELECT telegram_id, name FROM Students WHERE teacher = ?', (teacher,))
        result = cursor.fetchall()
        markup = types.ReplyKeyboardMarkup()
        for i in result:
            btn = types.KeyboardButton(str(i[1]))
            data_to_checking.append(str(i[1]))
            markup.add(btn)
        bot.send_message(message.chat.id,'Выберите ученика',reply_markup=markup)
        bot.register_next_step_handler(message,ShowStudentsToAddLesson,bot, db, duration, teacher, day,time,week,data_to_checking)
    else:
        bot.send_message(message.chat.id, 'Неверно введенные данные')
        GetLessonDuration(message, bot, db)
def ShowStudentsToAddLesson(message,bot, db, duration, teacher, day,time,week,data_to_cheking):
    cursor = db.cursor()
    if CheckingData(message.text,data_to_cheking):
        cursor.execute('SELECT telegram_id FROM Students WHERE  teacher = ? and name = ?', (teacher,message.text, ))
        student = cursor.fetchall()[0][0]
        AddLesson(message,bot,db,student,teacher,day,time,duration,week)
    else:
        bot.send_message(message.chat.id, 'Неверно введенные данные')
        GetLessonDuration(message, bot, db)
def AddLesson(message,bot,db,student,teacher,day,time,duration,week):
    cursor = db.cursor()
    current_date = datetime.now().date()
    current_day_of_week=current_date.weekday()
    time_to_message = time
    time = time.split()[0]
    if CheckFreeActivity(message,bot,db,day,student,time,duration,week)==True:
            name = cursor.execute('SELECT name FROM STUDENTS WHERE telegram_id = ?', (student,)).fetchone()[0]
            cursor.execute('INSERT INTO TeacherActivities{} (student_telegram_id ,student_name ,day ,duration,time,week) VALUES (?,?,?,?,?,?)'.format(teacher), (student, name, day, duration, time, week))
            if week == 0:
                #str(current_date + timedelta(days=14 - current_day_of_week)
                for i in range(duration):
                    cursor.execute("UPDATE SHEDULE{} SET '{}' = ? WHERE date <= ? and day_of_week = ?".format(teacher,time), (student,str(current_date + timedelta(days=7 - current_day_of_week)),day,))
                    db.commit()
                    time = str((datetime.strptime(time,'%H:%M')+timedelta(minutes=30)).time())[:-3]
                    if time<='1':
                        time=time[1:]
            elif week==-1:
                for i in range(duration):
                    cursor.execute(
                        "UPDATE SHEDULE{} SET '{}' = ? WHERE day_of_week = ?".format(teacher,time),(student, day,))
                    db.commit()
                    time = str((datetime.strptime(time, '%H:%M') + timedelta(minutes=30)).time())[:-3]
                    if time <= '1':
                        time = time[1:]
            elif week==1:
                for i in range(duration):
                    cursor.execute("UPDATE SHEDULE{} SET '{}' = ? WHERE date <= ? and date>?and day_of_week = ?".format(teacher,time), (student,str(current_date + timedelta(days=14 - current_day_of_week)),str(current_date + timedelta(days=7 - current_day_of_week)),day,))
                    db.commit()
                    time = str((datetime.strptime(time,'%H:%M')+timedelta(minutes=30)).time())[:-3]
                    if time<='1':
                        time=time[1:]
            bot.send_message(teacher,'Занятие успешно добавлено!',reply_markup=types.ReplyKeyboardRemove())
            mess_to_student = 'Учитель добавил занятие. День: ' + str(days[day]) + ' ,время: ' + time_to_message
            bot.send_message(student, mess_to_student)
            ShowMenu(message,bot,db)
    else:
            bot.send_message(message.chat.id,'Время занято')
def AddLessonByDate(message,bot,db,student,teacher,day,time,duration,date):
    cursor = db.cursor()
    time_to_message = time
    time = time.split()[0]
    for i in range(duration):
        cursor.execute("UPDATE SHEDULE{} SET '{}' = ? WHERE date = ?".format(teacher, time), (student, date,))
        db.commit()
        time = str((datetime.strptime(time, '%H:%M') + timedelta(minutes=30)).time())[:-3]
        if time <= '1':
            time = time[1:]
    if message!='':
        bot.send_message(teacher,'Занятие успешно добавлено!',reply_markup=types.ReplyKeyboardRemove())
        mess_to_student = 'Учитель добавил занятие. День: ' + str(days[day]) + ' ,время: ' + time_to_message
        bot.send_message(student, mess_to_student)
def CheckFreeActivity(message,bot,db,day,student,time,duration,week):
    current_date = datetime.now().date()
    current_day_of_week = current_date.weekday()
    cursor = db.cursor()
    for i in range(duration):
        if week==0:
            s = 'SELECT * FROM SHEDULE' + str(message.from_user.id)+' WHERE '+'"'+str(time)+'"'+' IS NOT NULL and date < ? and day_of_week= ?'
            cursor.execute(s,(str(current_date + timedelta(days=7 - current_day_of_week)),day,))
        elif week==-1:
            s = 'SELECT * FROM SHEDULE' + str(message.from_user.id) + ' WHERE ' + '"' + str(time) + '"' + ' IS NOT NULL and day_of_week= ?'
            cursor.execute(s, (day,))
        elif week==1:
            s = 'SELECT * FROM SHEDULE' + str(message.from_user.id) + ' WHERE ' + '"' + str(time) + '"' + ' IS NOT NULL and date < ? and date>? and day_of_week= ?'
            cursor.execute(s, (str(current_date + timedelta(days=7 - current_day_of_week)), str(current_date + timedelta(days=14 - current_day_of_week)), day,))
        result = cursor.fetchall()
        for j in result:
            if j[0]!=None:
                return False
        time = str((datetime.strptime(time, '%H:%M') + timedelta(minutes=30)).time())[:-3]
        if time <= '1':
            time = time[1:]
    return True
# Делает запрос с занятием
def MakeRequest(message,bot,db,duration,teacher,day,week,data_to_checking):
    time  = message.text
    if CheckingData(time,data_to_checking):
        student = message.from_user.id
        cursor = db.cursor()
        cursor.execute('INSERT INTO Requests (teacher,student,duration,day,time,week) VALUES (?,?,?,?,?,?)',(teacher,student,duration,day,time,week))
        db.commit()
        bot.send_message(message.chat.id,'Время отправлено, ожидайте ответ учителя',reply_markup=types.ReplyKeyboardRemove())
        bot.send_message(teacher,'У вас новый запрос на занятие')
    else:
        bot.send_message(message.chat.id, 'Неверно введенные данные')
        GetLessonDuration(message, bot, db)
# Показать запросы для учителя
def ShowRequests(message,bot,db):
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Requests WHERE teacher = ?',(message.from_user.id, ))
    result = cursor.fetchall()
    markup = types.ReplyKeyboardMarkup()
    print(result)
    if result:
        for i in result:
            student_name = cursor.execute('SELECT student_name FROM TeacherActivities{} WHERE student_telegram_id = ? '.format(i[1]),(i[2],)).fetchone()[0]
            btn = types.KeyboardButton(str(i[0])+'. '+student_name+' '+ days[i[4]]+' '+WeekToStr(i[-1])+' '+i[5])
            markup.add(btn)
        bot.send_message(message.chat.id, 'Выберите запрос', reply_markup=markup)
        bot.register_next_step_handler(message, MakeDecisionMaybe, bot, db, result)
    else:
        bot.send_message(message.chat.id,'Запросов нет')
        ShowMenu(message,bot,db)
def MakeDecisionMaybe(message,bot,db,result):
    lesson=message.text
    lesson=lesson.split()
    request_id=int((lesson[0])[:(len(lesson[0])-1)])
    for i in result:
        if i[0]==request_id:
            teacher=i[1]
            student = i[2]
            duration=i[3]
            day=i[4]
            time = i[5]
            week = i[6]
    markup = types.ReplyKeyboardMarkup()
    btn = types.KeyboardButton('Одобрить запрос и поставить занятие')
    markup.add(btn)
    btn = types.KeyboardButton('Отменить запрос')
    markup.add(btn)
    bot.send_message(message.chat.id,'Выберите нужный вариант',reply_markup=markup)
    bot.register_next_step_handler(message,MakeDecision,bot,db,teacher,student,duration,day,time,request_id,week)
def MakeDecision(message,bot,db,teacher,student,duration,day,time,request_id,week):
    if message.text=='Одобрить запрос и поставить занятие':
        AddLesson(message,bot,db,student,teacher,day,time,duration,week)
    elif message.text=='Отменить запрос':
        mess_to_student='Запрос на занятие'+days[day]+' '+time+' отклонен'
        bot.send_message(student,mess_to_student)
    cursor = db.cursor()
    cursor.execute('DELETE FROM Requests WHERE id = ?', (request_id, ))
    db.commit()
def FindStatus(telegram_id,db):
    cursor = db.cursor()
    cursor.execute('SELECT user_status FROM Users WHERE telegram_id = ?',(telegram_id, ))
    return cursor.fetchone()[0]
def DurationToTime(duration):
    if duration==1:
        time='30 минут'
    elif duration==2:
        time ='60 минут'
    elif duration==3:
        time ='90 минут'
    return time
def TimeToDuration(time):
    if time=='30 минут':
        duration=1
    elif time=='60 минут':
        duration=2
    elif time == '90 минут':
        duration = 3
    return duration
def WeekToInt(week):
    if week=='На этой неделе':
        return 0
    elif week =='На следующей неделе':
        return 1
    elif week=='Навсегда':
        return -1
def WeekToStr(week):
    if week==0:
        return 'На этой неделе'
    elif week ==1:
        return 'На следующей неделе'
    elif week==-1:
        return 'Навсегда'
def NewDay(bot,db):
    date_to_del = (datetime.now().date()-timedelta(days=1))
    cursor = db.cursor()
    teachers = cursor.execute('SELECT telegram_id FROM Teachers').fetchall()
    for i in teachers:
        teacher = i[0]
        cursor.execute('DELETE FROM SHEDULE{} where date = ?'.format(teacher),(date_to_del, ))
        last_date = cursor.execute('SELECT date FROM SHEDULE{}'.format(teacher)).fetchall()[-1][0]
        date_to_add = (datetime.strptime(last_date, '%Y-%m-%d')+timedelta(days=1)).date()
        day_of_week_to_add = date_to_add.weekday()
        cursor.execute('INSERT INTO SHEDULE{} (date,day_of_week) VALUES (?,?)'.format(teacher),(str(date_to_add),day_of_week_to_add, ))
        lessons_to_add = cursor.execute('SELECT * FROM TeacherActivities{} WHERE day = ? and week = -1'.format(teacher),(day_of_week_to_add,)).fetchall()
        for j in lessons_to_add:
            print(j)
            AddLessonByDate('',bot,db,j[1],teacher,day_of_week_to_add,j[4],j[5],date_to_add)
        db.commit()

def Student_menu(message,bot,db):
    welcome_text = 'Доброго времени суток!\nБот умеет выполнять следующие команды:\n/register - зарегистрироваться\n/add_lesson - добавить урок\n/delete_lesson'
    bot.send_message(message.chat.id, message)
def ShowMenu(message,bot,db):
    status = db.cursor().execute('SELECT user_status FROM Users WHERE telegram_id = ?',(message.chat.id, )).fetchone()[0]
    if status=='Teacher':
        TeacherMenu(message,bot)
    elif status=='Student':
        Student_menu(message,bot,db)
def CheckingData(message,data):
    flag = False
    for i in data:
        if message==i:
            flag=True
    if flag:
        return True
    else:
        return False
# def GetConstantlyLessons(message,bot,db,teacher,week):
#     cursor = db.cursor()
#     cursor.execute('Select * FROM TeacherActivities{} WHERE week = -1'.format(teacher))
#     result = cursor.fetchall()
#     markup = types.ReplyKeyboardMarkup()
#     if result:
#         for i in result:
#             btn = types.KeyboardButton(days[i[3]]+' '+str(i[2])+' '+str(i[4])+' - '+times[times.index(str(i[4]))+i[5]])
#             markup.add(btn)
#     bot.send_message(message.chat.id,'Выберите занятие, которое хотите удалить',reply_markup=markup)
#     bot.register_next_step_handler(message,DeliteLesson,bot,db,teacher)
def GetConstantlyLessons(message,bot,db,teacher,week):
    cursor = db.cursor()
    cursor.execute('Select * FROM TeacherActivities{} WHERE week = -1'.format(teacher))
    result = cursor.fetchall()
    shedule=[]
    if result:
        for i in result:
            shedule.append([i[3],i[2],i[4],times[times.index(str(i[4]))+i[5]]])
    return shedule