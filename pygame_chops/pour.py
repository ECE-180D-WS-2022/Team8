import pygame
import time
import threading
#define size of window
windowSize=(1200,900)

screen=pygame.display.set_mode(windowSize)

#set title on window
pygame.display.set_caption("Pouring") 
speed = 3

#look in same folder as script for images
p1 =pygame.image.load('pour\p1.png')
p2 =pygame.image.load('pour\p2.png')
p3 =pygame.image.load('pour\p3.png')
p4 =pygame.image.load('pour\p4.png')
p5 =pygame.image.load('pour\p5.png')
p6 =pygame.image.load('pour\p6.png')
p7 =pygame.image.load('pour\p7.png')
p8 =pygame.image.load('pour\p8.png')



pygame.font.init()
myfont = pygame.font.SysFont('Comic Sans MS', 40)


def pour():

    
    #blit puts one image on another
    time.sleep(1)
    pygame.display.update() #update the display
    global speed

    for i in range(1,8):
       # print('it:'+str(it))
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_1]: #s to start
            speed = 1
        elif keys_pressed[pygame.K_2]: #s to start
            speed = 2
        elif keys_pressed[pygame.K_3]:
            speed = 3
        
        if speed ==1:
            time.sleep(2)
        elif speed==2:
            time.sleep(0.75)
        else:
            time.sleep(0.1)

        var_name = "p"+str(i)
        backgroundColor=(255, 255, 255) 
        screen.fill(backgroundColor)
        screen.blit(globals()[var_name], (300, 110))
        pygame.display.update()


    


def main():
   
    
    backgroundColor=(255, 255, 255) 
    screen.fill(backgroundColor)
    
    #text 
    msg= myfont.render('Press \'s\' to start', False, (0,0,0))
    screen.blit(msg, (200,50))

    #display initial photo of bowl
    screen.blit(p1, (300, 110))
    #display
    pygame.display.update()

    run= True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print('User quit game')
                run=False
        
    
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_s]: #s to start
            pour()  
                  
                
    pygame.quit()

main()
    
