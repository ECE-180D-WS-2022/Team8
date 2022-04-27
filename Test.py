from email import message
from pickle import FALSE
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
SCREEN_HEIGHT = 800
SCREEN_WIDTH = 1200

MESSAGE = '10'

FLAG_SCORE = '99'

# BOARD POSITIONS
cutting = 3
stove = 2
# BOARD POSITIONS

# CONST GLOBALS

# globals
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
# colors
backgroundColor = (255, 255, 255)
green = (2, 100, 64)
black = (0, 0, 0)
# window
windowsize = (SCREEN_WIDTH, SCREEN_HEIGHT)
win = pygame.display.set_mode(windowsize)

# Vision processing code
init_cal = False
x_c_1 = 0
y_c_1 = 0
x_c_2 = 0
y_c_2 = 0
counter = 0
x_pos = 0

# recipe declarations
all_recipes = np.empty((0, 6), str)
pizza = np.array([['1', '2', '3', '4', '5', '8']])
vegetable_soup = np.array([['1', '2', '2', '3', '5', '9']])
pasta = np.array([['1', '5', '3', '2', '9', '0']])
# recipe declarations

controller_speech = '0'
# globals

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


# set title on window
pygame.display.set_caption("Chopping")

# load images
bg_img = pygame.image.load('images/kitchen_half.png')
bg_img = pygame.transform.scale(bg_img, windowsize)
bg_chopping = pygame.image.load('backgrounds/cuttingboard.png')
bg_chopping = pygame.transform.scale(bg_chopping, windowsize)
bg_stove = pygame.image.load('backgrounds/stove.png')
bg_stove = pygame.transform.scale(bg_stove, windowsize)
bg_pour = pygame.image.load('backgrounds/tile.png')
bg_pour = pygame.transform.scale(bg_pour, windowsize)

vs_score = pygame.image.load('images/score_page.png')
vs_score_opp = pygame.image.load('images/score_page_opp.png')

calimg = pygame.image.load('images/calibration_instructions.png')
modimg = pygame.image.load('images/game_mode_selection.png')
playimg = pygame.image.load('images/player_selection.png')

# videos
pygame.init()
pygame.mixer.quit()
intro = moviepy.editor.VideoFileClip('images/welcome_screen.mp4')
loading = moviepy.editor.VideoFileClip('images/loading_screen.mp4')
modvid = moviepy.editor.VideoFileClip('images/game_mode_selection_vid.mp4')
calvid = moviepy.editor.VideoFileClip(
    'images/calibration_instructions_vid.mp4')
countdown = moviepy.editor.VideoFileClip('images/3_2_1.mp4')
playvid = moviepy.editor.VideoFileClip('images/player_selection_vid.mp4')
play1vid = moviepy.editor.VideoFileClip('images/player_1_selected.mp4')
play2vid = moviepy.editor.VideoFileClip('images/player_2_selected.mp4')
# videos

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


def task(action, msg_begin):
    global speed
    global current_images
    action = int(action)
    string_action = classifier(action)
    size_of_vid = 0
    current_images.clear()
    win = pygame.display.set_mode(windowsize)
    if (string_action == 'Stir'):
        size_of_vid = load_vid("stirsauce")
        current_bg = bg_chopping
    elif(string_action == 'Cut'):
        size_of_vid = load_vid("choptomato")
        current_bg = bg_stove
    elif(string_action == 'Pour'):
        size_of_vid = load_vid("poursauce")
        current_bg = bg_pour
    speed = 1  # default
    for i in range(size_of_vid):
        win.blit(current_bg, (0, 0))
        win.blit(current_images[i], (0, 0))
        win.blit(msg_spoon, (50, 50))
        pygame.display.update()
        t.sleep(0.05)

    t.sleep(1)
    return


def classifier(num):  # classify for user output
    global current_goal
    if int(num) == int(FLAG_CUTTING):
        output = 'Cut'
    elif int(num) == int(FLAG_STIR):
        output = 'Stir'
    elif int(num) == 0:
        output = 'DONE'
    return output


def load_vid(pathname):
    global current_images
    current_graphics = glob.glob(str(pathname) + '/*.png')
    for i in current_graphics:
        current_images.append(pygame.image.load(i))
    return len(current_images)


def main():
    y = 10
    while y == 10:
        print(y)
        if y == 10:
            y = 11
            if y == 11:
                y = 10
                continue
                y = 11
            y = 11
        y = 11


main()
