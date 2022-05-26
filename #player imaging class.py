#player imaging class
class Playerimg():
	def __init__(self, x, y):
		self.images_right = []
		self.images_left = []
		self.index = 0
		self.counter = 0
		for num in range(1, 5):
			img_right = pygame.image.load(f'images/chef/chef{num}.png')
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

	def update(self):
		global walk_s
		global walk_memory
		walk_s+=1
		dx = 0
		dy = 0
		walk_cooldown = 5

        #moving left
		if (self.rect.x+150 - x_pos) < -18:
			dx -= 5
			self.counter += 1
			self.direction = 1
		#moving right
		elif (self.rect.x+150 - x_pos) > 18 and x_pos >=200:
			dx += 5
			self.counter += 1
			self.direction = -1


		#print(str(self.rect.x+150) +" " + str(x_pos))
		#print(str(x_pos))
		#print('direction: '+ str(self.direction))

		#handle animation
		print(str(self.index))

		if (walk_s==3):
			if abs(walk_memory+self.rect.x+150 - x_pos)/2>9:
				self.counter = 0	
				self.index += 1
				if self.index >= len(self.images_right):
					self.index = 0
				if self.direction == 1:
					self.image = self.images_right[self.index]
				if self.direction == -1:
					self.image = self.images_left[self.index]
			elif self.index == 1 or self.index==3:
				if self.direction == 1:
					self.image = self.images_right[2]
				if self.direction == -1:
					self.image = self.images_left[2]
			walk_s=0

		#add gravity
		self.vel_y += 1
		if self.vel_y > 10:
			self.vel_y = 10
		dy += self.vel_y

		#check for collision

		#update player 
		#print(dx)
		walk_memory = self.rect.x+150 - x_pos
		self.rect.x = x_pos - 150
		self.rect.y += dy

		if self.rect.bottom > SCREEN_HEIGHT:
			self.rect.bottom = SCREEN_HEIGHT
			dy = 0
		
		win.blit(self.image, self.rect)
#player imaging class