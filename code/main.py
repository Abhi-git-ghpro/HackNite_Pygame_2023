import pygame
from random import randint
from pygame import mixer
import sys
from level import Level
from settings import *
from game_data import level_0
from game_data import *
from overworld import Overworld

# Pygame setup
pygame.init()
mixer.init()
pygame.mixer.set_num_channels(20)
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
# s=['bg1.mp3','bg2.mp3','bg3.mp3']
# q=s[randint(0,2)]
# p='../Sounds/background/'+q
# pygame.mixer.Channel(True).play(pygame.mixer.Sound(p))
mixer.Channel(True).play(pygame.mixer.Sound('../Sounds/background/bg1.mp3'))
class Game:
	def __init__(self):
		self.max_level=1
		self.overworld=Overworld(0,self.max_level,screen,self.create_level)
		self.status='overworld'

	def create_level(self,current_level):
		self.level=Level(current_level,screen,self.create_overworld)
		self.status='level'

	def create_overworld(self,current_level,new_max_level):
		if new_max_level>self.max_level:
			self.max_level=new_max_level
		self.overworld=Overworld(current_level,self.max_level,screen,self.create_level)
		self.status='overworld'

	def run(self):
		if self.status=='overworld': 
			self.overworld.run()

		else:
			self.level.run()


game=Game()
# knight = Fighter(200, 260, 'Knight', 3, 10, 3)

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()
	
	screen.fill('black')
	#for i in range(1,4):
	# mixer.music.load('../Sounds/background/bg1.mp3')
	# mixer.music.play()
	
	
	game.run()
	pygame.display.update()
	clock.tick(60)
