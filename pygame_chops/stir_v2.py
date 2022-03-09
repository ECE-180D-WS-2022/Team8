import pygame
import time
import threading as th

import keyboard
#define size of window
windowSize=(1200,900)

win=pygame.display.set_mode(windowSize)
backgroundColor=(255, 255, 255) # red, green, blue tuple
#set title on window
pygame.display.set_caption("Stirring") 
speed = 3

clock = pygame.time.Clock()

#look in same folder as script for images
s1 =pygame.image.load('stir\s1.png')
s2 =pygame.image.load('stir\s2.png')
s3 =pygame.image.load('stir\s3.png')
s4 =pygame.image.load('stir\s4.png')
s5 =pygame.image.load('stir\s5.png')
s6 =pygame.image.load('stir\s6.png')
s7 =pygame.image.load('stir\s7.png')
s8 =pygame.image.load('stir\s8.png')
s9 =pygame.image.load('stir\s9.png')
s10 =pygame.image.load('stir\s10.png')
s11 =pygame.image.load('stir\s11.png')
s12 =pygame.image.load('stir\s12.png')
s13 =pygame.image.load('stir\s13.png')
s14 =pygame.image.load('stir\s14.png')
s15 =pygame.image.load('stir\s15.png')
s16 =pygame.image.load('stir\s16.png')
s17 =pygame.image.load('stir\s17.png')
s18 =pygame.image.load('stir\s18.png')
s19 =pygame.image.load('stir\s19.png')
s20 =pygame.image.load('stir\s20.png')
s21 =pygame.image.load('stir\s21.png')
s22 =pygame.image.load('stir\s22.png')
s23 =pygame.image.load('stir\s23.png')


pygame.font.init()
myfont = pygame.font.SysFont('Comic Sans MS', 40)




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

    for i in range(1,115):
        k=i
       # print('it:'+str(it))
        if (i>=24):
            k=i-23
        if (i>=47):
            k=i-46
        if (i>=70):
            k=i-69
        if (i>=93):
            k=i-92
        
        clock.tick(2*speed)  
        var_name = "s"+str(k)
        win.fill(backgroundColor)
        win.blit(globals()[var_name], (300, 110))
        pygame.display.update()
        
    print ("exit")



def main():

    win.fill(backgroundColor)
    
    msg= myfont.render('Press \'s\' to start', False, (0,0,0))
    win.blit(msg, (200,50))
    win.blit(s1, (300, 110))
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
    
