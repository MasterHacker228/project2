import telebot
import requests
from bs4 import BeautifulSoup
import time 
import cv2 as cv

time_for_cooldown = 1
bot = telebot.TeleBot('token')
url = 'ip'

with open('admins.txt') as file1:
	admins = list(map(int, file1.readlines()))

with open('allowed_persons.txt') as file2:
	allowed_persons = list(map(int, file2.readlines()))

for admin in admins:
	bot.send_message(admin, 'бот включился')

def buttons(message, markup):
		if message.chat.id in admins:
			item0 = telebot.types.KeyboardButton("/start")
			item1 = telebot.types.KeyboardButton("/check_door")
			item2 = telebot.types.KeyboardButton("/check_camera")
			item3 = telebot.types.KeyboardButton("/enable_checking")
			item4 = telebot.types.KeyboardButton("/disable_checking")


			markup.add(item0)
			markup.add(item1)
			markup.add(item2)
			markup.add(item3)
			markup.add(item4)

		else:
			item6 = telebot.types.KeyboardButton("/allow_request")

			markup.add(item6)

		if message.chat.id in allowed_persons:
			item5 = telebot.types.KeyboardButton("/ring")

			markup.add(item5)


def existence(text):
	if text != None:
		return 1
	return 0

def img_shot():
	cap = cv.VideoCapture(0)
	ret, frame = cap.read()
	cv.imwrite('camera.jpg', frame) 



@bot.message_handler(commands = ["start"])
def start(message, res = False):
	
	if message.chat.id in allowed_persons:
		bot.send_message(message.chat.id, message.chat.id)
		markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
		
		buttons(message, markup)

		if message.chat.id in admins:
			bot.send_message(message.chat.id, 'Здравствуйте, напишите:  \n /check_door для просмотра непрочитанных уведомлений, \n /enable_checking для включения отслеживания \n /disable_checking для прекращения отслеживания',   reply_markup = markup)
		bot.send_message(message.chat.id, 'Здравствуйте, напишите /ring, чтобы оповестить о своем приходе')
	else:
		bot.send_message(message.chat.id, 'напишите /allow_request')


@bot.message_handler(commands = ["allow_request"])
def allow_request (message):
	if message.chat.id not in allowed_persons:
		bot.send_message(message.chat.id, "ожидайте")
		for admin in admins:
			
			print_info(message, "send_to_telegram", text = "поступил запрос на добавление в список:\n")
			bot.send_message(admin, "принять запрос?")
			markup_inline = telebot.types.InlineKeyboardMarkup()
			item10 = telebot.types.InlineKeyboardButton('yes')
			item20 = telebot.types.InlineKeyboardButton('no')
			markup_inline.add(item10)
			markup_inline.add(item20)
			bot.send_message(admin, "Принять запрос?", reply_markup = markup_inline)

			markup_inline = types.InlineKeyboardMarkup()
			item = types.InlineKeyboardButton(text='a', callback_data='test')
			markup_inline.add(item)
			client.send_message(call.message.chat.id, 'x', reply_markup=markup_inline) 
			
	else:		
		bot.send_message(message.chat.id, "Вы уже добавлены в список")


def print_info(message, mode,  text = ''):

	if existence(message.from_user.first_name):
		user_first_name = message.from_user.first_name 
	else:
		user_first_name = 'not found'

	if existence(message.from_user.last_name):
		user_last_name = message.from_user.last_name
	else:
		user_last_name = 'not found'

	if existence(message.from_user.username):
		username = message.from_user.username
	else:
		username = 'not found'

	text_to_print = f'{text}user id: {message.from_user.id } \nuser: {user_first_name} {user_last_name} \nusername: {username}'

	if mode == "send_to_telegram":
		bot.send_message(admin, text_to_print)

	if mode == "send_to_log":
		return text_to_print
	

@bot.message_handler(commands = ["ring"])
def ring(message):
	if message.chat.id in allowed_persons:
		bot.send_message(message.chat.id, 'ожидайте')
		with open("log.txt", "a") as log:
			log.write(f"knock from telegram at time: {time.ctime()}\n")
			log.write(print_info(message, "send_to_log"))
		for admin in admins:
			print_info(message, "send_to_telegram")


@bot.message_handler(commands = ["enable_checking"])
def checking(message):
	cooldown = -1
	if message.chat.id in admins:
		with open("log.txt", "a")  as log:
			while message.text != "/disable_checking":
				
				response = requests.get(url)
				soup = str(BeautifulSoup(response.text, 'lxml'))

				if "on" in soup:
					print(1)
					if  time.time() - cooldown > time_for_cooldown:
						for admin in admins:
							bot.send_message(admin, 'on')
						log.write(f"knock at time: {time.ctime()}")
						cooldown = time.time()

	else:
		bot.send_message(message.chat.id, 'напишите /allow_request')

@bot.message_handler(commands = ["check_camera"])
def camera(message):
	if message.chat.id in admins:
		img_shot()
		with open("camera.jpg", "rb") as file:
			
			bot.send_photo(message.chat.id, file)

@bot.message_handler(commands = ["check_door"])
def check_door(message):
	if message.chat.id in admins:
		with open("log.txt", "r") as file:
			bot.send_document(message.chat.id, file)
		

@bot.message_handler(content_types = ["text"])
def handle_text(message):
	if message.chat.id in allowed_persons:

		if message.text != "/disable_checking":
			bot.send_message(message.chat.id, f'Вы написали: {message.text} я не могу распознать текст')
	else:
		bot.send_message(message.chat.id, 'напишите /allow_request')


bot.polling(none_stop = True, interval = 0)

