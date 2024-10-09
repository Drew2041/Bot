import telebot
from telebot import types
bot = telebot.TeleBot('7021408887:AAF3jPOyg_SNEZp4sJswucqcoQjyTQQVBYY')
PROVIDER_TOKEN = '381764678:TEST:92602'
from Teacher import *
from Student import *
from Parent import *
from Data import *
from Shedule import *
from Registration import *
days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
times = ['8:00', '8:30', '9:00', '9:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30','13:00']

@bot.message_handler(commands=['delete_lesson'])
def DeliteLessonChooseWeek_wrapper(message):
    DeliteLessonChooseWeek(message,bot,db)
@bot.callback_query_handler(func=lambda call: True)
def Handle_query(call):
    if call.data == '/delete_lesson':
        DeliteLessonChooseWeek_wrapper(call.message)
    elif call.data == '/add_student':
        FindStudentToAdd(call.message)
    elif call.data == '/show_teacher_shedule':
        ShowTeacherSheduleGetMyId(call.message)
    elif call.data =='/add_lesson':
        GetConstantly_wrapper(call.message)
    elif call.data == '/show_requests':
        ShowRequests_wrapper(call.message)
    elif call.data == '/delete_student':
        DeliteStudent_wrapper(call.message)
    elif call.data == '/register':
        Register(call.message)
    elif call.data == '/pay':
        Pay_wrapper(call.message)
    elif call.data == '/opportunities':
        Opportunities_wrapper(call.message)

@bot.message_handler(commands=['teacher_menu'])
def TeacherMenu_wrapper(message):
    TeacherMenu(message,bot)
@bot.message_handler(commands=['show_me'])
def Show(message):
    bot.send_message(message.chat.id,message)
@bot.message_handler(commands=['student_menu'])
def StudentMenu_wrappe(message):
    StudentMenu(message,bot,db)
@bot.message_handler(commands=['start'])
def Start_wrapper(message):
    Start(message,bot,db)
@bot.message_handler(commands=['register'])
def Register(message):
        bot.send_message(message.chat.id, 'Как вас зовут?', reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, RegisterUser,bot,db)
@bot.message_handler(commands=['add_lesson'])
def GetConstantly_wrapper(message):
    GetLessonDuration(message,bot,db)
@bot.message_handler(commands=['show_requests'])
def ShowRequests_wrapper(message):
    ShowRequests(message,bot,db)
@bot.message_handler(commands=['add_student'])
def FindStudentToAdd(message):
        bot.send_message(message.chat.id, 'Введите telegram_name ученика')
        bot.register_next_step_handler(message, LinkStudentToteacher,bot,db)
@bot.message_handler(commands=['delite_student'])
def DeliteStudent_wrapper(message):
        DeliteStudentChoose(message,bot,db)
def LinkStudentToteacher(message,bot,db):
    cursor.execute('SELECT telegram_id,name, teacher FROM Students WHERE telegram_name = ? ', (str(message.text),))
    result = cursor.fetchone()
    if result==None:
        bot.send_message(message.chat.id,'Пользователь с таким именем не найден')
    else:
        if result[2]==None:
            cursor.execute('UPDATE Students SET teacher = {} WHERE telegram_id = {}'.format(message.from_user.id,result[0]))
            bot.send_message(message.chat.id, 'Ученик успешно добавлен!')
            cursor.execute('SELECT name FROM teachers where telegram_id = ?', (message.chat.id,))
            mess_for_student='Учитель '+ cursor.fetchone()[0] + ' добавил вас в свои ученики'
            bot.send_message(result[0],mess_for_student)
            cursor.execute('SELECT name FROM Students WHERE telegram_id={}'.format(result[0]))
            cursor.execute('INSERT INTO TeacherStudents{} (student_telegram_id,student_name) values(?,?)'.format(message.from_user.id),(result[0],result[1],))
            db.commit()
        else:
            bot.send_message(message.chat.id, 'У данного пользователя уже есть учитель')
    TeacherMenu(message,bot)
@bot.message_handler(commands=['show_teacher_shedule'])
def ShowTeacherSheduleGetMyId(message):
    ShowTeacherSheduleChooseWeek(message,bot,db,message.chat.id)
@bot.message_handler(commands=['show_my_teacher_shedule'])
def ShowMyTeacherSheduleChooseWeek(message):
    cursor.execute('SELECT teacher FROM STUDENTS WHERE telegram_id = ?',(message.chat.id, ))
    result=cursor.fetchone()[0]
    ShowTeacherSheduleChooseWeek(message,bot,db,result)
def Pay_wrapper(message):
    markup = types.ReplyKeyboardMarkup()
    btn = types.KeyboardButton('Лоховской')
    markup.add(btn)
    btn = types.KeyboardButton('Нормальный')
    markup.add(btn)
    btn = types.KeyboardButton('Для мажоров')
    markup.add(btn)
    bot.send_message(message.chat.id,'Тут будут все тарифы и вся эта шляпа',reply_markup=markup)
    bot.register_next_step_handler(message,PayChoosePrice)
def PayChoosePrice(message):
    type_of_sub = message.text
    markup = types.ReplyKeyboardMarkup()
    btn = types.KeyboardButton('Месяц')
    markup.add(btn)
    btn = types.KeyboardButton('Три месяца')
    markup.add(btn)
    btn = types.KeyboardButton('Годовая')
    markup.add(btn)
    bot.send_message(message.chat.id, 'Сейчас прилетит оффер', reply_markup=markup)
    bot.register_next_step_handler(message, Pay,type_of_sub)
def Pay(message,type_of_sub):
    months = message.text
    if type_of_sub=='Лоховской':
        price = 100*100
    elif type_of_sub=='Нормальный':
        price = 150 * 100
    elif type_of_sub=='Для мажоров':
        price = 200 * 100
    if months=='Три месяца':
        price*=3
    elif months=='Годовая':
        price*=12
    price = types.LabeledPrice("Товар", price)
    bot.send_invoice(
        message.chat.id,
        title="Подписка на месяц",
        description="Описание товара",
        provider_token=PROVIDER_TOKEN,
        currency="rub",
        prices=[price],
        start_parameter="subscribe",
        invoice_payload="subscribe_payload")
    bot.send_message(message.chat.id, 'Оплачивайте это говно', reply_markup=types.ReplyKeyboardRemove())
@bot.pre_checkout_query_handler(func=lambda query: True)
def pre_checkout_query(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def successful_payment(message):
    bot.send_message(message.chat.id,
                     f"Спасибо за покупку! Вы успешно оплатили {message.successful_payment.total_amount / 100} рублей.")
bot.polling(none_stop=True)