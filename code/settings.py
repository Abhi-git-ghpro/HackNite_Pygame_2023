import pygame
pygame.font.init()

vertical_tile_number = 11
tile_size = 64 

screen_height = vertical_tile_number * tile_size
screen_width = 1200

test_font = pygame.font.Font(None, 50)
game_name = test_font.render('Zombie Apocalypse', False, (111, 196, 169))
game_name_rect = game_name.get_rect(center=(screen_width / 2, screen_height/4))
game_story=test_font.render("Reach to the end, save the scientist!! That's your only chance",False, (111, 196, 169))
game_story_rect = game_name.get_rect(center=(screen_width / 4, screen_height/2))
game_message = test_font.render('Please restart the game', False, (111, 196, 169))
game_message_rect = game_message.get_rect(center=(screen_width/2, 3*screen_height/4))