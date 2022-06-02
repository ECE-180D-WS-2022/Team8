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
sabotage_penalty = 7
time_bonus = 3
excellency_bonus = 125.23123123132
score = 135.462131231231
timer_time = 0
final_score = (500 - score) + (time_bonus * 10) + excellency_bonus - (sabotage_penalty * 10)
time_bonus = '+ ' + str(time_bonus) + ' x 10'
sabotage_penalty = '- ' + str(sabotage_penalty) + ' x 10'
excellency_bonus = '+ ' + str(int(excellency_bonus))
score = str(int(score)) + ' s'

SCREEN_HEIGHT = 800
SCREEN_WIDTH = 1200
windowsize = (SCREEN_WIDTH, SCREEN_HEIGHT)
win=pygame.display.set_mode(windowsize)
pygame.init()
mixer.init()
scoring_vid0 = moviepy.editor.VideoFileClip('images/score1.mp4')
scoring_vid1 = moviepy.editor.VideoFileClip('images/score2.mp4')

finalfont = pygame.font.Font('Bukhari Script.ttf', 120)
pygame.font.init()
myfont = pygame.font.Font('Georgia.ttf', 30)
msg_plate = myfont.render('Say shred or garnish to start', False, (0,0,0))
msg_stove = myfont.render('Say stir or pour to start', False, (0,0,0))
msg_cuttingboard = myfont.render('Say cut or roll to start', False, (0,0,0))
msg_counter = myfont.render('Say pour to start', False, (0,0,0))
msg_good = myfont.render('Good job!', False, (0,0,0))
smallFont = pygame.font.Font('Georgia.ttf', 25)
completion= smallFont.render('You have completed this task!', False, (0,0,0))
current_msg = myfont.render('Say spoon to start', False, (0,0,0))
bad_feedback = myfont.render('Do you know how to cook???', False, (0,0,0))
good_feedback = myfont.render('Ok not bad, bad', False, (0,0,0))
excellent_feedback = myfont.render('OK GORDON RAMSEY', False, (0,0,0))
terrible_feedback = myfont.render('WRONG', False, (0,0,0))
feedback_msg = bad_feedback
msg_go = myfont.render('Say go to enter', False, (0,0,0))
msg_finalscore = finalfont.render(str(int(final_score)), False, (236, 233, 218))

scorefont = pygame.font.Font('Bukhari Script.ttf', 72)
msg_time_bonus = scorefont.render(str(time_bonus),False,(236, 233, 218))
msg_time_bonus2 = scorefont.render(str(time_bonus),False,(187, 56, 49))
msg_excellency_bonus = scorefont.render(str(excellency_bonus),False,(236, 233, 218))
msg_excellency_bonus2 = scorefont.render(str(excellency_bonus),False,(187, 56, 49))
msg_sabotage_penalty = scorefont.render(str(sabotage_penalty),False,(236, 233, 218))
msg_sabotage_penalty2 = scorefont.render(str(sabotage_penalty),False,(187, 56, 49))
msg_score = scorefont.render(str(score),False,(236, 233, 218))
msg_score2 = scorefont.render(str(score),False,(187, 56, 49))

calimg = pygame.image.load('images/calibration_instructions.png')
modimg = pygame.image.load('images/game_mode_selection.png')
scorebreakimg = pygame.image.load('images/score_break.png')
calculateimg = pygame.image.load('images/calculating_scores.png')
finalscoreimg = pygame.image.load('images/final_score.png')

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
scoring_vid1.preview()
win.blit(finalscoreimg,(0,0))
win.blit(msg_finalscore,(470,400))
pygame.display.update()

t.sleep(10)


