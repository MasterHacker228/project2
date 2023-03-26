import telebot
import requests
from bs4 import BeautifulSoup
import time 

import face_recognition
import imutils
import pickle

import cv2
import os

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
	# find path of xml file containing haarcascade file 
    cascPathface = os.path.dirname(
    cv2.__file__) + "/data/haarcascade_frontalface_alt2.xml"
    # load the harcaascade in the cascade classifier
    faceCascade = cv2.CascadeClassifier(cascPathface)
    # load the known faces and embeddings saved in last file
    data = pickle.loads(open('face_enc', "rb").read())
 
    print("Streaming started")
    video_capture = cv2.VideoCapture(0)
    #    loop over frames from the video file stream

    # grab the frame from the threaded video stream
    ret, frame = video_capture.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray,
                                         scaleFactor=1.1,
                                         minNeighbors=5,
                                         minSize=(60, 60),
                                         flags=cv2.CASCADE_SCALE_IMAGE)
 
    # convert the input frame from BGR to RGB 
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # the facial embeddings for face in input
    encodings = face_recognition.face_encodings(rgb)
    names = []
    # loop over the facial embeddings incase
    # we have multiple embeddings for multiple fcaes
    for encoding in encodings:
       # Compare encodings with encodings in data["encodings"]
       # Matches contain array with boolean values and True for the embeddings it matches closely
       # and False for rest
        matches = face_recognition.compare_faces(data["encodings"],
         encoding)
        # set name =inknown if no encoding matches
        name = "Unknown"
        # check to see if we have found a match
        if True in matches:
            #Find positions at which we get True and store them
            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}
            # loop over the matched indexes and maintain a count for
            # each recognized face face
            for i in matchedIdxs:
                # Check the names at respective indexes we stored in matchedIdxs
                name = data["names"][i]
                # increase count for the name we got
                counts[name] = counts.get(name, 0) + 1
            # set name which has highest count
            name = max(counts, key=counts.get)
 
 
        # update the list of names
        names.append(name)
        # loop over the recognized faces
        for ((x, y, w, h), name) in zip(faces, names):
            # rescale the face coordinates
            # draw the predicted face name on the image
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, name, (x, y), cv2.FONT_HERSHEY_SIMPLEX,
             0.75, (0, 255, 0), 2)
    
    print(names)
    cv2.imwrite('camera.jpg', frame) 
    return names


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
		names = img_shot()
		with open("camera.jpg", "rb") as file:
			
			bot.send_photo(message.chat.id, file)
            
			for name in names:
				if name == "Unknown":
					bot.send_message(message.chat.id, "Unknown")
				else:
					bot.send_message(message.chat.id, name)

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
