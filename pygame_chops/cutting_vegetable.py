import pygame
#define size of window
windowSize=(900,500)
win=pygame.display.set_mode(windowSize)

#set title on window
pygame.display.set_caption("Chopping") 

#look in same folder as script for images
knife=pygame.image.load('knife.png')
carrot =pygame.image.load('carrot2.png')
carrot = pygame.transform.scale(carrot, (250, 220))
carrot_1 = pygame.image.load('carrot_cut1.png')
carrot_1 = pygame.transform.scale(carrot_1, (250, 220))
carrot_2 = pygame.image.load('carrot_cut2.png')
carrot_2 = pygame.transform.scale(carrot_2, (250, 220))
knife = pygame.transform.scale(knife, (250, 220))
knife2 = pygame.transform.scale(knife, (250, 220))
knife3 = pygame.transform.scale(knife, (250, 220))
board=pygame.image.load('cuttingboard2.png')
board = pygame.transform.scale(board, (300, 320))

pygame.font.init()
myfont = pygame.font.SysFont('Comic Sans MS', 40)

transparent = (0, 0, 0, 0) # leaf.image.fill(transparent)

def draw_window(knifeInfo):
    blueBackground=(255, 255, 255) # red, green, blue tuple
    win.fill(blueBackground)
    
    #blit puts one image on another
    win.blit(board, (300, 110))
    win.blit(carrot, (300, 110))
    win.blit(knife, (knifeInfo.x, knifeInfo.y))
    #pygame.draw.circle(win, (255, 255, 255), (300, 110, 4)
    if knifeInfo.x > 300 and knifeInfo.y >110 and knifeInfo.x < (300+300) and knifeInfo.y < (110+220):
        #print('You Win')
        msg= myfont.render('You are chopping', False, (0,0,0))
       # carrot = pygame.image.load('carrot_cut2.png')
        '''win.blit(carrot_1, (300, 110))
        carrot.fill(transparent)
        knife.fill(transparent)
        win.blit(knife2, (knifeInfo.x, knifeInfo.y))'''
    else:
        msg= myfont.render('Chop (w,a,s,d)', False, (0,0,0))
    win.blit(msg, (200,50))
    pygame.display.update() #update the display


def main():
    #upper left corner of pygame window is (0,0)
    knifeInfo = pygame.Rect(0,0, 50, 50)  #x,y,width,height
    

    run= True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print('User quit game')
                run=False
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_a]: #a to go left
            knifeInfo.x -= 1
        elif keys_pressed[pygame.K_d]: #d to go right
            knifeInfo.x += 1
        elif keys_pressed[pygame.K_w]: #w to go up
            knifeInfo.y -= 1
        elif keys_pressed[pygame.K_s]: #s to go down
            knifeInfo.y += 1
                
        draw_window(knifeInfo)        
                
    pygame.quit()

main()
    
