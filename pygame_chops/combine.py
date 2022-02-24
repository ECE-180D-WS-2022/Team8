import pygame
from pygame.locals import *
import time
import threading

pygame.init()
pygame.font.init()
myfont = pygame.font.SysFont('Comic Sans MS', 40)
clock = pygame.time.Clock()
fps = 60

backgroundColor=(255, 255, 255)
screen_width = 1200
screen_height = 900

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Cooking Papa 1.0')

#define game variables
tile_size = 50

atStove = False
atBoard = False

#load images
#sun_img = pygame.image.load('img/sun.png')
bg_img = pygame.image.load('img/background.png')
bg_img = pygame.transform.scale(bg_img, (1200, 900))
bg_chopping = pygame.image.load('img/chopping.png')
bg_chopping = pygame.transform.scale(bg_chopping, (1200, 900))
bg_stove = pygame.image.load('stir/background.png')

speed = 2

#look in same folder as script for images
c1 =pygame.image.load('choppingcarrot\c1.png')
c2 =pygame.image.load('choppingcarrot\c2.png')
c3 =pygame.image.load('choppingcarrot\c3.png')
c4 =pygame.image.load('choppingcarrot\c4.png')
c5 =pygame.image.load('choppingcarrot\c5.png')
c6 =pygame.image.load('choppingcarrot\c6.png')
c7 =pygame.image.load('choppingcarrot\c7.png')
c8 =pygame.image.load('choppingcarrot\c8.png')
c9 =pygame.image.load('choppingcarrot\c9.png')
c10 =pygame.image.load('choppingcarrot\c10.png')
c11 =pygame.image.load('choppingcarrot\c11.png')
c12 =pygame.image.load('choppingcarrot\c12.png')
c13 =pygame.image.load('choppingcarrot\c13.png')
c14 =pygame.image.load('choppingcarrot\c14.png')
c15 =pygame.image.load('choppingcarrot\c15.png')
c16 =pygame.image.load('choppingcarrot\c16.png')
c17 =pygame.image.load('choppingcarrot\c17.png')
c18 =pygame.image.load('choppingcarrot\c18.png')
c19 =pygame.image.load('choppingcarrot\c19.png')
c20 =pygame.image.load('choppingcarrot\c20.png')
c21 =pygame.image.load('choppingcarrot\c21.png')
c22 =pygame.image.load('choppingcarrot\c22.png')
c23 =pygame.image.load('choppingcarrot\c23.png')
c24 =pygame.image.load('choppingcarrot\c24.png')
c25 =pygame.image.load('choppingcarrot\c25.png')
c26 =pygame.image.load('choppingcarrot\c26.png')
c27 =pygame.image.load('choppingcarrot\c27.png')
board=pygame.image.load('cuttingboard2.png')

#stirring photos
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

transparent = (0, 0, 0, 0) 
'''player class, use this to move the player'''
class Player():
	def __init__(self, x, y):
		self.images_right = []
		self.images_left = []
		self.index = 0
		self.counter = 0
		for num in range(1, 5):
			img_right = pygame.image.load(f'img/guy{num}.png')
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
		if  self.rect.x < 350 and self.rect.x > 150:
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

		if self.rect.bottom > screen_height:
			self.rect.bottom = screen_height
			dy = 0

		#draw player onto screen
		screen.blit(self.image, self.rect)

def stir():

    
    #blit puts one image on another
    
    time.sleep(1)
    pygame.display.update() #update the display

    global speed
    for i in range(1,69):
        k=i
        if (i>=24):
            k=i-23
        if (i>=47):
            k=i-46

        

        
        if speed ==1:
            time.sleep(0.2)
        elif speed==2:
            time.sleep(0.1)
        else:
            time.sleep(0.01)
        var_name = "s"+str(k)
        print(var_name)
        screen.fill(backgroundColor)
        screen.blit(bg_stove, (0, 0))
        screen.blit(globals()[var_name], (350, 260))
        pygame.display.update()

def chop():
    time.sleep(1)
    pygame.display.update() #update the display
    it = 0
    global speed
    speed=3
    for i in range(2,28):
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
        screen.blit(board, (300, 110))
        var_name1 = "c"+str(i-1)
        var_name2 = "c"+str(i)
        globals()[var_name1].fill(transparent)
        screen.blit(globals()[var_name2], (300, 110))
        pygame.display.update()
        it+=1


class World():
	def __init__(self, data):
		self.tile_list = []

		#load images
		dirt_img = pygame.image.load('img/dirt.png')
		grass_img = pygame.image.load('img/grass.png')

		row_count = 0
		for row in data:
			col_count = 0
			for tile in row:
				if tile == 1:
					img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
					img_rect = img.get_rect()
					img_rect.x = col_count * tile_size
					img_rect.y = row_count * tile_size
					tile = (img, img_rect)
					self.tile_list.append(tile)
				if tile == 2:
					img = pygame.transform.scale(grass_img, (tile_size, tile_size))
					img_rect = img.get_rect()
					img_rect.x = col_count * tile_size
					img_rect.y = row_count * tile_size
					tile = (img, img_rect)
					self.tile_list.append(tile)
				col_count += 1
			row_count += 1

	def draw(self):
		for tile in self.tile_list:
			screen.blit(tile[0], tile[1])



world_data =[
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]


inWorld = True

player = Player(100, screen_height - 130)
world = World(world_data)

run = True
while run:

	clock.tick(fps)

	
#screen.blit(sun_img, (100, 100))

	if player.isAtBoard() == False:
		atStove = True
		atBoard = False
	else:
		atBoard = True
		atStove = False
	keys_pressed = pygame.key.get_pressed()
	if keys_pressed[pygame.K_UP] and player.rect.x > 150 and player.rect.x < 550:
		inWorld=False
	if keys_pressed[pygame.K_DOWN]:
		inWorld=True
	#if keys_pressed[pygame.K_a]: #a to go left
	#	inWorld = False
            
	
	if (inWorld):
		screen.blit(bg_img, (0, 0))
		world.draw()
		player.update()
	elif atBoard == True:
		screen.blit(bg_chopping, (0, 0))
		blueBackground=(255, 255, 255) # red, green, blue tuple
		screen.fill(blueBackground)
    
		msg= myfont.render('Press \'s\' to start', False, (0,0,0))
		screen.blit(msg, (200,50))
		screen.blit(board, (300, 110))
		screen.blit(c1, (300, 110))
		pygame.display.update()
		run= True
		'''while run:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					print('User quit game')
					run=False
        '''
		keys_pressed = pygame.key.get_pressed()
		if keys_pressed[pygame.K_s]: #s to start
			chop() 

	elif atStove == True:
		
		blueBackground=(255, 255, 255) # red, green, blue tuple
		screen.fill(blueBackground)
		screen.blit(bg_stove, (0, 0))
		msg= myfont.render('Press \'s\' to start', False, (0,0,0))
		screen.blit(msg, (200,50))
		screen.blit(s1, (350, 260))
		pygame.display.update()
		run= True
		'''while run:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					print('User quit game')
					run=False
        '''
		keys_pressed = pygame.key.get_pressed()
		if keys_pressed[pygame.K_s]: #s to start
			stir() 


	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False

	pygame.display.update()

pygame.quit()