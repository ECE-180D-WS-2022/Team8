'''
In this program, press 's' to begin and '1' '2' or '3' to adjust the speed of the cutting motion. Keep in mind that this version
is a lot faster for demonstration purposes but will be a lot slower in the game so we can have the user cutting for ~30 seconds'''

import pygame
import time
import threading as th
import keyboard

#variables
speed = 3
windowSize=(1200,900)
clock = pygame.time.Clock()

#window
win=pygame.display.set_mode(windowSize)
pygame.display.set_caption("Chopping") 

#font stuff
green = (2, 100,64)
black = (0,0,0)
pygame.font.init()
myfont = pygame.font.SysFont('Comic Sans MS', 40)

#look in same folder as script for images
c1 =pygame.image.load('images\choppingcarrot_resize\cc1.png')
c2 =pygame.image.load('images\choppingcarrot_resize\cc2.png')
c3 =pygame.image.load('images\choppingcarrot_resize\cc3.png')
c4 =pygame.image.load('images\choppingcarrot_resize\cc4.png')
c5 =pygame.image.load('images\choppingcarrot_resize\cc5.png')
c6 =pygame.image.load('images\choppingcarrot_resize\cc6.png')
c7 =pygame.image.load('images\choppingcarrot_resize\cc7.png')
c8 =pygame.image.load('images\choppingcarrot_resize\cc8.png')
c9 =pygame.image.load('images\choppingcarrot_resize\cc9.png')
c10 =pygame.image.load('images\choppingcarrot_resize\cc10.png')
c11 =pygame.image.load('images\choppingcarrot_resize\cc11.png')
c12 =pygame.image.load('images\choppingcarrot_resize\cc12.png')
c13 =pygame.image.load('images\choppingcarrot_resize\cc13.png')
c14 =pygame.image.load('images\choppingcarrot_resize\cc14.png')
c15 =pygame.image.load('images\choppingcarrot_resize\cc15.png')
c16 =pygame.image.load('images\choppingcarrot_resize\cc16.png')
c17 =pygame.image.load('images\choppingcarrot_resize\cc17.png')
c18 =pygame.image.load('images\choppingcarrot_resize\cc18.png')
c19 =pygame.image.load('images\choppingcarrot_resize\cc19.png')
c20 =pygame.image.load('images\choppingcarrot_resize\cc20.png')
c21 =pygame.image.load('images\choppingcarrot_resize\cc21.png')
c22 =pygame.image.load('images\choppingcarrot_resize\cc22.png')
c23 =pygame.image.load('images\choppingcarrot_resize\cc23.png')
c24 =pygame.image.load('images\choppingcarrot_resize\cc24.png')
c25 =pygame.image.load('images\choppingcarrot_resize\cc25.png')
c26 =pygame.image.load('images\choppingcarrot_resize\cc26.png')
c27 =pygame.image.load('images\choppingcarrot_resize\cc27.png')
board=pygame.image.load('images\cuttingboard3.png')


def key_capture_thread():
    global speed
    a = keyboard.read_key()
    if a== "1":
        speed=1
    if a== "2":
        speed=4
    if a== "3":
        speed=10
    th.Thread(target=key_capture_thread, args=(), name='key_capture_thread', daemon=True).start()


def chopping():
    th.Thread(target=key_capture_thread, args=(), name='key_capture_thread', daemon=True).start()
    i=0
    global speed

    #intialize progress bar 
    pygame.draw.rect(win, black, pygame.Rect(349, 720, 500, 30),2 )
    pygame.display.update() 

    for i in range(2,28):
        clock.tick(2*speed)        
        win.blit(board, (0, 0))
        var_name2 = "c"+str(i)
        #print(var_name2)
        win.blit(globals()[var_name2], (200, 110))

        #increment progress bar
        pygame.draw.rect(win, black, pygame.Rect(349, 720, 500, 30),2 )
        #increment progress bars
        x = round(i/27*10)
        for t in range(0,x):
            pygame.draw.rect(win, green, pygame.Rect(350+(50*t), 721, 48, 28) )
        pygame.display.update()
        
    print ("exit")


def main():
    #upper left corner of pygame window is (0,0)
   # knifeInfo = pygame.Rect(0,0, 50, 50)  #x,y,width,height
    
    run=False

    #fill background white
    blueBackground=(255, 255, 255) # red, green, blue tuple
    win.fill(blueBackground)

    #draw the board
    win.blit(board, (0, 0))
    
    #draw instructions
    msg= myfont.render('Press \'s\' to start', False, (0,0,0))
    win.blit(msg, (200,50))

    

    #draw the carrot uncut
    win.blit(c1, (200, 110))

    #draw progress bar outline
    pygame.draw.rect(win, black, pygame.Rect(349, 720, 500, 30),2 )


    pygame.display.update()
            
    
    
    run= True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print('User quit game')
                run=False
        keys_pressed = pygame.key.get_pressed()

        
        if keys_pressed[pygame.K_s]: #s to start
            chopping()


              
    pygame.quit()



main()
    
