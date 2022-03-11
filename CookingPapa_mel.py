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
from pygame.locals import *
import cv2

GOAL_STOVE = 27
GOAL_CUTTING = 27
TOTAL_CUTTING = 1
TOTAL_STOVE = 1
IDEAL_SPIN = 1
IDEAL_CUT = 1
FLAG_START = '01'
FLAG_CUTTING = '02'
FLAG_STOVE = '03'
FLAG_ROLLING = '04'
FLAG_POURING = '05'
STOP = '00'
SCREEN_HEIGHT = 900
SCREEN_WIDTH = 1200

MESSAGE = '10'

FLAG_SCORE = '99'

#BOARD POSITIONS
CUTTING = 1
STOVE = -1
#BOARD POSITIONS

##CONST GLOBALS

#globals
position = 0
in_cooking = 0
start = t.time()
end = t.time()
diff = end - start
total_stove = 0
total_cutting = 0
flag_player = 0
flag_opponent = 0
flag_received = 0
score = 0
message_received = ''
speed = 1

#Vision processing code 
cap = cv2.VideoCapture(2)
init_cal = False
x_c_1 = 0
y_c_1 = 0
x_c_2 = 0
y_c_2 = 0
lower_thresh_LED = np.array([159, 80, 200]) #RED LED
upper_thresh_LED = np.array([180, 255, 255]) #RED LED
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
#look in same folder as script for images
c1 =pygame.image.load('images/choppingcarrot/cc1.png')
c2 =pygame.image.load('images/choppingcarrot/cc2.png')
c3 =pygame.image.load('images/choppingcarrot/cc3.png')
c4 =pygame.image.load('images/choppingcarrot/cc4.png')
c5 =pygame.image.load('images/choppingcarrot/cc5.png')
c6 =pygame.image.load('images/choppingcarrot/cc6.png')
c7 =pygame.image.load('images/choppingcarrot/cc7.png')
c8 =pygame.image.load('images/choppingcarrot/cc8.png')
c9 =pygame.image.load('images/choppingcarrot/cc9.png')
c10 =pygame.image.load('images/choppingcarrot/cc10.png')
c11 =pygame.image.load('images/choppingcarrot/cc11.png')
c12 =pygame.image.load('images/choppingcarrot/cc12.png')
c13 =pygame.image.load('images/choppingcarrot/cc13.png')
c14 =pygame.image.load('images/choppingcarrot/cc14.png')
c15 =pygame.image.load('images/choppingcarrot/cc15.png')
c16 =pygame.image.load('images/choppingcarrot/cc16.png')
c17 =pygame.image.load('images/choppingcarrot/cc17.png')
c18 =pygame.image.load('images/choppingcarrot/cc18.png')
c19 =pygame.image.load('images/choppingcarrot/cc19.png')
c20 =pygame.image.load('images/choppingcarrot/cc20.png')
c21 =pygame.image.load('images/choppingcarrot/cc21.png')
c22 =pygame.image.load('images/choppingcarrot/cc22.png')
c23 =pygame.image.load('images/choppingcarrot/cc23.png')
c24 =pygame.image.load('images/choppingcarrot/cc24.png')
c25 =pygame.image.load('images/choppingcarrot/cc25.png')
c26 =pygame.image.load('images/choppingcarrot/cc26.png')
c27 =pygame.image.load('images/choppingcarrot/cc27.png')
#knife = pygame.transform.scale(knife, (250, 220))
board=pygame.image.load('images/cuttingboard2.png')
#board = pygame.transform.scale(board, (300, 320))
bg_img = pygame.image.load('images/background.png')
bg_img = pygame.transform.scale(bg_img, (1200, 900))
bg_chopping = pygame.image.load('images/chopping.png')
bg_chopping = pygame.transform.scale(bg_chopping, (1200, 900))

pygame.font.init()
myfont = pygame.font.SysFont('Comic Sans MS', 40)

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
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_thresh_LED = np.array([0, 0, 250]) #LED
    upper_thresh_LED = np.array([179, 10, 255]) #LED

    mask = cv2.inRange(hsv, lower_thresh_LED, upper_thresh_LED)
    _, mask = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    #cv2.imshow('calibrating frame', frame)
    if counter == 1:
        print('stand in middle of frame and remain still during calibration')
    if counter == 25:
        print('hold led near top of right shoulder')
    for i in contours:
        #get rid of noise first by calculating area
        area = cv2.contourArea(i)
        if area > 100 and area < 400:
            #cv2.drawContours(frame, [i], -1, (0, 255, 0), 2)
            x, y, width, height = cv2.boundingRect(i)
            cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 255, 0), 3)
            x2 = x + width
            y2 = y + height
            if counter == 300:
                x_c_1 = x + (width//2)
                y_c_1 = x + (height//2)
                print('top right corner calibration complete')
                print('hold led near left hip')
            if counter == 600:
                x_c_2 = x + (width//2)
                y_c_2 = x + (height//2)
                print('bottom left corner calibration complete')
    if counter == 600 and (x_c_2-x_c_1 <= 0 or x_c_1 == 0 or x_c_2 == 0 or y_c_2-y_c_1 <= 0 or y_c_1 == 0 or y_c_2 == 0):
        print('calibration failed...try again')
        counter = 0

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
        if counter <= 601:
            get_calibration_frames(frame)
        elif counter == 602:
            print('calibrating...')
            t.sleep(3)
            calibrate(frame, x_c_1, y_c_1, x_c_2, y_c_2)
        elif counter > 602:
            print('exiting calibration...')
            return
        counter = counter+1
        cv2.imshow('calibrating frame', frame)
        # Display the resulting frames
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

#vision processing code
green = (2, 100,64)
black = (0,0,0)


def task(TIME):
    global speed
    #print('hi')
    speed = 1
    i = 0
    windowsize = (SCREEN_WIDTH, SCREEN_HEIGHT)
    win=pygame.display.set_mode(windowsize)
    while (TIME > i):
        i = i + speed
        t.sleep(1)
        print (speed)
        win.blit(board, (0, 0))
        var_name2 = "c"+str(i)
        pygame.draw.rect(win, black, pygame.Rect(299, 520, 500, 30),2 )
        x = round(i/27*10)-1
        pygame.draw.rect(win, green, pygame.Rect(300+(50*x), 521, 48, 28) )
        #print(var_name2)
        win.blit(globals()[var_name2], (300, 110))
        pygame.display.update()
    return

def check_game():
    global total_cutting
    global total_stove
    global in_cooking #trip the flag if the recipe is met
    if total_cutting >= TOTAL_CUTTING and total_stove >= TOTAL_STOVE:
        in_cooking = 2

def recipe_randomizer(difficulty):  #randomize all recipe's length based off of difficulty
    if difficulty == 'hard':
        length = 4
    elif difficulty == 'normal':
        length = 3
    elif difficulty == 'easy':
        length = 2
    global all_recipes
    for k in range(recipe_count):
        print('Recipe: '+ str(k+1))
        for i in range(1,length+1):     #length is not inclusive
            all_recipes[k][i] = random.randint(2,3)
            print(str(i)+'. '+ classifier(all_recipes[k][i])) 

def print_recipes():
    global recipe_count
    global all_recipes
    for k in range(recipe_count):
        print('Recipe: '+str(k+1))
        for i in range(1,5):
            print(str(i)+'. ' + classifier(all_recipes[k][i]))

def classifier(num):    #classify for user output
    if int(num) == int(FLAG_CUTTING):
        output = 'Cut'
    elif int(num) == int(FLAG_STOVE):
        output = 'Stir'
    return output

def on_connect(client, userdata, flags, rc):
    global flag_player
    global flag_opponent
    print("Connection returned result: "+str(rc))
    
# Subscribing in on_connect() means that if we lose the connection and
# reconnect then subscriptions will be renewed.
# client.subscribe("ece180d/test")
# The callback of the client when it disconnects.
    txt = '0'
    while(flag_player == 0):
        r = sr.Recognizer()
        print("Which player are you playing as, Player 1 or Player 2?")
        with sr.Microphone(device_index=1) as source:
            audio = r.listen(source,phrase_time_limit = 2)
        try:
            txt = r.recognize_google(audio)
            txt = str(txt)
            print("You said " + txt)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        if txt.lower() == 'player one' or txt.lower() == 'player won' or txt.lower() == 'player 1':
            flag_player = 1
            flag_opponent = 2
        elif txt.lower() == 'player two' or txt.lower() == 'player to' or txt.lower() == 'player too' or txt.lower() == 'player 2':
            flag_player = 2
            flag_opponent = 1
    client.subscribe(str(flag_player)+'Team8', qos=1)
    #subscribing to mqtt to receive IMU data
    #messages must only be received once hence qos is 2
    client.subscribe(str(flag_player)+'Team8A',qos=2)

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
    global position
    #data received as b'message'
    temporary = str(message.payload)
    message_received = temporary[4:-1]
    flag_received = temporary[2:4]
    #print('flag received: '+ str(flag_received))
    #print(temporary)
    #print(message_received)
    #score flag received
    if (str(flag_received) == str(FLAG_STOVE) and position == STOVE):
        speed = int(message_received)
    elif (str(flag_received) == str(FLAG_CUTTING) and position == CUTTING):
        speed = int(message_received)
    elif str(flag_received) == str(FLAG_SCORE):
        if in_cooking == 2:
            if 1000-float(score) > 1000-float(message_received):
                print('You are better than the other idiot sandwich. Congration.')
                print('Your score: '+str(float(score))+'\n'+"Your opponent's score: " + str(float(message_received)))
            else:
                print('You lost. Try a little harder next time would ya?')
                print('Your score: '+str(float(score))+'\n'+"Your opponent's score: " + str(float(message_received)))
            client.loop_stop()
            client.disconnect()
    elif flag_received == str(MESSAGE):
        print(str(message_received))
#
#GAME STARTS HERE
#GAME STARTS HERE
#GAME STARTS HERE
#
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
##CONST GLOBALS
def main():
    global score
    global in_cooking
    global flag_opponent
    global flag_player
    global total_stove
    global total_cutting
    global x_pos
    global position
    #wait for player selection
    while(flag_player==0):
        pass
    t.sleep(1)
    print('Welcome to Cooking Papa!')
    #publish again in case of second to enter lobby

    #CALIBRATION PHASE
    calibration()
    cv2.destroyAllWindows()
    #CALIBRATION PHASE

    #STARTING SCREEN
    r = sr.Recognizer()
    print('Say Practice to practice and Fight to play against an opponent')
    txt = '0'
    while txt.lower() != 'practice' and txt.lower() != 'fight':
        with sr.Microphone(device_index=1) as source:
            audio = r.listen(source,phrase_time_limit = 2)
        try:
            txt = r.recognize_google(audio)
            txt = str(txt)
            print("You said " + txt)
            if txt == 'bracket':  #common word
                txt = 'practice'
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
    if txt.lower() == 'practice':
        flag_received = 99
    elif txt.lower() == 'fight':
        flag_received = 0
        client.publish(str(flag_opponent)+'Team8',str(FLAG_START)+'gamestart',qos=1)
    while(flag_received==0):
        pass
    #STARTING SCREEN

    #WAITING FOR OPPONENT
    t.sleep(2)
    client.publish(str(flag_opponent)+'Team8', str(FLAG_START)+'gamestart',qos=1)
    r = sr.Recognizer()
    if txt.lower() == 'practice':
        txt = 'ready'
    else:
        txt = '0'
    print("Say Ready to begin")
    while txt.lower() != 'ready':
        with sr.Microphone(device_index=1) as source:
            audio = r.listen(source,phrase_time_limit = 2)
        try:
            txt = r.recognize_google(audio)
            txt = str(txt)
            print("You said " + txt)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
    #WAITING FOR OPPONENT

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

    #PLAYER LOCALIZATION   
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
    #PLAYER LOCALIZATION

        in_cooking = 1
        if position == STOVE:
            #ask IMU for stove classifier data
            r = sr.Recognizer()
            print("Say spoon to start stirring")
            txt = '0'
            while txt.lower() == 'spoon':
                with sr.Microphone(device_index=1) as source:
                    audio = r.listen(source,phrase_time_limit = 2)
                try:
                    txt = r.recognize_google(audio)
                    txt = str(txt)
                    print("You said " + txt)
                except sr.UnknownValueError:
                    print("Google Speech Recognition could not understand audio")
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
            client.publish(str(flag_player)+'Team8B', str(FLAG_STOVE), qos=1)
            t.sleep(5)
            client.publish(str(flag_opponent)+'Team8',str(MESSAGE) + 'Your opponent is at the stove', qos = 1)
            print('starting')
            task(GOAL_STOVE)
            total_stove = total_stove + 1
            client.publish(str(flag_player)+'Team8B', str(STOP), qos=1)

        elif position == CUTTING:
            #ask IMU for cutting classifier data
            r = sr.Recognizer()
            print("Say knife to start cutting")
            txt = '0'
            while txt.lower() == 'knife':
                with sr.Microphone(device_index=1) as source:
                    audio = r.listen(source,phrase_time_limit = 2)
                try:
                    txt = r.recognize_google(audio)
                    txt = str(txt)
                    print("You said " + txt)
                except sr.UnknownValueError:
                    print("Google Speech Recognition could not understand audio")
                if txt.lower() == 'night':   #common word
                    txt = 'knife'
            print('waiting for input')
            client.publish(str(flag_player)+'Team8B', str(FLAG_CUTTING), qos=1)
            t.sleep(5)
            client.publish(str(flag_opponent)+'Team8',str(MESSAGE) + 'Your opponent is at the stove', qos = 1)
            print('starting')
            task(GOAL_CUTTING)
            total_cutting = total_cutting + 1
            client.publish(str(flag_player)+'Team8B', str(STOP), qos=1)
        in_cooking = 0

        #game ending conditions
        check_game()
    end_game = t.time()
    score = end_game-start_game
    print('Your time was: ' + str(score))
    client.publish(str(flag_opponent)+'Team8', str(FLAG_SCORE)+str(score), qos=1)
    print("waiting for opponent's time...")
    while True:
        pass
main()
