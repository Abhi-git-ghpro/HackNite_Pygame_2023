import pygame
from random import randint
from support import import_csv_layout, import_cut_graphics
from settings import *
from tiles import *
from enemy import Enemy
from decoration import Water
from player import Player
from particles import ParticleEffect
from game_data import levels
from pygame import mixer
import random
import button
mixer.init()


class Level:
	def __init__(self,current_level,surface,create_overworld):
		# general setup
		self.display_surface = surface
		self.world_shift = 0
		self.current_x = None
		self.running=True
		self.current_time=pygame.time.get_ticks()

		#overworld
		self.create_overworld=create_overworld
		self.current_level=current_level
		level_data=levels[self.current_level]
		self.latest_max_level=level_data['unlock']

		# player 
		player_layout = import_csv_layout(level_data['player'])
		self.player = pygame.sprite.GroupSingle()
		self.goal = pygame.sprite.GroupSingle()
		self.player_setup(player_layout)
		self.damage_to_enemy_per_attack=100

		# dust 
		self.dust_sprite = pygame.sprite.GroupSingle()
		self.player_on_ground = False

		# terrain setup
		if self.current_level==0:
			terrain_layout = import_csv_layout(level_data['terrain'])
			self.terrain_sprites = self.create_tile_group(terrain_layout,'terrain')

			# crates 
			crate_layout = import_csv_layout(level_data['crates'])
			self.crate_sprites = self.create_tile_group(crate_layout,'crates')

			# enemy 
			enemy_layout = import_csv_layout(level_data['enemies'])
			self.enemy_sprites = self.create_tile_group(enemy_layout,'enemies')
			self.damage_to_player_per_attack=15

			# constraint 
			constraint_layout = import_csv_layout(level_data['constraints'])
			self.constraint_sprites = self.create_tile_group(constraint_layout,'constraint')

			# decoration 
			level_width = len(terrain_layout[0]) * tile_size
			self.water = Water(screen_height - 20,level_width)

		#background
		self.background = pygame.image.load(level_data['background'])

	def create_tile_group(self,layout,type):
		if self.current_level==0:
			sprite_group = pygame.sprite.Group()

			for row_index, row in enumerate(layout):
				for col_index,val in enumerate(row):
					if val != '-1':
						x = col_index * tile_size
						y = row_index * tile_size

						if type == 'terrain':
							terrain_tile_list = import_cut_graphics('../graphics/terrain/terrain_tiles.png')
							tile_surface = terrain_tile_list[int(val)]
							sprite = StaticTile(tile_size,x,y,tile_surface)
						
						if type == 'crates':
							sprite = Crate(tile_size,x,y)

						if type == 'enemies':
							sprite = Enemy(tile_size,x,y)

						if type == 'constraint':
							sprite = Tile(tile_size,x,y)

						sprite_group.add(sprite)
			
			return sprite_group

	def player_setup(self,layout):
		for row_index, row in enumerate(layout):
			for col_index,val in enumerate(row):
				x = col_index * tile_size
				y = row_index * tile_size
				if val == '0':
					sprite = Player((x,y),self.display_surface,self.create_jump_particles,self.current_level)
					self.start_pos = (x, y) 
					self.player.add(sprite)
				if val == '1':
					hat_surface = pygame.image.load('../graphics/character/hat.png').convert_alpha()
					sprite = StaticTile(tile_size,x,y,hat_surface)
					self.goal.add(sprite)

	def damage_to_player_by_enemy(self):
		for enemy in self.enemy_sprites.sprites():
			if self.player.sprite.health and enemy.health and enemy.rect.colliderect(self.player.sprite.rect):
				
				self.player.sprite.reduce_health(self.damage_to_player_per_attack)
				if not self.player.sprite.player_alive:
					pygame.time.delay(1000)
					
					self.player.sprite.animate()
					self.running=False
		
		# self.player.sprite.reduce_health(self.damage_to_player_per_attack)
		
	def damage_to_enemy_by_player(self):
		for enemy in self.enemy_sprites.sprites():
			if enemy.isAlive and self.player.sprite.confirm_damage_dealing() and enemy.rect.colliderect(self.player.sprite.rect):
				enemy.take_damage(self.damage_to_enemy_per_attack)

	def enemy_collision_reverse(self):
		for enemy in self.enemy_sprites.sprites():
			if pygame.sprite.spritecollide(enemy,self.constraint_sprites,False):
				enemy.reverse()
			#Changing
			enemy.vision=pygame.Rect(0,0,2,20)
			enemy.vision.center=(enemy.rect.centerx +16 *1,enemy.rect.centery)
			if enemy.vision.colliderect(self.player.sprite.rect):
				enemy.damage()
				
				self.damage_to_player_by_enemy()
				self.damage_to_enemy_by_player()
			dist=self.player.sprite.rect.x - enemy.rect.x
			if dist<64 and dist >0:
				enemy.kill(1)
			elif dist>64 and dist >180:
				enemy.kill(0)
				self.damage_to_player_by_enemy()
				self.damage_to_enemy_by_player()
			#Change end
	
	def create_jump_particles(self,pos):
		if self.player.sprite.facing_right:
			pos -= pygame.math.Vector2(10,5)
		else:
			pos += pygame.math.Vector2(10,-5)
		jump_particle_sprite = ParticleEffect(pos,'jump')
		self.dust_sprite.add(jump_particle_sprite)

	def horizontal_movement_collision(self):
		player = self.player.sprite
		player.rect.x += player.direction.x * player.speed
		if self.current_level==0:
			collidable_sprites = self.terrain_sprites.sprites() + self.crate_sprites.sprites()
			for sprite in collidable_sprites:
				if sprite.rect.colliderect(player.rect):
					if player.direction.x < 0: 
						player.rect.left = sprite.rect.right
						player.on_left = True
						self.current_x = player.rect.left
					elif player.direction.x > 0:
						player.rect.right = sprite.rect.left
						player.on_right = True
						self.current_x = player.rect.right
				
			if player.on_left and (player.rect.left < self.current_x or player.direction.x >= 0):
				player.on_left = False
			if player.on_right and (player.rect.right > self.current_x or player.direction.x <= 0):
				player.on_right = False

	def vertical_movement_collision(self):
		player = self.player.sprite
		player.apply_gravity()
		if self.current_level==0:
			collidable_sprites = self.terrain_sprites.sprites() + self.crate_sprites.sprites()

			for sprite in collidable_sprites:
				if sprite.rect.colliderect(player.rect):
					if player.direction.y > 0: 
						player.rect.bottom = sprite.rect.top
						player.direction.y = 0
						player.on_ground = True
					elif player.direction.y < 0:
						player.rect.top = sprite.rect.bottom
						player.direction.y = 0
						player.on_ceiling = True

			if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
				player.on_ground = False
			if player.on_ceiling and player.direction.y > 0.1:
				player.on_ceiling = False

	def scroll_x(self):
		player = self.player.sprite
		player_x = player.rect.centerx
		direction_x = player.direction.x

		if player_x < screen_width / 4 and direction_x < 0:
			self.world_shift = 8
			player.speed = 0
		elif player_x > screen_width - (screen_width / 4) and direction_x > 0:
			self.world_shift = -8
			player.speed = 0
		else:
			self.world_shift = 0
			player.speed = 8

	def get_player_on_ground(self):
		if self.player.sprite.on_ground:
			self.player_on_ground = True
		else:
			self.player_on_ground = False

	def create_landing_dust(self):
		if not self.player_on_ground and self.player.sprite.on_ground and not self.dust_sprite.sprites():
			if self.player.sprite.facing_right:
				offset = pygame.math.Vector2(10,15)
			else:
				offset = pygame.math.Vector2(-10,15)
			fall_dust_particle = ParticleEffect(self.player.sprite.rect.midbottom - offset,'land')
			self.dust_sprite.add(fall_dust_particle)

	def game_over(self):
		if self.player.sprite.rect.y>704:
			self.player.sprite.rect.y=200
			self.running=False

	def win(self):
		if pygame.sprite.spritecollide(self.player.sprite,self.goal,False):
			self.running='win'
			self.current_level+=1

	def run(self):
		if self.running==True and self.current_level==0:
			# run the entire game / level 
			self.display_surface.blit(self.background, (0, 0))

			# terrain 
			if self.current_level==0:
				self.terrain_sprites.update(self.world_shift)
				self.terrain_sprites.draw(self.display_surface)
				
				# enemy 
				self.enemy_sprites.update(self.world_shift)
				self.constraint_sprites.update(self.world_shift)
				self.enemy_collision_reverse()
				self.enemy_sprites.draw(self.display_surface)

				# crate 
				self.crate_sprites.update(self.world_shift)
				self.crate_sprites.draw(self.display_surface)

				# water 
				self.water.draw(self.display_surface,self.world_shift)

			# else:
			# 	self.apply_gravity()

			# dust particles 
			self.dust_sprite.update(self.world_shift)
			self.dust_sprite.draw(self.display_surface)

			# player sprites
			self.player.update()
			self.horizontal_movement_collision()
			
			self.get_player_on_ground()
			self.vertical_movement_collision()
			self.create_landing_dust()
			
			self.scroll_x()
			self.player.draw(self.display_surface)
			self.goal.update(self.world_shift)
			self.goal.draw(self.display_surface)

			#gen setup
			self.game_over()
			self.win()

		elif self.running=='win':
			game_story=test_font.render("Reached the end, save the scientist from the zombies",False, (111, 196, 169))
			game_message = test_font.render('Press up arrow to load levels map', False, (111, 196, 169))

			self.display_surface.blit(game_message,game_message_rect)
			self.display_surface.blit(game_story,game_story_rect)
			self.display_surface.blit(game_name,game_name_rect)

			keys=pygame.key.get_pressed()
			if keys[pygame.K_UP]:
				self.create_overworld(self.current_level,self.latest_max_level)

		elif self.running==False:	

			game_message=test_font.render("You lost, restart the game",False,(111, 196, 169))

			self.display_surface.blit(game_message,game_message_rect)

			self.display_surface.blit(game_name,game_name_rect)

		elif self.current_level==1:
			
			sword_clash=mixer.Sound('../Sounds/Knight/sword_clash.mp3')
			knight_hurt=mixer.Sound('../Sounds/Knight/knight_hurt.mp3')
			blood=mixer.Sound('../Sounds/Knight/blood.mp3')
			knight_death=mixer.Sound('../Sounds/Knight/knight_death.mp3')
			bandit_death=mixer.Sound('../Sounds/Knight/bandit_death.mp3')
			game_over_sound=mixer.Sound('../Sounds/player/demon_game_over.mp3')
			victory_song=mixer.Sound('../Sounds/Knight/victory_song.mp3')
			clock = pygame.time.Clock()
			fps = 60

			#game window
			bottom_panel = 150
			screen_width = 800
			screen_height = 400+ bottom_panel

			screen = pygame.display.set_mode((screen_width, screen_height))
			pygame.display.set_caption('Battle')

			#define game variables
			current_fighter = 1
			total_fighters = 3
			action_cooldown = 0
			action_wait_time = 90
			attack = False
			potion = False
			potion_effect = 24
			clicked = False
			game_over = 0


			#define fonts
			font = pygame.font.SysFont('Times New Roman', 26)

			#define colours
			red = (255, 0, 0)
			green = (0, 255, 0)

			#load images
			#background image
			background_img = pygame.image.load('../graphics/background/lab_background.png').convert_alpha()
			#panel image
			panel_img = pygame.image.load('../graphics/img/Icons/panel.png').convert_alpha()
			#button images
			potion_img = pygame.image.load('../graphics/img/Icons/potion.png').convert_alpha()
			restart_img = pygame.image.load('../graphics/img/Icons/restart.png').convert_alpha()
			#load victory and defeat images
			victory_img = pygame.image.load('../graphics/img/Icons/victory.png').convert_alpha()
			defeat_img = pygame.image.load('../graphics/img/Icons/defeat.png').convert_alpha()
			#sword image
			sword_img = pygame.image.load('../graphics/img/Icons/sword.png').convert_alpha()


			#create function for drawing text
			def draw_text(text, font, text_col, x, y):
				img = font.render(text, True, text_col)
				screen.blit(img, (x, y))


			#function for drawing background
			def draw_bg():
				screen.blit(background_img, (0, 0))


			#function for drawing panel
			def draw_panel():
				#draw panel rectangle
				#screen_height - bottom_panel
				screen.blit(panel_img, (0, 0))
				#show knight stats
				draw_text(f'{knight.name} HP: {knight.hp}', font, red, 100, bottom_panel - 120)
				for count, i in enumerate(bandit_list):
					#show name and health
					draw_text(f'{i.name} HP: {i.hp}', font, red, 550, bottom_panel - 80 - count * 60)

			#fighter class
			class Fighter():
				def __init__(self, x, y, name, max_hp, strength, potions):
					self.name = name
					self.max_hp = max_hp
					self.hp = max_hp
					self.strength = strength
					self.start_potions = potions
					self.potions = potions
					self.alive = True
					self.wait_for_music=0
					self.knight_dies=1
					self.play_demon_game_over=1
					self.animation_list = []
					self.frame_index = 0
					self.action = 0#0:idle, 1:attack, 2:hurt, 3:dead
					self.update_time = pygame.time.get_ticks()
					#load idle images
					temp_list = []
					for i in range(8):
						img = pygame.image.load(f'../graphics/img/{self.name}/Idle/{i}.png')
						if self.name=='Knight':
							img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
						else:
							img = pygame.transform.scale(img, (img.get_width() , img.get_height()))
						temp_list.append(img)
					self.animation_list.append(temp_list)
					#load attack images
					temp_list = []
					for i in range(8):
						img = pygame.image.load(f'../graphics/img/{self.name}/Attack/{i}.png')
						if self.name=='Knight':
							img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
						else:
							img = pygame.transform.scale(img, (img.get_width() , img.get_height()))
						temp_list.append(img)
					self.animation_list.append(temp_list)
					#load hurt images
					temp_list = []
					for i in range(3):
						img = pygame.image.load(f'../graphics/img/{self.name}/Hurt/{i}.png')
						if self.name=='Knight':
							img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
						else:
							img = pygame.transform.scale(img, (img.get_width() , img.get_height()))
						temp_list.append(img)
					self.animation_list.append(temp_list)
					#load death images
					temp_list = []
					for i in range(10):
						img = pygame.image.load(f'../graphics/img/{self.name}/Death/{i}.png')
						if self.name=='Knight':
							img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
						else:
							img = pygame.transform.scale(img, (img.get_width() , img.get_height()))
						temp_list.append(img)
					self.animation_list.append(temp_list)
					self.image = self.animation_list[self.action][self.frame_index]
					self.rect = self.image.get_rect()
					self.rect.center = (x, y)


				def update(self):
					animation_cooldown = 100
					#handle animation
					#update image
					self.image = self.animation_list[self.action][self.frame_index]
					#check if enough time has passed since the last update
					if pygame.time.get_ticks() - self.update_time > animation_cooldown:
						self.update_time = pygame.time.get_ticks()
						self.frame_index += 1
					#if the animation has run out then reset back to the start
					if self.frame_index >= len(self.animation_list[self.action]):
						if self.action == 3:
							self.frame_index = len(self.animation_list[self.action]) - 1
						else:
							self.idle()


				
				def idle(self):
					#set variables to idle animation
					self.action = 0
					self.frame_index = 0
					self.update_time = pygame.time.get_ticks()


				def attack(self, target):
					#deal damage to enemy
					rand = random.randint(-5, 5)
					damage = self.strength + rand
					mixer.Sound.play(sword_clash)
					target.hp -= damage
					#run enemy hurt animation
					target.hurt()
					#check if target has died
					if target.hp < 1:
						target.hp = 0
						target.alive = False
						mixer.Sound.play(bandit_death)
						target.death()
					damage_text = DamageText(target.rect.centerx, target.rect.y, str(damage), red)
					damage_text_group.add(damage_text)
					#set variables to attack animation
					self.action = 1
					self.frame_index = 0
					self.update_time = pygame.time.get_ticks()

				def hurt(self):
					#set variables to hurt animation
					self.action = 2
					self.frame_index = 0
					mixer.Sound.play(knight_hurt)
					self.update_time = pygame.time.get_ticks()

				def death(self):
					#set variables to death animation
					self.action = 3
					self.frame_index = 0
					self.update_time = pygame.time.get_ticks()


				def reset (self):
					self.alive = True
					self.potions = self.start_potions
					self.hp = self.max_hp
					self.frame_index = 0
					self.action = 0
					self.update_time = pygame.time.get_ticks()


				def draw(self):
					screen.blit(self.image, self.rect)
				def play_knight_death(self):
					
					if self.knight_dies:

						mixer.Sound.play(knight_death)
						self.knight_dies=0
					
				def play_game_over(self):
					self.wait_for_music=pygame.time.get_ticks()
					if self.play_demon_game_over:
						mixer.Sound.play(game_over_sound)
						self.play_demon_game_over=0
					return

			class HealthBar():
				def __init__(self, x, y, hp, max_hp):
					self.x = x
					self.y = y
					self.hp = hp
					self.max_hp = max_hp


				def draw(self, hp):
					#update with new health
					self.hp = hp
					#calculate health ratio
					ratio = self.hp / self.max_hp
					pygame.draw.rect(screen, red, (self.x, self.y, 150, 20))
					pygame.draw.rect(screen, green, (self.x, self.y, 150 * ratio, 20))



			class DamageText(pygame.sprite.Sprite):
				def __init__(self, x, y, damage, colour):
					pygame.sprite.Sprite.__init__(self)
					self.image = font.render(damage, True, colour)
					self.rect = self.image.get_rect()
					self.rect.center = (x, y)
					self.counter = 0


				def update(self):
					#move damage text up
					self.rect.y -= 1
					#delete the text after a few seconds
					self.counter += 1
					if self.counter > 30:
						self.kill()



			damage_text_group = pygame.sprite.Group()


			knight = Fighter(300, 400, 'Knight', 50, 13, 3)
			bandit1 = Fighter(450, 400, 'Zombie', 30, 5, 2)
			bandit2 = Fighter(600, 400, 'Zombie', 30, 7, 1)

			bandit_list = []
			bandit_list.append(bandit1)
			bandit_list.append(bandit2)

			knight_health_bar = HealthBar(100, bottom_panel - 75, knight.hp, knight.max_hp)
			bandit1_health_bar = HealthBar(550, bottom_panel - 40, bandit1.hp, bandit1.max_hp)
			bandit2_health_bar = HealthBar(550, bottom_panel - 100, bandit2.hp, bandit2.max_hp)

			#create buttons
			potion_button = button.Button(screen, 100, screen_height - bottom_panel + 70, potion_img, 64, 64)
			restart_button = button.Button(screen, 330, 120, restart_img, 120, 30)

			
			run = True
			while run:

				clock.tick(fps)

				#draw background
				draw_bg()
				time_machine_image=pygame.image.load('../graphics/img/Scientist/time_machine.png').convert_alpha()
				time_machine_image=pygame.transform.scale(time_machine_image,(128,128))
				screen.blit(time_machine_image, (650, 400))

				#draw panel
				draw_panel()
				knight_health_bar.draw(knight.hp)
				bandit1_health_bar.draw(bandit1.hp)
				bandit2_health_bar.draw(bandit2.hp)

				#draw fighters
				knight.update()
				knight.draw()
				for bandit in bandit_list:
					bandit.update()
					bandit.draw()

				#draw the damage text
				damage_text_group.update()
				damage_text_group.draw(screen)

				#control player actions
				#reset action variables
				attack = False
				potion = False
				target = None
				#make sure mouse is visible
				pygame.mouse.set_visible(True)
				pos = pygame.mouse.get_pos()
				for count, bandit in enumerate(bandit_list):
					if bandit.rect.collidepoint(pos):
						#hide mouse
						pygame.mouse.set_visible(False)
						#show sword in place of mouse cursor
						screen.blit(sword_img, pos)
						if clicked == True and bandit.alive == True:
							attack = True
							target = bandit_list[count]
				if potion_button.draw():
					potion = True
				#show number of potions remaining
				draw_text(str(knight.potions), font, red, 150, screen_height - bottom_panel + 70)


				if game_over == 0:
					#player action
					if knight.alive == True:
						if current_fighter == 1:
							action_cooldown += 1
							if action_cooldown >= action_wait_time:
								#look for player action
								#attack
								if attack == True and target != None:
									mixer.Sound.play(sword_clash)
									knight.attack(target)
									
									current_fighter += 1
									action_cooldown = 0
								#potion
								if potion == True:
									if knight.potions > 0:
										#check if the potion would heal the player beyond max health
										if knight.max_hp - knight.hp > potion_effect:
											heal_amount = potion_effect
										else:
											heal_amount = knight.max_hp - knight.hp
										knight.hp += heal_amount
										knight.potions -= 1
										damage_text = DamageText(knight.rect.centerx, knight.rect.y, str(heal_amount), green)
										damage_text_group.add(damage_text)
										current_fighter += 1
										action_cooldown = 0
					else:
						game_over = -1


					#enemy action
					for count, bandit in enumerate(bandit_list):
						if current_fighter == 2 + count:
							if bandit.alive == True:
								action_cooldown += 1
								if action_cooldown >= action_wait_time:
									#check if bandit needs to heal first
									if (bandit.hp / bandit.max_hp) < 0.5 and bandit.potions > 0:
										#check if the potion would heal the bandit beyond max health
										if bandit.max_hp - bandit.hp > potion_effect:
											heal_amount = potion_effect
										else:
											heal_amount = bandit.max_hp - bandit.hp
										bandit.hp += heal_amount
										bandit.potions -= 1
										damage_text = DamageText(bandit.rect.centerx, bandit.rect.y, str(heal_amount), green)
										damage_text_group.add(damage_text)
										current_fighter += 1
										action_cooldown = 0
									#attack
									else:
										bandit.attack(knight)
										current_fighter += 1
										action_cooldown = 0
							else:
								current_fighter += 1

					#if all fighters have had a turn then reset
					if current_fighter > total_fighters:
						current_fighter = 1


				#check if all bandits are dead
				alive_bandits = 0
				for bandit in bandit_list:
					if bandit.alive == True:
						alive_bandits += 1
				if alive_bandits == 0:
					game_over = 1


				#check if game is over
				if game_over != 0:
					if game_over == 1:
						mixer.Sound.play(victory_song)
						victory_background=pygame.image.load('../graphics/background/ending.png')
						self.display_surface.blit(victory_background,(0,0))

						#pygame.time.delay(2000)
						scientist_img=pygame.image.load('../graphics/img/Scientist/scientist.png').convert_alpha()
						scientist_img=pygame.transform.scale(scientist_img,(128,128))
						screen.blit(scientist_img, (650, 280))
						new_font=pygame.font.Font(None,25)
						new_font.set_bold(True)

						game_over_text=new_font.render('You saved me! I can finally launch the antidote and save the world from zombies',False,'red')
						
						# game_over_text=new_font.render('You saved me! Here is the antidote you came here looking for',False,(255,20,147))
						game_over_text_rect=game_over_text.get_rect(center=(450,250))

						self.display_surface.blit(game_over_text,game_over_text_rect)
							
						time_machine_text=new_font.render('Here is my time machine, you can use it to return back to your time',False,'red')
						# time_machine_text=new_font.render('Here is my time machine as you know I had for years',False,	(255,20,147))
						time_machine_text_rect=time_machine_text.get_rect(center=(500,300))

						self.display_surface.blit(time_machine_text,time_machine_text_rect)
						
					if game_over == -1:
						knight.play_knight_death()
						knight.play_game_over()
						
						#screen.blit(defeat_img, (290, 50))
					if game_over!=1:
						if restart_button.draw():
							knight.reset()
							for bandit in bandit_list:
								bandit.reset()
							current_fighter = 1
							action_cooldown
							game_over = 0
						
				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						run = False
					if event.type == pygame.MOUSEBUTTONDOWN:
						clicked = True
					else:
						clicked = False

				pygame.display.update()

			pygame.quit()

						
			self.player.sprite.animate()
			pygame.time.delay(1000)

