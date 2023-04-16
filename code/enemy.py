import pygame 
from tiles import AnimatedTile
from random import randint
from pygame import mixer

class Enemy(AnimatedTile):
	def __init__(self,size,x,y):
		super().__init__(size,x,y,'../graphics/enemy/run')
		self.rect.y += size - self.image.get_size()[1]
		self.speed=randint(3,5)
		self.vision=pygame.Rect(0,0,100,20)
		self.x=self.speed
		self.current_time=0
		self.damage_cooldown=0
		#Health
		self.health=100
		self.isAlive=True
		self.kill_sound=mixer.Sound('../Sounds/player/kill_sound.mp3')
	def move(self):
		
		self.rect.x += self.speed
		#Update ai vision as enemy moves
		# self.vision.center=(self.rect.centerx +75 *1,self.rect.centery)
		# pygame.draw.rect(main.screen,"RED",self.vision)
	def stop(self):
		self.x=self.speed
		self.speed=1
	def damage(self):
		self.current_time=pygame.time.get_ticks()
		if self.damage_cooldown!=1:
			#print("I will deal damage")
			self.damage_cooldown=1
		if self.current_time-pygame.time.get_ticks()<3000:
			self.damage_cooldown=0
	def take_damage(self,incoming_damage):
		if self.health:
			self.health-=incoming_damage
			mixer.Sound.play(self.kill_sound)
			if self.health<=0:
				self.isALive=False
				self.speed=0
		else:
			pass
	def resume(self):
		self.speed=self.x
	def reverse_image(self):
		if self.speed > 0:
			self.image = pygame.transform.flip(self.image,True,False)

	def reverse(self):
		self.speed *= -1

	def update(self,shift):
		self.rect.x += shift
		if self.health:
			self.animate()
		self.move()
		self.reverse_image()
	#Adding a function to kill
	def kill(self,dir):
		
		if dir:
				
			self.speed*=-1
		else:
			self.speed=self.speed
	
# class Fighter():
# 	def __init__(self, x, y, name, max_hp, strength, potions):


# 		self.name = name
# 		self.max_hp = max_hp
# 		self.hp = max_hp
# 		self.strength = strength
# 		self.start_potions = potions
# 		self.potions = potions
# 		self.alive = True
# 		self.animation_list = []
# 		self.frame_index = 0
# 		self.action = 0  # 0:idle, 1:attack, 2:hurt, 3:dead
# 		self.update_time = pygame.time.get_ticks()
# 		# load idle images
# 		self.action = 0		#0:idle, 1:attack, 2:hurt, 3:dead 4:jump 5:Move
# 		self.update_time = pygame.time.get_ticks()
# 		#Movement
# 		self.move_time=0
# 		self.jump_time=0
# 		self.action_time=100
# 		#load idle images
# 		temp_list = []
# 		for i in range(8):
# 			img = pygame.image.load(f'../graphics/{self.name}/Idle/{i}.png')
# 			img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
# 			temp_list.append(img)
# 		self.animation_list.append(temp_list)
# 			# load attack images
# 		temp_list = []
# 		for i in range(8):
# 			img = pygame.image.load(f'../graphics/{self.name}/Attack/{i}.png')
# 			img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
# 			temp_list.append(img)
# 		self.animation_list.append(temp_list)
# 			# load hurt images
# 		temp_list = []
# 		for i in range(3):
# 			img = pygame.image.load(f'../graphics/{self.name}/Hurt/{i}.png')
# 			img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
# 			temp_list.append(img)
# 		self.animation_list.append(temp_list)
# 			# load death images
# 		temp_list = []
# 		for i in range(10):
# 			img = pygame.image.load(f'../graphics/{self.name}/Death/{i}.png')
# 			img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
# 			temp_list.append(img)
# 		#Jump
# 		temp_list = []
# 		for i in range(5):
# 			img = pygame.image.load(f'../graphics/{self.name}/Attack/{i}.png')
# 			img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
# 			temp_list.append(img)
# 		self.animation_list.append(temp_list)
# 		#Move
# 		temp_list = []
# 		for i in range(2):
# 			img = pygame.image.load(f'../graphics/{self.name}/Attack/{i}.png')
# 			img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
# 			temp_list.append(img)
# 		self.animation_list.append(temp_list)

# 		self.animation_list.append(temp_list)
# 		self.image = self.animation_list[self.action][self.frame_index]
# 		self.rect = self.image.get_rect()
# 		self.rect.center = (x, y)


# 	def update(self):


# 		animation_cooldown = 100
# 		# handle animation
# 		# update image
# 		self.image = self.animation_list[self.action][self.frame_index]
# 		# check if enough time has passed since the last update
# 		if pygame.time.get_ticks() - self.update_time > animation_cooldown:
# 			self.update_time = pygame.time.get_ticks()
# 			self.frame_index += 1
# 		# if the animation has run out then reset back to the start
# 		if self.frame_index >= len(self.animation_list[self.action]):
# 			if self.action == 3:
# 				self.frame_index = len(self.animation_list[self.action]) - 1
# 			else:
# 				self.idle()


# 	def idle(self):

# 		# set variables to idle animation
# 		self.action = 0
# 		self.frame_index = 0
# 		self.update_time = pygame.time.get_ticks()
# 	def draw(self):


# 		screen.blit(self.image, self.rect)
# 	def move(self):
# 		self.move_time=pygame.time.get_ticks()
# 		self.action=5
# 		self.frame_index=0
# 		self.update_time = pygame.time.get_ticks()
# 	def jump(self):
# 		self.jump_time=pygame.time.get_ticks()
# 		self.action=4
# 		self.frame_index=0
# 		self.update_time = pygame.time.get_ticks()
# 	def move_update(self):
# 		keys=pygame.key.get_pressed()
# 		if keys[pygame.K_RIGHT] or keys[pygame.K_LEFT] :
# 			if pygame.time.get_ticks()-self.move_time>self.action_time*3:
# 				self.move()
# 		if keys[pygame.K_SPACE]:
# 			if pygame.time.get_ticks()-self.move_time>self.action_time*5:
# 				self.jumo()



