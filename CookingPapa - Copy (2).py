from email import message
from multiprocessing.dummy import freeze_support
from pickle import FALSE
from ssl import ALERT_DESCRIPTION_BAD_CERTIFICATE_HASH_VALUE
#from socketserver import ThreadingUnixDatagramServer
import time as t 
import paho.mqtt.client as mqtt
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
from multiprocessing import Process, Pipe
from pygame import mixer
from scipy.io import wavfile
import noisereduce as nr

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
time_bonus = 0
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
chop_tomato = []
garnish_parsley = []
garnish_pepper = []
garnish_salt = []
pour_pasta = []
pour_sauce = []
pour_tomato = []
rolling_dough = []
shred_cheese = []
stir_pasta = []
stir_sauce = []



#colors
backgroundColor=(255, 255, 255)
green = (2, 100,64)
black = (0,0,0)
#window

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
pizza = np.array([['pizza','4o2','2t2','5t3','3o3','5s1','8o4','9p4']])
vegetable_soup = np.array([['vegetable soup','2','2','3','5','9']])
pasta = np.array([['pasta','5p3','3p3','2t2','5t3','3s3','5s1','9p4']])
#recipe declarations

#global helper literals
action_to_do = '0'
ingr_to_do = '0'
area_to_go = '0'
#global helper literals

controller_speech = '0'
#globals

#player imaging class
class Playerimg():
	def __init__(self, x, y):
		self.images_right = []
		self.images_left = []
		self.index = 0
		self.counter = 0
		for num in range(1, 5):
			img_right = pygame.image.load(f'images/chef{num}.png')
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
		dx = 0
		dy = 0
		walk_cooldown = 5

        #moving left
		if (self.rect.x - x_pos) < 0:
			self.counter += 1
			self.direction = -1
		#moving right
		if (self.rect.x - x_pos) > 0:
			self.counter += 1
			self.direction = -1

		#handle animation
		if self.counter > walk_cooldown:
			self.counter = 0	
			self.index += 1
			if self.index >= len(self.images_right):
				self.index = 0
			if self.direction == 1:
				self.image = self.images_right[self.index]
			if self.direction == -1:
				self.image = self.images_left[self.index]


		#add gravity
		self.vel_y += 1
		if self.vel_y > 10:
			self.vel_y = 10
		dy += self.vel_y

		#check for collision

		#update player 
		#print(dx)
		self.rect.x = x_pos - 150
		self.rect.y += dy

		if self.rect.bottom > SCREEN_HEIGHT:
			self.rect.bottom = SCREEN_HEIGHT
			dy = 0
#player imaging class

#fonts           

file_pattern = re.compile(r'.*?(\d+).*?')
def get_order(file):
    match = file_pattern.match(Path(file).name)
    if not match:
        return math.inf
    return int(match.groups()[0])

def load_vids():        #there has to be a better way I just do not know how else
    global chop_tomato, garnish_parsley,garnish_pepper,garnish_salt,pour_pasta,pour_sauce,pour_tomato,rolling_dough,shred_cheese,stir_pasta,stir_sauce
    loading_graphics = sorted(glob.glob('animationPNGs/'+"chop_tomato" + '/*.png'),key = get_order)
    for i in loading_graphics:
        chop_tomato.append(pygame.image.load(i))
    loading_graphics = sorted(glob.glob('animationPNGs/'+"garnish_parsley" + '/*.png'),key = get_order)
    for i in loading_graphics:
        garnish_parsley.append(pygame.image.load(i))
    loading_graphics = sorted(glob.glob('animationPNGs/'+"garnish_pepper" + '/*.png'),key = get_order)
    for i in loading_graphics:
        garnish_pepper.append(pygame.image.load(i))
    loading_graphics = sorted(glob.glob('animationPNGs/'+"garnish_salt" + '/*.png'),key = get_order)
    for i in loading_graphics:
        garnish_salt.append(pygame.image.load(i))
    loading_graphics = sorted(glob.glob('animationPNGs/'+"pour_pasta" + '/*.png'),key = get_order)
    for i in loading_graphics:
        pour_pasta.append(pygame.image.load(i))
    loading_graphics = sorted(glob.glob('animationPNGs/'+"pour_sauce" + '/*.png'),key = get_order)
    for i in loading_graphics:
        pour_sauce.append(pygame.image.load(i))
    loading_graphics = sorted(glob.glob('animationPNGs/'+"pour_tomato" + '/*.png'),key = get_order)
    for i in loading_graphics:
        pour_tomato.append(pygame.image.load(i))
    loading_graphics = sorted(glob.glob('animationPNGs/'+"rolling_dough" + '/*.png'),key = get_order)
    for i in loading_graphics:
        rolling_dough.append(pygame.image.load(i))
    loading_graphics = sorted(glob.glob('animationPNGs/'+"shred_cheese" + '/*.png'),key = get_order)
    for i in loading_graphics:
        shred_cheese.append(pygame.image.load(i))
    loading_graphics = sorted(glob.glob('animationPNGs/'+"stir_pasta" + '/*.png'),key = get_order)
    for i in loading_graphics:
        stir_pasta.append(pygame.image.load(i))
    loading_graphics = sorted(glob.glob('animationPNGs/'+"stir_sauce" + '/*.png'),key = get_order)
    for i in loading_graphics:
        stir_sauce.append(pygame.image.load(i))
   
#vision processing code
def track_player(frame,lower_thresh_player,upper_thresh_player):
    global x_pos
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
    global speed, current_images, timer_set, last_action, current_recipe, ingr_to_do, area_to_go

    #Beginning of task code
    t.sleep(CONTROLLER_BUFFER)
    timer_set = 1
    action = int(action)
    string_action = naming(action)
    win = pygame.display.set_mode(windowsize)
    #if elif statements]
    if area_to_go == '1' or area_to_go == '4':
        current_bg = bg_tile
    elif area_to_go == '2':
        current_bg = bg_cuttingboard
    elif area_to_go == '3':
        current_bg = bg_stove

    if (string_action == 'Stir'):
        if ingr_to_do == 'p':
            current_images = stir_pasta
        elif ingr_to_do == 's':
            current_images = stir_sauce
        else:
            current_images = stir_sauce
    elif(string_action == 'Cut'):
        current_images = chop_tomato
    elif(string_action == 'Roll'):
        current_images = rolling_dough
    elif(string_action == 'Pour'):
        if ingr_to_do == 't':
            current_images = pour_tomato
        elif ingr_to_do == 's':
            current_images = pour_sauce
        if ingr_to_do == 'p':
            current_images = pour_pasta
    elif(string_action == 'Shred'):
        current_images = shred_cheese
    elif(string_action == 'Garnish'):
        if ingr_to_do == 'p':
            current_images = garnish_parsley
    #if elif statements
    speed = 0  #default
    win.blit(current_bg,(0,0))
    win.blit(current_images[0],(0,0))
    pygame.display.update()
    for i in current_images:
        while speed == 0:
            pass #dont let it run if speed = 0
        #print('Working '+str(i))
        feedback = 'This aint it' if speed == 1 else 'Ok' if speed == 2 else 'OK GORDON RAMSEY' if speed == 3 else 'Learn to cook'
        win.blit(current_bg,(0,0))
        win.blit(i,(0,0))
        pygame.display.update()
        if speed != 0:
            t.sleep(0.05/speed)

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

def displayScore2(score, opponent_score, feedback):
    scoreFont = pygame.font.Font("chianti.ttf", 80)
    score_display = scoreFont.render(str(score)+' pts', False, (0,0,0))
    opponent_display = scoreFont.render('Enemy: ' +str(opponent_score) +' pts', False,(0,0,0))
    if feedback =='practice':
        win.blit(final_score,(0,0))
        win.blit(score_display, (590,620))
        return
    elif feedback == 'won':
        win.blit(final_score_won,(0,0))
    else:
        win.blit(final_score_lost,(0,0))
    win.blit(score_display, (590,620))
    win.blit(opponent_display, (590,700))

	

def check_game():
    global all_recipes, current_recipe, timer_time, in_cooking
    length = len(all_recipes[0])
    for k in range(len(all_recipes)):
        if all_recipes[k][0] != '0':
            for i in range(1,length):
                if all_recipes[k][i][0] != '0':
                    all_recipes[k][i] = '0' + str(timer_time)   #indicate done flag and store time
                    if i == length - 1:
                        all_recipes[k][0] = '0'
                        if k == len(all_recipes) - 1:
                            in_cooking = 2
                            return
                    return

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
            msg_recipe = myfont.render('Recipe '+str(k+1)+ ' of ' + str(recipe_count) + ' ' + str(all_recipes[k][0]).upper() + '!',False,(0,0,0))
            win.blit(msg_recipe,(10,10))
            for i in range(1,length):
                action = naming(int(all_recipes[k][i][0]),1) 
                station = naming(int(all_recipes[k][i][2]),2)
                msg_action = myfont.render(str(i)+'. ' + action + ' - '+ station + '!', False,(0,0,0))
                win.blit(msg_action,(10,10+30*i))
        if can_break == 1:
            break       #only print the next available recipe

def classifier(str):    #classify for user output
    global current_goal, action_to_do, ingr_to_do, area_to_go
    action_to_do = str[0]
    ingr_to_do = str[1]
    area_to_go = str[2]

def naming(num,type):
    action = 'Cut' if num == 2 else 'Stir' if num == 3 else 'Roll' if num == 4 else 'Pour' if num == 5 else 'Shred' if num == 8 else 'Garnish'
    station = 'counter' if num == 1 else 'board' if num == 2 else 'stove' if num == 3 else 'plate'
    if type == 1:
        return action
    elif type == 2:
        return station

def next_action():
    global all_recipes
    global current_recipe
    length = len(all_recipes[0])
    for k in range(len(all_recipes)):
        if all_recipes[k][0] != '0':
            current_recipe = all_recipes[k][0]
            for i in range(1,length):
                if all_recipes[k][i][0] != '0':
                    classifier(all_recipes[k][i])   #defining classified action
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
                displayScore2(score, float(message_received),'won')
                #print('You are better than the other idiot sandwich. Congration.')
                #print('Your score: '+str(float(score))+'\n'+"Your opponent's score: " + str(float(message_received)))
                client.publish(str(flag_opponent)+'Team8', str(FLAG_SCORE)+str(score), qos=1)
            else:
                displayScore2(score, float(message_received), 'lost')
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
    elif flag_received == str(SWITCH):
        temp = meh
        meh = excellent
        excellent = temp

def from_speech():
    global speech_said
    r = sr.Recognizer()
    txt = '0'
    rate, data = wavfile.read("receive.wav")
    # perform noise reduction
    reduced_noise = nr.reduce_noise(y=data, sr=rate)
    wavfile.write("receive_reduced_noise.wav", rate, reduced_noise)
    hello=sr.AudioFile('receive_reduced_noise.wav')
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
    with sr.Microphone(device_index=0) as source:
        audio = r.listen(source, phrase_time_limit = 1.25)
    try:
        txt = r.recognize_google(audio)
        txt = str(txt)
        return txt
    except sr.UnknownValueError:
        txt = '0'
        return txt

#########################
###MULTIPROCESSED CODE###
#########################

def multi_timer(timer_type,conn):
    global timer_time
    while True:
        timer_set = conn.recv()
        if timer_type == str(1): #space for other timer types
        #Starting a normal timer
            index = 0
            while(timer_set == 1): #only reset timer IF timer_set is run, otherwise dont 
                t.sleep(1)
                index = index+1
            if(timer_set == 0):
                conn.send(index)
                print(index)

def multi_background_music(music_to_load):
    mixer.init()
    mixer.music.load(music_to_load)
    mixer.music.play()
    while(1):
        pass
    

#########################
###MULTIPROCESSED CODE###
#########################

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
    calvid.preview()
    calibration()
    cv2.destroyAllWindows()
    ##################
    #CALIBRATION PHASE
    ##################

    ################
    #MULTIPROCESSING CALL
    ################
    conn1, conn2 = Pipe()
    timers = Process(target = multi_timer, args=(1,conn2))
    timers.start()
    ################
    #MULTIPROCESSING CALL
    ################

    ################
    #STARTING SCREEN
    ################
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
    client.subscribe(str(flag_player)+'Team8C', qos = 1)
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
        pygame.display.set_caption('Cooking Papa Beta Testing')
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
            screen.blit(playerimg.image, playerimg.rect)
            print_recipes()
            pygame.display.update()
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                #will only trigger/pause the code if speech is detected to have been said
            if speech_said == True:
                txt = from_speech()
                if txt == 'go' or txt == 'no':
                    next_action()
                    if x_pos > 900:
                        if int(area_to_go) == COUNTER:
                            position = COUNTER
                            cv2.destroyAllWindows()
                            in_cooking = 1
                            break
                        else:
                            continue
                    elif x_pos > 600 and x_pos < 900:
                        if int(area_to_go) == CUTTING_BOARD:
                            position = CUTTING_BOARD
                            cv2.destroyAllWindows()
                            in_cooking = 1
                            break
                        else:
                            continue
                    elif x_pos > 300 and x_pos < 600:
                        if int(area_to_go) == STOVE:
                            position = STOVE
                            cv2.destroyAllWindows()
                            in_cooking = 1
                            break
                        else:
                            continue
                    elif x_pos < 300:
                        if int(area_to_go) == PLATE:
                            position = PLATE
                            cv2.destroyAllWindows()
                            in_cooking = 1
                            break
                        else:
                            continue
                elif txt == 'switch' or txt == 'scramble':
                    if txt == 'scramble':
                        client.publish(str(flag_opponent)+'Team8', str(SCRAMBLE), qos=1)
                    elif txt == 'switch':
                        client.publish(str(flag_opponent)+'Team8', str(SWITCH), qos=1)
                else:   #reset speech_said boolean
                    speech_said = False
    ####################
    #PLAYER LOCALIZATION
    ####################

    ###############
    #PLAYER ACTIONS
    ###############
        if position == PLATE:
            #ask IMU for plate classifier data
            txt = '0'
            screen.blit(bg_tile,(0,0))
            screen.blit(msg_plate,(50,50))
            screen.blit(msg_exit,(900,50))
            pygame.display.update()
            action = '0'
            while txt.lower() != 'cheese' and txt.lower() != 'garnish':
                if speech_said == True:
                    txt = from_speech()
                    if txt.lower() == 'cheese' and int(action_to_do) == int(FLAG_SHRED): 
                        action = FLAG_SHRED
                    elif txt.lower() == 'garnish' and int(action_to_do) == int(FLAG_GARNISH): 
                        action = FLAG_GARNISH
                    else:
                        txt = '0'   #reset for while loop
            client.publish(str(flag_opponent)+'Team8',str(MESSAGE)+'Your opponent is plating',qos = 1)
            client.publish(str(flag_player)+'Team8B', str(action), qos=1)
            conn1.send(1)
            task(action)
            conn1.send(0)
            t.sleep(1)
            timer_time = conn1.recv()
            client.publish(str(flag_player)+'Team8B', str(STOP), qos=1)
        elif position == STOVE:
            #ask IMU for stove classifier data
            txt = '0'
            screen.blit(bg_stove,(0,0))
            screen.blit(msg_stove,(50,50))
            screen.blit(msg_exit,(900,50))
            pygame.display.update()
            action = '0'
            while txt.lower() != 'spoon' and txt.lower() != 'pour':
                if speech_said == True:
                    txt = from_speech()
                    if 'o' in txt:
                        txt = 'spoon'
                    elif txt == 'poor' or txt == '4':
                        txt = 'pour'
                    if txt.lower() == 'spoon' and int(action_to_do) == int(FLAG_STIR): 
                        action = FLAG_STIR
                    elif txt.lower() == 'pour' and int(action_to_do) == int(FLAG_POURING): 
                        action = FLAG_POURING
                    else:
                        txt = '0'   #reset for while loop
            client.publish(str(flag_opponent)+'Team8',str(MESSAGE)+'Your opponent is at the stove',qos = 1)
            client.publish(str(flag_player)+'Team8B', str(action), qos=1)
            conn1.send(1)
            task(action)
            conn1.send(0)
            t.sleep(1)
            timer_time = conn1.recv()
            client.publish(str(flag_player)+'Team8B', str(STOP), qos=1)
        elif position == CUTTING_BOARD:
            #ask IMU for cutting classifier data
            txt = '0'
            screen.blit(bg_cuttingboard,(0,0))
            screen.blit(msg_cuttingboard,(50,50))
            screen.blit(msg_exit,(900,50))
            pygame.display.update()
            action = '0'
            while txt.lower() != 'knife' and txt.lower() != 'roll':
                if speech_said == True:
                    txt = from_speech()
                    if 'i' in txt:
                        txt = 'knife'
                    elif 'o' in txt:
                        txt = 'roll'
                    if txt.lower() == 'knife' and int(action_to_do) == int(FLAG_CUTTING): 
                        action = FLAG_CUTTING
                    elif txt.lower() == 'roll' and int(action_to_do) == int(FLAG_ROLLING): 
                        action = FLAG_ROLLING
                    else:
                        txt = '0'   #reset for while loop
            client.publish(str(flag_opponent)+'Team8',str(MESSAGE)+'Your opponent is at the cutting board',qos = 1)
            client.publish(str(flag_player)+'Team8B', str(action), qos=1)
            conn1.send(1)
            task(action)
            conn1.send(0)
            t.sleep(1)
            timer_time = conn1.recv()
            client.publish(str(flag_player)+'Team8B', str(STOP), qos=1)
        elif position == COUNTER:
            #ask IMU for rolling classifier data
            txt = '0'
            screen.blit(bg_tile,(0,0))
            screen.blit(msg_counter,(50,50))
            screen.blit(msg_exit,(900,50))
            pygame.display.update()
            action = '0'
            while txt.lower() != 'pour':
                if speech_said == True:
                    txt = from_speech()
                    if txt == 'poor' or txt == '4':
                        txt = 'pour'
                    if txt.lower() == 'pour' and int(action_to_do) == int(FLAG_POURING): 
                        action = FLAG_POURING
                    else:
                        txt = '0'   #reset for while loop
            client.publish(str(flag_opponent)+'Team8',str(MESSAGE)+'Your opponent is at the counter',qos = 1)
            client.publish(str(flag_player)+'Team8B', str(action), qos=1)
            conn1.send(1)
            task(action)
            conn1.send(0)
            t.sleep(1)
            timer_time = conn1.recv()
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
    end_game = t.time()
    score = end_game-start_game
    #print('Your time was: ' + str(score))
    if flag_player == 2:
        displayScore2(score,0,'practice')
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
if __name__ == '__main__':
    freeze_support()
    load_vids()
    background_music = Process(target=multi_background_music, args=("sounds/background_music_italian.mp3",))
    background_music.start()
    client = mqtt.Client()
    windowsize = (SCREEN_WIDTH, SCREEN_HEIGHT)
    win=pygame.display.set_mode(windowsize)
    pygame.display.set_caption("Cooking Papa Beta Start")
    bg_img = pygame.image.load('backgrounds/game_background.png')
    bg_img = pygame.transform.scale(bg_img, windowsize).convert()
    bg_cuttingboard = pygame.image.load('backgrounds/cuttingboard.png')
    bg_cuttingboard = pygame.transform.scale(bg_cuttingboard, windowsize).convert()
    bg_stove = pygame.image.load('backgrounds/stove.png')
    bg_stove = pygame.transform.scale(bg_stove, windowsize).convert()
    bg_tile = pygame.image.load('backgrounds/tile.png')
    bg_tile = pygame.transform.scale(bg_tile, windowsize).convert()

    vs_score = pygame.image.load('images/score_page.png')
    vs_score_opp = pygame.image.load('images/score_page_opp.png')

    calimg = pygame.image.load('images/calibration_instructions.png')
    modimg = pygame.image.load('images/game_mode_selection.png')
    playimg = pygame.image.load('images/player_selection.png')

    final_score =  pygame.image.load('images\FinalScore_Practice.png')
    final_score_lost =  pygame.image.load('images\FinalScore_Lost.png')
    final_score_won =  pygame.image.load('images\FinalScore_Won.png')


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
    #fonts

    pizza_finish = pygame.image.load('finished_dishes/finished_pizza.png')
    pasta_finish = pygame.image.load('finished_dishes/finished_pasta.png')
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