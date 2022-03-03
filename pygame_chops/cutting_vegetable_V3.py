'''
In this program, press 's' to begin and '1' '2' or '3' to adjust the speed of the cutting motion. Keep in mind that this version
is a lot faster for demonstration purposes but will be a lot slower in the game so we can have the user cutting for ~30 seconds'''

import pygame
import time

import cv2


import threading as th

import keyboard

speed=1
keep_going = True


windowSize=(1200,900)

win=pygame.display.set_mode(windowSize)

#set title on window
pygame.display.set_caption("Chopping") 
speed = 3
#look in same folder as script for images
c1 =pygame.image.load('choppingcarrot/c1.png')
c2 =pygame.image.load('choppingcarrot/c2.png')
c3 =pygame.image.load('choppingcarrot/c3.png')
c4 =pygame.image.load('choppingcarrot/c4.png')
c5 =pygame.image.load('choppingcarrot/c5.png')
c6 =pygame.image.load('choppingcarrot/c6.png')
c7 =pygame.image.load('choppingcarrot/c7.png')
c8 =pygame.image.load('choppingcarrot/c8.png')
c9 =pygame.image.load('choppingcarrot/c9.png')
c10 =pygame.image.load('choppingcarrot/c10.png')
c11 =pygame.image.load('choppingcarrot/c11.png')
c12 =pygame.image.load('choppingcarrot/c12.png')
c13 =pygame.image.load('choppingcarrot/c13.png')
c14 =pygame.image.load('choppingcarrot/c14.png')
c15 =pygame.image.load('choppingcarrot/c15.png')
c16 =pygame.image.load('choppingcarrot/c16.png')
c17 =pygame.image.load('choppingcarrot/c17.png')
c18 =pygame.image.load('choppingcarrot/c18.png')
c19 =pygame.image.load('choppingcarrot/c19.png')
c20 =pygame.image.load('choppingcarrot/c20.png')
c21 =pygame.image.load('choppingcarrot/c21.png')
c22 =pygame.image.load('choppingcarrot/c22.png')
c23 =pygame.image.load('choppingcarrot/c23.png')
c24 =pygame.image.load('choppingcarrot/c24.png')
c25 =pygame.image.load('choppingcarrot/c25.png')
c26 =pygame.image.load('choppingcarrot/c26.png')
c27 =pygame.image.load('choppingcarrot/c27.png')
#knife = pygame.transform.scale(knife, (250, 220))
board=pygame.image.load('cuttingboard2.png')
#board = pygame.transform.scale(board, (300, 320))

pygame.font.init()
myfont = pygame.font.SysFont('Comic Sans MS', 40)

transparent = (0, 0, 0, 0) # leaf.image.fill(transparent)
clock = pygame.time.Clock()

def draw_window():
    global speed
    input_speed=0
    for i in range(2,28):
        clock.tick(2*speed)        
        win.blit(board, (300, 110))
        var_name2 = "c"+str(i)
        #print(var_name2)
        win.blit(globals()[var_name2], (300, 110))
        pygame.display.update()


    


def key_capture_thread():
    global speed
    global keep_going
    a = keyboard.read_key()
    if a== "1":
        speed=1
    if a== "2":
        speed=4
    if a== "3":
        speed=10
    th.Thread(target=key_capture_thread, args=(), name='key_capture_thread', daemon=True).start()



def do_stuff():
    th.Thread(target=key_capture_thread, args=(), name='key_capture_thread', daemon=True).start()
    i=0
    global speed
        
    for i in range(2,28):
        clock.tick(2*speed)        
        win.blit(board, (300, 110))
        var_name2 = "c"+str(i)
        #print(var_name2)
        win.blit(globals()[var_name2], (300, 110))
        pygame.display.update()
        
    print ("exit")


def main():
    #upper left corner of pygame window is (0,0)
   # knifeInfo = pygame.Rect(0,0, 50, 50)  #x,y,width,height
    
    run=False
    blueBackground=(255, 255, 255) # red, green, blue tuple
    win.fill(blueBackground)
    
    msg= myfont.render('Press \'s\' to start', False, (0,0,0))
    win.blit(msg, (200,50))
    win.blit(board, (300, 110))
    win.blit(c1, (300, 110))
    pygame.display.update()
            
    
    
    run= True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print('User quit game')
                run=False
        keys_pressed = pygame.key.get_pressed()

        
        if keys_pressed[pygame.K_s]: #s to start
            do_stuff()


                  
                
    pygame.quit()



main()
    
