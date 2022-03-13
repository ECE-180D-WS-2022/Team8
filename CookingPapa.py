from email import message
from pickle import FALSE
from pynput import keyboard
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

GOAL_STIR = 23
GOAL_CUTTING = 27
TOTAL_CUTTING = 1
TOTAL_STOVE = 1
CONTROLLER_BUFFER = 3
FLAG_START = '01'
FLAG_CUTTING = '02'
FLAG_STIR = '03'
FLAG_ROLLING = '04'
FLAG_POURING = '05'
STOP = '00'
SCREEN_HEIGHT = 900
SCREEN_WIDTH = 1200

MESSAGE = '10'

FLAG_SCORE = '99'

#BOARD POSITIONS
CUTTING = 3
STOVE = 2
#BOARD POSITIONS

##CONST GLOBALS

#globals
position = 0
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
length = 0

#colors
backgroundColor=(255, 255, 255)
green = (2, 100,64)
black = (0,0,0)
#window
windowsize = (SCREEN_WIDTH, SCREEN_HEIGHT)
win=pygame.display.set_mode(windowsize)

#Vision processing code 
cap = cv2.VideoCapture(2)
init_cal = False
x_c_1 = 0
y_c_1 = 0
x_c_2 = 0
y_c_2 = 0
counter = 0 
x_pos  = 0
recipe_count = 2

all_recipes = np.zeros((recipe_count,5), dtype = int)
#globals

#player imaging class
class Playerimg():
	def __init__(self, x, y):
		self.images_right = []
		self.images_left = []
		self.index = 0
		self.counter = 0
		for num in range(1, 5):
			img_right = pygame.image.load(f'img/chef{num}.png')
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
		self.rect.x = x_pos
		self.rect.y += dy

		if self.rect.bottom > SCREEN_HEIGHT:
			self.rect.bottom = SCREEN_HEIGHT
			dy = 0
#player imaging class

#pygame base code

#set title on window
pygame.display.set_caption("Chopping") 

#load images
bg_img = pygame.image.load('images/kitchen_half.png')
bg_img = pygame.transform.scale(bg_img, (1200, 900))
bg_chopping = pygame.image.load('images/chopping.png')
bg_chopping = pygame.transform.scale(bg_chopping, (1200, 900))
bg_stove = pygame.image.load('images/stir/background2.png')

c1 =pygame.image.load('images/choppingcarrot_resize/cc1.png')
c2 =pygame.image.load('images/choppingcarrot_resize/cc2.png')
c3 =pygame.image.load('images/choppingcarrot_resize/cc3.png')
c4 =pygame.image.load('images/choppingcarrot_resize/cc4.png')
c5 =pygame.image.load('images/choppingcarrot_resize/cc5.png')
c6 =pygame.image.load('images/choppingcarrot_resize/cc6.png')
c7 =pygame.image.load('images/choppingcarrot_resize/cc7.png')
c8 =pygame.image.load('images/choppingcarrot_resize/cc8.png')
c9 =pygame.image.load('images/choppingcarrot_resize/cc9.png')
c10 =pygame.image.load('images/choppingcarrot_resize/cc10.png')
c11 =pygame.image.load('images/choppingcarrot_resize/cc11.png')
c12 =pygame.image.load('images/choppingcarrot_resize/cc12.png')
c13 =pygame.image.load('images/choppingcarrot_resize/cc13.png')
c14 =pygame.image.load('images/choppingcarrot_resize/cc14.png')
c15 =pygame.image.load('images/choppingcarrot_resize/cc15.png')
c16 =pygame.image.load('images/choppingcarrot_resize/cc16.png')
c17 =pygame.image.load('images/choppingcarrot_resize/cc17.png')
c18 =pygame.image.load('images/choppingcarrot_resize/cc18.png')
c19 =pygame.image.load('images/choppingcarrot_resize/cc19.png')
c20 =pygame.image.load('images/choppingcarrot_resize/cc20.png')
c21 =pygame.image.load('images/choppingcarrot_resize/cc21.png')
c22 =pygame.image.load('images/choppingcarrot_resize/cc22.png')
c23 =pygame.image.load('images/choppingcarrot_resize/cc23.png')
c24 =pygame.image.load('images/choppingcarrot_resize/cc24.png')
c25 =pygame.image.load('images/choppingcarrot_resize/cc25.png')
c26 =pygame.image.load('images/choppingcarrot_resize/cc26.png')
c27 =pygame.image.load('images/choppingcarrot_resize/cc27.png')
board=pygame.image.load('images\cuttingboard3.png')

#stirring photos
s1 =pygame.image.load('images/stir/s1.png')
s2 =pygame.image.load('images/stir/s2.png')
s3 =pygame.image.load('images/stir/s3.png')
s4 =pygame.image.load('images/stir/s4.png')
s5 =pygame.image.load('images/stir/s5.png')
s6 =pygame.image.load('images/stir/s6.png')
s7 =pygame.image.load('images/stir/s7.png')
s8 =pygame.image.load('images/stir/s8.png')
s9 =pygame.image.load('images/stir/s9.png')
s10 =pygame.image.load('images/stir/s10.png')
s11 =pygame.image.load('images/stir/s11.png')
s12 =pygame.image.load('images/stir/s12.png')
s13 =pygame.image.load('images/stir/s13.png')
s14 =pygame.image.load('images/stir/s14.png')
s15 =pygame.image.load('images/stir/s15.png')
s16 =pygame.image.load('images/stir/s16.png')
s17 =pygame.image.load('images/stir/s17.png')
s18 =pygame.image.load('images/stir/s18.png')
s19 =pygame.image.load('images/stir/s19.png')
s20 =pygame.image.load('images/stir/s20.png')
s21 =pygame.image.load('images/stir/s21.png')
s22 =pygame.image.load('images/stir/s22.png')
s23 =pygame.image.load('images/stir/s23.png')
fire =pygame.image.load('images/stir/fire.png')
#stirring photos

vs_score = pygame.image.load('images/score_page.png')

poc1 = pygame.image.load('images/pour/poc1.png')
poc2 = pygame.image.load('images/pour/poc2.png')
poc3 = pygame.image.load('images/pour/poc3.png')
poc4 = pygame.image.load('images/pour/poc4.png')
poc5 = pygame.image.load('images/pour/poc5.png')
poc6 = pygame.image.load('images/pour/poc6.png')
poc7 = pygame.image.load('images/pour/poc8.png')
poc8 = pygame.image.load('images/pour/poc8.png')
poc9 = pygame.image.load('images/pour/poc9.png')
poc10 = pygame.image.load('images/pour/poc10.png')
poc11 = pygame.image.load('images/pour/poc11.png')
poc12 = pygame.image.load('images/pour/poc12.png')
poc13 = pygame.image.load('images/pour/poc13.png')

calimg = pygame.image.load('images/calibration_instructions.png')
modimg = pygame.image.load('images/game_mode_selection.png')
playimg = pygame.image.load('images/player_selection.png')
play1img = pygame.image.load('images/player1_selected.png')
play2img = pygame.image.load('images/player2_selected.png')
#videos
pygame.init()
pygame.mixer.quit()
intro = moviepy.editor.VideoFileClip('images/welcome_screen.mp4')
loading = moviepy.editor.VideoFileClip('images/loading_screen.mp4')


#fonts
#pygame.font.init()
myfont = pygame.font.SysFont('Arial', 40)
msg_spoon= myfont.render('Say spoon to start', False, (0,0,0))
msg_knife= myfont.render('Say knife to start', False, (0,0,0))
msg_good = myfont.render('Good job!', False, (0,0,0))
smallFont = pygame.font.SysFont('Arial', 30)
completion= smallFont.render('You have completed this task!', False, (0,0,0))

#vision processing code

def track_player(frame, lower_thresh_player, upper_thresh_player):
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
            x_pos = (x + int(w/2))*2

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
    while (True):
        ret, frame = cap.read()
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
        cv2.imshow('calibrating frame', frame)
        # Display the resulting frames
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

#vision processing code

def progressBarChops(current, total):
    #increment progress bar
    pygame.draw.rect(win, black, pygame.Rect(349, 820, 500, 30),2 )
    #increment progress bars
    x = round(current/total*10)
    for t in range(0,x):
        pygame.draw.rect(win, green, pygame.Rect(350+(50*t), 821, 48, 28) )

def task(action, back, x, y, msg_begin):
    global speed
    global current_goal
    action = int(action)
    string_action = classifier(action)
    
    if (string_action == 'Stir'):
        letter="s"
    elif(string_action == 'Cut'):
        letter="c"

    speed = 1   #default
    i = 0
    ##windowsize = (SCREEN_WIDTH, SCREEN_HEIGHT)
    ##win=pygame.display.set_mode(windowsize)
    drawBackground(back, globals()[letter+'1'], x, y, msg_begin)
    while (current_goal > i):
        i = i + speed
        t.sleep(0.01)
        print (speed)
        win.blit(back, (0, 0))
        var_name2 = letter+str(i)
        #print(var_name2)
        win.blit(globals()[var_name2], (x, y))
        progressBarChops(i, current_goal)
        pygame.display.update()
    

    taskCompleted(back, globals()[letter+str(current_goal)], x, y, completion)

    t.sleep(1)
    return

def drawBackground(back, action_frame, coord_x, coord_y, msg):
    win.fill(backgroundColor)
    win.blit(back, (0, 0))
    win.blit(action_frame, (coord_x, coord_y))
    win.blit(msg, (200,50))
	 #draw progress bar outline
    pygame.draw.rect(win, black, pygame.Rect(349, 820, 500, 30),2 )
    pygame.display.update()

def taskCompleted(backdrop, action_frame, coord_x, coord_y, msg):
    drawBackground(backdrop, action_frame, coord_x, coord_y, msg)
    progressBarChops(1, 1)
    pygame.display.update()

def displayScore(score, feedback):
    msg_score= myfont.render(str(round(score)), False, (0,0,0))
    msg_feedback= myfont.render(feedback, False, (0,0,0))
    str(round(score))
    win.blit(vs_score, (0,0))
    win.blit(msg_score, (900,670))
    win.blit(msg_feedback, (350,400))
    pygame.display.update()

def pourCarrots():
    for i in range(1,14):
       # print('it:'+str(it))
        t.sleep(0.1)
        win.blit(bg_stove, (0, 0))
        win.blit(s1, (340, 220))
	    #draw progress bar outline
        pygame.draw.rect(win, black, pygame.Rect(349, 820, 500, 30),2 )
        var_name1 = "poc"+str(i)
        win.blit(globals()[var_name1], (450, 50))
        pygame.display.update()

def check_game():
    global all_recipes
    global recipe_count
    global in_cooking #trip the flag if the recipe is met
    global last_action
    for k in range(recipe_count):
        if all_recipes[k][0] != 0:
            for i in range(1,length+1):
                if all_recipes[k][i] != 0:      #ignore 0 bit
                    if last_action == all_recipes[k][i]:
                        all_recipes[k][i] = 0
                        if k == recipe_count - 1 and i == length:
                            in_cooking = 2  #game finished
                            all_recipes[k][0] = 0
                        return
                    elif last_action != all_recipes[k][i]: #must do in order
                        print("Cowabummer, you did the wrong action. You need to " + classifier(all_recipes[k][i])+ " next!")
                        return
            all_recipes[k][0] = 0       #recipe done
    in_cooking = 2 #game finished

def recipe_randomizer(difficulty):  #randomize all recipe's length based off of difficulty
    global length
    if difficulty == 'hard':
        length = 4
    elif difficulty == 'normal':
        length = 3
    elif difficulty == 'easy':
        length = 2
    global all_recipes
    for k in range(recipe_count):
        print('Recipe: '+ str(k+1))
        all_recipes[k][0] = 1
        for i in range(1,length+1):     #length is not inclusive
            all_recipes[k][i] = random.randint(2,3)
            print(str(i)+'. '+ classifier(all_recipes[k][i])) 

def print_recipes():
    global recipe_count
    global all_recipes
    for k in range(recipe_count):
        if all_recipes[k][0] != 0:
            print('Recipe: '+str(k+1))
            for i in range(1,5):
                print(str(i)+'. ' + classifier(all_recipes[k][i]))

def classifier(num):    #classify for user output
    global current_goal
    if int(num) == int(FLAG_CUTTING):
        output = 'Cut'
        current_goal = GOAL_CUTTING
    elif int(num) == int(FLAG_STIR):
        output = 'Stir'
        current_goal = GOAL_STIR
    elif int(num) == 0:
        output = 'DONE'
    return output

def check_action(action):
    global all_recipes

def on_connect(client, userdata, flags, rc):
    global flag_player
    global flag_opponent
    print("Connection returned result: "+str(rc))
    
# Subscribing in on_connect() means that if we lose the connection and
# reconnect then subscriptions will be renewed.
# client.subscribe("ece180d/test")
# The callback of the client when it disconnects.

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
    #data received as b'message'
    temporary = str(message.payload)
    message_received = temporary[4:-1]
    flag_received = temporary[2:4]
    print('flag received: '+ str(flag_received))
    #print(temporary)
    #print(message_received)
    #score flag received
    if (str(flag_received) == str(FLAG_STIR)):
        speed = int(message_received)
    elif (str(flag_received) == str(FLAG_CUTTING)):
        speed = int(message_received)
    elif str(flag_received) == str(FLAG_SCORE):
        if in_cooking == 2:
            if 1000-float(score) > 1000-float(message_received):
                displayScore(score, 'You are better than the other idiot sandwich. Congration.')
                #print('You are better than the other idiot sandwich. Congration.')
                #print('Your score: '+str(float(score))+'\n'+"Your opponent's score: " + str(float(message_received)))
            else:
                displayScore(score, 'You lost. Try a little harder next time would ya?')
                print('You lost. Try a little harder next time would ya?')
                print('Your score: '+str(float(score))+'\n'+"Your opponent's score: " + str(float(message_received)))
            client.loop_stop()
            client.disconnect()
    elif flag_received == str(MESSAGE):
        print(str(message_received))

def from_speech():
    r = sr.Recognizer()
    txt = '0'
    with sr.Microphone(device_index=1) as source:
        audio = r.listen(source,phrase_time_limit = 1.25)
    try:
        txt = r.recognize_google(audio)
        txt = str(txt)
        return txt
    except sr.UnknownValueError:
        txt = '0'
        return txt

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
    #####################
    #GLOBAL DECLARATIONS
    #####################
    intro.preview()
    t.sleep(1)
    print('Welcome to Cooking Papa!')
    loading.preview()
    t.sleep(3)
    #

    ##################
    #CALIBRATION PHASE
    ##################
    calibration()
    cv2.destroyAllWindows()
    ##################
    #CALIBRATION PHASE
    ##################

    ################
    #STARTING SCREEN
    ################
    txt = '0'
    while txt.lower() != 'practice' and txt.lower() != 'fight':
        print('Say Practice to practice and Fight to play against an opponent')
        #win.blit(intro, (0,0))
        txt = "practice"#from_speech()
        if txt == 'brackets':  #common word
            txt = 'practice'
    ################
    #STARTING SCREEN
    ################

    #####################
    #WAITING FOR OPPONENT
    #####################
    if txt.lower() == 'practice':
        flag_player = 1
    else:
        
    while(flag_player == 0):
        win.blit(playimg,(0,0))
        pygame.display.update()
        #print("Which player are you playing as, Player 1 or Player 2?")
        txt = from_speech()
        if txt.lower() == 'player one' or txt.lower() == 'player won' or txt.lower() == 'player 1':
            flag_player = 1
            flag_opponent = 2
            play1img.preview()
        elif txt.lower() == 'player two' or txt.lower() == 'player to' or txt.lower() == 'player too' or txt.lower() == 'player 2':
            flag_player = 2
            flag_opponent = 1
            play2img.preview()
    client.subscribe(str(flag_player)+'Team8', qos=1)
    #subscribing to mqtt to receive IMU data
    #messages must only be received once hence qos is 2
    client.subscribe(str(flag_player)+'Team8A',qos=2)
    #####################
    #WAITING FOR OPPONENT
    #####################

    print("Let's Begin, Timer starts in...")
    print("3")
    t.sleep(1)
    print("2")
    t.sleep(1)
    print("1")
    t.sleep(1)
    print("GO!")
    start_game = t.time()
    print('Randomizing Recipes: ')
    recipe_randomizer('hard') 

    ####################
    #PLAYER LOCALIZATION
    ####################   
    while(in_cooking != 2):
        print('Move left to go to the stove, Move right to go to the chopping board')
        clock = pygame.time.Clock()
        fps = 60
        playerimg = Playerimg(100, 900 - 130)
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Cooking Papa 1.0')
        while True:
            ret, frame = cap.read()
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            track_player(frame, lower_thresh_player, upper_thresh_player)
            #define game variables
            clock.tick(fps)
            screen.blit(bg_img, (0, 0))
            playerimg.update()
            screen.blit(playerimg.image, playerimg.rect)
            pygame.display.update()
            cv2.imshow('calibrating frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            if x_pos > 1200:
                position = STOVE
                cv2.destroyAllWindows()
                break
            elif x_pos < 400: 
                position = CUTTING
                cv2.destroyAllWindows()
                break
    ####################
    #PLAYER LOCALIZATION
    ####################
        position = random.randint(2,3)
    ###############
    #PLAYER ACTIONS
    ###############
        in_cooking = 1
        if position == STOVE:
            #ask IMU for stove classifier data
            pourCarrots()
            drawBackground(bg_stove, s1, 340, 220, msg_spoon)
            txt = '0'
            while txt.lower() == 'spoon':
                print("Say 'spoon' to start stirring")
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
            print('waiting for input')
            client.publish(str(flag_player)+'Team8B', str(FLAG_STIR), qos=1)
            t.sleep(CONTROLLER_BUFFER)
            client.publish(str(flag_opponent)+'Team8',str(MESSAGE) + 'Your opponent is at the stove', qos = 1)
            print('starting')
            task(FLAG_STIR, bg_stove,340, 220, msg_spoon)
            last_action = int(FLAG_STIR)
            client.publish(str(flag_player)+'Team8B', str(STOP), qos=1)

        elif position == CUTTING:
            #ask IMU for cutting classifier data
            drawBackground(board, c1, 200, 110, msg_knife)
            txt = '0'
            while txt.lower() == 'knife':
                print("Say knife to start cutting")
                txt = from_speech()
                if txt.lower() == 'night':   #common word
                    txt = 'knife'
        
            print('waiting for input')
            client.publish(str(flag_player)+'Team8B', str(FLAG_CUTTING), qos=1)
            t.sleep(CONTROLLER_BUFFER)
            client.publish(str(flag_opponent)+'Team8',str(MESSAGE) + 'Your opponent is at the stove', qos = 1)
            print('starting')
            task(FLAG_CUTTING, board,200, 110,msg_knife)
            last_action = int(FLAG_CUTTING)
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
    displayScore(score, 'Good Job!')
    client.publish(str(flag_opponent)+'Team8', str(FLAG_SCORE)+str(score), qos=1)
    #########
    #GAME END
    #########
    print("waiting for opponent's time...")
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
main()


