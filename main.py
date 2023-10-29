import telebot
from telebot import types
import sqlite3
import requests
from currency_converter import CurrencyConverter

currency = CurrencyConverter()

bot = telebot.TeleBot('6533333130:AAGKqC8tVx5In1c2hptxUMNPlCd83F9QvIM')

names = None
password = None
api_key_weather = '5bf6d92716f2de00e4c2585a2bc21cfd'
amount_curr = 0

@bot.message_handler(commands=['start'])
def main(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=False)
    markup2 =types.InlineKeyboardMarkup()

    btn_id = types.InlineKeyboardButton('✔️ Show your id', callback_data='get_id')
    btn_hi = types.InlineKeyboardButton('👋 Say hi', callback_data='hi')
    btn_reg = types.InlineKeyboardButton('🔐 Save your login and password', callback_data='registration')
    btn_weather = types.InlineKeyboardButton('☀️ Check weather', callback_data='weather')
    btn_curr = types.InlineKeyboardButton('📊 Convert currencies', callback_data='curr')
    btn_info = types.InlineKeyboardButton('💡 Learn about telebot', url='https://pypi.org/project/pyTelegramBotAPI/')

    btn_help = types.KeyboardButton('/help')

    markup.row(btn_help)
    markup2.add(btn_id, btn_hi)
    markup2.add(btn_reg)
    markup2.add(btn_weather, btn_curr)
    markup2.add(btn_info)

    bot.send_message(message.chat.id, "Hey! I'm a simple bot. Wanna see what i can do?",reply_markup=markup2)
    bot.send_message(message.chat.id, "If you need help click on keyboard button", reply_markup=markup)
def get_curr(message):
    global amount_curr
    try:
        amount_curr = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, 'Entered wrong value')
        # bot.register_next_step_handler(message, get_curr)

    if amount_curr > 0:
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('USD/GBP', callback_data='usd/gbp')
        btn2 = types.InlineKeyboardButton('USD/TRY', callback_data='usd/try')
        btn3 = types.InlineKeyboardButton('Enter the currency', callback_data='else')

        markup.add(btn1, btn2)
        markup.add(btn3)
        bot.send_message(message.chat.id, 'Choose currency pair ratio', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Enter positive number')
        bot.register_next_step_handler(message, get_curr)

@bot.message_handler(commands=['help'])
def help(message):
        main(message)

@bot.callback_query_handler(func=lambda call: True)
def answer(call):
    if call.data == 'users':
        conn = sqlite3.connect('Registration.sql')
        cur = conn.cursor()
        try:
            cur.execute('SELECT * FROM users')
            users = cur.fetchall()
            data = ''
            count = 1
            for el in users:
                data += f'{count}.Name: "{el[1]}" Password: "{el[2]}" \n'
                count += 1
            cur.close()
            conn.close()
            bot.send_message(call.message.chat.id, data)
        except sqlite3.OperationalError:
            bot.send_message(call.message.chat.id, 'Users list is empty')
    elif call.data == 'usd/gbp' or call.data == 'usd/try':
        value = call.data.upper().split('/')
        res = currency.convert(amount_curr, value[0], value[1])
        bot.send_message(call.message.chat.id, f"{amount_curr} {call.data[:3].upper()} is {round(res,2)} {call.data[4:].upper()}")
    elif call.data == 'else':
        bot.send_message(call.message.chat.id, 'Enter other currency pair ratio with "/":')
        try:
            bot.register_next_step_handler(call.message, other_curr)
        except IndexError:
            bot.send_message(call.message.chat.id, 'Enter other currency pair ratio with "/":')
    elif call.data == 'get_id':
        bot.send_message(call.message.chat.id, f'ID - {call.from_user.id}')
    elif call.data == 'hi':
        bot.send_message(call.message.chat.id, f'Hi {call.from_user.first_name}')
    elif call.data == 'registration':
        conn = sqlite3.connect('Registration.sql')
        cur = conn.cursor()
        cur.execute(
            'CREATE TABLE IF NOT EXISTS users (id int auto_increment primary key, name varchar(50), pass varchar(50))')
        conn.commit()
        cur.close()
        conn.close()
        bot.send_message(call.message.chat.id, "I can save your login and passwords to keep they private. Enter your login:")
        bot.register_next_step_handler(call.message, user_name)
    elif call.data == 'weather':
        bot.send_message(call.message.chat.id, 'Enter a name of city:')
        bot.register_next_step_handler(call.message, get_city)
    elif call.data == 'curr':
        bot.send_message(call.message.chat.id, 'Enter amount')
        bot.register_next_step_handler(call.message, get_curr)
    elif call.data == 'clean':
        try:
            conn = sqlite3.connect('Registration.sql')
            cur = conn.cursor()
            cur.execute('DROP TABLE users')
            conn.close()

            bot.send_message(call.message.chat.id, 'Users list was succesfully deleted')
        except sqlite3.OperationalError:
            bot.send_message(call.message.chat.id, 'Users list not exists')

def other_curr(message):
    try:
        value = message.text.upper().split('/')
        res = currency.convert(amount_curr, value[0], value[1])
        bot.send_message(message.chat.id,
                         f"{amount_curr} {value[0]} is {round(res, 2)} {value[1]}")
        bot.register_next_step_handler(message, get_curr)
    except Exception:
        else_markup = types.InlineKeyboardMarkup()
        else_btn = types.InlineKeyboardButton('Enter the currency', callback_data='else')
        else_markup.add(else_btn)
        bot.send_message(message.chat.id, "Wrong pair ratio, must consists '/'", reply_markup=else_markup)


def get_city(message):
    city_name = message.text.strip().lower()
    try:
        response = requests.get(
            f'https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key_weather}&units=metric').json()[
            'main']['temp']
        bot.send_message(message.chat.id, f'{response}°C in {city_name.capitalize()}')
    except KeyError:
        bot.send_message(message.chat.id, 'Wrong city')
def user_name(message):
    global names
    names = message.text.strip()
    bot.send_message(message.chat.id, 'Enter your password:')
    bot.register_next_step_handler(message, user_pass)

def user_pass(message):
    global password
    password = message.text.strip()

    conn = sqlite3.connect('Registration.sql')
    cur = conn.cursor()

    cur.execute(f'INSERT INTO users (name, pass) VALUES ("%s","%s")' % (names, password))
    conn.commit()
    cur.close()
    conn.close()

    markup3 = telebot.types.InlineKeyboardMarkup()
    btn1 = telebot.types.InlineKeyboardButton('Users list', callback_data='users')
    btn2 = telebot.types.InlineKeyboardButton('Clean users list', callback_data='clean')
    markup3.add(btn1, btn2)

    bot.send_message(message.chat.id, 'Registred!', reply_markup=markup3)


bot.polling(none_stop=True)
