import pygame 
from pygame import mixer
from support import import_folder
from settings import *

new_font=pygame.font.Font(None,50)
HealthText=new_font.render('Health',False, (225, 0, 225))

class HealthBar():
	def __init__(self, x, y, hp, max_hp,screen):
		self.x = x
		self.y = y
		self.hp = hp
		self.max_hp = max_hp
		self.screen=screen

	def draw(self, hp):
		#update with new health
		self.hp = hp
		#calculate health ratio
		ratio = self.hp / self.max_hp
		pygame.draw.rect(self.screen, 'red', (self.x, self.y, 150, 20))
		pygame.draw.rect(self.screen, 'green', (self.x, self.y, 150 * ratio, 20))
		global HealthText
		HealthText_rect=HealthText.get_rect(center=(self.x,self.y))

class Player(pygame.sprite.Sprite):
	def __init__(self,pos,surface,create_jump_particles,level):
		super().__init__()
		self.import_character_assets()
		self.frame_index = 0
		self.animation_speed = 0.15
		self.image = self.animations['idle'][self.frame_index]
		self.rect = self.image.get_rect(topleft = pos)

		# dust particles 
		self.import_dust_run_particles()
		self.dust_frame_index = 0
		self.dust_animation_speed = 0.15
		self.display_surface = surface
		self.create_jump_particles = create_jump_particles

		# player movement
		self.direction = pygame.math.Vector2(0,0)
		self.speed = 8
		self.gravity = 0.8
		self.jump_speed = -16

		# player status
		self.status = 'idle'
		self.facing_right = True
		self.on_ground = False
		self.on_ceiling = False
		self.on_left = False
		self.on_right = False
		self.health=3000
		self.player_alive=True

		#level_1
		self.player_vel = pygame.math.Vector2(0, 0)
		self.is_jump=False
		self.floor=500

		self.current_level=level
		bottom_panel = 150

		self.health_bar = HealthBar(self.rect.x,10, self.health, 3000,self.display_surface)

	def import_character_assets(self):
		character_path = '../graphics/character/'
		self.animations = {'idle':[],'run':[],'jump':[],'fall':[],'Attack':[],'Hurt':[],'Death':[]}

		for animation in self.animations.keys():
			full_path = character_path + animation
			self.animations[animation] = import_folder(full_path,need_to_scale=1)
			
			for images in self.animations[animation]:
				images=pygame.transform.scale(images,(500,500))

	def import_dust_run_particles(self):
		self.dust_run_particles = import_folder('../graphics/character/dust_particles/run')
	
	def animate(self):
		animation = self.animations[self.status]

		# loop over frame index 
		self.frame_index += self.animation_speed
		if self.frame_index >= len(animation):
			self.frame_index = 0

		image = animation[int(self.frame_index)]
		if self.facing_right:
			self.image = image
		else:
			flipped_image = pygame.transform.flip(image,True,False)
			self.image = flipped_image

		# set the rect
		if self.on_ground and self.on_right:
			self.rect = self.image.get_rect(bottomright = self.rect.bottomright)
		elif self.on_ground and self.on_left:
			self.rect = self.image.get_rect(bottomleft = self.rect.bottomleft)
		elif self.on_ground:
			self.rect = self.image.get_rect(midbottom = self.rect.midbottom)
		elif self.on_ceiling and self.on_right:
			self.rect = self.image.get_rect(topright = self.rect.topright)
		elif self.on_ceiling and self.on_left:
			self.rect = self.image.get_rect(topleft = self.rect.topleft)
		elif self.on_ceiling:
			self.rect = self.image.get_rect(midtop = self.rect.midtop)

	def run_dust_animation(self):
		if self.status == 'run' and self.on_ground:
			self.dust_frame_index += self.dust_animation_speed
			if self.dust_frame_index >= len(self.dust_run_particles):
				self.dust_frame_index = 0

			dust_particle = self.dust_run_particles[int(self.dust_frame_index)]

			if self.facing_right:
				pos = self.rect.bottomleft - pygame.math.Vector2(6,10)
				self.display_surface.blit(dust_particle,pos)
			else:
				pos = self.rect.bottomright - pygame.math.Vector2(6,10)
				flipped_dust_particle = pygame.transform.flip(dust_particle,True,False)
				self.display_surface.blit(flipped_dust_particle,pos)

	def get_input(self):
		keys = pygame.key.get_pressed()

		if keys[pygame.K_RIGHT]:
			self.direction.x = 1
			self.facing_right = True
			# mixer.music.load('../Sounds/player/running_grass.mp3')
			# mixer.music.play()
		elif keys[pygame.K_LEFT]:
			self.direction.x = -1
			self.facing_right = False
		else:
			self.direction.x = 0

		if keys[pygame.K_SPACE]:
			if self.current_level==0 and self.on_ground:
				self.jump()
			elif self.current_level==1:
				self.player_jump()
			self.create_jump_particles(self.rect.midbottom)
		
	def reduce_health(self,incoming_damage):
		print("Current health is ",self.health)
		if self.health-incoming_damage<=0:
			self.player_alive=False
			self.get_status(y=0)
			self.animate()
			#return False
		else:
			self.health-=incoming_damage
			self.get_status(x=0)
			self.animate()
	
	def confirm_damage_dealing(self):
		keys = pygame.key.get_pressed()
		if keys[pygame.K_t]:
			return True
		
	def get_status(self,x=1,y=1):
		if self.direction.y < 0:
			self.status = 'jump'
		elif self.direction.y > 1:
			self.status = 'fall'
		else:
			if self.direction.x != 0:
				self.status = 'run'
			else:
				self.status = 'idle'
		if not x:
			self.status='Attack'
		if not y:
			self.status='Death'
		# if not self.player_alive:
		# 	self.status='Death'

	def apply_gravity(self):
		self.direction.y+=self.gravity
		self.rect.y+=self.direction.y

	def call_gravity(self):
		if self.rect.bottom<500:
			self.gravity+=1
			self.rect.y+=self.gravity
		else:
			self.gravity=0
			self.rect.y=500

	def call_jump(self):
		self.gravity-=0.3
		self.rect.y+=self.gravity

	def jump(self):
		jump_sound=pygame.mixer.Sound('../Sounds/player/jump.mp3')
		mixer.Sound.play(jump_sound)
		
		self.direction.y = self.jump_speed

	def player_jump(self):
		if not self.is_jump:
			self.is_jump=True
			self.player_vel.y=-self.jump_speed

		else:
			self.player_vel.y+=self.gravity
			self.rect.y += self.player_vel.y
			
			if self.rect.bottom>=self.floor:
				self.is_jump=False
				self.rect.bottom=self.floor
				self.player_vel.y=0

	def update(self):
		self.get_input()
		self.get_status()
		self.animate()
		self.run_dust_animation()
		if self.current_level==1:
			self.call_gravity()
		self.health_bar.draw(self.health)
