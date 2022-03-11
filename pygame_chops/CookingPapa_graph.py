import pygame
from pygame.locals import *
import time
import threading

#time
clock = pygame.time.Clock()
fps = 60
speed = 10


#colors
backgroundColor=(255, 255, 255)
green = (2, 100,64)
black = (0,0,0)

#win
win_width = 1200
win_height = 900
win = pygame.display.set_mode((win_width, win_height))
pygame.display.set_caption('Cooking Papa 1.0')


#text & font
pygame.font.init()
myfont = pygame.font.SysFont('Arial', 40)
msg= myfont.render('Press \'s\' to start', False, (0,0,0))
smallFont = pygame.font.SysFont('Arial', 30)
completion= smallFont.render('You have completed this task! Say \'kitchen\' to return to the kitchen to move onto the next step', False, (0,0,0))

#flags
atStove = False
atBoard = False
inWorld = True
start = False
run = True
doneChopping = False
doneStirring = False
finishedRecipe = False


#load images
bg_img = pygame.image.load('images/kitchen_half.png')
bg_img = pygame.transform.scale(bg_img, (1200, 900))
bg_chopping = pygame.image.load('images/chopping.png')
bg_chopping = pygame.transform.scale(bg_chopping, (1200, 900))
bg_stove = pygame.image.load('images/stir/background2.png')



#look in same folder as script for images
c1 =pygame.image.load('images/choppingcarrot_resize/cc1.png')
c2 =pygame.image.load('images/choppingcarrot_resize/cc2.png')
c3 =pygame.image.load('images/choppingcarrot_resize/cc3.png')
c4 =pygame.image.load('images/choppingcarrot_resize/cc4.png')
c5 =pygame.image.load('images/choppingcarrot_resize/cc5.png')
c6 =pygame.image.load('images/choppingcarrot_resize/cc6.png')
c7 =pygame.image.load('images/choppingcarrot_resize/cc7.png')
c8 =pygame.image.load('images/choppingcarrot_resize/cc8.png')
c9 =pygame.image.load('images/choppingcarrot_resize/cc9.png')
c10 =pygame.image.load('images/choppingcarrot_resize/cc10.png')
c11 =pygame.image.load('images/choppingcarrot_resize/cc11.png')
c12 =pygame.image.load('images/choppingcarrot_resize/cc12.png')
c13 =pygame.image.load('images/choppingcarrot_resize/cc13.png')
c14 =pygame.image.load('images/choppingcarrot_resize/cc14.png')
c15 =pygame.image.load('images/choppingcarrot_resize/cc15.png')
c16 =pygame.image.load('images/choppingcarrot_resize/cc16.png')
c17 =pygame.image.load('images/choppingcarrot_resize/cc17.png')
c18 =pygame.image.load('images/choppingcarrot_resize/cc18.png')
c19 =pygame.image.load('images/choppingcarrot_resize/cc19.png')
c20 =pygame.image.load('images/choppingcarrot_resize/cc20.png')
c21 =pygame.image.load('images/choppingcarrot_resize/cc21.png')
c22 =pygame.image.load('images/choppingcarrot_resize/cc22.png')
c23 =pygame.image.load('images/choppingcarrot_resize/cc23.png')
c24 =pygame.image.load('images/choppingcarrot_resize/cc24.png')
c25 =pygame.image.load('images/choppingcarrot_resize/cc25.png')
c26 =pygame.image.load('images/choppingcarrot_resize/cc26.png')
c27 =pygame.image.load('images/choppingcarrot_resize/cc27.png')
board=pygame.image.load('images\cuttingboard3.png')

#stirring photos
s1 =pygame.image.load('images/stir/s1.png')
s2 =pygame.image.load('images/stir/s2.png')
s3 =pygame.image.load('images/stir/s3.png')
s4 =pygame.image.load('images/stir/s4.png')
s5 =pygame.image.load('images/stir/s5.png')
s6 =pygame.image.load('images/stir/s6.png')
s7 =pygame.image.load('images/stir/s7.png')
s8 =pygame.image.load('images/stir/s8.png')
s9 =pygame.image.load('images/stir/s9.png')
s10 =pygame.image.load('images/stir/s10.png')
s11 =pygame.image.load('images/stir/s11.png')
s12 =pygame.image.load('images/stir/s12.png')
s13 =pygame.image.load('images/stir/s13.png')
s14 =pygame.image.load('images/stir/s14.png')
s15 =pygame.image.load('images/stir/s15.png')
s16 =pygame.image.load('images/stir/s16.png')
s17 =pygame.image.load('images/stir/s17.png')
s18 =pygame.image.load('images/stir/s18.png')
s19 =pygame.image.load('images/stir/s19.png')
s20 =pygame.image.load('images/stir/s20.png')
s21 =pygame.image.load('images/stir/s21.png')
s22 =pygame.image.load('images/stir/s22.png')
s23 =pygame.image.load('images/stir/s23.png')
fire =pygame.image.load('images/stir/fire.png')

intro = pygame.image.load('images/CookingPapa_intro.png')
recipes = pygame.image.load('images/CookingPapa_recipeS.png')

poc1 = pygame.image.load('images/pour/poc1.png')
poc2 = pygame.image.load('images/pour/poc2.png')
poc3 = pygame.image.load('images/pour/poc3.png')
poc4 = pygame.image.load('images/pour/poc4.png')
poc5 = pygame.image.load('images/pour/poc5.png')
poc6 = pygame.image.load('images/pour/poc6.png')
poc7 = pygame.image.load('images/pour/poc8.png')
poc8 = pygame.image.load('images/pour/poc8.png')
poc9 = pygame.image.load('images/pour/poc9.png')
poc10 = pygame.image.load('images/pour/poc10.png')
poc11 = pygame.image.load('images/pour/poc11.png')
poc12 = pygame.image.load('images/pour/poc12.png')
poc13 = pygame.image.load('images/pour/poc13.png')

'''player class, use this to move the player'''
class Player():
	def __init__(self, x, y):
		self.images_right = []
		self.images_left = []
		self.index = 0
		self.counter = 0
		for num in range(1, 5):
			img_right = pygame.image.load(f'img/chef{num}.png')
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

	def isAtBoard(self):
		if  self.rect.x < 600:
			return True
		else:
			return False


	def update(self):
		dx = 0
		dy = 0
		walk_cooldown = 5

		#get keypresses
		key = pygame.key.get_pressed()
		if key[pygame.K_SPACE] and self.jumped == False:
			self.vel_y = -15
			self.jumped = True
		if key[pygame.K_SPACE] == False:
			self.jumped = False
		if key[pygame.K_LEFT]:
			dx -= 5
			self.counter += 1
			self.direction = -1
		if key[pygame.K_RIGHT]:
			dx += 5
			self.counter += 1
			self.direction = 1
		if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
			self.counter = 0
			self.index = 0
			if self.direction == 1:
				self.image = self.images_right[self.index]
			if self.direction == -1:
				self.image = self.images_left[self.index]


		#handle animation
		if self.counter > walk_cooldown:
			self.counter = 0	
			self.index += 1
			if self.index >= len(self.images_right):
				self.index = 0
			if self.direction == 1:
				self.image = self.images_right[self.index]
			if self.direction == -1:
				self.image = self.images_left[self.index]


		#add gravity
		self.vel_y += 1
		if self.vel_y > 10:
			self.vel_y = 10
		dy += self.vel_y

		#check for collision

		#update player coordinates
		self.rect.x += dx
		self.rect.y += dy

		if self.rect.bottom > win_height:
			self.rect.bottom = win_height
			dy = 0

		#draw player onto win
		win.blit(self.image, self.rect)


def stirring():
    pourCarrots()
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
        
        time.sleep(0.05) 
        var_name = "s"+str(k)
        win.fill(backgroundColor)
        win.blit(bg_stove,(0,0))
        win.blit(globals()[var_name], (340, 220))
        #redraw progress bar outline
        pygame.draw.rect(win, backgroundColor, pygame.Rect(349, 821, 498, 28))
        pygame.draw.rect(win, black, pygame.Rect(349, 820, 500, 30),2 )
        '''
        if (speed==3):
            win.blit(great, (200,50))
        elif speed==2:
            win.blit(good, (200,50))
        else:
            win.blit(ok, (200,50))
        '''
        #increment progress bars
        x = round(i/115*10)
        for t in range(0,x):
            pygame.draw.rect(win, green, pygame.Rect(350+(50*t), 821, 48, 28) )
        pygame.display.update()
    global doneStirring
    doneStirring=True


def chopping():
    for i in range(1,28):
       # print('it:'+str(it))
        time.sleep(0.1)
        win.blit(board, (0, 0))
        var_name1 = "c"+str(i)
        win.blit(globals()[var_name1], (200, 110))
		#increment progress bar
        pygame.draw.rect(win, black, pygame.Rect(349, 720, 500, 30),2 )
        #increment progress bars
        x = round(i/27*10)
        for t in range(0,x):
            pygame.draw.rect(win, green, pygame.Rect(350+(50*t), 721, 48, 28) )
        pygame.display.update()
    global doneChopping
    doneChopping=True




def drawChoppingBackground():
	win.fill(backgroundColor)
	win.blit(board, (0, 0))
	win.blit(c1, (200, 110))
	win.blit(msg, (200,50))
	 #draw progress bar outline
	pygame.draw.rect(win, black, pygame.Rect(349, 720, 500, 30),2 )
	pygame.display.update()

def drawStoveBackground():
	win.fill(backgroundColor)
	win.blit(bg_stove, (0, 0))
	win.blit(msg, (200,50))
	win.blit(s1, (340, 220))
	 #draw progress bar outline
	pygame.draw.rect(win, black, pygame.Rect(349, 820, 500, 30),2 )
	pygame.draw.rect(win, backgroundColor, pygame.Rect(350, 821, 498, 28))

def finishedStirring():
    win.fill(backgroundColor)
    win.blit(bg_stove,(0,0))
    win.blit(s23, (340, 220))
        #redraw progress bar outline
    pygame.draw.rect(win, backgroundColor, pygame.Rect(349, 821, 498, 28))
    pygame.draw.rect(win, black, pygame.Rect(349, 820, 500, 30),2 )
        #increment progress bars
    x = round(115/115*10)
    for t in range(0,x):
        pygame.draw.rect(win, green, pygame.Rect(350+(50*t), 821, 48, 28) )
    pygame.display.update()
    win.blit(completion, (100,100))

def pourCarrots():
    for i in range(1,14):
       # print('it:'+str(it))
        time.sleep(0.1)
        win.fill(backgroundColor)
        win.blit(bg_stove, (0, 0))
        win.blit(msg, (200,50))
        win.blit(s1, (340, 220))
	    #draw progress bar outline
        pygame.draw.rect(win, black, pygame.Rect(349, 820, 500, 30),2 )
        pygame.draw.rect(win, backgroundColor, pygame.Rect(350, 821, 498, 28))
        var_name1 = "poc"+str(i)
        win.blit(globals()[var_name1], (450, 50))
        pygame.display.update()

def finishedChopping():
    win.fill(backgroundColor)
    win.blit(board, (0, 0))
    win.blit(c27, (200, 110))
	#increment progress bar
    pygame.draw.rect(win, black, pygame.Rect(349, 720, 500, 30),2 )
    #increment progress bars
    x = round(27/27*10)
    for t in range(0,x):
        pygame.draw.rect(win, green, pygame.Rect(350+(50*t), 721, 48, 28) )
    win.blit(completion, (100,800))

def chops():
	if doneChopping:
		finishedChopping()
	else:
		drawChoppingBackground()
	keys_pressed = pygame.key.get_pressed()
	if keys_pressed[pygame.K_s]: #s to start
		chopping()

def stirs():
    global doneStirrings
    if doneStirring:
        finishedStirring()
        time.sleep(5)
        global finishedRecipe
        finishedRecipe = True
    else:
        drawStoveBackground()
    keys_pressed = pygame.key.get_pressed()
    if keys_pressed[pygame.K_s]: #s to start
        stirring() 


player = Player(100, win_height - 130)


while run:
	win.blit(intro, (0, 0))
	clock.tick(fps)

	if player.isAtBoard() == False:
		atStove = True
		atBoard = False
	else:
		atBoard = True
		atStove = False

	keys_pressed = pygame.key.get_pressed()
	if keys_pressed[pygame.K_UP]:
		inWorld=False
	if keys_pressed[pygame.K_DOWN]:
		inWorld=True
	if keys_pressed[pygame.K_SPACE]:
		start=True     
	

	if (inWorld):
		win.blit(bg_img, (0, 0))
		player.update()
	elif atBoard == True:	
		chops()
	elif atStove == True:
		stirs()


	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False

	if (start==False):
		win.blit(intro, (0, 0))

	pygame.display.update()

pygame.quit()