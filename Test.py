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
import pyaudio
import re 
import math
from pathlib import Path

p = pyaudio.PyAudio()
info = p.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')

for i in range(0, numdevices):
    if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
        print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))

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
pizza = np.array([['pizza','4','2','5t','3','5s','8','9']])
vegetable_soup = np.array([['vegetable soup','2','2','3','5','9']])
pasta = np.array([['pasta','5p','3','2','5t','3','5s','9']])
#recipe declarations
controller_speech = '0'
# player imaging class


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

    # moving left
        if (self.rect.x - x_pos) < 0:
            self.counter += 1
            self.direction = -1
        # moving right
        if (self.rect.x - x_pos) > 0:
            self.counter += 1
            self.direction = -1

        # handle animation
        if self.counter > walk_cooldown:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.images_right):
                self.index = 0
            if self.direction == 1:
                self.image = self.images_right[self.index]
            if self.direction == -1:
                self.image = self.images_left[self.index]

        # add gravity
        self.vel_y += 1
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        # check for collision

        # update player
        # print(dx)
        self.rect.x = x_pos - 150
        self.rect.y += dy

        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            dy = 0
# player imaging class

# pygame base code
# fonts
# pygame.font.init()
myfont = pygame.font.SysFont('Bukhari Script.ttf', 40)
msg_spoon = myfont.render('Say spoon to start', False, (0, 0, 0))
msg_knife = myfont.render('Say knife to start', False, (0, 0, 0))
msg_good = myfont.render('Good job!', False, (0, 0, 0))
smallFont = pygame.font.SysFont('Bukhari Script.ttf', 30)
completion = smallFont.render(
    'You have completed this task!', False, (0, 0, 0))
# fonts

def recipe_randomizer(difficulty):
    global all_recipes
    #length = len(all_recipes[0])
    global recipe_count
    recipe_count = 0
    if difficulty == 'hard':
        recipe_count = 5
    elif difficulty == 'normal':
        recipe_count = 4
    elif difficulty =='easy':
        recipe_count = 3
    for k in range(recipe_count):
        recipe = random.randint(1,2)  #randomization, will be replaced with a shuffle command (random.shuffle())
        if recipe == 1:
            all_recipes = np.append(all_recipes, pizza, axis=0)
        elif recipe == 2:
            all_recipes = np.append(all_recipes, pasta, axis=0)

def task(action):
    global speed
    global current_images
    action = int(action)
    string_action = classifier(action)
    size_of_vid = 0
    current_images.clear()
    win = pygame.display.set_mode(windowsize)
    if (string_action == 'Stir'):
        size_of_vid = load_vid("stir_sauce")
        #current_bg = bg_chopping
    elif(string_action == 'Cut'):
        size_of_vid = load_vid("chop_tomato")
        #current_bg = bg_stove
    elif(string_action == 'Pour'):
        size_of_vid = load_vid("pour_sauce")
        #current_bg = bg_pour
    speed = 1  # default
    for i in range(size_of_vid):
        #win.blit(current_bg, (0, 0))
        win.blit(current_images[i], (0, 0))
        print('blitting image: ' + str(i))
        #win.blit(msg_spoon, (50, 50))
        pygame.display.update()
        t.sleep(.1)

    t.sleep(1)
    return

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

file_pattern = re.compile(r'.*?(\d+).*?')
def get_order(file):
    match = file_pattern.match(Path(file).name)
    if not match:
        return math.inf
    return int(match.groups()[0])

def load_vid(pathname):
    global current_images
    current_graphics = sorted(glob.glob('animationPNGs/'+str(pathname) + '/*.png'),key = get_order)
    print(current_graphics)
    for i in current_graphics:
        current_images.append(pygame.image.load(i).convert())
    return len(current_images)

def main():
    task(2)

main()
