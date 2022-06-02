from email import message
from email.iterators import walk
from multiprocessing.dummy import freeze_support
from pickle import FALSE
from ssl import ALERT_DESCRIPTION_BAD_CERTIFICATE_HASH_VALUE
#from socketserver import ThreadingUnixDatagramServer
import time as t
from matplotlib.pyplot import flag 
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
FLAG_RECEIVE = '11'
STOP = '00'
SCRAMBLE = '13'
SWITCH = '14'
SCREEN_HEIGHT = 800
SCREEN_WIDTH = 1200

MESSAGE = '10'

FLAG_SCORE = '99'

#BOARD POSITIONS
counter = 1
board = 2
stove = 3
plate = 4
#BOARD POSITIONS

##CONST GLOBALS

#globals

#scoring parameters
counter2 = 0
sabotage_penalty = 0
time_bonus = 0
excellency_bonus = 0 
score = 0
final_score = 0
#scoring parameters

#opponent params
opp_sabotage_penalty = 0
opp_time_bonus = 0
opp_excellency_bonus = 0 
opp_score = 0
opp_final_score = 0
#opponent params

timer_time = 0
score_received = 0 
walk_s = 0
walk_memory = 0
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
message_received = ''
speed = 1
current_goal = 0
gamestart = 1
speech_said = False
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
practice_flag = 0


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
counter2 = 0 
x_pos  = 0

#recipe declarations
#CUT = '02' STIR = '03' ROLL = '04' POUR = '05' SHRED = '08' GARNISH = '09'
#1 - counter, 2 - cutting board, 3 - stove, 4 - plating
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
		self.counter2 = 0
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
			self.counter2 += 1
			self.direction = 1
		#moving right
		elif (self.rect.x+150 - x_pos) > 18 and x_pos >=200:
			dx += 5
			self.counter2 += 1
			self.direction = -1


		#print(str(self.rect.x+150) +" " + str(x_pos))
		#print(str(x_pos))
		#print('direction: '+ str(self.direction))

		#handle animation

		if (walk_s==3):
			if abs(walk_memory+self.rect.x+150 - x_pos)/2>9:
				self.counter2 = 0	
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
#player imaging class

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
    global counter2
    x_c_1 = 200
    x_c_2 = 400
    y_c_1 = 250
    y_c_2 = 495
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    cv2.rectangle(frame, (x_c_1, y_c_1), (x_c_2, y_c_2), (0, 255, 0), 3)

def calibrate(frame, x_c_1, y_c_1, x_c_2, y_c_2):
    global lower_thresh_player
    global upper_thresh_player
    global flag_player
    global flag_opponent
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
    if int(avg_h) <= 20 and int(avg_h) >= 0 and int(avg_s) <= 255 and int(avg_v) <= 255 and int(avg_s) >= 40 and int(avg_v) >= 20:
        flag_player = 1
        flag_opponent = 2
    elif int(avg_h) <= 180 and int(avg_h) >= 160 and int(avg_s) <= 255 and int(avg_v) <= 255 and int(avg_s) >= 40 and int(avg_v) >= 20:
        flag_player = 1
        flag_opponent = 2
    else:
        flag_player = 2
        flag_opponent = 1

def calibration():
    global counter2
    global lower_thresh_player
    global upper_thresh_player
    surface = pygame.display.set_mode([1200,800])
    while (True):
        ret, frame = cap.read()
        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        cv2.flip(frame, 1)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        if counter2 <= 301:
            get_calibration_frames(frame)
        elif counter2 == 302:
            print('calibrating...')
            t.sleep(1)
            calibrate(frame, x_c_1, y_c_1, x_c_2, y_c_2)
        elif counter2 > 302:
            print('exiting calibration...')
            return
        counter2 = counter2+1
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
    global speed, current_images, last_action, current_recipe, ingr_to_do, area_to_go, timer_time, excellency_bonus
    #Beginning of task code
    t.sleep(CONTROLLER_BUFFER)
    action = int(action)
    string_action = naming(action,1)
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
    task_start = t.time()
    for i in current_images:
        #print('Working '+str(i))

        win.blit(current_bg,(0,0))
        win.blit(i,(0,0))
        win.blit(feedback_msg,(900,50))
        pygame.display.update()
        if speed != 0:
            t.sleep(0.05/speed)
        if speed == 3:
            excellency_bonus = excellency_bonus + 0.05
        while speed == 0:
            t.sleep(.05)
    task_end = t.time()
    timer_time = task_end - task_start
    #ending of task code
    last_action = action
    return

def displayScore():
    global practice_flag, time_bonus, excellency_bonus, sabotage_penalty, excellency_bonus, score, final_score
    global opp_time_bonus, opp_excellency_bonus, opp_sabotage_penalty, opp_score, opp_final_score
    time_bonus = '+ ' + str(time_bonus) + ' x 10'
    sabotage_penalty = '- ' + str(sabotage_penalty) + ' x 10'
    excellency_bonus = '+ ' + str(int(excellency_bonus))
    score = str(int(score)) + ' s'
    scorefont = pygame.font.Font('Bukhari Script.ttf', 72)
    finalfont = pygame.font.Font('Bukhari Script.ttf', 120)
    msg_time_bonus = scorefont.render(str(time_bonus),False,(236, 233, 218))
    msg_time_bonus2 = scorefont.render(str(time_bonus),False,(187, 56, 49))
    msg_excellency_bonus = scorefont.render(str(excellency_bonus),False,(236, 233, 218))
    msg_excellency_bonus2 = scorefont.render(str(excellency_bonus),False,(187, 56, 49))
    msg_sabotage_penalty = scorefont.render(str(sabotage_penalty),False,(236, 233, 218))
    msg_sabotage_penalty2 = scorefont.render(str(sabotage_penalty),False,(187, 56, 49))
    msg_score = scorefont.render(str(score),False,(236, 233, 218))
    msg_score2 = scorefont.render(str(score),False,(187, 56, 49))
    msg_finalscore = finalfont.render(str(final_score), False, (236, 233, 218))

    scoring_vid0.preview()
    win.blit(scorebreakimg,(0,0))
    pygame.display.update()
    win.blit(msg_time_bonus2,(590,265))
    win.blit(msg_time_bonus,(585,260))
    t.sleep(1)
    pygame.display.update()
    win.blit(msg_excellency_bonus2,(815,388))
    win.blit(msg_excellency_bonus,(810,383))
    t.sleep(1)
    pygame.display.update()
    win.blit(msg_sabotage_penalty2,(805,508))
    win.blit(msg_sabotage_penalty,(800,503))
    t.sleep(1)
    pygame.display.update()
    win.blit(msg_score2,(555,633))
    win.blit(msg_score,(550,628))
    t.sleep(1)
    pygame.display.update()
    t.sleep(2)
    if practice_flag == 1:
        scoring_vid1.preview()
        win.blit(finalscoreimg,(0,0))
        win.blit(msg_finalscore,(470,400))
        pygame.display.update()
    elif practice_flag == 0:
        opp_final_score = (500 - opp_score) + (opp_time_bonus * 10) + opp_excellency_bonus - (opp_sabotage_penalty * 10)
        opp_final_score = int(opp_final_score)
        opp_time_bonus = '+ ' + str(opp_time_bonus) + ' x 10'
        opp_sabotage_penalty = '- ' + str(opp_sabotage_penalty) + ' x 10'
        opp_excellency_bonus = '+ ' + str(int(opp_excellency_bonus))
        opp_score = str(int(opp_score)) + ' s'
        msg_opp_time_bonus = scorefont.render(str(opp_time_bonus),False,(236, 233, 218))
        msg_opp_time_bonus2 = scorefont.render(str(opp_time_bonus),False,(187, 56, 49))
        msg_opp_excellency_bonus = scorefont.render(str(opp_excellency_bonus),False,(236, 233, 218))
        msg_opp_excellency_bonus2 = scorefont.render(str(opp_excellency_bonus),False,(187, 56, 49))
        msg_opp_sabotage_penalty = scorefont.render(str(opp_sabotage_penalty),False,(236, 233, 218))
        msg_opp_sabotage_penalty2 = scorefont.render(str(opp_sabotage_penalty),False,(187, 56, 49))
        msg_opp_score = scorefont.render(str(opp_score),False,(236, 233, 218))
        msg_opp_score2 = scorefont.render(str(opp_score),False,(187, 56, 49))
        msg_opp_finalscore = finalfont.render(str(opp_final_score), False, (236, 233, 218))
        opp_scoring_vid0.preview()
        win.blit(opp_scorebreakimg,(0,0))
        pygame.display.update()
        win.blit(msg_opp_time_bonus2,(590,265))
        win.blit(msg_opp_time_bonus,(585,260))
        t.sleep(1)
        pygame.display.update()
        win.blit(msg_opp_excellency_bonus2,(815,388))
        win.blit(msg_opp_excellency_bonus,(810,383))
        t.sleep(1)
        pygame.display.update()
        win.blit(msg_opp_sabotage_penalty2,(805,508))
        win.blit(msg_opp_sabotage_penalty,(800,503))
        t.sleep(1)
        pygame.display.update()
        win.blit(msg_opp_score2,(555,633))
        win.blit(msg_opp_score,(550,628))
        t.sleep(1)
        pygame.display.update()
        t.sleep(2)
        opp_scoring_vid1.preview()
        win.blit(opponentimg,(0,0))
        win.blit(msg_opp_finalscore,(900,400))
        win.blit(msg_finalscore,(300,400))
        pygame.display.update()

def check_game():
    global all_recipes, current_recipe, timer_time, in_cooking, time_bonus
    length = len(all_recipes[0])
    for k in range(len(all_recipes)):
        if all_recipes[k][0] != '0':
            for i in range(1,length):
                if all_recipes[k][i][0] != '0':
                    all_recipes[k][i] = '0' + str(timer_time)   #indicate done flag and store time
                    if (timer_time < 12):
                        time_bonus = time_bonus + 1
                    if i == length - 1:
                        all_recipes[k][0] = '0'
                        if k == len(all_recipes) - 1:
                            in_cooking = 2
                            return
                    return

def recipe_randomizer(difficulty):  #randomize all recipe's length based off of difficulty
    global all_recipes
    global recipe_count
    recipe_count = 0
    if difficulty == 'hard':
        recipe_count = 3
    elif difficulty == 'normal':
        recipe_count = 2
    elif difficulty =='easy':
        recipe_count = 1
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
            msg_recipe = myfont.render(str(k+1)+ ' of ' + str(recipe_count) + ': ' + str(all_recipes[k][0]).upper() + '!',False,(0,0,0))
            win.blit(msg_recipe,(25,10))
            for i in range(1,length):
                action = naming(int(all_recipes[k][i][0]),1)
                if len(all_recipes[k][i]) == 3: 
                    station = naming(int(all_recipes[k][i][2]),2)
                    msg_action = smallFont.render(str(i)+'. ' + action + ' - '+ station + '!', False,(0,0,0))
                else:
                    msg_action = smallFont.render(str(i)+'. ' + action + '!', False,(0,0,0))
                win.blit(msg_action,(25,30+25*i))
        if can_break == 1:
            break       #only print the next available recipe

def classifier(str):    #classify for user output
    global current_goal, action_to_do, ingr_to_do, area_to_go
    action_to_do = str[0]
    ingr_to_do = str[1]
    area_to_go = str[2]
    print(action_to_do)
    print(ingr_to_do)
    print(area_to_go)

def naming(num,type):
    action = 'Cut' if num == 2 else 'Stir' if num == 3 else 'Roll' if num == 4 else 'Pour' if num == 5 else 'Shred' if num == 8 else 'Garnish' if num == 9 else 'Done'
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
    global speech_said
    global meh, good, excellent
    global current_recipe
    global counter, board, stove, plate
    global feedback_msg
    global final_score, score_received
    global score, sabotage_penalty, time_bonus, excellency_bonus
    global opp_score, opp_sabotage_penalty, opp_time_bonus, opp_excellency_bonus, opp_final_score
    #data received as b'message'
    temporary = str(message.payload)
    message_received = temporary[4:-1]
    flag_received = temporary[2:4]
    #print(temporary)
    #print(message_received)
    #score flag received
    if (str(flag_received) == str(FLAG_RECEIVE)):
        if int(message_received) == 1:
            speed = meh
            feedback_msg = bad_feedback
        elif int(message_received) == 2:
            speed = good
            feedback_msg = good_feedback
        elif int(message_received) == 3:
            speed = excellent
            feedback_msg = excellent_feedback
        elif int(message_received) == 0:
            speed = 0
    elif str(flag_received) == str(FLAG_SCORE):
        if in_cooking == 2:
            temp = str(message_received)
            tempadd = ''
            index = 0
            for i in range(len(temp)):
                if temp[i] != ' ':
                    tempadd = tempadd + temp[i]
                else:
                    if index == 0:
                        opp_score = int(tempadd)
                    elif index == 1:
                        opp_sabotage_penalty = int(tempadd)
                    elif index == 2:
                        opp_time_bonus = int(tempadd)
                    elif index == 3:
                        opp_excellency_bonus = int(tempadd)
                    index = index + 1
                    tempadd = ''
            client.publish(str(flag_opponent)+'Team8', str(FLAG_SCORE) + str(int(score))+' '+str(int(sabotage_penalty))+' '+str(int(time_bonus))+' '+str(int(excellency_bonus)), qos=1)
        score_received = 1

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
        scramble_rec_vid.preview()
        temp = meh
        meh = excellent
        excellent = temp
    elif flag_received == str(SWITCH):
        switch_rec_vid.preview()
        temp1 = counter
        temp2 = board
        temp3 = stove
        temp4 = plate
        counter = temp2
        board = temp3
        stove = temp4
        plate = temp1

def from_speech():
    global speech_said
    r = sr.Recognizer()
    txt = '0'
    # try:
    #     rate, data = wavfile.read("receive.wav")
    # except ValueError:
    #     txt = '0'
    #     speech_said = False
    #     return txt.lower()
    # # perform noise reduction
    # reduced_noise = nr.reduce_noise(y=data, sr=rate)
    # wavfile.write("receive_reduced_noise.wav", rate, reduced_noise)
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
        except ValueError:
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

def play_error():
    pygame.mixer.Sound.play(error_sound)
    pygame.mixer.music.stop()
#########################
###MULTIPROCESSED CODE###
#########################

def multi_background_music(music_to_load):
    mixer.init()
    mixer.music.load(music_to_load)
    mixer.music.play(-1)
    
#########################
###MULTIPROCESSED CODE###
#########################

def main():
    #####################
    #GLOBAL DECLARATIONS
    #####################
    global score, excellency_bonus, time_bonus, sabotage_penalty, final_score
    global in_cooking
    global flag_opponent, flag_player
    global last_action
    global x_pos
    global position
    global current_recipe
    global speech_said
    global action_to_do, area_to_go, ingr_to_do
    global practice_flag
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

    #####################
    #PLAYER SUBSCRIPTIONS
    #####################
    if flag_player == 1:
        play1vid.preview()
    elif flag_player == 2:
        play2vid.preview()
    client.subscribe(str(flag_player)+'Team8', qos=1)
    client.subscribe(str(flag_player)+'Team8A',qos=2)
    client.subscribe(str(flag_player)+'Team8C', qos = 1)
    #####################
    #PLAYER SUBSCRIPTIONS
    #####################
    endloop = 0
    while(endloop != 1):
        ################
        #STARTING SCREEN
        ################
        txt = '0'
        modvid.preview()
        while txt.lower() != 'practice' and txt.lower() != 'competition':
            if speech_said == True:
            #win.blit(intro, (0,0))
                txt = from_speech()
                if txt == 'brackets':  #common word
                    txt = 'practice'
                if 'sh' in txt:
                    txt = 'competition'
                speech_said = False
        ################
        #STARTING SCREEN
        ################

        #####################
        #WAITING FOR OPPONENT
        #####################
        practice_flag = 0
        if txt.lower() == 'practice':
            practice_flag = 1
        #####################
        #WAITING FOR OPPONENT
        #####################
        difficulty = '0'
        speech_said = False
        difficulty_sel_vid.preview()
        while (txt.lower() != 'easy' and txt.lower() != 'normal' and txt.lower() != 'hard'):
            win.blit(diffimg,(0,0))
            pygame.display.update()
            if speech_said == True:
                txt = from_speech()
                if txt.lower() == 'easy':
                    difficulty = 'easy'
                    difficulty_sel_vid1.preview()
                elif txt.lower() == 'normal':
                    difficulty = 'normal'
                    difficulty_sel_vid2.preview()
                elif txt.lower() == 'hard':
                    difficulty = 'hard'
                    difficulty_sel_vid3.preview()
                else:
                    txt = '0'
                speech_said = False
        recipe_randomizer(difficulty) 
        countdown.preview()
        start_game = t.time()
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
                screen.blit(msg_go,(500, 50))
                pygame.display.update()
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    #will only trigger/pause the code if speech is detected to have been said
                if speech_said == True:
                    txt = from_speech()
                    if 'o' in txt or 'g' in txt:
                        txt = 'go'
                    if txt == 'go' or txt == 'no':
                        next_action()
                        if x_pos >= 900:
                            if int(area_to_go) == counter:
                                position = counter
                                cv2.destroyAllWindows()
                                in_cooking = 1
                                break
                            else:
                                play_error()
                                continue
                        elif x_pos > 600 and x_pos < 900:
                            if int(area_to_go) == board:
                                position = board
                                cv2.destroyAllWindows()
                                in_cooking = 1
                                break
                            else:
                                play_error()
                                continue
                        elif x_pos > 300 and x_pos < 600:
                            if int(area_to_go) == stove:
                                position = stove
                                cv2.destroyAllWindows()
                                in_cooking = 1
                                break
                            else:
                                play_error()
                                continue
                        elif x_pos < 300:
                            if int(area_to_go) == plate:
                                position = plate
                                cv2.destroyAllWindows()
                                in_cooking = 1
                                break
                            else:
                                play_error()
                                continue
                    elif txt == 'switch' or txt == 'scramble':
                        sabotage_penalty = sabotage_penalty + 1 #increase sabotage penalty
                        if txt == 'scramble':
                            sabatoge_send_vid.preview()
                            client.publish(str(flag_opponent)+'Team8', str(SCRAMBLE), qos=1)
                        elif txt == 'switch':
                            sabatoge_send_vid.preview()
                            client.publish(str(flag_opponent)+'Team8', str(SWITCH), qos=1)
                    else:   #reset speech_said boolean
                        speech_said = False
        ####################
        #PLAYER LOCALIZATION
        ####################

        ###############
        #PLAYER ACTIONS
        ###############
            if position == plate:
                #ask IMU for plate classifier data
                txt = '0'
                screen.blit(bg_tile,(0,0))
                screen.blit(msg_plate,(50,50))
                pygame.display.update()
                action = '0'
                while txt.lower() != 'shred' and txt.lower() != 'garnish':
                    if speech_said == True:
                        txt = from_speech()
                        if txt.lower() == 'shred' and int(action_to_do) == int(FLAG_SHRED): 
                            action = FLAG_SHRED
                            if practice_flag == 1:
                                shred_vid.preview()
                        elif txt.lower() == 'garnish' and int(action_to_do) == int(FLAG_GARNISH): 
                            action = FLAG_GARNISH
                            if practice_flag == 1:
                                garnish_vid.preview()
                        else:
                            txt = '0'   #reset for while loop
                            play_error()
                client.publish(str(flag_opponent)+'Team8',str(MESSAGE)+'Your opponent is plating',qos = 1)
                client.publish(str(flag_player)+'Team8B', str(action), qos=1)
                task(action)
                t.sleep(.2)
                client.publish(str(flag_player)+'Team8B', str(STOP), qos=1)
            elif position == stove:
                #ask IMU for stove classifier data
                txt = '0'
                screen.blit(bg_stove,(0,0))
                screen.blit(msg_stove,(50,50))
                pygame.display.update()
                action = '0'
                while txt.lower() != 'stir' and txt.lower() != 'pour':
                    if speech_said == True:
                        txt = from_speech()
                        if 'st' in txt:
                            txt = 'stir'
                        elif txt == 'sir' or txt == 'her' or txt == 'dirt' or txt == 'ter':
                            txt = 'stir'
                        elif txt == 'poor' or txt == '4' or txt == 'port' or txt == 'for' or txt == 'spore':
                            txt = 'pour'
                        if txt.lower() == 'stir' and int(action_to_do) == int(FLAG_STIR): 
                            action = FLAG_STIR
                            if practice_flag == 1:
                                stir_vid.preview()
                        elif txt.lower() == 'pour' and int(action_to_do) == int(FLAG_POURING): 
                            action = FLAG_POURING
                            if practice_flag == 1:
                                pour_vid.preview()
                        else:
                            txt = '0'   #reset for while loop
                            play_error()
                client.publish(str(flag_opponent)+'Team8',str(MESSAGE)+'Your opponent is at the stove',qos = 1)
                client.publish(str(flag_player)+'Team8B', str(action), qos=1)
                task(action)
                t.sleep(.2)
                client.publish(str(flag_player)+'Team8B', str(STOP), qos=1)
            elif position == board:
                #ask IMU for cutting classifier data
                txt = '0'
                screen.blit(bg_cuttingboard,(0,0))
                screen.blit(msg_cuttingboard,(50,50))
                pygame.display.update()
                action = '0'
                while txt.lower() != 'cut' and txt.lower() != 'roll':
                    if speech_said == True:
                        txt = from_speech()
                        if 'u' in txt or 'c' in txt:
                            txt = 'cut'
                        elif 'o' in txt:
                            txt = 'roll'
                        if txt.lower() == 'cut' and int(action_to_do) == int(FLAG_CUTTING): 
                            action = FLAG_CUTTING
                            if practice_flag == 1:
                                cut_vid.preview()
                        elif txt.lower() == 'roll' and int(action_to_do) == int(FLAG_ROLLING): 
                            action = FLAG_ROLLING
                            if practice_flag == 1:
                                roll_vid.preview()
                        else:
                            txt = '0'   #reset for while loop
                            play_error()
                client.publish(str(flag_opponent)+'Team8',str(MESSAGE)+'Your opponent is at the cutting board',qos = 1)
                client.publish(str(flag_player)+'Team8B', str(action), qos=1)
                task(action)
                t.sleep(.2)
                client.publish(str(flag_player)+'Team8B', str(STOP), qos=1)
            elif position == counter:
                #ask IMU for rolling classifier data
                txt = '0'
                screen.blit(bg_tile,(0,0))
                screen.blit(msg_counter,(50,50))
                pygame.display.update()
                action = '0'
                while txt.lower() != 'pour':
                    if speech_said == True:
                        txt = from_speech()
                        if txt == 'poor' or txt == '4' or txt == 'for' or txt == 'spore' or txt == 'port':
                            txt = 'pour'
                        if txt.lower() == 'pour' and int(action_to_do) == int(FLAG_POURING): 
                            action = FLAG_POURING
                            if practice_flag == 1:
                                pour_vid.preview()
                        else:
                            txt = '0'   #reset for while loop
                            play_error()
                client.publish(str(flag_opponent)+'Team8',str(MESSAGE)+'Your opponent is at the counter',qos = 1)
                client.publish(str(flag_player)+'Team8B', str(action), qos=1)
                task(action)
                t.sleep(.2)
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
        final_score = (500 - score) + (time_bonus * 10) + excellency_bonus - (sabotage_penalty * 10)
        final_score = int(final_score)
        if practice_flag == 1:
            displayScore()
        else:
            client.publish(str(flag_opponent)+'Team8', str(FLAG_SCORE) + str(score)+' '+str(sabotage_penalty)+' '+str(time_bonus)+' '+str(excellency_bonus), qos=1)
            while score_received == 0:
                loading.preview()
                pass
            displayScore()
            if final_score >= opp_final_score:
                win_vid.preview()
            else:
                lose_vid.preview()
        t.sleep(5)
        reset_vid.preview()
        txt = '0'
        speech_said = False
        while(txt.lower() != 'yes' and txt.lower() != 'no'):
            if speech_said == True:
                txt = from_speech()
                if 'e' in txt:
                    txt = 'yes'
                elif 'o' in txt:
                    txt = 'no'
                if txt.lower() == 'yes':
                    endloop = 0
                elif txt.lower() == 'no':
                    endloop = 1
                else:
                    txt = '0'
                speech_said = False
    client.loop_stop()
    client.disconnect()
    #########
    #GAME END
    #########

##################
#GAME STARTS HERE#
#GAME STARTS HERE#
#GAME STARTS HERE#
##################
if __name__ == '__main__':
    freeze_support()
    load_vids()
    #background_music = Process(target=multi_background_music, args=("sounds/background_music_italian.mp3",))
    #background_music.daemon = True
    #background_music.start()
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
    diffimg = pygame.image.load('images/difficulty_selection.png')
    finalscoreimg = pygame.image.load('images/final_score.png')

    #videos
    pygame.init()
    mixer.init()
    reset_vid = moviepy.editor.VideoFileClip('images/play_again.mp4')
    error_sound = pygame.mixer.Sound("sounds/error_sound.wav")
    intro = moviepy.editor.VideoFileClip('images/welcome_screen.mp4')
    loading = moviepy.editor.VideoFileClip('images/loading_screen.mp4')
    modvid = moviepy.editor.VideoFileClip('images/game_mode_selection_vid.mp4')
    calvid = moviepy.editor.VideoFileClip('images/calibration_instructions_vid.mp4')
    countdown = moviepy.editor.VideoFileClip('images/3_2_1.mp4')
    playvid = moviepy.editor.VideoFileClip('images/player_selection_vid.mp4')
    play1vid = moviepy.editor.VideoFileClip('images/player_1_selected.mp4')
    play2vid = moviepy.editor.VideoFileClip('images/player_2_selected.mp4')
    difficulty_sel_vid = moviepy.editor.VideoFileClip('images/difficulty_selection.mp4')
    difficulty_sel_vid1 = moviepy.editor.VideoFileClip('images/difficulty_selection1.mp4')
    difficulty_sel_vid2 = moviepy.editor.VideoFileClip('images/difficulty_selection2.mp4')
    difficulty_sel_vid3 = moviepy.editor.VideoFileClip('images/difficulty_selection3.mp4')
    switch_rec_vid = moviepy.editor.VideoFileClip('images/switch_sabotage.mp4')
    sabatoge_send_vid = moviepy.editor.VideoFileClip('images/send_sabotage.mp4')
    scramble_rec_vid = moviepy.editor.VideoFileClip('images/scramble_sabotage.mp4')
    cut_vid = moviepy.editor.VideoFileClip('images/loading_screen.mp4')
    stir_vid = moviepy.editor.VideoFileClip('images/loading_screen.mp4')
    roll_vid = moviepy.editor.VideoFileClip('images/loading_screen.mp4')
    pour_vid = moviepy.editor.VideoFileClip('images/loading_screen.mp4')
    shred_vid = moviepy.editor.VideoFileClip('images/loading_screen.mp4')
    garnish_vid = moviepy.editor.VideoFileClip('images/loading_screen.mp4')
    win_vid = moviepy.editor.VideoFileClip('images/win.mp4')
    lose_vid = moviepy.editor.VideoFileClip('images/lose.mp4')
    #videos

    #fonts
    pygame.font.init()
    myfont = pygame.font.Font('Georgia.ttf', 30)
    msg_plate = myfont.render('Say shred or garnish to start', False, (0,0,0))
    msg_stove = myfont.render('Say stir or pour to start', False, (0,0,0))
    msg_cuttingboard = myfont.render('Say cut or roll to start', False, (0,0,0))
    msg_counter = myfont.render('Say pour to start', False, (0,0,0))
    msg_good = myfont.render('Good job!', False, (0,0,0))
    smallFont = pygame.font.Font('Georgia.ttf', 25)
    completion= smallFont.render('You have completed this task!', False, (0,0,0))
    feedbackfont = pygame.font.Font('Bukhari Script.ttf', 100)
    bad_feedback = myfont.render('BAD', False, (0,0,0))
    good_feedback = myfont.render('GOOD', False, (0,0,0))
    excellent_feedback = myfont.render('EXCELLENT', False, (0,0,0))
    terrible_feedback = myfont.render('BRUH', False, (0,0,0))
    feedback_msg = bad_feedback
    msg_go = myfont.render('Say go to enter', False, (0,0,0))
    #fonts

    scorebreakimg = pygame.image.load('images/score_break.png')
    calculateimg = pygame.image.load('images/calculating_scores.png')
    opponentimg = pygame.image.load('images/opponent_score.png')
    opp_scorebreakimg = pygame.image.load('images/opp_score_break.png')
    scoring_vid0 = moviepy.editor.VideoFileClip('images/score1.mp4')
    scoring_vid1 = moviepy.editor.VideoFileClip('images/score2.mp4')
    opp_scoring_vid0 = moviepy.editor.VideoFileClip('images/opponent_score1.mp4')
    opp_scoring_vid1 = moviepy.editor.VideoFileClip('images/opponent_score2.mp4')

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