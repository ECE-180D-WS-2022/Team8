from email import message
from pickle import FALSE
from socketserver import ThreadingUnixDatagramServer
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

GOAL_STIR = 23
GOAL_CUTTING = 27
TOTAL_CUTTING = 1
TOTAL_STOVE = 1
CONTROLLER_BUFFER = 2
FLAG_START = '01'
FLAG_CUTTING = '02'
FLAG_STIR = '03'
FLAG_ROLLING = '04'
FLAG_POURING = '05'
FLAG_CHEESE = '08'
FLAG_GARNISH = '09'
STOP = '00'
SCRAMBLE = '13'
SWITCH = '14'
SCREEN_HEIGHT = 900
SCREEN_WIDTH = 1200

MESSAGE = '10'

FLAG_SCORE = '99'

#BOARD POSITIONS
cutting = 3
stove = 2
#BOARD POSITIONS

##CONST GLOBALS

#globals
recipe_count = 0
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
gamestart = 1
speech_said = False
timer_set = 0
timer_time = 0
timer_flag = 0
meh = 1
good = 2 
excellent = 3
current_images = []
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
all_recipes = np.empty((0,6), str)
pizza = np.array([['1','2','3','4','5','8']])
vegetable_soup = np.array([['1','2','2','3','5','9']])
pasta = np.array([['1','5','3','2','9','0']])
#recipe declarations

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

#pygame base code

#set title on window
pygame.display.set_caption("Chopping") 

#load images
bg_img = pygame.image.load('images/kitchen_half.png')
bg_img = pygame.transform.scale(bg_img, (1200, 900))
bg_chopping = pygame.image.load('images/chopping.png')
bg_chopping = pygame.transform.scale(bg_chopping, (1200, 900))
bg_stove = pygame.image.load('images/stir/background2.png')
board=pygame.image.load('images\cuttingboard3.png')

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
carrot_chop_vid = cv2.VideoCapture(" .mp4")
potato_chop_vid = cv2.VideoCapture(" .mp4")
stir_vid = cv2.VideoCapture(" .mp4")
pour_vid = cv2.VideoCapture(" .mp4")
#videos

#fonts
#pygame.font.init()
myfont = pygame.font.SysFont('Bukhari Script.ttf', 40)
msg_spoon= myfont.render('Say spoon to start', False, (0,0,0))
msg_knife= myfont.render('Say knife to start', False, (0,0,0))
msg_good = myfont.render('Good job!', False, (0,0,0))
smallFont = pygame.font.SysFont('Arial', 30)
completion= smallFont.render('You have completed this task!', False, (0,0,0))
#fonts           

def load_vid(pathname):
    global current_images
    current_graphics = glob.glob(str(pathname) +'/*.png')
    for i in current_graphics:
        current_images.append(pygame.image.load(current_graphics[i]))
    return len(current_images)
    
#vision processing code
def track_player():
    global x_pos
    global prev_x
    global prev_y
    global lower_thresh_player
    global upper_thresh_player
    while True:
        ret, frame = cap.read()
        frame = cv2.flip(frame,0)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
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
    surface = pygame.display.set_mode([1200,900])
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

def task(action, x, y, msg_begin):
    global speed
    global current_goal
    global current_images
    action = int(action)
    string_action = classifier(action)
    if (string_action == 'Stir'):
        load_vid()
        current_bg = bg_chopping
    elif(string_action == 'Cut'):
        current_vid = carrot_chop_vid
        current_bg = bg_stove
    elif(string_action == 'Pour'):
        current_vid = pour_vid
    speed = 1   #default
    i = 0
    drawBackground(current_bg, globals()['s1'], x, y, msg_begin)
    while (current_vid.isOpened()):
        ret, frame = cap.read()
     
    # This condition prevents from infinite looping
    # incase video ends.
        if ret == False:
            break
        if cv2.waitKey(25) & 0xFF == ord('q'): 
            break
        t.sleep(0.1)
        win.blit(current_bg, (0, 0))
        # cv2.imwrite('Frame'+str(i)+'.jpg', frame)
        # i += 1
        # frame_jpg = pygame.image.load('images\Frame'+str(i)+'.jpg')
        win.blit(globals()[frame], (x, y))
        pygame.display.update()

    t.sleep(1)
    return

def drawBackground(bg, action_frame, coord_x, coord_y, msg):
    win.fill(backgroundColor)
    win.blit(bg, (0, 0))
    win.blit(action_frame, (coord_x, coord_y))
    win.blit(msg, (200,50))
	 #draw progress bar outline
    pygame.draw.rect(win, black, pygame.Rect(349, 820, 500, 30),2 )
    pygame.display.update()

def taskCompleted(backdrop, action_frame, coord_x, coord_y, msg):
    drawBackground(backdrop, action_frame, coord_x, coord_y, msg)
    progressBarChops(1, 1)
    pygame.display.update()

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
    length = len(all_recipes[0])
    for k in range(recipe_count):
        if all_recipes[k][0][0] != '0':
            for i in range(1,length+1):
                if all_recipes[k][i][0] != '0':      #ignore 0 bit
                    if last_action == int(all_recipes[k][i]):
                        all_recipes[k][i] = '0' + str(timer_time)
                        if k == recipe_count - 1 and i == length:
                            in_cooking = 2  #game finished
                            all_recipes[k][0] = '0'
                        return
                    elif last_action != all_recipes[k][i]: #must do in order
                        print("Cowabummer, you did the wrong action. You need to " + classifier(int(all_recipes[k][i]))+ " next!")
                        return
            all_recipes[k][0] = '0'       #recipe done
    in_cooking = 2 #game finished

def recipe_randomizer(difficulty):  #randomize all recipe's length based off of difficulty
    global all_recipes
    length = len(all_recipes[0])
    global recipe_count
    recipe_count = 0
    if difficulty == 'hard':
        recipe_count = 5
    elif difficulty == 'normal':
        recipe_count = 4
    elif difficulty =='easy':
        recipe_count = 3
    for k in range(recipe_count):
        print('Recipe: '+ str(k+1))
        recipe = random.randint(1,3)  #randomization, will be replaced with a shuffle command (random.shuffle())
        if recipe == 1:
            all_recipes = np.append(all_recipes, pizza, axis=0)
        elif recipe == 2:
            all_recipes = np.append(all_recipes, vegetable_soup,axis=0)
        elif recipe == 3:
            all_recipes = np.append(all_recipes, pasta,axis=0)

def print_recipes():
    global all_recipes
    length = len(all_recipes[0])
    for k in range(len(all_recipes)):
        if all_recipes[k][0] != '0':
            print('Recipe: '+str(k+1))
            for i in range(1,length+1):
                print(str(i)+'. ' + classifier(int(all_recipes[k][i])))

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
    #data received as b'message'
    temporary = str(message.payload)
    message_received = temporary[4:-1]
    flag_received = temporary[2:4]
    print('flag received: '+ str(flag_received))
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
    r = sr.Recognizer()
    txt = '0'
    hello=sr.AudioFile('receive.wav')
    with hello as source:
        audio = r.record(source)
    try:
        s = r.recognize_google(audio)
        s = str(s)
        f = open('receive.wav','wb')
        f.truncate(0)
        return s
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
    action_time = threading.Thread(target=timer, args=(1,), daemon=True)
    player_mem = threading.Thread(target=track_player, daemon=True)
    action_time.start()
    player_mem.start()
    #both daemons will terminate upon the end of the program 
    ################
    #THREADING CALL
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
        txt = from_speech()
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
        txt = from_speech()
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
        print('Move left to go to the stove, Move right to go to the chopping board')
        clock = pygame.time.Clock()
        fps = 60
        playerimg = Playerimg(100, 900 - 130)
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Cooking Papa 1.0')
        speech_said = False
        #while True:
            # ret, frame = cap.read()
            # frame = cv2.flip(frame,0)
            # hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            # track_player(frame, lower_thresh_player, upper_thresh_player)
            # #define game variables
        while True:
            clock.tick(fps)
            screen.blit(bg_img, (0, 0))
            playerimg.update()
            screen.blit(playerimg.image, playerimg.rect)
            pygame.display.update()
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                #will only trigger/pause the code if speech is detected to have been said
            if speech_said == True:
                if x_pos > 800 and from_speech() == 'stove':
                    position = stove
                    end1 = t.time()
                    cv2.destroyAllWindows()
                    in_cooking = 1
                    break
                elif x_pos < 400 and from_speech() == 'cutting board':
                    position = cutting
                    end2 = t.time()
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
        if position == 2:
            #ask IMU for stove classifier data
            drawBackground(bg_stove, 340, 220, msg_spoon)
            txt = '0'
            while txt.lower() != 'spoon':
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
            timer_set = 1
            task(FLAG_STIR, bg_stove,340, 220, msg_spoon)
            last_action = int(FLAG_STIR)
            timer_set = 0
            client.publish(str(flag_player)+'Team8B', str(STOP), qos=1)
        elif position == 3:
            #ask IMU for cutting classifier data
            drawBackground(board, 200, 110, msg_knife)
            txt = '0'
            while txt.lower() != 'knife':
                print("Say knife to start cutting")
                txt = from_speech()
                if txt.lower() == 'night':   #common word
                    txt = 'knife'
        
            print('waiting for input')
            client.publish(str(flag_player)+'Team8B', str(FLAG_CUTTING), qos=1)
            t.sleep(CONTROLLER_BUFFER)
            client.publish(str(flag_opponent)+'Team8',str(MESSAGE) + 'Your opponent is at the stove', qos = 1)
            print('starting')
            timer_set = 1
            task(FLAG_CUTTING,board,200,110,msg_knife)
            timer_set = 0 
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