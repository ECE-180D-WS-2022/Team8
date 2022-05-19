from email import message
from pickle import FALSE
#from socketserver import ThreadingUnixDatagramServer
import string
import time as t 
import paho.mqtt.client as mqtt
import threading
import ctypes
import speech_recognition as sr
import random
import numpy as np
import pygame
from pygame import movie
from pygame.locals import *
import cv2
import moviepy.editor
import glob
import re 
import math
from pathlib import Path

CONTROLLER_BUFFER = 2
FLAG_START = '01'
FLAG_CUTTING = '02'
FLAG_STIR = '03'
FLAG_ROLLING = '04'
FLAG_POURING = '05'
FLAG_SHRED = '08'
FLAG_GARNISH = '09'
STOP = '00'
SCRAMBLE = '13'
SWITCH = '14'
SCREEN_HEIGHT = 800
SCREEN_WIDTH = 1200
COUNTER = 1
CUTTING_BOARD = 2
STOVE = 3
PLATE = 4

MESSAGE = '10'

FLAG_SCORE = '99'

#BOARD POSITIONS
cutting = 3
stove = 2
#BOARD POSITIONS

##CONST GLOBALS

#globals
recipe_count = 0
position = 0    #will be 1 - counter, 2 - cutting board, 3 - stove, 4 - plating
in_cooking = 0
start = t.time()
end = t.time()
diff = end - start
last_action = 0
flag_player = 0
flag_opponent = 0
flag_received = 0
score = 0
message_received = ''
speed = 1
current_goal = 0
gamestart = 1
speech_said = False
timer_set = 0
timer_time = 0
timer_flag = 0
meh = 1
good = 2 
excellent = 3
current_images = []
current_recipe = '0'
current_ingr = '0'
#colors
backgroundColor=(255, 255, 255)
green = (2, 100,64)
black = (0,0,0)
#window
windowsize = (SCREEN_WIDTH, SCREEN_HEIGHT)
win=pygame.display.set_mode(windowsize)

#Vision processing code 
init_cal = False
x_c_1 = 0
y_c_1 = 0
x_c_2 = 0
y_c_2 = 0
counter = 0 
x_pos  = 0

#recipe declarations
all_recipes = np.empty((0,8), str)
pizza = np.array([['pizza','4','2','5t','3','5s','8','9p']])
vegetable_soup = np.array([['vegetable soup','2','2','3','5','9']])
pasta = np.array([['pasta','5p','3p','2','5t','3s','5s','9p']])
#recipe declarations

controller_speech = '0'
#globals

walk_s = 0
walk_memory = 0


#player imaging class
class Playerimg():
	def __init__(self, x, y):
		self.images_right = []
		self.images_left = []
		self.index = 0
		self.counter = 0
		for num in range(1, 5):
			img_right = pygame.image.load(f'images/chef/chef{num}.png')
			img_right = pygame.transform.scale(img_right, (300, 600))
			img_left = pygame.transform.flip(img_right, True, False)
			self.images_right.append(img_right)
			self.images_left.append(img_left)
		self.image = self.images_right[self.index]
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.vel_y = 0
		self.jumped = False
		self.direction = 0

	def update(self):
		global walk_s
		global walk_memory
		walk_s+=1
		dx = 0
		dy = 0
		walk_cooldown = 5

        #moving left
		if (self.rect.x+150 - x_pos) < -18:
			dx -= 5
			self.counter += 1
			self.direction = 1
		#moving right
		elif (self.rect.x+150 - x_pos) > 18 and x_pos >=200:
			dx += 5
			self.counter += 1
			self.direction = -1


		#print(str(self.rect.x+150) +" " + str(x_pos))
		#print(str(x_pos))
		#print('direction: '+ str(self.direction))

		#handle animation
		print(str(self.index))

		if (walk_s==3):
			if abs(walk_memory+self.rect.x+150 - x_pos)/2>9:
				self.counter = 0	
				self.index += 1
				if self.index >= len(self.images_right):
					self.index = 0
				if self.direction == 1:
					self.image = self.images_right[self.index]
				if self.direction == -1:
					self.image = self.images_left[self.index]
			elif self.index == 1 or self.index==3:
				if self.direction == 1:
					self.image = self.images_right[2]
				if self.direction == -1:
					self.image = self.images_left[2]
			walk_s=0

		#add gravity
		self.vel_y += 1
		if self.vel_y > 10:
			self.vel_y = 10
		dy += self.vel_y

		#check for collision

		#update player 
		#print(dx)
		walk_memory = self.rect.x+150 - x_pos
		self.rect.x = x_pos - 150
		self.rect.y += dy

		if self.rect.bottom > SCREEN_HEIGHT:
			self.rect.bottom = SCREEN_HEIGHT
			dy = 0
		
		win.blit(self.image, self.rect)
#player imaging class


#pygame base code

#set title on window
pygame.display.set_caption("Chopping") 

#load images
bg_img = pygame.image.load('animationPNGs/backgrounds/game_background.png')
bg_img = pygame.transform.scale(bg_img, windowsize).convert()
bg_cuttingboard = pygame.image.load('animationPNGs/backgrounds/cuttingboard.png')
bg_cuttingboard = pygame.transform.scale(bg_cuttingboard, windowsize).convert()
bg_stove = pygame.image.load('animationPNGs/backgrounds/stove.png')
bg_stove = pygame.transform.scale(bg_stove, windowsize).convert()
bg_tile = pygame.image.load('animationPNGs/backgrounds/tile.png')
bg_tile = pygame.transform.scale(bg_tile, windowsize).convert()

vs_score = pygame.image.load('images/score_page.png')
vs_score_opp = pygame.image.load('images/score_page_opp.png')

calimg = pygame.image.load('images/calibration_instructions.png')
modimg = pygame.image.load('images/game_mode_selection.png')
playimg = pygame.image.load('images/player_selection.png')

#videos
pygame.init()
pygame.mixer.quit()
intro = moviepy.editor.VideoFileClip('images/welcome_screen.mp4')
loading = moviepy.editor.VideoFileClip('images/loading_screen.mp4')
modvid = moviepy.editor.VideoFileClip('images/game_mode_selection_vid.mp4')
calvid = moviepy.editor.VideoFileClip('images/calibration_instructions_vid.mp4')
countdown = moviepy.editor.VideoFileClip('images/3_2_1.mp4')
playvid = moviepy.editor.VideoFileClip('images/player_selection_vid.mp4')
play1vid = moviepy.editor.VideoFileClip('images/player_1_selected.mp4')
play2vid = moviepy.editor.VideoFileClip('images/player_2_selected.mp4')
#videos

#fonts
#pygame.font.init()
myfont = pygame.font.SysFont('Bukhari Script.ttf', 40)
msg_plate = myfont.render('Say cheese or garnish to start', False, (0,0,0))
msg_stove = myfont.render('Say spoon to start', False, (0,0,0))
msg_cuttingboard = myfont.render('Say knife or roll to start', False, (0,0,0))
msg_counter = myfont.render('Say pour to start', False, (0,0,0))
msg_exit = myfont.render('Say exit to return', False, (0,0,0))
msg_good = myfont.render('Good job!', False, (0,0,0))
smallFont = pygame.font.SysFont('Bukhari Script.ttf', 30)
completion= smallFont.render('You have completed this task!', False, (0,0,0))
current_msg = myfont.render('Say spoon to start', False, (0,0,0))

pizza_finish = pygame.image.load('animationPNGs/finished_dishes/finished_pizza.png')
pasta_finish = pygame.image.load('animationPNGs/finished_dishes/finished_pasta.png')
#fonts           

file_pattern = re.compile(r'.*?(\d+).*?')
def get_order(file):
    match = file_pattern.match(Path(file).name)
    if not match:
        return math.inf
    return int(match.groups()[0])

def load_vid(pathname):
    global current_images
    current_graphics = sorted(glob.glob('animationPNGs/'+str(pathname) + '/*.png'),key = get_order)
    for i in current_graphics:
        current_images.append(pygame.image.load(i))
    return len(current_images)
    
#vision processing code
def track_player(frame,lower_thresh_player,upper_thresh_player):
    global x_pos
    global prev_x
    global prev_y
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # Threshold the HSV image to get colors of interest
    mask = cv2.inRange(hsv, lower_thresh_player, upper_thresh_player)
    ret,thresh = cv2.threshold(mask,127,255,0)
    res = cv2.bitwise_and(frame,frame, mask= mask)
    #from threshholding cv doc
    th3 = cv2.adaptiveThreshold(mask,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for i in contours:
        area = cv2.contourArea(i)
        if area > 4000:
            x,y,w,h = cv2.boundingRect(i)
            #print(prev_x)
            #print(x)
            #if abs(prev_x - x) <= 150:
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
            x_pos = 1200 - (x + int(w/2))*2

def get_calibration_frames(frame):
    global x_c_1
    global x_c_2
    global y_c_1
    global y_c_2
    global counter
    x_c_1 = 200
    x_c_2 = 400
    y_c_1 = 250
    y_c_2 = 495
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    cv2.rectangle(frame, (x_c_1, y_c_1), (x_c_2, y_c_2), (0, 255, 0), 3)

def calibrate(frame, x_c_1, y_c_1, x_c_2, y_c_2):
    global lower_thresh_player
    global upper_thresh_player
    global prev_x
    global prev_y
    global x_pos
    cv2.rectangle(frame, (x_c_1, y_c_1), (x_c_2, y_c_2), (0, 255, 0), 3)
    calibration_frame = frame[y_c_1:y_c_2, x_c_1:x_c_2]
    cal_hsv = cv2.cvtColor(calibration_frame, cv2.COLOR_BGR2HSV)
    x_pos = int(abs(x_c_1 - x_c_2)/2)
    h_val = cal_hsv[:,:,0]
    s_val = cal_hsv[:,:,1]
    v_val = cal_hsv[:,:,2]
    h_val.sort()
    s_val.sort()
    v_val.sort()
    #discard outliers
    (h,w) = h_val.shape
    h_low = h//8
    w_low = w//8
    h_high = h-h_low
    w_high = w-w_low
    h_val_ab = h_val[h_low:h_high,w_low:w_high]
    s_val_ab = s_val[h_low:h_high,w_low:w_high]
    v_val_ab = v_val[h_low:h_high,w_low:w_high]
    avg_h = np.average(h_val_ab)
    avg_s = np.average(s_val_ab)
    avg_v = np.average(v_val_ab)
    hsv_avg = np.array([int(avg_h),int(avg_s),int(avg_v)])
    lower_thresh_player = np.array([int(avg_h)-30,int(avg_s)-40,int(avg_v)-40])
    upper_thresh_player = np.array([int(avg_h)+30,int(avg_s)+100,int(avg_v)+100])

def calibration():
    global counter
    global lower_thresh_player
    global upper_thresh_player
    surface = pygame.display.set_mode([1200,800])
    while (True):
        ret, frame = cap.read()
        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        cv2.flip(frame, 1)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        if counter <= 301:
            get_calibration_frames(frame)
        elif counter == 302:
            print('calibrating...')
            t.sleep(1)
            calibrate(frame, x_c_1, y_c_1, x_c_2, y_c_2)
        elif counter > 302:
            print('exiting calibration...')
            return
        counter = counter+1
    # The video uses BGR colors and PyGame needs RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        surf = pygame.surfarray.make_surface(frame)
        for event in pygame.event.get():
            if event.type == pygame.KEYUP:
                background_color = red
                surface.fill(background_color)
                pygame.display.update
                end_time = self.time()
        surface.blit(calimg,(0,0))
        # Show the PyGame surface!
        surface.blit(surf, (300,300))
        pygame.display.flip()
#vision processing code

def progress_bar(current, total):
    #increment progress bar
    pygame.draw.rect(win, black, pygame.Rect(349, 820, 500, 30),2 )
    #increment progress bars
    x = round(current/total*10)
    for t in range(0,x):
        pygame.draw.rect(win, green, pygame.Rect(350+(50*t), 821, 48, 28) )

def task(action):
    global speed
    global current_images
    global timer_set
    global last_action
    global current_recipe
    global current_ingr

    #Beginning of task code
    t.sleep(CONTROLLER_BUFFER)
    timer_set = 1
    action = int(action)
    string_action = classifier(action)
    size_of_vid = 0
    current_images.clear()
    win = pygame.display.set_mode(windowsize)
    #if elif statements
    if (string_action == 'Stir'):
        if current_recipe == 'pizza':
            size_of_vid = load_vid("stir_sauce")
        elif current_recipe == 'pasta':
            if current_ingr == 'p':
                size_of_vid = load_vid("stir_pasta")
            elif current_ingr == 's':
                size_of_vid = load_vid("stir_sauce")
        current_bg = bg_stove
    elif(string_action == 'Cut'):
        if current_recipe == 'pizza':
            size_of_vid = load_vid("chop_tomato")
        elif current_recipe == 'pasta':
            size_of_vid = load_vid("chop_tomato")
        current_bg = bg_cuttingboard
    elif(string_action == 'Roll'):
        size_of_vid = load_vid("rolling_dough")
        current_bg = bg_cuttingboard
    elif(string_action == 'Pour'):
        if current_recipe == 'pizza':
            if current_ingr == 't':
                size_of_vid = load_vid("pour_tomato")
                current_bg = bg_stove
            elif current_ingr == 's':
                size_of_vid = load_vid("pour_sauce")
                current_bg = bg_tile
        elif current_recipe  == 'pasta':
            if current_ingr == 'p':
                size_of_vid = load_vid("pour_pasta")
                current_bg = bg_stove
            elif current_ingr == 's':
                size_of_vid = load_vid("pour_sauce")
                current_bg = bg_tile
            elif current_ingr == 't':
                size_of_vid = load_vid("pour_tomato")
                current_bg = bg_stove
    elif(string_action == 'Shred'):
        size_of_vid = load_vid("shred_cheese")
        current_bg = bg_tile
    elif(string_action == 'Garnish'):
        if current_recipe == 'pizza':
            if current_ingr == 'p':
                size_of_vid = load_vid("garnish_parsley")
                current_bg = bg_tile
        elif current_recipe == 'pasta':
            if current_ingr == 'p':
                size_of_vid = load_vid("garnish_parsley")
                current_bg = bg_tile
    #if elif statements
    speed = 0  #default
    #print(size_of_vid)
    win.blit(current_bg,(0,0))
    win.blit(current_images[0],(0,0))
    pygame.display.update()
    for i in range(1,size_of_vid):
        while speed == 0:
            pass #dont let it run if speed = 0
        #print('Working '+str(i))
        win.blit(current_bg,(0,0))
        win.blit(current_images[i],(0,0))
        pygame.display.update()
        t.sleep(0.1/speed)

    #ending of task code
    last_action = action
    timer_set = 0 
    return

def displayScore(score, opponent_score, feedback):
    global flag_player
    msg_score= myfont.render(str(round(score)), False, (0,0,0))
    msg_opponent = myfont.render(str(round(opponent_score)), False,(0,0,0))
    msg_feedback= myfont.render(feedback, False, (0,0,0))
    str(round(score))
    if flag_player == 3:
        win.blit(vs_score, (0,0))
    else:
        win.blit(vs_score_opp,(0,0))
    win.blit(msg_score, (900,670))
    win.blit(msg_opponent, (1000,750))
    win.blit(msg_feedback, (350,400))
    pygame.display.update()

def check_game():
    global all_recipes
    global in_cooking #trip the flag if the recipe is met
    global last_action
    global recipe_count
    global current_recipe
    length = len(all_recipes[0])
    for k in range(recipe_count):
        if all_recipes[k][0]!= '0':     #ignore your finished recipes
            for i in range(1,length):
                if all_recipes[k][i][0] != '0':      #ignore 0 bit
                    if last_action == int(all_recipes[k][i][0]):
                        all_recipes[k][i] = '0' + str(timer_time)
                        if k == recipe_count - 1 and i == length-1:
                            in_cooking = 2  #game finished ending condition
                            all_recipes[k][0] = '0'
                            if current_recipe == 'pasta':
                                win.blit(pasta_finish,(0,0))
                            elif current_recipe == 'pizza':
                                win.blit(pizza_finish,(0,0))
                            pygame.display.update()
                            t.sleep(3)
                        if i != length-1:
                            return
                    elif last_action != all_recipes[k][i]: #must do in order
                        print("Cowabummer, you did the wrong action. You need to " + classifier(int(all_recipes[k][i][0]))+ " next!")
                        return
            all_recipes[k][0] = '0'       #recipe done
            if current_recipe == 'pasta':
                win.blit(pasta_finish,(0,0))
            elif current_recipe == 'pizza':
                win.blit(pizza_finish,(0,0))
            pygame.display.update()
            t.sleep(3)
    in_cooking = 2 #game finished

def recipe_randomizer(difficulty):  #randomize all recipe's length based off of difficulty
    global all_recipes
    #length = len(all_recipes[0])
    global recipe_count
    recipe_count = 0
    if difficulty == 'hard':
        recipe_count = 5
    elif difficulty == 'normal':
        recipe_count = 4
    elif difficulty =='easy':
        recipe_count = 2
    for k in range(recipe_count):
        #print('Recipe: '+ str(k+1))
        recipe = random.randint(1,2)  #randomization, will be replaced with a shuffle command (random.shuffle())
        if recipe == 1:
            all_recipes = np.append(all_recipes, pizza, axis=0)
        elif recipe == 2:
            all_recipes = np.append(all_recipes, pasta, axis=0)
        # elif recipe == 3:
        #     all_recipes = np.append(all_recipes, pasta,axis=0)

def print_recipes():
    global all_recipes
    length = len(all_recipes[0])
    can_break = 0
    for k in range(len(all_recipes)):
        if all_recipes[k][0] != '0':
            can_break = 1
            msg_recipe = myfont.render('Recipe '+str(k+1)+ ': ' + str(all_recipes[k][0]),False,(0,0,0))
            win.blit(msg_recipe,(50,50))
            for i in range(1,length):
                msg_action = myfont.render(str(i)+'. ' + classifier(int(all_recipes[k][i][0])), False,(0,0,0))
                win.blit(msg_action,(100,50+50*i))
        if can_break == 1:
            break       #only print the next available recipe

def classifier(num):    #classify for user output
    global current_goal
    if int(num) == int(FLAG_CUTTING):
        output = 'Cut'
    elif int(num) == int(FLAG_STIR):
        output = 'Stir'
    elif int(num) == int(FLAG_ROLLING):
        output = 'Roll'
    elif int(num) == int(FLAG_POURING):
        output = 'Pour'
    elif int(num) == int(FLAG_SHRED):
        output = 'Shred'
    elif int(num) == int(FLAG_GARNISH):
        output = 'Garnish'
    elif int(num) == 0:
        output = 'DONE'
    return output

def next_action():
    global all_recipes
    global current_recipe
    global current_ingr
    length = len(all_recipes[0])
    for k in range(len(all_recipes)):
        if all_recipes[k][0] != '0':
            current_recipe = all_recipes[k][0]
            for i in range(1,length):
                if all_recipes[k][i][0] != '0':
                    if len(all_recipes[k][i]) > 1:
                        current_ingr = all_recipes[k][i][1] #dictates which vid will play
                        return
#MQTT Connections
def on_connect(client, userdata, flags, rc):
    global gamestart
    print("Connection returned result: "+str(rc))
    gamestart = rc

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print('Unexpected Disconnect')
    else:
        print('Expected Disconnect')

def sabotage(type):
    if type == 'scramble':
        client.publish(str(flag_opponent)+'Team8', str(SCRAMBLE), qos=1)
    elif type == 'switch':
        client.publich(str(flag_opponent)+'Team8', str(SWITCH), qos=1)

def on_message(client, userdata, message):
    global flag_received
    global in_cooking
    global speed
    global message_received
    global cutting
    global stove
    global speech_said
    global meh, good, excellent
    global current_recipe
    #data received as b'message'
    temporary = str(message.payload)
    message_received = temporary[4:-1]
    flag_received = temporary[2:4]
    #print(temporary)
    #print(message_received)
    #score flag received
    if (str(flag_received) == str(FLAG_STIR)):
        if int(message_received) == 1:
            speed = meh
        elif int(message_received) == 2:
            speed = good
        elif int(message_received) == 3:
            speed = excellent
    elif (str(flag_received) == str(FLAG_CUTTING)):
        if int(message_received) == 1:
            speed = meh
        elif int(message_received) == 2:
            speed = good
        elif int(message_received) == 3:
            speed = excellent
    elif (str(flag_received) == str(FLAG_POURING)):
        if int(message_received) == 1:
            speed = meh
        elif int(message_received) == 2:
            speed = good
        elif int(message_received) == 3:
            speed = excellent
    elif (str(flag_received) == str(FLAG_ROLLING)):
        if int(message_received) == 1:
            speed = meh
        elif int(message_received) == 2:
            speed = good
        elif int(message_received) == 3:
            speed = excellent
    elif (str(flag_received) == str(FLAG_SHRED)):
        if int(message_received) == 1:
            speed = meh
        elif int(message_received) == 2:
            speed = good
        elif int(message_received) == 3:
            speed = excellent
    elif (str(flag_received) == str(FLAG_GARNISH)):
        if int(message_received) == 1:
            speed = meh
        elif int(message_received) == 2:
            speed = good
        elif int(message_received) == 3:
            speed = excellent
    elif str(flag_received) == str(FLAG_SCORE):
        if in_cooking == 2:
            if 1000-float(score) > 1000-float(message_received):
                displayScore(score, float(message_received),'You are better than the other idiot sandwich. Congration.')
                #print('You are better than the other idiot sandwich. Congration.')
                #print('Your score: '+str(float(score))+'\n'+"Your opponent's score: " + str(float(message_received)))
                client.publish(str(flag_opponent)+'Team8', str(FLAG_SCORE)+str(score), qos=1)
            else:
                displayScore(score, float(message_received), 'You lost. Try a little harder next time would ya?')
                #print('You lost. Try a little harder next time would ya?')
                #print('Your score: '+str(float(score))+'\n'+"Your opponent's score: " + str(float(message_received)))
                client.publish(str(flag_opponent)+'Team8', str(FLAG_SCORE)+str(score), qos=1)
            client.loop_stop()
            client.disconnect()
    elif flag_received == str(MESSAGE):
        print(str(message_received))
    elif str(message.topic) == (str(flag_player)+'Team8C'):
        print("Receiving speech")
        f = open('receive.wav', 'wb')
        f.seek(0)
        f.write(message.payload)
        f.close()
        speech_said = True
    elif flag_received == str(SCRAMBLE):
        cutting = 2
        stove = 3
    elif flag_received == str(SWITCH):
        temp = meh
        meh = excellent
        excellent = temp

def from_speech():
    global speech_said
    r = sr.Recognizer()
    txt = '0'
    hello=sr.AudioFile('receive.wav')
    with hello as source:
        try:
            audio = r.record(source)
            s = r.recognize_google(audio)
            s = str(s)
            f = open('receive.wav','wb')
            f.truncate(0)
            speech_said = False
            print(s)
            return s.lower()
        except sr.UnknownValueError:
            txt = '0'
            speech_said = False
            return txt.lower()
        except sr.ValueError:
            txt = '0'
            speech_said = False
            return txt.lower()

def temp_speech():
    r = sr.Recognizer()
    txt = '0'
    with sr.Microphone(device_index=3) as source:
        audio = r.listen(source, phrase_time_limit = 1.25)
    try:
        txt = r.recognize_google(audio)
        txt = str(txt)
        return txt
    except sr.UnknownValueError:
        txt = '0'
        return txt
def timer(timer_type):
    global timer_set
    global timer_time
    global timer_flag
    global flag_received
    while True:
        if timer_type == 1: #space for other timer types
        #Starting a normal timer
            if timer_set == 1: #only reset timer IF timer_set is run, otherwise dont 
                index = 0
                while(timer_set!= 0):
                    t.sleep(1)
                    index = index+1
                timer_time = index
#MQTT Connections

def main():
    #####################
    #GLOBAL DECLARATIONS
    #####################
    global score
    global in_cooking
    global flag_opponent
    global flag_player
    global last_action
    global x_pos
    global position
    global timer_set
    global timer_time
    global current_msg
    global current_recipe
    global speech_said
    #####################
    #GLOBAL DECLARATIONS
    #####################
    intro.preview()

    ##################
    #CALIBRATION PHASE
    ##################
    loading.preview()
    loading.preview()
    calvid.preview()
    calibration()
    cv2.destroyAllWindows()
    ##################
    #CALIBRATION PHASE
    ##################

    ################
    #THREADING CALL
    ################
    #action_time = threading.Thread(target=timer, args=(1,), daemon=True)
    #player_mem = threading.Thread(target=track_player, daemon=True)
    #action_time.start()
    #player_mem.start()
    #both daemons will terminate upon the end of the program 
    ################
    #THREADING CALL
    ################

    ################
    #STARTING SCREEN
    ################
    '''
    txt = '0'
    modvid.preview()
    while txt.lower() != 'practice' and txt.lower() != 'competition':
        win.blit(modimg,(0,0))
        print('Say Practice to practice and Competition to play against an opponent')
        #win.blit(intro, (0,0))
        txt = temp_speech()
        if txt == 'brackets':  #common word
            txt = 'practice'
    ################
    #STARTING SCREEN
    ################

    #####################
    #WAITING FOR OPPONENT
    #####################
    if txt.lower() == 'practice':
        flag_player = 2
        client.subscribe('2Team8A', qos = 2)
    else:
        playvid.preview()
    while(flag_player == 0):
        win.blit(playimg,(0,0))
        pygame.display.update()
        #print("Which player are you playing as, Player 1 or Player 2?")
        txt = temp_speech()
        if txt.lower() == 'player one' or txt.lower() == 'player won' or txt.lower() == 'player 1':
            flag_player = 1
            flag_opponent = 2
            play1vid.preview()
        elif txt.lower() == 'player two' or txt.lower() == 'player to' or txt.lower() == 'player too' or txt.lower() == 'player 2':
            flag_player = 2
            flag_opponent = 1
            play2vid.preview()
    client.subscribe(str(flag_player)+'Team8', qos=1)
    #subscribing to mqtt to receive IMU data
    #messages must only be received once hence qos is 2
    client.subscribe(str(flag_player)+'Team8A',qos=2)
    client.subscribe(str(flag_player)+'Team8C', qos = 1)'''
    #####################
    #WAITING FOR OPPONENT
    #####################

    loading.preview()
    start_game = t.time()
    print('Randomizing Recipes: ')
    recipe_randomizer('easy') 

    ####################
    #PLAYER LOCALIZATION
    ####################
    while(in_cooking != 2):
        clock = pygame.time.Clock()
        fps = 60
        playerimg = Playerimg(100, 900 - 130)
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Cooking Papa 2.0')
        speech_said = False
            
        while True:
            ret, frame = cap.read()
            frame = cv2.flip(frame,0)
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            track_player(frame, lower_thresh_player, upper_thresh_player)
            #define game variables
            clock.tick(fps)
            screen.blit(bg_img, (0, 0))
            playerimg.update()
           # screen.blit(playerimg.image, playerimg.rect)
            print_recipes()
            pygame.display.update()
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                #will only trigger/pause the code if speech is detected to have been said
            if speech_said == True:
                txt = from_speech()
                if "o" in txt:
                    txt = 'go'
                if txt == 'go' or txt == 'no':
                    if x_pos > 900:
                        position = COUNTER
                        cv2.destroyAllWindows()
                        in_cooking = 1
                        break
                    elif x_pos > 600 and x_pos < 900:
                        position = CUTTING_BOARD
                        cv2.destroyAllWindows()
                        in_cooking = 1
                        break
                    elif x_pos > 300 and x_pos < 600:
                        position = STOVE
                        cv2.destroyAllWindows()
                        in_cooking = 1
                        break
                    elif x_pos < 300:
                        position = PLATE
                        cv2.destroyAllWindows()
                        in_cooking = 1
                        break
                    else:   #reset speech_said boolean
                        speech_said = False
    ####################
    #PLAYER LOCALIZATION
    ####################

    ###############
    #PLAYER ACTIONS
    ###############
        next_action()
        print(current_ingr)
        print(current_recipe)
        if position == PLATE:
            #ask IMU for plate classifier data
            txt = '0'
            screen.blit(bg_tile,(0,0))
            screen.blit(msg_plate,(50,50))
            screen.blit(msg_exit,(900,50))
            pygame.display.update()
            while txt.lower() != 'cheese' and txt.lower() != 'garnish' and txt.lower() != 'exit':
                if speech_said == True:
                    txt = from_speech()
            if txt.lower() == 'exit':   #back to stage selection
                continue
            client.publish(str(flag_opponent)+'Team8',str(MESSAGE)+'Your opponent is plating',qos = 1)
            if txt.lower() == 'cheese':
                client.publish(str(flag_player)+'Team8B', str(FLAG_SHRED), qos=1)
                task(FLAG_SHRED)
            elif txt.lower() == 'garnish':
                client.publish(str(flag_player)+'Team8B', str(FLAG_GARNISH), qos=1)
                task(FLAG_GARNISH)
            client.publish(str(flag_player)+'Team8B', str(STOP), qos=1)
        elif position == STOVE:
            #ask IMU for stove classifier data
            txt = '0'
            screen.blit(bg_stove,(0,0))
            screen.blit(msg_stove,(50,50))
            screen.blit(msg_exit,(900,50))
            pygame.display.update()
            while txt.lower() != 'spoon' and txt.lower() != 'exit':
                if speech_said == True:
                    txt = from_speech()
                    check = txt.lower()
                    i = 0
                    for i in range (len(check)-1):  #double o will also trigger the spoon keyword
                        charO = check[i]
                        if charO == 'o':
                            charO2 = check[i+1]
                            if charO2 == 'o':
                                txt = 'spoon'
                                break
            if txt.lower() == 'exit':
                continue
            client.publish(str(flag_opponent)+'Team8',str(MESSAGE) + 'Your opponent is at the stove', qos = 1)
            client.publish(str(flag_player)+'Team8B', str(FLAG_STIR), qos=1)
            task(FLAG_STIR)
            client.publish(str(flag_player)+'Team8B', str(STOP), qos=1)
        elif position == CUTTING_BOARD:
            #ask IMU for cutting classifier data
            txt = '0'
            screen.blit(bg_cuttingboard,(0,0))
            screen.blit(msg_cuttingboard,(50,50))
            screen.blit(msg_exit,(900,50))
            pygame.display.update()
            while txt.lower() != 'knife' and txt.lower() != 'exit' and txt.lower() != 'roll':
                if speech_said == True:
                    txt = from_speech()
                    if txt.lower() == 'night':   #common word
                        txt = 'knife'
                    if txt.lower() == 'toll':
                        txt = 'roll'
            if txt.lower() == 'exit':
                continue
            client.publish(str(flag_opponent)+'Team8',str(MESSAGE) + 'Your opponent is at the cutting board', qos = 1)
            if txt.lower() == 'roll':
                client.publish(str(flag_player)+'Team8B', str(FLAG_ROLLING), qos=1)
                task(FLAG_ROLLING)
            elif txt.lower() == 'knife':
                client.publish(str(flag_player)+'Team8B', str(FLAG_CUTTING), qos=1)
                task(FLAG_CUTTING)
            client.publish(str(flag_player)+'Team8B', str(STOP), qos=1)
        elif position == COUNTER:
            #ask IMU for rolling classifier data
            txt = '0'
            screen.blit(bg_tile,(0,0))
            screen.blit(msg_counter,(50,50))
            screen.blit(msg_exit,(900,50))
            pygame.display.update()
            while txt.lower()!= 'pour' and txt.lower() != 'exit':
                if speech_said == True:
                    txt = from_speech()
                    if txt.lower() == 'toll':   #common word
                        txt = 'roll'
                    if txt.lower() == 'boar' or txt.lower() == 'poor':
                        txt = 'pour'
            if txt.lower() == 'exit':
                continue
            client.publish(str(flag_opponent)+'Team8',str(MESSAGE) + 'Your opponent is at the counter', qos = 1)
            if txt.lower() == 'pour':
                client.publish(str(flag_player)+'Team8B', str(FLAG_POURING), qos=1)
                task(FLAG_POURING)
            client.publish(str(flag_player)+'Team8B', str(STOP), qos=1)
        in_cooking = 0
    ###############
    #PLAYER ACTIONS
    ###############


    #########
    #GAME END
    #########
        check_game()
        print_recipes()
        loading.preview()
    end_game = t.time()
    score = end_game-start_game
    #print('Your time was: ' + str(score))
    if flag_player == 2:
        displayScore(score,0,'Good Job!')
        t.sleep(10)
        client.loop_stop()
        client.disconnect()
    client.publish(str(flag_opponent)+'Team8', str(FLAG_SCORE)+str(score), qos=1)
    #########
    #GAME END
    #########
    while True:
        pass

##################
#GAME STARTS HERE#
#GAME STARTS HERE#
#GAME STARTS HERE#
##################
client = mqtt.Client()
# add additional client options (security, certifications, etc.)
# many default options should be good to start off.
# add callbacks to client.
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
# 2. connect to a broker using one of the connect*() functions.
client.connect_async("test.mosquitto.org")
client.loop_start()
cap = cv2.VideoCapture(0)
while gamestart != 0:
    loading.preview()
    t.sleep(0.6)
fps = cap.get(cv2.CAP_PROP_FPS)
#cam is 30fps
cap.set(cv2.CAP_PROP_FPS, 30)
main()