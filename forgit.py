import sqlite3
import telebot
from telebot import types
import requests
import base64
import os
import mysql.connector
from mysql.connector import Error
import time
from slugify import slugify
from ftplib import FTP

users = {}
bot = telebot.TeleBot("nety")
named_tuple = time.localtime() # получить struct_time
time_string = time.strftime("%Y-%m-%d %H:%M:%S", named_tuple)


def create_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection

def uploadImg(path, fname):
	with FTP('nety', 'nety', 'nety') as ftp:
		with open(path, 'rb') as image_file:
			ftp.storbinary('STOR '+ fname+ '', image_file)
def execute_query(connection, query, user_id):
    global users
    users[user_id].append(False)
    print(users)
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        if users[user_id][6] == False:
            users[user_id].append(cursor.lastrowid)
            users[user_id][6] = True
    except Error as e:
        print(f"The error '{e}' occurred")
    cursor.close()
@bot.message_handler(commands=['start'])
def handle_start(message):
    global users
    if message.from_user.username == None:
        bot.send_message(call.message.chat.id, 'Поставьте логин')
    if message.from_user.username != None:
        users[message.from_user.id] = []
        users[message.from_user.id].append(message.from_user.username)
        keyboard = types.InlineKeyboardMarkup() #наша клавиатура
        print(users)
        key_yes = types.InlineKeyboardButton(text='Мой питомец потерялся', callback_data='yes') #кнопка «Да»
        keyboard.add(key_yes); #добавляем кнопку в клавиатур
        key_no= types.InlineKeyboardButton(text='Я нашел питомца', callback_data='no')
        keyboard.add(key_no)
        question = 'Выберите вид'
        bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "yes": #call.data это callback_data, которую мы указали при объявлении кнопки
        users[call.message.chat.id].append(12)
        bot.send_message(call.message.chat.id, 'Напишите заголовок')
		#bot.register_next_step_handler(message, get_title)
    elif call.data == "no":
        users[call.message.chat.id].append(11)
        bot.send_message(call.message.chat.id, 'Напишите заголовок')
		#bot.register_next_step_handler(message, get_title)
@bot.message_handler(content_types=['text'])
def get_title(message): #получаем фамилию
	users[message.from_user.id].append(message.text)
	bot.send_message(message.from_user.id, 'Отправьте фотографию')
	bot.register_next_step_handler(message, handle_docs_photo)
@bot.message_handler(content_types=['photo'])
def handle_docs_photo(message):
    try:
        chat_id = message.chat.id
        file_info_1 = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info_1.file_path)
        src = 'C:\yabex\photos\h_' + file_info_1.file_path.split('/')[-1]
        users[message.from_user.id].append('h_' + file_info_1.file_path.split('/')[-1])
        users[message.from_user.id].append(src)
        print(users)
        bot.send_message(message.from_user.id, 'Напишите немного текста')
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.register_next_step_handler(message, get_pass)
    except Exception as e:
        bot.reply_to(message, e)
@bot.message_handler(content_types=['text'])
def get_pass(message):
    users[message.from_user.id].append(message.text)
    bot.send_message(message.from_user.id, 'Подождите')
    #if users[message.from_user.id][0] == 0:
        
    #elif users[message.from_user.id][0] == 1:
    for i in range(len(users[message.from_user.id])):
        users[message.from_user.id][i] = str(users[message.from_user.id][i]).replace("'", "")
    uploadImg(users[message.from_user.id][4], users[message.from_user.id][3])
    connection = create_connection("net", "net", "net", "net")
    download = """<div class="wrap" style="background-color:inherit!important"> Telegram для связи @"""+users[message.from_user.id][0]+"""</div>"""
    img = '<p ><img width="560px" src="/uploads/fotos/'+users[message.from_user.id][3]+'"></p>'
    create_post = """
	    INSERT INTO `dle_post` (`id`, `autor`, `date`, `short_story`, `full_story`, `xfields`, `title`, `descr`, `keywords`, `category`, `alt_name`, `comm_num`, `allow_comm`, `allow_main`, `approve`, `fixed`, `allow_br`, `symbol`, `tags`, `metatitle`) VALUES (NULL, 'Copymaster', '"""+ time_string +"""', '"""+ img +"""<p>"""+users[message.from_user.id][5]+"""</p>"""+ download + """', '', '', '"""+ users[message.from_user.id][2] +"""', '', '', '"""+users[message.from_user.id][1] +"""', '"""+ slugify(users[message.from_user.id][2])+"""', '0', '1', '1', '1', '0', '0', '', '', '');
	    """
    execute_query(connection, create_post, message.from_user.id)
    post_extras = """
	    INSERT INTO `dle_post_extras` (`eid`, `news_id`, `news_read`, `allow_rate`, `rating`, `vote_num`, `votes`, `view_edit`, `disable_index`, `related_ids`, `access`, `editdate`, `editor`, `reason`, `user_id`, `disable_search`, `need_pass`, `allow_rss`, `allow_rss_turbo`, `allow_rss_dzen`) VALUES (NULL, '"""+ str(users[message.from_user.id][7]) +"""', '0', '1', '0', '0', '0', '0', '0', '', '', '', '', '', '1', '0', '0', '1', '0', '0');
	    """
    post_extras_cats ="""
    INSERT INTO `dle_post_extras_cats` (`id`, `news_id`, `cat_id`) VALUES (NULL, '"""+ str(users[message.from_user.id][7]) +"""', '"""+ users[message.from_user.id][1] +"""');
    """
    execute_query(connection, post_extras, message.from_user.id)
    execute_query(connection, post_extras_cats, message.from_user.id)
    link = "https://doska.sanyandhisfriends.xyz/index.php?newsid="+ str(users[message.from_user.id][7]) +".html"
    bot.send_message(message.from_user.id, link)
    connection.close()
    bot.send_message(message.from_user.id, '/start - для нового поста')
bot.infinity_polling()
