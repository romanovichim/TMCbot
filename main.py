#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import threading
#import pypyodbc as pyodbc
import datetime

import telebot
from telebot.types import (InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery, InlineQuery,
                           InlineQueryResultArticle, InputTextMessageContent)
from telebot import types
from time import time, sleep

import settings
import random

import re
import sqlite3

ELEMENTS_ON_PAGE = 1
BOOKS_CHANGER = 3

# Insert your telegram bot`s token here
TOKEN = settings.Telegram.TOKEN
bot = telebot.TeleBot(TOKEN)
save_path = r'C:/Users/user/Desktop/tmc2/tmcphoto/'

menuback = u'\U0001F519'

toptmc = u'\U0001F51D'

user_dict = {}

#класс заявок

class User:
    def __init__(self, tmc):
        self.tmc = tmc
        self.name = None
        self.territory = None
        self.address = None
        self.telephone = None
        self.photo_path = None
        self.state = None
        self.tui = None
        self.ident = None
        self.category = None

address_dict = {}

class Address:
    def __init__(self, ad):
        self.ad = ad

like_user_dict = {}

class Like_User:
    def __init__(self,like_tmc):
        self.like_tmc = like_tmc
        self.like_name = None
        self.like_terr = None
        self.like_address = None
        self.like_phone = None
        self.like_tui = None
        self.like_ident = None
        self.like_datetime = None



        
#Меню





@bot.message_handler(commands=['start'])
@bot.message_handler(func=lambda message:message.text == 'Меню')
@bot.message_handler(func=lambda message:message.text == 'меню')
@bot.message_handler(func=lambda message:message.text == 'Меню'+menuback)
def processmenu(message):
    #bot.send_message(message.chat.id,"Если вы хотите передать ТМЦ - оформите заявку,если вы хотите получить ТМЦ, которого нет в списке заявок, оформите хотелку")
    #markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard = True)
    #markup.row('Добавить заявку','Добавить хотелку')
    #markup.row('Удалить заявку','Удалить хотелку')
    #markup.row('Просмотр заявок','Просмотр хотелок')
    #markup.row('Помощь')
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard = True)
    markup.row('Хочу Найти','Хочу Отдать')
    markup.row('Посмотреть что есть')
    markup.row('Личный кабинет','Помощь')
    bot.send_message(message.chat.id, "Выберите:", reply_markup=markup)

#Обработчик ошибки
def process_error(message):
    try:
        bot.reply_to(message,'Что-то пошло не так!Попробуйте ещё раз!')
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard = True)
        markup.add('Меню'+menuback)
        bot.send_message(message.chat.id, 'Нажмите Меню,чтобы выйти в меню', reply_markup=markup)
    except Exception as e:
        print(str(e))
        print("вылет из ошибка")

#Хотелки - Хочу Найти
        
@bot.message_handler(func=lambda message:'Хочу Найти' == message.text, content_types=['text'])
def processwantfind(message):
    #Определяем есть ли две записи в базе данных, если нет, то меню из двух - ПОИСК и Оставить заявку - Сортируем по количеству записей
    #Если есть то фигачим меню из четырех
    #Определяем количество записей
    db = sqlite3.connect(r'C:\Users\user\tmcone.db')
    cursor = db.cursor()
    cursor.execute('''SELECT COUNT (*) FROM tmclist ''')    
    values = cursor.fetchone()
    if values[0] < 2:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard = True)
        markup.row('Поиск','Оставить заявку')
        markup.add('Меню'+menuback)
        bot.send_message(message.chat.id, "Выберите:", reply_markup=markup)   
    #если больше двух
    if values[0] > 2:
        db = sqlite3.connect(r'C:\Users\user\tmcone.db')
        cursor = db.cursor()
        cursor.execute('''SELECT tmc, COUNT(tmc) AS Quant
                            FROM tmclist
                            GROUP By tmc
                            ORDER By Quant DESC
                            LIMIT 2 ''')        
        valuesone = cursor.fetchone()
        #valuesone[0] -первое место
        valuestwo = cursor.fetchone()
        #valuestwo[0] -второе место
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard = True)
        markup.row(toptmc+valuesone[0],'Поиск')
        markup.row(toptmc+valuestwo[0],'Оставить заявку')
        markup.add('Меню'+menuback)
        bot.send_message(message.chat.id, "Выберите:", reply_markup=markup)


#Хочу найти - Оставить заявку
    
@bot.message_handler(func=lambda message:'Оставить заявку' == message.text, content_types=['text'])
def likeprocessapplication(message):
    try:
        #проверяем есть ли с таким айдишником человек в базе, если да то приветствуем
        identready = message.chat.id
        db = sqlite3.connect(r'C:\Users\user\tmcone.db')
        cursor = db.cursor()
        cursor.execute('''SELECT COUNT (*) FROM likelist
                          WHERE like_tui = ?''',(identready,))    
        values = cursor.fetchone()
        if values[0] == 0:
            msg = bot.send_message(message.chat.id, """\Напишите мне, какое тмц вы хотите?:""")
            bot.register_next_step_handler(msg, likeprocess_name_step)
        else:
            #Приветстувем и на новый хенд
            #Достаем имя
            db = sqlite3.connect(r'C:\Users\user\tmcone.db')
            cursor = db.cursor()
            cursor.execute('''SELECT like_name FROM likelist
                                WHERE like_tui = ?''',(identready,))
            sname = cursor.fetchone()
            bot.send_message(message.chat.id,"Доброго времени суток!")
            #chat_id = message.chat.id
            #like_name = sname[0]
            #like_user = Like_User(like_name)
            #like_user_dict[chat_id] = like_user
            likeprocess_dop_step(message)
        
        db.commit()
        db.close()
    except Exception as e:
        print(str(e))
        process_error(message)
    
#Основная проходка





def likeprocess_name_step(message):
    try:
        chat_id = message.chat.id
        like_tmc = message.text
        like_user = Like_User(like_tmc)
        like_user_dict[chat_id] = like_user
        msg = bot.send_message(message.chat.id, 'Пришлите мне своё ФИО?')
        bot.register_next_step_handler(msg, likeprocessmain_tmc_step)
    except Exception as e:
        print(str(e))
        process_error(message)

def likeprocessmain_tmc_step(message):
    try:
        chat_id = message.chat.id
        like_name = message.text
        like_user = like_user_dict[chat_id]
        like_user.like_name = like_name
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard = True)
        markup.add('Аппарат ТБ')
        markup.add('Тверь','Север')
        msg = bot.send_message(message.chat.id, 'Территория(ГОСБ)', reply_markup=markup)
        bot.register_next_step_handler(msg, likeprocess_territory_step)
    except Exception as e:
        print(str(e))
        process_error(message)
        

#Допы



        #chat_id = message.chat.id
        #tmc = message.text
        #user = User(tmc)
        #user_dict[chat_id] = user
        #identready = message.chat.id
        #Сюда вставить добор имени
        #db = sqlite3.connect(r'C:\Users\user\tmcone.db')
        #cursor = db.cursor()
        #cursor.execute('''SELECT name FROM tmclist
        #                        WHERE tui = ?''',(identready,))
        #sname = cursor.fetchone()
        #user = user_dict[chat_id]
        #user.name = sname[0]

#имя
    
def likeprocess_dop_step(message):
    try:
        msg = bot.send_message(message.chat.id, 'Напишите мне, какое тмц вы хотите получить?')
        bot.register_next_step_handler(msg, likeprocessdop_tmc_step)
    except Exception as e:
        print(str(e))
        process_error(message) 



#тмц
        
def likeprocessdop_tmc_step(message):
    try:
        # 
        chat_id = message.chat.id
        like_tmc = message.text
        like_user = Like_User(like_tmc)
        like_user_dict[chat_id] = like_user
        identready = message.chat.id
        #Сюда вставить добор имени
        db = sqlite3.connect(r'C:\Users\user\tmcone.db')
        cursor = db.cursor()
        cursor.execute('''SELECT like_name FROM likelist
                                WHERE like_tui = ?''',(identready,))
        sname = cursor.fetchone()
        like_user = like_user_dict[chat_id]
        like_user.like_name = sname[0]
        #
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard = True)
        markup.add('Аппарат ТБ')
        markup.add('Тверь','Север')
        msg = bot.send_message(message.chat.id, 'Территория(ГОСБ)', reply_markup=markup)
        bot.register_next_step_handler(msg, likeprocess_territory_step)
    except Exception as e:
        print(str(e))
        process_error(message)

                   


# Переделываем досюда

#территория
        
def likeprocess_territory_step(message):
    try:
        chat_id = message.chat.id
        like_terr = message.text
        like_user = like_user_dict[chat_id]
        like_user.like_terr = like_terr
        msg = bot.send_message(message.chat.id, 'Выберите адрес')
        if like_user.like_terr == "Аппарат ТБ":
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard = True)
            markup.add('Б.Андроньевская д8')
            markup.add('Б.Андроньевская д18')
            markup.add('2-ой Южнопортовый проезд')
            msg = bot.send_message(message.chat.id, 'Выберите', reply_markup=markup)
            bot.register_next_step_handler(msg, likeprocess_address_step)
        else:
            addressg = like_terr
            like_user.like_address = like_user.like_terr
            bot.send_message(message.chat.id,"Напишите контактный телефон")
            bot.register_next_step_handler(msg, likeprocess_telephone_step)
    except Exception as e:
        print(str(e))
        process_error(message)


#Адрес
        
def likeprocess_address_step(message):
    try:
        chat_id = message.chat.id
        like_address = message.text
        like_user = like_user_dict[chat_id]
        like_user.like_address = like_address
        msg = bot.send_message(message.chat.id, 'Напишите контактный телефон')
        bot.register_next_step_handler(msg, likeprocess_telephone_step)
    except Exception as e:
       print(str(e))
       process_error(message) 
#Телефон
        
def likeprocess_telephone_step(message):
    try:
        chat_id = message.chat.id
        like_telephone = message.text
        like_user = like_user_dict[chat_id]
        like_user.like_telephone =  like_telephone
        #Смотрим есть ли такое в базе, если есть то предлагаем позвонить
        #Сначала чекаем кол-во
        conn = sqlite3.connect(r"C:\Users\user\tmcone.db")
        cursor = conn.cursor()
        #cursor.execute("SELECT * FROM tmclist WHERE tmc LIKE ? ", ('%'+like_user.like_tmc+'%',))
        cursor.execute("SELECT COUNT(*) FROM tmclist WHERE tmc LIKE ? ", ('%'+like_user.like_tmc+'%',))
        cheker = cursor.fetchone()
        if cheker[0] > 0: 
            conn = sqlite3.connect(r"C:\Users\user\tmcone.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tmclist WHERE tmc LIKE ? ", ('%'+like_user.like_tmc+'%',))
            books = cursor.fetchall()
            bot.send_message(message.chat.id,"По вашему запросу есть заявки, если они вас не устраивают,просто опубликуйте заявку")
            sleep(5)
            for row in books:
                bot.send_message(message.chat.id, 'Заявка: ' + row[0] + '\nТМЦ:'+ row[1] + 'Состояние:' + row[6]   + '\nАдрес:' + row[3] + '\nТелефон:' + row[4] )
                keyboard = types.InlineKeyboardMarkup()
                callback_button = types.InlineKeyboardButton(text="Подробности", callback_data=str(row[8]))
                keyboard.add(callback_button)
                bot.send_message(message.chat.id,'Нажмите чтобы посмотреть поподробнее', reply_markup=keyboard)
                
        # Получаем результат сделанного запроса
        #books = cursor.fetchall()
        #bot.send_chat_action(message.chat.id, 'typing')
        #if books is not None:
            #bot.send_message(message.chat.id,"По вашему запросу есть заявки, если они вас не устраивают,просто опубликуйте заявку")
            #sleep(5)
            #for row in books:
                #bot.send_message(message.chat.id, 'Заявка: ' + row[0] + '\nТМЦ:'+ row[1] + 'Состояние:' + row[6]   + '\nАдрес:' + row[3] + '\nТелефон:' + row[4] )
                #keyboard = types.InlineKeyboardMarkup()
                #callback_button = types.InlineKeyboardButton(text="Подробности", callback_data=str(row[8]))
                #keyboard.add(callback_button)
                #bot.send_message(message.chat.id,'Нажмите чтобы посмотреть поподробнее', reply_markup=keyboard)

        conn.commit()
        conn.close()
    
        bot.send_message(chat_id, 'Ваша заявка: ' + like_user.like_name + '\nТМЦ:' + like_user.like_tmc + '\nТерритория:' + like_user.like_terr + '\nАдрес:' + like_user.like_address + '\nТелефон:' + like_user.like_telephone)
        #photo = open(user.photo_path, 'rb')
        #bot.send_chat_action(message.chat.id,'upload_photo')
        #bot.send_photo(chat_id,photo)
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard = True)
        markup.add('Да','Нет')
        msg = bot.send_message(message.chat.id, 'Опубликовать заявку?', reply_markup=markup)
        bot.register_next_step_handler(msg, likeprocess_publish_step)
    except Exception as e:
        print(str(e))
        process_error(message)        

#Публикация заявки и перехват айди пользователя а также запихон в базу

def likeprocess_publish_step(message):
    try:
        if message.text == 'Да':
            chat_id = message.chat.id

            photo_name = str(random.randrange(0,1000000,1)) # изменяем потом на идентификатор
            like_user = like_user_dict[chat_id]
            like_user.like_ident =  photo_name
            
            like_tui = chat_id
            like_user = like_user_dict[chat_id]
            like_user.like_tui = like_tui
            db = sqlite3.connect(r'C:\Users\user\tmcone.db')
            cursor = db.cursor()
            cursor.execute('''INSERT INTO likelist(like_name,like_tmc,like_terr,like_address,like_phone,like_tui,like_ident,like_datetime)
                              VALUES(?,?,?,?,?,?,?,date('now'))''',(like_user.like_name,like_user.like_tmc,like_user.like_terr,like_user.like_address,like_user.like_telephone,like_user.like_tui,like_user.like_ident))
            db.commit()
            db.close()
            bot.send_message(message.chat.id,"Заявка опубликована!Спасибо!")
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard = True)
            markup.add('Меню'+menuback)
            bot.send_message(message.chat.id, 'Нажмите Меню,чтобы выйти в меню', reply_markup=markup)
        else:
            processmenu(message)
    except Exception as e:
        print(str(e))
        process_error(message)




#конец хотелки









#теперь поиск

#Поиск
@bot.message_handler(func=lambda message:'Поиск' == message.text, content_types=['text'])
def processisch(message):
    #отправлем обратно меню
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard = True)
    markup.add('Меню'+menuback)
    msg = bot.send_message(message.chat.id, """
    Наберите, что вы хотите найти и отправьте
    Например:Мышь
    Либо нажмите Меню,чтобы выйти
    """, reply_markup=markup)
    #search = message.text
    bot.register_next_step_handler(msg, searchresulted)

def searchresulted(message):
    search = message.text
    if search == 'Меню'+menuback:
        processmenu(message)
        return
    conn = sqlite3.connect(r"C:\Users\user\tmcone.db")
    cursor = conn.cursor()
    #cursor.execute("SELECT Ссылканаавито,Номер FROM chatbot")
    #cursor.execute('''SELECT Ссылканаавито,Номер FROM chatbot
    #                  WHERE Регион = ?''',("Юг",))
    cursor.execute("SELECT * FROM tmclist WHERE tmc LIKE ? ", ('%'+search+'%',))
    # Получаем результат сделанного запроса
    books = cursor.fetchall()
    if books ==[]:
        bot.send_message(message.chat.id,'Пока ничего нет.Сделайте запрос на оснащение')
        bot.send_message(message.chat.id,'Или оставьте нам заявку в разделе - Хочу Найти')
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard = True)
        markup.add('Меню'+menuback)
        bot.send_message(message.chat.id, 'Нажмите Меню,чтобы выйти в меню', reply_markup=markup)
        return
    bot.send_chat_action(message.chat.id, 'typing')
    for row in books:
            bot.send_message(message.chat.id, 'Заявка: ' + row[0] + '\nТМЦ:'+ row[1] + 'Состояние:' + row[6]   + '\nАдрес:' + row[3] + '\nТелефон:' + row[4] )
            keyboard = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(text="Подробности", callback_data=str(row[8]))
            keyboard.add(callback_button)
            bot.send_message(message.chat.id,'Нажмите чтобы посмотреть поподробнее', reply_markup=keyboard)
    conn.commit()
    conn.close()
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard = True)
    markup.add('Меню'+menuback)
    bot.send_message(message.chat.id, 'Нажмите Меню,чтобы выйти в меню', reply_markup=markup)


#call на подробности заявки


@bot.callback_query_handler(func=lambda call: call.message.text == "Нажмите чтобы посмотреть поподробнее")
def callback_inline(call):
    #В CALL перелается строка  вернем её в инт
    identint = int(call.data)
    #тащим путь фотографии
    db = sqlite3.connect(r'C:\Users\user\tmcone.db')
    cursor = db.cursor()
    cursor.execute('''SELECT * FROM tmclist
                      WHERE ident = ?''',(identint,))
    for row in cursor:
        bot.send_message(call.message.chat.id, 'Ваша заявка: ' + row[0] + '\nТМЦ:' + row[1] + '\nТерритория:' + row[2] + '\nАдрес:' + row[3] + '\nТелефон:' + row[4] + '\nСостояние:' + row[6] + '\nФото:')
        photo = open(row[5], 'rb')
        bot.send_chat_action(call.message.chat.id,'upload_photo')
        bot.send_photo(call.message.chat.id,photo)
        
    db.commit()
    db.close()
    bot.send_message(call.message.chat.id,"Чтобы посмотреть другие заявки прокрутите наверх" + "\nЕсли вы забираете ТМЦ не забудьте напомнить удалить заявку,заявителю")
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard = True)
    markup.add('Меню'+menuback)
    bot.send_message(call.message.chat.id, 'Нажмите Меню,чтобы выйти в меню', reply_markup=markup)
    




#прехватчик с топтмц
 
@bot.message_handler(func=lambda m: re.search(toptmc, m.text) is not None)
def echo_search(message):
    #здесь выводим поиск по топ тмц
    #обрезать первый символ из строки
    search = message.text
    search =search.replace(toptmc,'')
    conn = sqlite3.connect(r"C:\Users\user\tmcone.db")
    cursor = conn.cursor()
    #cursor.execute("SELECT Ссылканаавито,Номер FROM chatbot")
    #cursor.execute('''SELECT Ссылканаавито,Номер FROM chatbot
    #                  WHERE Регион = ?''',("Юг",))
    cursor.execute("SELECT * FROM tmclist WHERE tmc LIKE ? ", ('%'+search+'%',))
    # Получаем результат сделанного запроса
    books = cursor.fetchall()
    bot.send_chat_action(message.chat.id, 'typing')
    for row in books:
            bot.send_message(message.chat.id, 'Заявка: ' + row[0] + '\nТМЦ:'+ row[1] + 'Состояние:' + row[6]   + '\nАдрес:' + row[3] + '\nТелефон:' + row[4] )
            keyboard = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(text="Подробности", callback_data=str(row[8]))
            keyboard.add(callback_button)
            bot.send_message(message.chat.id,'Нажмите чтобы посмотреть поподробнее', reply_markup=keyboard)
    conn.commit()
    conn.close()
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard = True)
    markup.add('Меню'+menuback)
    bot.send_message(message.chat.id, 'Нажмите Меню,чтобы выйти в меню', reply_markup=markup)



#Регистрция заявки - Хочу Отдать
#Регистрация заявки
    
@bot.message_handler(func=lambda message:'Хочу Отдать' == message.text, content_types=['text'])
def processapplication(message):
    try:
        #проверяем есть ли с таким айдишником человек в базе, если да то приветствуем
        identready = message.chat.id
        db = sqlite3.connect(r'C:\Users\user\tmcone.db')
        cursor = db.cursor()
        cursor.execute('''SELECT COUNT (*) FROM tmclist
                          WHERE tui = ?''',(identready,))    
        values = cursor.fetchone()
        if values[0] == 0:
            msg = bot.send_message(message.chat.id, """Напишите мне \n что за ТМЦ вы хотите отдать?""")
            bot.register_next_step_handler(msg, process_tmc_step)
        else:
            #Приветстувем и на новый хенд
            #Достаем имя
            db = sqlite3.connect(r'C:\Users\user\tmcone.db')
            cursor = db.cursor()
            cursor.execute('''SELECT name FROM tmclist
                                WHERE tui = ?''',(identready,))
            sname = cursor.fetchone()
            bot.send_message(message.chat.id,"Доброго времени суток!")
            process_dop_step(message)
        
        db.commit()
        db.close()
    except Exception as e:
        process_error(message)

#основ тмц

def process_tmc_step(message):
    try:
        chat_id = message.chat.id
        tmc = message.text
        user = User(tmc)
        user_dict[chat_id] = user
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard = True)
        markup.add('ИТ','Спец. Обор.')
        markup.add('Мебель','Прочее')
        msg = bot.send_message(message.chat.id, 'Выберите категорию ТМЦ:', reply_markup=markup)
        bot.register_next_step_handler(msg, process_cat_step)
    except Exception as e:
        print(str(e))
        process_error(message)

def process_cat_step(message):
    try:
        chat_id = message.chat.id
        category = message.text
        user = user_dict[chat_id]
        user.category = category
        msg = bot.send_message(message.chat.id, """Напишите мне ваше ФИО""")
        bot.register_next_step_handler(msg, process_name_step)
    except Exception as e:
        process_error(message)

def process_name_step(message):
    try:
        chat_id = message.chat.id
        name = message.text
        user = user_dict[chat_id]
        user.name = name
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Аппарат ТБ')
        markup.add('Юг','Север')
        markup.add('Восток','Запад')
        markup.add('Брянск','Кострома')
        markup.add('Иваново','Тверь')
        markup.add('Тула','Смоленск')
        markup.add('Рязань','Калуга')
        msg = bot.send_message(message.chat.id, 'Выберите Территория(ГОСБ)', reply_markup=markup)
        bot.register_next_step_handler(msg,process_territory_step )
    except Exception as e:
        process_error(message)

    
#Сначала по ветке dop
def process_dop_step(message):
    try:
        msg = bot.send_message(message.chat.id, ' Напишите мне \nЧто за тмц вы хотите отдать?')
        bot.register_next_step_handler(msg, processdop_tmc_step)
    except Exception as e:
        process_error(message)

#dopтмц
        
def processdop_tmc_step(message):
    try:
        chat_id = message.chat.id
        tmc = message.text
        user = User(tmc)
        user_dict[chat_id] = user
        identready = message.chat.id
        #Сюда вставить добор имени
        db = sqlite3.connect(r'C:\Users\user\tmcone.db')
        cursor = db.cursor()
        cursor.execute('''SELECT name FROM tmclist
                                WHERE tui = ?''',(identready,))
        sname = cursor.fetchone()
        user = user_dict[chat_id]
        user.name = sname[0]
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard = True)
        markup.add('ИТ','Спец. Обор.')
        markup.add('Мебель','Прочее')
        msg = bot.send_message(message.chat.id, 'Выберите категорию ТМЦ:', reply_markup=markup)
        bot.register_next_step_handler(msg, processdop_cat_step)
    except Exception as e:
        process_error(message)

#dopКатегория
    
def processdop_cat_step(message):
    try:
        chat_id = message.chat.id
        category = message.text
        user = user_dict[chat_id]
        user.category = category
        #if category == "ИТ":
        #    bot.send_message(message.chat.id,"Помните!Оборудование с инвентарным номером обменивается через SAP")
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Аппарат ТБ')
        markup.add('Юг','Север')
        markup.add('Восток','Запад')
        markup.add('Брянск','Кострома')
        markup.add('Иваново','Тверь')
        markup.add('Тула','Смоленск')
        markup.add('Рязань','Калуга')
        msg = bot.send_message(message.chat.id, 'Выберите Территория(ГОСБ)', reply_markup=markup)
        bot.register_next_step_handler(msg,process_territory_step )
    except Exception as e:
        process_error(message) 


#def process_dop_step(message):
#    try:
#        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard = True)
#        markup.add('ИТ','Спец. Обор.')
#        markup.add('Мебель','Прочее')
#        msg = bot.send_message(message.chat.id, 'Выберите категорию ТМЦ:', reply_markup=markup)
#        bot.register_next_step_handler(msg, process_cat_step)
#    except Exception as e:
#        process_error(message)



#def process_name_step(message):
#    try:
#        chat_id = message.chat.id
#        name = message.text
#        user = User(name)
#        user_dict[chat_id] = user
#        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard = True)
#        markup.add('ИТ','Спец. Обор.')
#        markup.add('Мебель','Прочее')
#        msg = bot.send_message(message.chat.id, 'Выберите категорию ТМЦ:', reply_markup=markup)
#        bot.register_next_step_handler(msg, process_cat_step)
#    except Exception as e:
#        process_error(message)
        
#Категория
    
#def process_cat_step(message):
#    try:
#        chat_id = message.chat.id
#        category = message.text
#        user = user_dict[chat_id]
#        user.category = category
#        if category == "ИТ":
#            bot.send_message(message.chat.id,"Помните!Оборудование с инвентарным номером обменивается через SAP")
#        msg = bot.send_message(message.chat.id, 'Что за тмц?')
#        bot.register_next_step_handler(msg, process_tmc_step)
#    except Exception as e:
#       process_error(message) 

#тмц
        
#def process_tmc_step(message):
#    try:
#        chat_id = message.chat.id
#        tmc = message.text
#        user = user_dict[chat_id]
#        user.tmc = tmc
#        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
#        markup.add('Аппарат ТБ')
#        markup.add('Юг','Север')
#        markup.add('Восток','Запад')
#        markup.add('Брянск','Кострома')
#        markup.add('Иваново','Тверь')
#        markup.add('Тула','Смоленск')
#        markup.add('Рязань','Калуга')
#        msg = bot.send_message(message.chat.id, 'Территория(ГОСБ)', reply_markup=markup)
#        bot.register_next_step_handler(msg, process_territory_step)
#    except Exception as e:
#        process_error(message)
                    


# меняем до сюда 
#территория
        
def process_territory_step(message):
    try:
        chat_id = message.chat.id
        territory= message.text
        user = user_dict[chat_id]
        user.territory = territory
        msg = bot.send_message(message.chat.id, 'Выберите адрес')
        if user.territory == "Аппарат ТБ":
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('Б.Андроньевская д8')
            markup.add('Б.Андроньевская д18')
            markup.add('2-ой Южнопортовый проезд')
            msg = bot.send_message(message.chat.id, 'Выберите', reply_markup=markup)
            bot.register_next_step_handler(msg, process_address_step)
        else:
            addressg = territory
            user.address = user.territory
            bot.send_message(message.chat.id,"Напишите контактный телефон")
            bot.register_next_step_handler(msg, process_telephone_step)
    except Exception as e:
        process_error(message)


#Адрес
        
def process_address_step(message):
    try:
        chat_id = message.chat.id
        address = message.text
        user = user_dict[chat_id]
        user.address = address
        msg = bot.send_message(message.chat.id, 'Напишите контактный телефон')
        bot.register_next_step_handler(msg, process_telephone_step)
    except Exception as e:
       process_error(message) 
#Телефон
        
def process_telephone_step(message):
    try:
        chat_id = message.chat.id
        telephone = message.text
        user = user_dict[chat_id]
        user.telephone =  telephone
        msg = bot.send_message(message.chat.id, 'Отправьте Фото')
        bot.register_next_step_handler(msg, process_photo_step)
    except Exception as e:
        process_error(message)
        
#Фото
        
def process_photo_step(message):
    try:
        chat_id = message.chat.id
        #photo_path = message.text
        raw = message.photo[2].file_id
        photo_name = str(random.randrange(0,1000000,1)) # изменяем потом на идентификатор
        user = user_dict[chat_id]
        user.ident =  photo_name
        path = os.path.join(save_path,photo_name+".jpg")
        photo_path = path
        file_info = bot.get_file(raw)
        downloaded_file = bot.download_file(file_info.file_path)
        with open(path,'wb') as new_file:
            new_file.write(downloaded_file)
        user = user_dict[chat_id]
        user.photo_path = photo_path
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard = True)
        markup.add('Хорошее','Удовл.','Запчасти')
        msg = bot.send_message(message.chat.id, 'Какое состояние у ТМЦ?', reply_markup=markup)
        bot.register_next_step_handler(msg, process_state_step)
    except Exception as e:
        process_error(message)
        
#Состояние
        
def process_state_step(message):
    try:
        chat_id = message.chat.id
        state = message.text
        user = user_dict[chat_id]
        user.state = state
        #msg = bot.reply_to(message, '')
        bot.send_message(chat_id, 'Ваша заявка: ' + user.name + '\nТМЦ:' + user.tmc + '\nТерритория:' + user.territory + '\nАдрес:' + user.address + '\nТелефон:' + user.telephone + '\nСостояние:' + user.state + '\nФото:')
        photo = open(user.photo_path, 'rb')
        bot.send_chat_action(message.chat.id,'upload_photo')
        bot.send_photo(chat_id,photo)
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard = True)
        markup.add('Да','Нет')
        msg = bot.send_message(message.chat.id, 'Опубликовать заявку?', reply_markup=markup)
        bot.register_next_step_handler(msg, process_publish_step)
    except Exception as e:
        process_error(message)        

#Публикация заявки и перехват айди пользователя а также запихон в базу

def process_publish_step(message):
    try:
        if message.text == 'Да':
            chat_id = message.chat.id
            tui = chat_id
            user = user_dict[chat_id]
            user.tui = tui
            db = sqlite3.connect(r'C:\Users\user\tmcone.db')
            cursor = db.cursor()
            cursor.execute('''INSERT INTO tmclist(name,tmc,territory,address,telephone,photo_path,state,tui,ident,category,datetime)
                              VALUES(?,?,?,?,?,?,?,?,?,?,date('now'))''',(user.name,user.tmc,user.territory,user.address,user.telephone,user.photo_path,user.state,user.tui,user.ident,user.category))
            db.commit()
            db.close()
            bot.send_message(message.chat.id,"Заявка опубликована!Спасибо!")
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard = True)
            markup.add('Меню'+menuback)
            bot.send_message(message.chat.id, 'Нажмите Меню,чтобы выйти в меню', reply_markup=markup)
        else:
            processmenu(message)
    except Exception as e:
        process_error(message)















@bot.message_handler(func=lambda message:'Личный кабинет' == message.text, content_types=['text'])
def processcab(message):
    #чекаем есть ли человек в заявках или лайках
    #Удаление заявок
    iduser = message.chat.id
    db = sqlite3.connect(r'C:\Users\user\tmcone.db')
    cursor = db.cursor()
    cursor.execute('''SELECT COUNT(*) FROM tmclist
                      WHERE tui = ?''',(iduser,))
    values = cursor.fetchone()
    if values[0] > 0:
        cursor.execute('''SELECT * FROM tmclist
                      WHERE tui = ? LIMIT 1''',(iduser,))
        for row in cursor:
            bot.send_message(message.chat.id, 'Доброго времени суток: \n' + row[0])

    if values[0] == 0:
        iduser = message.chat.id
        db = sqlite3.connect(r'C:\Users\user\tmcone.db')
        cursor = db.cursor()
        cursor.execute('''SELECT COUNT(*) FROM likelist
                          WHERE like_tui = ?''',(iduser,))
        values = cursor.fetchone()
        if values[0] > 0:
             cursor.execute('''SELECT * FROM likelist
                      WHERE like_tui = ? LIMIT 1''',(iduser,))
             for row in cursor:
                 bot.send_message(message.chat.id, 'Доброго времени суток: \n' + row[0])

    #ЕСЛИ ПОЛЬЗОВАТЕЛЯ НЕТ В СИСТЕМЕ ТО КИДАЕМ ЧТО ПОКА НИЧЕГО НЕТ
    iduser = message.chat.id
    db = sqlite3.connect(r'C:\Users\user\tmcone.db')
    cursor = db.cursor()
    cursor.execute('''SELECT COUNT(*) FROM tmclist
                      WHERE tui = ?''',(iduser,))
    tvalues = cursor.fetchone()
    iduser = message.chat.id
    db = sqlite3.connect(r'C:\Users\user\tmcone.db')
    cursor = db.cursor()
    cursor.execute('''SELECT COUNT(*) FROM likelist
                      WHERE like_tui = ?''',(iduser,))
    lvalues = cursor.fetchone()
    summ = tvalues[0] + lvalues[0]
    if summ == 0:
        bot.send_message(message.chat.id, "Вы пока не добавили ни одной заявки в систему, добавьте заявку, чтобы я с вами познакомился")    
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard = True)
        markup.add('Меню'+menuback)
        bot.send_message(message.chat.id, 'Нажмите Меню,чтобы выйти в меню', reply_markup=markup)

    if summ > 0:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard = True)
        markup.row('Удаление заявок','Удаление хотелок')
        markup.row('Изменить ФИО')
        markup.add('Меню'+menuback)
        bot.send_message(message.chat.id, "Выберите:", reply_markup=markup)  
        
    #ЕСЛИ ЕСТЬ ТО КИДАЕМ МЕНЮ
    
    

@bot.message_handler(func=lambda message:'Изменить ФИО' == message.text, content_types=['text'])
def processisch(message):
    #отправлем обратно меню
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard = True)
    markup.add('Меню'+menuback)
    msg = bot.send_message(message.chat.id, """
    Наберите, свое ФИО
    Либо нажмите Меню,чтобы выйти
    """, reply_markup=markup)
    #search = message.text
    
    bot.register_next_step_handler(message, FIOresulted)

def FIOresulted(message):
    newFIO = message.text
    iduser = message.chat.id
    db = sqlite3.connect(r'C:\Users\user\tmcone.db')
    cursor = db.cursor()
    cursor.execute('''UPDATE tmclist SET name = ?
                      WHERE tui = ?''',(newFIO,iduser,))
    db.commit()
    db.close()
    db = sqlite3.connect(r'C:\Users\user\tmcone.db')
    cursor = db.cursor()
    cursor.execute('''UPDATE likelist SET like_name = ?
                      WHERE like_tui = ?''',(newFIO,iduser,))
    db.commit()
    db.close()
    bot.send_message(message.chat.id, "ФИО изменено") 
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard = True)
    markup.add('Меню'+menuback)
    bot.send_message(message.chat.id, 'Нажмите Меню,чтобы выйти в меню', reply_markup=markup)


#Удаление заявок
@bot.message_handler(func=lambda message:'Удаление заявок' == message.text, content_types=['text'])
def processdel(message):
    iduser = message.chat.id
    db = sqlite3.connect(r'C:\Users\user\tmcone.db')
    cursor = db.cursor()
    cursor.execute('''SELECT COUNT(*) FROM tmclist
                      WHERE tui = ?''',(iduser,))
    values = cursor.fetchone()
    if values[0] == 0:
        bot.send_message(message.chat.id, "Вы пока не зарегестрировали ни одной заявки")
    #print(values[0]) - кол-во заявок
    cursor.execute('''SELECT * FROM tmclist
                      WHERE tui = ?''',(iduser,))
    #for row in cursor:
    #       print('{0},{1},{2},{3},{4},{5},{6},{7},{8}'.format(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]))
    #for row in cursor:
    #       print(row[0]+row[1]+row[2]+row[3]+row[4]+row[6])
                 
    for row in cursor:
        bot.send_message(message.chat.id, 'Ваша заявка: ' + row[0] + '\nТМЦ:' + row[1] + '\nТерритория:' + row[2] + '\nАдрес:' + row[3] + '\nТелефон:' + row[4] + '\nСостояние:' + row[6] + '\nФото:')
        photo = open(row[5], 'rb')
        bot.send_chat_action(message.chat.id,'upload_photo')
        #теперь коллбэкнаудаление
        keyboard = types.InlineKeyboardMarkup()
        callback_button = types.InlineKeyboardButton(text="Удалить", callback_data=str(row[8]))
        keyboard.add(callback_button)
        bot.send_photo(message.chat.id,photo)
        bot.send_message(message.chat.id,"Нажимите чтобы удалить", reply_markup=keyboard)
        #bot.send_chat_action(message.chat.id,'typing')
    
    db.commit()
    db.close()
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard = True)
    markup.add('Меню'+menuback)
    bot.send_message(message.chat.id, 'Нажмите Меню,чтобы выйти в меню', reply_markup=markup)

#перехватим
    
@bot.callback_query_handler(func=lambda call: call.message.text == "Нажимите чтобы удалить")
def callback_inline(call):
    #удаление
    #Спрашиваем почему удаление
    #сначала удаляем фотку потом удаляем саму заявку а то нет пути к фото
    #В CALL перелается строка  вернем её в инт
    #identint = int(call.data)
    #тащим путь фотографии
    #db = sqlite3.connect(r'C:\Users\ivan\tmcone.db')
    #cursor = db.cursor()
    #cursor.execute('''SELECT photo_path FROM tmclist
    #                  WHERE ident = ?''',(identint,))
    #values = cursor.fetchone()
    ###print(values[0]) путь к фото
    #os.remove(values[0])
    #cursor = db.cursor()
    #cursor.execute('''DELETE FROM tmclist
    #                  WHERE ident = ?''',(identint,))
    #db.commit()
    #db.close()
    #bot.send_message(call.message.chat.id,"Удалена заявка с номером " + call.data)
    #теперь коллбэкнаудаление
    keyboard = types.InlineKeyboardMarkup()
    callback_button1 = types.InlineKeyboardButton(text="ДА", callback_data=call.data+"+ДА")
    callback_button2 = types.InlineKeyboardButton(text="НЕТ", callback_data=call.data+"+НЕТ")
    keyboard.add(callback_button1,callback_button2)
    bot.send_message(call.message.chat.id,"Вы передали ТМЦ?", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.message.text == "Вы передали ТМЦ?")
def callback_inline(call):
    #print(call.data[call.data.find('+')+1:])
    сallregnum = call.data.split("+")[0]
    #print(сallregnum)
    #Копия для статистики
    #delcheck = call.message.text
    delcheck = call.data[call.data.find('+')+1:]
    #identint = int(call.data)
    #print(call.data.split("+")[0])
    identint = int(call.data.split("+")[0])
    db = sqlite3.connect(r'C:\Users\user\tmcone.db')
    cursor = db.cursor()
    cursor.execute('''INSERT INTO tmccheckdel
                      SELECT name,tmc,territory,address,telephone,photo_path,state,tui,ident,category,datetime,state FROM tmclist
                      WHERE ident = ?''',(identint,))
    db.commit()
    db = sqlite3.connect(r'C:\Users\user\tmcone.db')
    cursor = db.cursor()
    cursor.execute("UPDATE tmccheckdel SET delcheck = ? WHERE  ident = ? ",(delcheck,identint,))
    db.commit()
    #Удаление
    #identint = int(call.data)
    #тащим путь фотографии
    db = sqlite3.connect(r'C:\Users\user\tmcone.db')
    cursor = db.cursor()
    cursor.execute('''SELECT photo_path FROM tmclist
                      WHERE ident = ?''',(identint,))
    values = cursor.fetchone()
    ###print(values[0]) путь к фото
    os.remove(values[0])
    cursor = db.cursor()
    cursor.execute('''DELETE FROM tmclist
                      WHERE ident = ?''',(identint,))
    db.commit()
    db.close()    
    bot.send_message(call.message.chat.id,"Удалена заявка с номером " + call.data)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard = True)
    markup.add('Меню'+menuback)
    bot.send_message(call.message.chat.id, 'Нажмите Меню,чтобы выйти в меню', reply_markup=markup)


        
#конец удаления заявки

#удаление хотелок

@bot.message_handler(func=lambda message:'Удаление хотелок' == message.text, content_types=['text'])
def likeprocessdel(message):
    iduser = message.chat.id
    db = sqlite3.connect(r'C:\Users\user\tmcone.db')
    cursor = db.cursor()
    cursor.execute('''SELECT COUNT(*) FROM likelist
                      WHERE like_tui = ?''',(iduser,))
    values = cursor.fetchone()
    if values[0] == 0:
        bot.send_message(message.chat.id, "Вы пока не зарегестрировали ни одной хотелки")
    #print(values[0]) - кол-во заявок
    cursor.execute('''SELECT * FROM likelist
                      WHERE like_tui = ?''',(iduser,))
    #for row in cursor:
    #       print('{0},{1},{2},{3},{4},{5},{6},{7},{8}'.format(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]))
    #for row in cursor:
    #       print(row[0]+row[1]+row[2]+row[3]+row[4]+row[6])
                 
    for row in cursor:
        bot.send_message(message.chat.id, 'Ваша хотелка: ' + row[0] + '\nТМЦ:' + row[1] + '\nТерритория:' + row[2] + '\nАдрес:' + row[3] + '\nТелефон:' + row[4] )
        #photo = open(row[5], 'rb')
        #bot.send_chat_action(message.chat.id,'upload_photo')
        #теперь коллбэкнаудаление
        keyboard = types.InlineKeyboardMarkup()
        callback_button = types.InlineKeyboardButton(text="Удалить", callback_data=str(row[6]))
        keyboard.add(callback_button)
        #bot.send_photo(message.chat.id,photo)
        bot.send_message(message.chat.id,"Нажимите чтобы удалить хотелку", reply_markup=keyboard)
        #bot.send_chat_action(message.chat.id,'typing')
    
    db.commit()
    db.close()
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard = True)
    markup.add('Меню'+menuback)
    bot.send_message(message.chat.id, 'Нажмите Меню,чтобы выйти в меню', reply_markup=markup)

#перехватим
    
@bot.callback_query_handler(func=lambda call: call.message.text == "Нажимите чтобы удалить хотелку")
def callback_inline(call):
    #удаление
    #Спрашиваем почему удаление
    #сначала удаляем фотку потом удаляем саму заявку а то нет пути к фото
    #В CALL перелается строка  вернем её в инт
    #identint = int(call.data)
    #тащим путь фотографии
    #db = sqlite3.connect(r'C:\Users\ivan\tmcone.db')
    #cursor = db.cursor()
    #cursor.execute('''SELECT photo_path FROM tmclist
    #                  WHERE ident = ?''',(identint,))
    #values = cursor.fetchone()
    ###print(values[0]) путь к фото
    #os.remove(values[0])
    #cursor = db.cursor()
    #cursor.execute('''DELETE FROM tmclist
    #                  WHERE ident = ?''',(identint,))
    #db.commit()
    #db.close()
    #bot.send_message(call.message.chat.id,"Удалена заявка с номером " + call.data)
    #теперь коллбэкнаудаление
    #print(call.data)
    keyboard = types.InlineKeyboardMarkup()
    callback_button1 = types.InlineKeyboardButton(text="ДА", callback_data=call.data+"+ДА")
    callback_button2 = types.InlineKeyboardButton(text="НЕТ", callback_data=call.data+"+НЕТ")
    keyboard.add(callback_button1,callback_button2)
    bot.send_message(call.message.chat.id,"Вы отдали хотелку?", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.message.text == "Вы отдали хотелку?")
def callback_inline(call):
    #print(call.data[call.data.find('+')+1:])
    сallregnum = call.data.split("+")[0]
    #print(сallregnum)
    #Копия для статистики
    #delcheck = call.message.text
    delcheck = call.data[call.data.find('+')+1:]
    #identint = int(call.data)
    #print(call.data.split("+")[0])
    identint = int(call.data.split("+")[0])
    db = sqlite3.connect(r'C:\Users\user\tmcone.db')
    cursor = db.cursor()
    cursor.execute('''INSERT INTO likecheckdel
                      SELECT like_name,like_tmc,like_terr,like_address,like_phone,like_tui,like_ident,like_datetime,like_terr FROM likelist
                      WHERE like_ident = ?''',(identint,))
    db.commit()
    db = sqlite3.connect(r'C:\Users\user\tmcone.db')
    cursor = db.cursor()
    cursor.execute("UPDATE likecheckdel SET like_delcheck = ? WHERE  like_ident = ? ",(delcheck,identint,))
    db.commit()
    #Удаление
    #identint = int(call.data)
    #тащим путь фотографии
    db = sqlite3.connect(r'C:\Users\user\tmcone.db')
    #cursor = db.cursor()
    #cursor.execute('''SELECT photo_path FROM tmclist
    #                  WHERE ident = ?''',(identint,))
    #values = cursor.fetchone()
    ###print(values[0]) путь к фото
    #os.remove(values[0])
    cursor = db.cursor()
    cursor.execute('''DELETE FROM likelist
                      WHERE like_ident = ?''',(identint,))
    db.commit()
    db.close()    
    bot.send_message(call.message.chat.id,"Удалена заявка с номером " + call.data)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard = True)
    markup.add('Меню'+menuback)
    bot.send_message(call.message.chat.id, 'Нажмите Меню,чтобы выйти в меню', reply_markup=markup)



















#инструкция

@bot.message_handler(commands=['help'])
@bot.message_handler(func=lambda message:'Помощь' == message.text, content_types=['text'])
def processinstr(message):
    #отправлем инструкцию
    bot.send_message(message.chat.id,"""Вас приветствует чат-бот СРБ,я предназначен для обмена ТМЦ.
    Я принимаю заявки на обмен тмц, а также ваши хотелки.
                       Внимание
                       
    !!!тмц с индентификатором передается через sap!!!
    !!!если что-то не так,шлите /start в чат!!!
    Свои пожелания можете писать разарботчику:@Hugmymind в телеграмме
    """)
    #отправлем обратно меню
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard = True)
    markup.add('Меню'+menuback)
    bot.send_message(message.chat.id, 'Нажмите Меню,чтобы выйти в меню', reply_markup=markup)

#Посмотреть что есть
@bot.message_handler(func=lambda message:message.text == 'Посмотреть что есть')
def processrightmenu(message):
    #bot.send_message(message.chat.id,"Если вы хотите передать ТМЦ - оформите заявку,если вы хотите получить ТМЦ, которого нет в списке заявок, оформите хотелку")
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard = True)
    markup.row('Просмотреть, что хотят отдать')
    markup.row('Просмотреть, что хотят найти')
    markup.row('Меню'+menuback )
    bot.send_message(message.chat.id, "Выберите:", reply_markup=markup)

#Просмотр хотелок
#Просмотреть, что хотят найти
@bot.message_handler(func=lambda message:'Просмотреть, что хотят найти' == message.text, content_types=['text'])
@bot.message_handler(func=lambda message:'Просмотр хотелок' == message.text, content_types=['text'])    
def likeprocess_pr_last(message):
    try:
        db = sqlite3.connect(r'C:\Users\user\tmcone.db')
        cursor = db.cursor()
        cursor.execute('''SELECT COUNT(*) FROM likelist''')
        values = cursor.fetchone()
        numrecord = values[0]
        if numrecord == 0:
            bot.send_message(message.chat.id,"Пока никто ничего не хочет.Станьте первым!")
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard = True)
            markup.add('Меню'+menuback)
            bot.send_message(message.chat.id, 'Нажмите Меню,чтобы выйти в меню', reply_markup=markup)
        #Теперь выводим курсор- минимальный
        cursor.execute('''SELECT * FROM likelist''')
        for row in cursor:
            #bot.send_message(message.chat.id, 'Заявка: ' + row[0] + '\nТМЦ:'+ row[1] + 'Состояние:' + row[6]   + '\nАдрес:' + row[3] + '\nТелефон:' + row[4] )
            #теперь коллбэкнаудаление
            bot.send_message(message.chat.id,'Заявка: ' + row[0] + '\nТМЦ:'+ row[1]  + '\nАдрес:' + row[3] + '\nТелефон:' + row[4])
            
        db.commit()
        db.close()
        #отправлем обратно меню
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard = True)
        markup.add('Меню'+menuback)
        bot.send_message(message.chat.id, 'Нажмите Меню,чтобы выйти в меню', reply_markup=markup)
    except Exception as e:
        process_error(message)

#Просмотреть, что хотят отдать


@bot.message_handler(func=lambda message:'Просмотреть, что хотят отдать' == message.text, content_types=['text'])  
@bot.message_handler(func=lambda message:'Просмотр заявок' == message.text, content_types=['text'])
def processcat(message):
    try:
        #отправлем обратно меню
    #    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard = True)
    #    markup.add('Меню'+menuback)
    #    bot.send_message(message.chat.id, 'Нажмите/Напишите Меню,чтобы выйти в меню', reply_markup=markup)
    #    keyboard = InlineKeyboardMarkup()
    #    keyboard.add(InlineKeyboardButton('Север', callback_data='a_1'))
    #    keyboard.add(InlineKeyboardButton('Аппарат ТБ', callback_data='b_1'))
    #    keyboard.add(InlineKeyboardButton('Тверь', callback_data='c_1'))
    #    bot.reply_to(message, 'Выберите территорию: ', reply_markup=keyboard)
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard = True)
        markup.add('ИТ+','Спец. Обор.+')
        markup.add('Мебель+','Прочее+')
        markup.row('Меню'+menuback )
        bot.send_message(message.chat.id, "Выберите:", reply_markup=markup)    
    except Exception as e:
        print(str(e))
        process_error(message)

#ИТ - i
#Спце - s
#Мебель - m
#Прочее - p


#каллбэчим каждую категорию
@bot.message_handler(func=lambda message:'ИТ+' == message.text, content_types=['text'])
def processcat(message):
    try:
        #отправлем обратно меню
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard = True)
        markup.add('Меню'+menuback)
        bot.send_message(message.chat.id, 'Нажмите/Напишите Меню,чтобы выйти в меню', reply_markup=markup)
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton('Север', callback_data='ai_1'))
        keyboard.add(InlineKeyboardButton('Аппарат ТБ', callback_data='bi_1'))
        keyboard.add(InlineKeyboardButton('Тверь', callback_data='ci_1'))
        bot.reply_to(message, 'Выберите территорию: ', reply_markup=keyboard)    
    except Exception as e:
        print(str(e))
        process_error(message)


@bot.message_handler(func=lambda message:'Спец. Обор.+' == message.text, content_types=['text'])
def processcat(message):
    try:
        #отправлем обратно меню
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard = True)
        markup.add('Меню'+menuback)
        bot.send_message(message.chat.id, 'Нажмите/Напишите Меню,чтобы выйти в меню', reply_markup=markup)
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton('Север', callback_data='as_1'))
        keyboard.add(InlineKeyboardButton('Аппарат ТБ', callback_data='bs_1'))
        keyboard.add(InlineKeyboardButton('Тверь', callback_data='cs_1'))
        bot.reply_to(message, 'Выберите территорию: ', reply_markup=keyboard)    
    except Exception as e:
        print(str(e))
        process_error(message)

@bot.message_handler(func=lambda message:'Мебель+' == message.text, content_types=['text'])
def processcat(message):
    try:
        #отправлем обратно меню
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard = True)
        markup.add('Меню'+menuback)
        bot.send_message(message.chat.id, 'Нажмите/Напишите Меню,чтобы выйти в меню', reply_markup=markup)
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton('Север', callback_data='am_1'))
        keyboard.add(InlineKeyboardButton('Аппарат ТБ', callback_data='bm_1'))
        keyboard.add(InlineKeyboardButton('Тверь', callback_data='cm_1'))
        bot.reply_to(message, 'Выберите территорию: ', reply_markup=keyboard)    
    except Exception as e:
        print(str(e))
        process_error(message)

@bot.message_handler(func=lambda message:'Прочее+' == message.text, content_types=['text'])
def processcat(message):
    try:
        #отправлем обратно меню
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard = True)
        markup.add('Меню'+menuback)
        bot.send_message(message.chat.id, 'Нажмите/Напишите Меню,чтобы выйти в меню', reply_markup=markup)
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton('Север', callback_data='ap_1'))
        keyboard.add(InlineKeyboardButton('Аппарат ТБ', callback_data='bp_1'))
        keyboard.add(InlineKeyboardButton('Тверь', callback_data='cp_1'))
        bot.reply_to(message, 'Выберите территорию: ', reply_markup=keyboard)    
    except Exception as e:
        print(str(e))
        process_error(message)

#КОЛБЕЧИМ

@bot.callback_query_handler(func=lambda x: re.search(r'ci_([0-9])+', x.data) is not None)
def search_by_title(callback: CallbackQuery):  # search books by title
    msg = callback.message
    conn = sqlite3.connect(r"C:\Users\user\tmcone.db")
    cursor = conn.cursor()
    #cursor.execute("SELECT Ссылканаавито,Номер FROM chatbot")
    #cursor.execute('''SELECT Ссылканаавито,Номер FROM chatbot
    #                  WHERE Регион = ?''',("Юг",))
    cursor.execute('''SELECT * FROM tmclist
                    WHERE territory = ?  and category = ?''', ("Тверь","ИТ",))

    #cursor.execute('''SELECT Ссылканаавито FROM chatbot
     #                     WHERE Регион = ? and Типобъекта = ?''', ("Калуга","Здание",))
    # Получаем результат сделанного запроса
    books = cursor.fetchall()
    conn.close()
    if books ==[]:
        bot.edit_message_text('Пока ничего нет.Сделайте запрос на оснащение', chat_id=msg.chat.id, message_id=msg.message_id)
        return
    bot.send_chat_action(msg.chat.id, 'typing')
    try:
        _, page = callback.data.split('_')
        #page = callback.data.split('_')
    except ValueError as err:
        print('ошибка')
        return
    page = int(page)
    if len(books) % ELEMENTS_ON_PAGE == 0:
        page_max = len(books) // ELEMENTS_ON_PAGE
    else:
        page_max = len(books) // ELEMENTS_ON_PAGE + 1
    msg_text = ''
    msg_text += f'<code>Страница {page}/{page_max}</code>'
    for book in books[ELEMENTS_ON_PAGE * (page - 1):ELEMENTS_ON_PAGE * page]:
        msg_text += '\nВаша заявка: ' + book[0] + '\nТМЦ:' + book[1] + '\nТерритория:' + book[2] + '\nАдрес:' + book[3] + '\nТелефон:' + book[4] + '\nСостояние:' + book[6]
        #msg_text += '<a href="'+book[0]+'">'+book[0]+'</a>\n'
        
    #msg_text += f'<code>Страница {page}/{page_max}</code>'    
    keyboard = get_keyboard(page, page_max, 'ci',book[5])
    if keyboard:
        bot.edit_message_text(msg_text, chat_id=msg.chat.id,disable_web_page_preview=False, message_id=msg.message_id, parse_mode='HTML',
                              reply_markup=keyboard)
    else:
        bot.edit_message_text(msg_text, chat_id=msg.chat.id,disable_web_page_preview=False, message_id=msg.message_id, parse_mode='HTML')

@bot.callback_query_handler(func=lambda x: re.search(r'cs_([0-9])+', x.data) is not None)
def search_by_title(callback: CallbackQuery):  # search books by title
    msg = callback.message
    conn = sqlite3.connect(r"C:\Users\user\tmcone.db")
    cursor = conn.cursor()
    #cursor.execute("SELECT Ссылканаавито,Номер FROM chatbot")
    #cursor.execute('''SELECT Ссылканаавито,Номер FROM chatbot
    #                  WHERE Регион = ?''',("Юг",))
    cursor.execute('''SELECT * FROM tmclist
                    WHERE territory = ?  and category = ?''', ("Тверь","Спец. Обор.",))

    #cursor.execute('''SELECT Ссылканаавито FROM chatbot
     #                     WHERE Регион = ? and Типобъекта = ?''', ("Калуга","Здание",))
    # Получаем результат сделанного запроса
    books = cursor.fetchall()
    conn.close()
    if books ==[]:
        bot.edit_message_text('Пока ничего нет.Сделайте запрос на оснащение', chat_id=msg.chat.id, message_id=msg.message_id)
        return
    bot.send_chat_action(msg.chat.id, 'typing')
    try:
        _, page = callback.data.split('_')
        #page = callback.data.split('_')
    except ValueError as err:
        print('ошибка')
        return
    page = int(page)
    if len(books) % ELEMENTS_ON_PAGE == 0:
        page_max = len(books) // ELEMENTS_ON_PAGE
    else:
        page_max = len(books) // ELEMENTS_ON_PAGE + 1
    msg_text = ''
    msg_text += f'<code>Страница {page}/{page_max}</code>'
    for book in books[ELEMENTS_ON_PAGE * (page - 1):ELEMENTS_ON_PAGE * page]:
        msg_text += '\nВаша заявка: ' + book[0] + '\nТМЦ:' + book[1] + '\nТерритория:' + book[2] + '\nАдрес:' + book[3] + '\nТелефон:' + book[4] + '\nСостояние:' + book[6]
        #msg_text += '<a href="'+book[0]+'">'+book[0]+'</a>\n'
        
    #msg_text += f'<code>Страница {page}/{page_max}</code>'    
    keyboard = get_keyboard(page, page_max, 'cs',book[5])
    if keyboard:
        bot.edit_message_text(msg_text, chat_id=msg.chat.id,disable_web_page_preview=False, message_id=msg.message_id, parse_mode='HTML',
                              reply_markup=keyboard)
    else:
        bot.edit_message_text(msg_text, chat_id=msg.chat.id,disable_web_page_preview=False, message_id=msg.message_id, parse_mode='HTML')


@bot.callback_query_handler(func=lambda x: re.search(r'cm_([0-9])+', x.data) is not None)
def search_by_title(callback: CallbackQuery):  # search books by title
    msg = callback.message
    conn = sqlite3.connect(r"C:\Users\user\tmcone.db")
    cursor = conn.cursor()
    #cursor.execute("SELECT Ссылканаавито,Номер FROM chatbot")
    #cursor.execute('''SELECT Ссылканаавито,Номер FROM chatbot
    #                  WHERE Регион = ?''',("Юг",))
    cursor.execute('''SELECT * FROM tmclist
                    WHERE territory = ?  and category = ?''', ("Тверь","Мебель",))

    #cursor.execute('''SELECT Ссылканаавито FROM chatbot
     #                     WHERE Регион = ? and Типобъекта = ?''', ("Калуга","Здание",))
    # Получаем результат сделанного запроса
    books = cursor.fetchall()
    conn.close()
    if books ==[]:
        bot.edit_message_text('Пока ничего нет.Сделайте запрос на оснащение', chat_id=msg.chat.id, message_id=msg.message_id)
        return
    bot.send_chat_action(msg.chat.id, 'typing')
    try:
        _, page = callback.data.split('_')
        #page = callback.data.split('_')
    except ValueError as err:
        print('ошибка')
        return
    page = int(page)
    if len(books) % ELEMENTS_ON_PAGE == 0:
        page_max = len(books) // ELEMENTS_ON_PAGE
    else:
        page_max = len(books) // ELEMENTS_ON_PAGE + 1
    msg_text = ''
    msg_text += f'<code>Страница {page}/{page_max}</code>'
    for book in books[ELEMENTS_ON_PAGE * (page - 1):ELEMENTS_ON_PAGE * page]:
        msg_text += '\nВаша заявка: ' + book[0] + '\nТМЦ:' + book[1] + '\nТерритория:' + book[2] + '\nАдрес:' + book[3] + '\nТелефон:' + book[4] + '\nСостояние:' + book[6]
        #msg_text += '<a href="'+book[0]+'">'+book[0]+'</a>\n'
        
    #msg_text += f'<code>Страница {page}/{page_max}</code>'    
    keyboard = get_keyboard(page, page_max, 'cm',book[5])
    if keyboard:
        bot.edit_message_text(msg_text, chat_id=msg.chat.id,disable_web_page_preview=False, message_id=msg.message_id, parse_mode='HTML',
                              reply_markup=keyboard)
    else:
        bot.edit_message_text(msg_text, chat_id=msg.chat.id,disable_web_page_preview=False, message_id=msg.message_id, parse_mode='HTML')


@bot.callback_query_handler(func=lambda x: re.search(r'cp_([0-9])+', x.data) is not None)
def search_by_title(callback: CallbackQuery):  # search books by title
    msg = callback.message
    conn = sqlite3.connect(r"C:\Users\user\tmcone.db")
    cursor = conn.cursor()
    #cursor.execute("SELECT Ссылканаавито,Номер FROM chatbot")
    #cursor.execute('''SELECT Ссылканаавито,Номер FROM chatbot
    #                  WHERE Регион = ?''',("Юг",))
    cursor.execute('''SELECT * FROM tmclist
                    WHERE territory = ?  and category = ?''', ("Тверь","Прочее",))

    #cursor.execute('''SELECT Ссылканаавито FROM chatbot
     #                     WHERE Регион = ? and Типобъекта = ?''', ("Калуга","Здание",))
    # Получаем результат сделанного запроса
    books = cursor.fetchall()
    conn.close()
    if books ==[]:
        bot.edit_message_text('Пока ничего нет.Сделайте запрос на оснащение', chat_id=msg.chat.id, message_id=msg.message_id)
        return
    bot.send_chat_action(msg.chat.id, 'typing')
    try:
        _, page = callback.data.split('_')
        #page = callback.data.split('_')
    except ValueError as err:
        print('ошибка')
        return
    page = int(page)
    if len(books) % ELEMENTS_ON_PAGE == 0:
        page_max = len(books) // ELEMENTS_ON_PAGE
    else:
        page_max = len(books) // ELEMENTS_ON_PAGE + 1
    msg_text = ''
    msg_text += f'<code>Страница {page}/{page_max}</code>'
    for book in books[ELEMENTS_ON_PAGE * (page - 1):ELEMENTS_ON_PAGE * page]:
        msg_text += '\nВаша заявка: ' + book[0] + '\nТМЦ:' + book[1] + '\nТерритория:' + book[2] + '\nАдрес:' + book[3] + '\nТелефон:' + book[4] + '\nСостояние:' + book[6]
        #msg_text += '<a href="'+book[0]+'">'+book[0]+'</a>\n'
        
    #msg_text += f'<code>Страница {page}/{page_max}</code>'    
    keyboard = get_keyboard(page, page_max, 'cp',book[5])
    if keyboard:
        bot.edit_message_text(msg_text, chat_id=msg.chat.id,disable_web_page_preview=False, message_id=msg.message_id, parse_mode='HTML',
                              reply_markup=keyboard)
    else:
        bot.edit_message_text(msg_text, chat_id=msg.chat.id,disable_web_page_preview=False, message_id=msg.message_id, parse_mode='HTML')



@bot.callback_query_handler(func=lambda x: re.search(r'ai_([0-9])+', x.data) is not None)
def search_by_title(callback: CallbackQuery):  # search books by title
    msg = callback.message
    conn = sqlite3.connect(r"C:\Users\user\tmcone.db")
    cursor = conn.cursor()
    #cursor.execute("SELECT Ссылканаавито,Номер FROM chatbot")
    #cursor.execute('''SELECT Ссылканаавито,Номер FROM chatbot
    #                  WHERE Регион = ?''',("Юг",))
    cursor.execute('''SELECT * FROM tmclist
                    WHERE territory = ?  and category = ?''', ("Север","ИТ",))

    #cursor.execute('''SELECT Ссылканаавито FROM chatbot
     #                     WHERE Регион = ? and Типобъекта = ?''', ("Калуга","Здание",))
    # Получаем результат сделанного запроса
    books = cursor.fetchall()
    conn.close()
    if books ==[]:
        bot.edit_message_text('Пока ничего нет.Сделайте запрос на оснащение', chat_id=msg.chat.id, message_id=msg.message_id)
        return
    bot.send_chat_action(msg.chat.id, 'typing')
    try:
        _, page = callback.data.split('_')
        #page = callback.data.split('_')
    except ValueError as err:
        print('ошибка')
        return
    page = int(page)
    if len(books) % ELEMENTS_ON_PAGE == 0:
        page_max = len(books) // ELEMENTS_ON_PAGE
    else:
        page_max = len(books) // ELEMENTS_ON_PAGE + 1
    msg_text = ''
    msg_text += f'<code>Страница {page}/{page_max}</code>'
    for book in books[ELEMENTS_ON_PAGE * (page - 1):ELEMENTS_ON_PAGE * page]:
        msg_text += '\nВаша заявка: ' + book[0] + '\nТМЦ:' + book[1] + '\nТерритория:' + book[2] + '\nАдрес:' + book[3] + '\nТелефон:' + book[4] + '\nСостояние:' + book[6]
        #msg_text += '<a href="'+book[0]+'">'+book[0]+'</a>\n'
        
    #msg_text += f'<code>Страница {page}/{page_max}</code>'    
    keyboard = get_keyboard(page, page_max, 'ai',book[5])
    if keyboard:
        bot.edit_message_text(msg_text, chat_id=msg.chat.id,disable_web_page_preview=False, message_id=msg.message_id, parse_mode='HTML',
                              reply_markup=keyboard)
    else:
        bot.edit_message_text(msg_text, chat_id=msg.chat.id,disable_web_page_preview=False, message_id=msg.message_id, parse_mode='HTML')

@bot.callback_query_handler(func=lambda x: re.search(r'as_([0-9])+', x.data) is not None)
def search_by_title(callback: CallbackQuery):  # search books by title
    msg = callback.message
    conn = sqlite3.connect(r"C:\Users\user\tmcone.db")
    cursor = conn.cursor()
    #cursor.execute("SELECT Ссылканаавито,Номер FROM chatbot")
    #cursor.execute('''SELECT Ссылканаавито,Номер FROM chatbot
    #                  WHERE Регион = ?''',("Юг",))
    cursor.execute('''SELECT * FROM tmclist
                    WHERE territory = ?  and category = ?''', ("Север","Спец. Обор.",))

    #cursor.execute('''SELECT Ссылканаавито FROM chatbot
     #                     WHERE Регион = ? and Типобъекта = ?''', ("Калуга","Здание",))
    # Получаем результат сделанного запроса
    books = cursor.fetchall()
    conn.close()
    if books ==[]:
        bot.edit_message_text('Пока ничего нет.Сделайте запрос на оснащение', chat_id=msg.chat.id, message_id=msg.message_id)
        return
    bot.send_chat_action(msg.chat.id, 'typing')
    try:
        _, page = callback.data.split('_')
        #page = callback.data.split('_')
    except ValueError as err:
        print('ошибка')
        return
    page = int(page)
    if len(books) % ELEMENTS_ON_PAGE == 0:
        page_max = len(books) // ELEMENTS_ON_PAGE
    else:
        page_max = len(books) // ELEMENTS_ON_PAGE + 1
    msg_text = ''
    msg_text += f'<code>Страница {page}/{page_max}</code>'
    for book in books[ELEMENTS_ON_PAGE * (page - 1):ELEMENTS_ON_PAGE * page]:
        msg_text += '\nВаша заявка: ' + book[0] + '\nТМЦ:' + book[1] + '\nТерритория:' + book[2] + '\nАдрес:' + book[3] + '\nТелефон:' + book[4] + '\nСостояние:' + book[6]
        #msg_text += '<a href="'+book[0]+'">'+book[0]+'</a>\n'
        
    #msg_text += f'<code>Страница {page}/{page_max}</code>'    
    keyboard = get_keyboard(page, page_max, 'as',book[5])
    if keyboard:
        bot.edit_message_text(msg_text, chat_id=msg.chat.id,disable_web_page_preview=False, message_id=msg.message_id, parse_mode='HTML',
                              reply_markup=keyboard)
    else:
        bot.edit_message_text(msg_text, chat_id=msg.chat.id,disable_web_page_preview=False, message_id=msg.message_id, parse_mode='HTML')


@bot.callback_query_handler(func=lambda x: re.search(r'am_([0-9])+', x.data) is not None)
def search_by_title(callback: CallbackQuery):  # search books by title
    msg = callback.message
    conn = sqlite3.connect(r"C:\Users\user\tmcone.db")
    cursor = conn.cursor()
    #cursor.execute("SELECT Ссылканаавито,Номер FROM chatbot")
    #cursor.execute('''SELECT Ссылканаавито,Номер FROM chatbot
    #                  WHERE Регион = ?''',("Юг",))
    cursor.execute('''SELECT * FROM tmclist
                    WHERE territory = ?  and category = ?''', ("Север","Мебель",))

    #cursor.execute('''SELECT Ссылканаавито FROM chatbot
     #                     WHERE Регион = ? and Типобъекта = ?''', ("Калуга","Здание",))
    # Получаем результат сделанного запроса
    books = cursor.fetchall()
    conn.close()
    if books ==[]:
        bot.edit_message_text('Пока ничего нет.Сделайте запрос на оснащение', chat_id=msg.chat.id, message_id=msg.message_id)
        return
    bot.send_chat_action(msg.chat.id, 'typing')
    try:
        _, page = callback.data.split('_')
        #page = callback.data.split('_')
    except ValueError as err:
        print('ошибка')
        return
    page = int(page)
    if len(books) % ELEMENTS_ON_PAGE == 0:
        page_max = len(books) // ELEMENTS_ON_PAGE
    else:
        page_max = len(books) // ELEMENTS_ON_PAGE + 1
    msg_text = ''
    msg_text += f'<code>Страница {page}/{page_max}</code>'
    for book in books[ELEMENTS_ON_PAGE * (page - 1):ELEMENTS_ON_PAGE * page]:
        msg_text += '\nВаша заявка: ' + book[0] + '\nТМЦ:' + book[1] + '\nТерритория:' + book[2] + '\nАдрес:' + book[3] + '\nТелефон:' + book[4] + '\nСостояние:' + book[6]
        #msg_text += '<a href="'+book[0]+'">'+book[0]+'</a>\n'
        
    #msg_text += f'<code>Страница {page}/{page_max}</code>'    
    keyboard = get_keyboard(page, page_max, 'am',book[5])
    if keyboard:
        bot.edit_message_text(msg_text, chat_id=msg.chat.id,disable_web_page_preview=False, message_id=msg.message_id, parse_mode='HTML',
                              reply_markup=keyboard)
    else:
        bot.edit_message_text(msg_text, chat_id=msg.chat.id,disable_web_page_preview=False, message_id=msg.message_id, parse_mode='HTML')


@bot.callback_query_handler(func=lambda x: re.search(r'ap_([0-9])+', x.data) is not None)
def search_by_title(callback: CallbackQuery):  # search books by title
    msg = callback.message
    conn = sqlite3.connect(r"C:\Users\user\tmcone.db")
    cursor = conn.cursor()
    #cursor.execute("SELECT Ссылканаавито,Номер FROM chatbot")
    #cursor.execute('''SELECT Ссылканаавито,Номер FROM chatbot
    #                  WHERE Регион = ?''',("Юг",))
    cursor.execute('''SELECT * FROM tmclist
                    WHERE territory = ?  and category = ?''', ("Север","Прочее",))

    #cursor.execute('''SELECT Ссылканаавито FROM chatbot
     #                     WHERE Регион = ? and Типобъекта = ?''', ("Калуга","Здание",))
    # Получаем результат сделанного запроса
    books = cursor.fetchall()
    conn.close()
    if books ==[]:
        bot.edit_message_text('Пока ничего нет.Сделайте запрос на оснащение', chat_id=msg.chat.id, message_id=msg.message_id)
        return
    bot.send_chat_action(msg.chat.id, 'typing')
    try:
        _, page = callback.data.split('_')
        #page = callback.data.split('_')
    except ValueError as err:
        print('ошибка')
        return
    page = int(page)
    if len(books) % ELEMENTS_ON_PAGE == 0:
        page_max = len(books) // ELEMENTS_ON_PAGE
    else:
        page_max = len(books) // ELEMENTS_ON_PAGE + 1
    msg_text = ''
    msg_text += f'<code>Страница {page}/{page_max}</code>'
    for book in books[ELEMENTS_ON_PAGE * (page - 1):ELEMENTS_ON_PAGE * page]:
        msg_text += '\nВаша заявка: ' + book[0] + '\nТМЦ:' + book[1] + '\nТерритория:' + book[2] + '\nАдрес:' + book[3] + '\nТелефон:' + book[4] + '\nСостояние:' + book[6]
        #msg_text += '<a href="'+book[0]+'">'+book[0]+'</a>\n'
        
    #msg_text += f'<code>Страница {page}/{page_max}</code>'    
    keyboard = get_keyboard(page, page_max, 'ap',book[5])
    if keyboard:
        bot.edit_message_text(msg_text, chat_id=msg.chat.id,disable_web_page_preview=False, message_id=msg.message_id, parse_mode='HTML',
                              reply_markup=keyboard)
    else:
        bot.edit_message_text(msg_text, chat_id=msg.chat.id,disable_web_page_preview=False, message_id=msg.message_id, parse_mode='HTML')



@bot.callback_query_handler(func=lambda x: re.search(r'bi_([0-9])+', x.data) is not None)
def search_by_title(callback: CallbackQuery):  # search books by title
    msg = callback.message
    conn = sqlite3.connect(r"C:\Users\user\tmcone.db")
    cursor = conn.cursor()
    #cursor.execute("SELECT Ссылканаавито,Номер FROM chatbot")
    #cursor.execute('''SELECT Ссылканаавито,Номер FROM chatbot
    #                  WHERE Регион = ?''',("Юг",))
    cursor.execute('''SELECT * FROM tmclist
                    WHERE territory = ?  and category = ?''', ("Аппарат ТБ","ИТ",))

    #cursor.execute('''SELECT Ссылканаавито FROM chatbot
     #                     WHERE Регион = ? and Типобъекта = ?''', ("Калуга","Здание",))
    # Получаем результат сделанного запроса
    books = cursor.fetchall()
    conn.close()
    if books ==[]:
        bot.edit_message_text('Пока ничего нет.Сделайте запрос на оснащение', chat_id=msg.chat.id, message_id=msg.message_id)
        return
    bot.send_chat_action(msg.chat.id, 'typing')
    try:
        _, page = callback.data.split('_')
        #page = callback.data.split('_')
    except ValueError as err:
        print('ошибка')
        return
    page = int(page)
    if len(books) % ELEMENTS_ON_PAGE == 0:
        page_max = len(books) // ELEMENTS_ON_PAGE
    else:
        page_max = len(books) // ELEMENTS_ON_PAGE + 1
    msg_text = ''
    msg_text += f'<code>Страница {page}/{page_max}</code>'
    for book in books[ELEMENTS_ON_PAGE * (page - 1):ELEMENTS_ON_PAGE * page]:
        msg_text += '\nВаша заявка: ' + book[0] + '\nТМЦ:' + book[1] + '\nТерритория:' + book[2] + '\nАдрес:' + book[3] + '\nТелефон:' + book[4] + '\nСостояние:' + book[6]
        #msg_text += '<a href="'+book[0]+'">'+book[0]+'</a>\n'
        
    #msg_text += f'<code>Страница {page}/{page_max}</code>'    
    keyboard = get_keyboard(page, page_max, 'bi',book[5])
    if keyboard:
        bot.edit_message_text(msg_text, chat_id=msg.chat.id,disable_web_page_preview=False, message_id=msg.message_id, parse_mode='HTML',
                              reply_markup=keyboard)
    else:
        bot.edit_message_text(msg_text, chat_id=msg.chat.id,disable_web_page_preview=False, message_id=msg.message_id, parse_mode='HTML')

@bot.callback_query_handler(func=lambda x: re.search(r'bs_([0-9])+', x.data) is not None)
def search_by_title(callback: CallbackQuery):  # search books by title
    msg = callback.message
    conn = sqlite3.connect(r"C:\Users\user\tmcone.db")
    cursor = conn.cursor()
    #cursor.execute("SELECT Ссылканаавито,Номер FROM chatbot")
    #cursor.execute('''SELECT Ссылканаавито,Номер FROM chatbot
    #                  WHERE Регион = ?''',("Юг",))
    cursor.execute('''SELECT * FROM tmclist
                    WHERE territory = ?  and category = ?''', ("Аппарат ТБ","Спец. Обор.",))

    #cursor.execute('''SELECT Ссылканаавито FROM chatbot
     #                     WHERE Регион = ? and Типобъекта = ?''', ("Калуга","Здание",))
    # Получаем результат сделанного запроса
    books = cursor.fetchall()
    conn.close()
    if books ==[]:
        bot.edit_message_text('Пока ничего нет.Сделайте запрос на оснащение', chat_id=msg.chat.id, message_id=msg.message_id)
        return
    bot.send_chat_action(msg.chat.id, 'typing')
    try:
        _, page = callback.data.split('_')
        #page = callback.data.split('_')
    except ValueError as err:
        print('ошибка')
        return
    page = int(page)
    if len(books) % ELEMENTS_ON_PAGE == 0:
        page_max = len(books) // ELEMENTS_ON_PAGE
    else:
        page_max = len(books) // ELEMENTS_ON_PAGE + 1
    msg_text = ''
    msg_text += f'<code>Страница {page}/{page_max}</code>'
    for book in books[ELEMENTS_ON_PAGE * (page - 1):ELEMENTS_ON_PAGE * page]:
        msg_text += '\nВаша заявка: ' + book[0] + '\nТМЦ:' + book[1] + '\nТерритория:' + book[2] + '\nАдрес:' + book[3] + '\nТелефон:' + book[4] + '\nСостояние:' + book[6]
        #msg_text += '<a href="'+book[0]+'">'+book[0]+'</a>\n'
        
    #msg_text += f'<code>Страница {page}/{page_max}</code>'    
    keyboard = get_keyboard(page, page_max, 'bs',book[5])
    if keyboard:
        bot.edit_message_text(msg_text, chat_id=msg.chat.id,disable_web_page_preview=False, message_id=msg.message_id, parse_mode='HTML',
                              reply_markup=keyboard)
    else:
        bot.edit_message_text(msg_text, chat_id=msg.chat.id,disable_web_page_preview=False, message_id=msg.message_id, parse_mode='HTML')


@bot.callback_query_handler(func=lambda x: re.search(r'bm_([0-9])+', x.data) is not None)
def search_by_title(callback: CallbackQuery):  # search books by title
    msg = callback.message
    conn = sqlite3.connect(r"C:\Users\user\tmcone.db")
    cursor = conn.cursor()
    #cursor.execute("SELECT Ссылканаавито,Номер FROM chatbot")
    #cursor.execute('''SELECT Ссылканаавито,Номер FROM chatbot
    #                  WHERE Регион = ?''',("Юг",))
    cursor.execute('''SELECT * FROM tmclist
                    WHERE territory = ?  and category = ?''', ("Аппарат ТБ","Мебель",))

    #cursor.execute('''SELECT Ссылканаавито FROM chatbot
     #                     WHERE Регион = ? and Типобъекта = ?''', ("Калуга","Здание",))
    # Получаем результат сделанного запроса
    books = cursor.fetchall()
    conn.close()
    if books ==[]:
        bot.edit_message_text('Пока ничего нет.Сделайте запрос на оснащение', chat_id=msg.chat.id, message_id=msg.message_id)
        return
    bot.send_chat_action(msg.chat.id, 'typing')
    try:
        _, page = callback.data.split('_')
        #page = callback.data.split('_')
    except ValueError as err:
        print('ошибка')
        return
    page = int(page)
    if len(books) % ELEMENTS_ON_PAGE == 0:
        page_max = len(books) // ELEMENTS_ON_PAGE
    else:
        page_max = len(books) // ELEMENTS_ON_PAGE + 1
    msg_text = ''
    msg_text += f'<code>Страница {page}/{page_max}</code>'
    for book in books[ELEMENTS_ON_PAGE * (page - 1):ELEMENTS_ON_PAGE * page]:
        msg_text += '\nВаша заявка: ' + book[0] + '\nТМЦ:' + book[1] + '\nТерритория:' + book[2] + '\nАдрес:' + book[3] + '\nТелефон:' + book[4] + '\nСостояние:' + book[6]
        #msg_text += '<a href="'+book[0]+'">'+book[0]+'</a>\n'
        
    #msg_text += f'<code>Страница {page}/{page_max}</code>'    
    keyboard = get_keyboard(page, page_max, 'bm',book[5])
    if keyboard:
        bot.edit_message_text(msg_text, chat_id=msg.chat.id,disable_web_page_preview=False, message_id=msg.message_id, parse_mode='HTML',
                              reply_markup=keyboard)
    else:
        bot.edit_message_text(msg_text, chat_id=msg.chat.id,disable_web_page_preview=False, message_id=msg.message_id, parse_mode='HTML')


@bot.callback_query_handler(func=lambda x: re.search(r'bp_([0-9])+', x.data) is not None)
def search_by_title(callback: CallbackQuery):  # search books by title
    msg = callback.message
    conn = sqlite3.connect(r"C:\Users\user\tmcone.db")
    cursor = conn.cursor()
    #cursor.execute("SELECT Ссылканаавито,Номер FROM chatbot")
    #cursor.execute('''SELECT Ссылканаавито,Номер FROM chatbot
    #                  WHERE Регион = ?''',("Юг",))
    cursor.execute('''SELECT * FROM tmclist
                    WHERE territory = ?  and category = ?''', ("Аппарат ТБ","Прочее",))

    #cursor.execute('''SELECT Ссылканаавито FROM chatbot
     #                     WHERE Регион = ? and Типобъекта = ?''', ("Калуга","Здание",))
    # Получаем результат сделанного запроса
    books = cursor.fetchall()
    conn.close()
    if books ==[]:
        bot.edit_message_text('Пока ничего нет.Сделайте запрос на оснащение', chat_id=msg.chat.id, message_id=msg.message_id)
        return
    bot.send_chat_action(msg.chat.id, 'typing')
    try:
        _, page = callback.data.split('_')
        #page = callback.data.split('_')
    except ValueError as err:
        print('ошибка')
        return
    page = int(page)
    if len(books) % ELEMENTS_ON_PAGE == 0:
        page_max = len(books) // ELEMENTS_ON_PAGE
    else:
        page_max = len(books) // ELEMENTS_ON_PAGE + 1
    msg_text = ''
    msg_text += f'<code>Страница {page}/{page_max}</code>'
    for book in books[ELEMENTS_ON_PAGE * (page - 1):ELEMENTS_ON_PAGE * page]:
        msg_text += '\nВаша заявка: ' + book[0] + '\nТМЦ:' + book[1] + '\nТерритория:' + book[2] + '\nАдрес:' + book[3] + '\nТелефон:' + book[4] + '\nСостояние:' + book[6]
        #msg_text += '<a href="'+book[0]+'">'+book[0]+'</a>\n'
        
    #msg_text += f'<code>Страница {page}/{page_max}</code>'    
    keyboard = get_keyboard(page, page_max, 'bp',book[5])
    if keyboard:
        bot.edit_message_text(msg_text, chat_id=msg.chat.id,disable_web_page_preview=False, message_id=msg.message_id, parse_mode='HTML',
                              reply_markup=keyboard)
    else:
        bot.edit_message_text(msg_text, chat_id=msg.chat.id,disable_web_page_preview=False, message_id=msg.message_id, parse_mode='HTML')









def get_keyboard(page: int, pages: int, t: str, photop: str) -> InlineKeyboardMarkup or None:  # make keyboard for current page
    if pages == 1:
        return None
    keyboard = InlineKeyboardMarkup()
    row = []
    if page == 1:
        row.append(InlineKeyboardButton('≻', callback_data=f'{t}_2'))
        if pages >= BOOKS_CHANGER:
            next_l = min(pages, page + BOOKS_CHANGER)
            row.append(InlineKeyboardButton(f'{next_l} >>',
                                            callback_data=f'{t}_{next_l}'))
        keyboard.row(*row)
    elif page == pages:
        if pages >= BOOKS_CHANGER:
            previous_l = max(1, page - BOOKS_CHANGER)
            row.append(InlineKeyboardButton(f'<< {previous_l}',
                                            callback_data=f'{t}_{previous_l}'))
        row.append(InlineKeyboardButton('<', callback_data=f'{t}_{pages-1}'))
        keyboard.row(*row)
    else:
        if pages >= BOOKS_CHANGER:
            next_l = min(pages, page + BOOKS_CHANGER)
            previous_l = max(1, page - BOOKS_CHANGER)

            if previous_l != page - 1:
                row.append(InlineKeyboardButton(f'<< {previous_l}',
                                                callback_data=f'{t}_{previous_l}'))

            row.append(InlineKeyboardButton('<', callback_data=f'{t}_{page-1}'))
            row.append(InlineKeyboardButton('>', callback_data=f'{t}_{page+1}'))

            if next_l != page + 1:
                row.append(InlineKeyboardButton(f'{next_l} >>',
                                                callback_data=f'{t}_{next_l}'))
            keyboard.row(*row)
        else:
            keyboard.row(InlineKeyboardButton('<', callback_data=f'{t}_{page-1}'),
                         InlineKeyboardButton('>', callback_data=f'{t}_{page+1}'))
    keyboard.add(InlineKeyboardButton('Посмотреть фото', callback_data= photop))
    return keyboard

@bot.callback_query_handler(func=lambda x: re.search(r'C:+', x.data) is not None)
def search_by_title(callback: CallbackQuery): 
    #print(callback.data)
    photo = open(callback.data, 'rb')
    bot.send_chat_action(callback.message.chat.id,'upload_photo')
    bot.send_photo(callback.message.chat.id,photo)


if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(str(e))
            #print(e.message)
            sleep(5)
            continue
            #non stop polling not looking at error
    

