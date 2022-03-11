import pygame
import time
import threading as th
import keyboard

#variables
windowSize=(1200,900)
speed = 3
clock = pygame.time.Clock()

#setup screen
win=pygame.display.set_mode(windowSize)
backgroundColor=(255, 255, 255) # red, green, blue tuple
pygame.display.set_caption("Stirring") 


#colors
green = (2, 100,64)
black = (0,0,0)


#text
pygame.font.init()
myfont = pygame.font.SysFont('Comic Sans MS', 40)
good= myfont.render('Good job!', False, (0,0,0))
great=myfont.render('Great job!', False, (0,0,0))
ok=myfont.render('Ok job!', False, (0,0,0))


#load all images
s1 =pygame.image.load('images\stir\s1.png')
s2 =pygame.image.load('images\stir\s2.png')
s3 =pygame.image.load('images\stir\s3.png')
s4 =pygame.image.load('images\stir\s4.png')
s5 =pygame.image.load('images\stir\s5.png')
s6 =pygame.image.load('images\stir\s6.png')
s7 =pygame.image.load('images\stir\s7.png')
s8 =pygame.image.load('images\stir\s8.png')
s9 =pygame.image.load('images\stir\s9.png')
s10 =pygame.image.load('images\stir\s10.png')
s11 =pygame.image.load('images\stir\s11.png')
s12 =pygame.image.load('images\stir\s12.png')
s13 =pygame.image.load('images\stir\s13.png')
s14 =pygame.image.load('images\stir\s14.png')
s15 =pygame.image.load('images\stir\s15.png')
s16 =pygame.image.load('images\stir\s16.png')
s17 =pygame.image.load('images\stir\s17.png')
s18 =pygame.image.load('images\stir\s18.png')
s19 =pygame.image.load('images\stir\s19.png')
s20 =pygame.image.load('images\stir\s20.png')
s21 =pygame.image.load('images\stir\s21.png')
s22 =pygame.image.load('images\stir\s22.png')
s23 =pygame.image.load('images\stir\s23.png')
bg_stove = pygame.image.load('images/stir/background2.png')





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



def stirring():
    th.Thread(target=key_capture_thread, args=(), name='key_capture_thread', daemon=True).start()
    i=0
    global speed


     
    
    pygame.draw.rect(win, black, pygame.Rect(299, 520, 500, 30),2 )
    pygame.display.update()

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

        #redraw background
        win.fill(backgroundColor)

        #draw next frame
        win.blit(globals()[var_name], (300, 110))

        #redraw progress bar outline
        pygame.draw.rect(win, black, pygame.Rect(299, 520, 500, 30),2 )

        '''
        if (speed==3):
            win.blit(great, (200,50))
        elif speed==2:
            win.blit(good, (200,50))
        else:
            win.blit(ok, (200,50))
        '''

        #increment progress barS
        x = round(i/115*10)
        for t in range(0,x):
            pygame.draw.rect(win, green, pygame.Rect(300+(50*t), 521, 48, 28) )

        pygame.display.update()
        
    print ("exit")



def main():

    win.fill(backgroundColor)

    
    msg= myfont.render('Press \'s\' to start', False, (0,0,0))

    #blit puts one image on another  
    #display instructions 
    win.blit(msg, (200,50))

    #draw soup
    win.blit(s1, (300, 110))

    pygame.draw.rect(win, black, pygame.Rect(299, 520, 500, 30),2 )
    #update pictures
    pygame.display.update()
    run= True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print('User quit game')
                run=False
        
        #if you press s, the screen begins stirring
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_s]: #s to start
            stirring()
                  
                
    pygame.quit()

main()
    
