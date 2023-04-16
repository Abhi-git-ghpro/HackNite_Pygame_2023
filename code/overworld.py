import pygame
from game_data import levels
import settings
class Node(pygame.sprite.Sprite):
    def __init__(self,pos,status,icon_speed):
        super().__init__()
        self.image=pygame.Surface((100,80))
        if status=='available':
            self.image.fill((105,89,205))
        else:
            self.image.fill('grey')
        self.rect=self.image.get_rect(center=pos)

        self.detection_zone=pygame.Rect(self.rect.centerx-(icon_speed/2),self.rect.centery,icon_speed,icon_speed)

class Icon(pygame.sprite.Sprite):
    def __init__(self,pos):
        super().__init__()
        self.pos=pos
        self.image=pygame.Surface((20,20))
        self.image.fill('blue')
        self.rect=self.image.get_rect(center=pos)

    def update(self):
        self.rect.center=self.pos

class Overworld:
    def __init__(self,start_level,max_level,surface,create_level):
        #setup
        self.display_surface=surface
        self.max_level=max_level
        self.current_level=start_level
        self.create_level=create_level

        #movement logic
        self.move_direction=pygame.math.Vector2(0,0)
        self.speed=8
        self.moving=False

        #sprites
        self.setup_nodes()
        self.setup_icon()

    def setup_nodes(self):
        self.nodes=pygame.sprite.Group()

        for index,node_data in enumerate(levels.values()):

            if index<=self.max_level:
                node_sprite=Node(node_data['node_pos'],'available',self.speed)

            else:
                node_sprite=Node(node_data['node_pos'],'locked',self.speed)

            self.nodes.add(node_sprite)

    def draw_paths(self):
        points=[node['node_pos'] for index,node in enumerate(levels.values()) if index<=self.max_level]

#        if self.current_level:
        pygame.draw.lines(self.display_surface,(72,118,255),False,points,6)
        # else:
        #     pygame.draw.line(self.display_surface, 'red', (110,400), (300,220), 6)

    def setup_icon(self):
        self.icon=pygame.sprite.GroupSingle()
        icon_sprite=Icon(self.nodes.sprites()[self.current_level].rect.center)
        self.icon.add(icon_sprite)

    def input(self):
        keys=pygame.key.get_pressed()

        if not self.moving:
            if keys[pygame.K_RIGHT] and self.current_level<self.max_level:
                self.move_direction=self.get_movement_data('next')
                self.current_level+=1
                self.moving=True

            elif keys[pygame.K_LEFT] and self.current_level>0:
                self.move_direction=self.get_movement_data('previous')
                self.current_level-=1
                self.moving=True

            elif keys[pygame.K_RETURN]:
                self.create_level(self.current_level)

    def get_movement_data(self,target):
        start=pygame.math.Vector2(self.nodes.sprites()[self.current_level].rect.center)
        if target=='next':
            end=pygame.math.Vector2(self.nodes.sprites()[self.current_level+1].rect.center)
        else:
            end=pygame.math.Vector2(self.nodes.sprites()[self.current_level-1].rect.center)

        return (end-start).normalize()

    def update_icon_pos(self):
        # self.icon.sprite.rect.center=self.nodes.sprites()[self.current_level].rect.center
        if self.moving and self.move_direction:
            self.icon.sprite.pos+=self.move_direction*self.speed
            target_node=self.nodes.sprites()[self.current_level]
            print(target_node)
            if target_node.detection_zone.collidepoint(self.icon.sprite.pos):
                self.moving=False
                self.move_direction=pygame.math.Vector2(0,0)

    def describe_game(self):
        self.display_surface
        
        new_font=pygame.font.Font(None,50)
        game_title=new_font.render('Zombie Apocalypse',False, (225, 0, 225))
        game_title_rect=game_title.get_rect(center=(settings.screen_width / 2, settings.screen_height/9))
        new_font=pygame.font.Font(None,25)
        game_name = new_font.render('You are in a world engulfed by zombies and you have been sent to the past to save a scientist.', False, (225, 0, 0))
        game_story=new_font.render("The scientist made the antidote, find your way to him",False, (225, 0, 0))
        game_name_rect = game_name.get_rect(center=(settings.screen_width / 2, settings.screen_height/5.5))
        game_story_rect=game_story.get_rect(center=(settings.screen_width / 2, settings.screen_height/4.5))
        self.display_surface.blit(game_title,game_title_rect)
        self.display_surface.blit(game_name,game_name_rect)
        self.display_surface.blit(game_story,game_story_rect)
    
    def write_level(self):
        new_font=pygame.font.Font(None,30)
        level_0=new_font.render('Back to the past', False, (205,133,63))
        level_1=new_font.render('Save the scientist', False, (205,133,63))
        level_0_rect=level_0.get_rect(center=(110,460))
        level_1_rect=level_1.get_rect(center=(300,280))
        self.display_surface.blit(level_0,level_0_rect)
        self.display_surface.blit(level_1,level_1_rect)
    def run(self):
        self.overworld_background=pygame.image.load('../graphics/background/overworld_background.png')
        self.display_surface.blit(self.overworld_background,(0,0))
        self.input()
        self.icon.update()
        self.draw_paths()
        self.describe_game()
        self.write_level()
        self.nodes.draw(self.display_surface)
        self.icon.draw(self.display_surface)
        self.update_icon_pos()
