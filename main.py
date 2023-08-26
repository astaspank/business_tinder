import sqlite3

def create_database():
    conn = sqlite3.connect('users_db.db')

    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        telegram_id INTEGER UNIQUE,
        full_name TEXT,
        birth_date TEXT,
        company TEXT,
        position TEXT,
        avatar_url TEXT
    )
    ''')

    conn.commit()
    conn.close()

create_database()


import telebot
import sqlite3
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = 'YOUR_TOKEN'
bot = telebot.TeleBot(TOKEN)

# Словарь для временного хранения данных пользователей
user_data = {}

@bot.message_handler(commands=['start'])
def start_message(message):
    msg = bot.send_message(message.chat.id, "Введите ваше ФИО:")
    bot.register_next_step_handler(msg, process_full_name_step)

def process_full_name_step(message):
    user_data[message.chat.id] = {'full_name': message.text}
    msg = bot.send_message(message.chat.id, "Введите вашу дату рождения (дд.мм.гггг):")
    bot.register_next_step_handler(msg, process_birth_date_step)

def process_birth_date_step(message):
    user_data[message.chat.id]['birth_date'] = message.text
    msg = bot.send_message(message.chat.id, "Введите название вашей компании:")
    bot.register_next_step_handler(msg, process_company_step)

def process_company_step(message):
    user_data[message.chat.id]['company'] = message.text
    msg = bot.send_message(message.chat.id, "Введите вашу должность:")
    bot.register_next_step_handler(msg, process_position_step)

def process_position_step(message):
    user_data[message.chat.id]['position'] = message.text

    # Получение аватарки пользователя
    user_info = bot.get_user_profile_photos(message.chat.id)
    if user_info and user_info.total_count > 0:
        user_data[message.chat.id]['avatar_url'] = user_info.photos[0][0].file_id
    else:
        user_data[message.chat.id]['avatar_url'] = None

    save_to_db(user_data[message.chat.id], message.chat.id)
    bot.send_message(message.chat.id, "Ваш профиль успешно создан!")

def save_to_db(data, user_id):
    with sqlite3.connect("users_db.db") as con:
        cursor = con.cursor()
        cursor.execute('''INSERT OR REPLACE INTO users (telegram_id, full_name, birth_date, company, position, avatar_url)
                          VALUES (?, ?, ?, ?, ?, ?)''',
                       (user_id, data['full_name'], data['birth_date'], data['company'], data['position'], data['avatar_url']))
        con.commit()





@bot.message_handler(commands=['show_profiles'])
def show_profiles(message):
    with sqlite3.connect("users_db.db") as con:
        cursor = con.cursor()
        cursor.execute("SELECT full_name, birth_date, company, position, avatar_url FROM users")



        for row in cursor.fetchall():
            full_name, birth_date, company, position, avatar_url = row
            profile_info = f"ФИО: {full_name}\nДата рождения: {birth_date}\nКомпания: {company}\nДолжность: {position}"
            bot.send_message(message.chat.id, profile_info)
            if avatar_url:
                bot.send_photo(message.chat.id, avatar_url)


bot.polling(none_stop=True)
