import pygame
import time
import threading
#define size of window
windowSize=(1200,900)

win=pygame.display.set_mode(windowSize)
backgroundColor=(255, 255, 255) # red, green, blue tuple
#set title on window
pygame.display.set_caption("Stirring") 
speed = 3

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

pygame.font.init()
myfont = pygame.font.SysFont('Comic Sans MS', 40)


def draw_window():

    
    #blit puts one image on another
    
    time.sleep(1)
    pygame.display.update() #update the display

    global speed
    for i in range(1,75):
        k=i
       # print('it:'+str(it))
        if (i>=16):
            k=i-15
        if (i>=31):
            k=i-30
        if (i>=46):
            k=i-45
        if (i>=61):
            k=i-60
        
        '''keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_1]: #s to start
            speed = 1
        elif keys_pressed[pygame.K_2]: #s to start
            speed = 2
        elif keys_pressed[pygame.K_3]:
            speed = 3'''
        
        if speed ==1:
            time.sleep(0.2)
        elif speed==2:
            time.sleep(0.1)
        else:
            time.sleep(0.02)
        var_name = "s"+str(k)
        win.fill(backgroundColor)
        win.blit(globals()[var_name], (300, 110))
        pygame.display.update()




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
            draw_window()  
                  
                
    pygame.quit()

main()
    
