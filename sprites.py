import pygame
from settings import *
from support import *
from random import randint, choice
from timer import Timer
import math


# 通用精灵
class Generic(pygame.sprite.Sprite):
    def __init__(self, cache, pos, surf, groups, z=LAYERS['main']):
        super().__init__(groups)
        self.cache = cache
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = z
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2, -self.rect.height * 0.75)

    def show(self):
        self.cache.display_surface.blit(self.image, self.rect)


class Text(Generic):
    def __init__(self, cache, player, groups, number, content='here', color=(0, 0, 0), font='Arial', size=16,
                 z=LAYERS['text']):
        self.number = number
        self.player = player
        self.pos = pygame.math.Vector2(10, 10 + 20 * self.number) + cache.offset
        self.font = pygame.font.SysFont(font, size)
        self.content = content
        surf = self.font.render(content, True, color)
        self.color = color
        super().__init__(
            cache=cache,
            pos=self.pos,
            surf=surf,
            groups=groups,
            z=z)

    def update(self):
        self.pos = pygame.math.Vector2(10, 10 + 20 * self.number) + self.cache.offset
        self.image = self.font.render(self.content, True, self.color)
        self.rect = self.image.get_rect(topleft=self.pos)

    def get_content(self, content='none'):
        self.content = content


class Tool(Generic):
    def __init__(self, cache, groups, player, z):
        self.player = player
        self.cache = cache
        self.pos = pygame.math.Vector2(0, 0)
        self.ori_image = self.cache.tools_surf[self.player.selected_tool]
        super().__init__(cache=cache, pos=self.pos, surf=self.ori_image, groups=groups, z=z)

        self.angle = 0
        self.angle_offset = 0
        self.show_angle = 0
        self.inner_pos = pygame.math.Vector2(8, 64)
        self.inner_flipped_pos = pygame.math.Vector2(64, 64)

    def update(self):
        self.pos = (self.player.pos[0] + 20, self.player.pos[1] + 20)
        self.ori_image = self.cache.tools_surf[self.player.selected_tool]
        self.pointing()

    def pointing(self):
        # 计算工具贴图底边角度
        if not self.player.timers['tool'].active:
            self.angle = self.player.pointing_direction - 45  # -225 ~ 135
            while self.angle < -180:
                self.angle += 360

        if -135 < self.angle < 45:
            angle = self.show_angle - 90
            if angle < -180:
                angle += 360
            if self.player.timers['tool'].active:
                self.angle_offset -= 450 * self.cache.dt
                self.show_angle = self.angle + self.angle_offset
            else:
                self.angle_offset = 90
                self.show_angle = self.angle
            if self.show_angle > 180:
                self.show_angle -= 360
            if self.show_angle < -180:
                self.show_angle += 360
            self.image, self.rect = rotate_from_point(pygame.transform.flip(self.ori_image, True, False), self.pos,
                                                      self.inner_flipped_pos, angle)
        else:
            if self.player.timers['tool'].active:
                self.angle_offset += 450 * self.cache.dt
                self.show_angle = self.angle + self.angle_offset
            else:
                self.angle_offset = -90
                self.show_angle = self.angle
            if self.show_angle > 180:
                self.show_angle -= 360
            if self.show_angle < -180:
                self.show_angle += 360
            self.image, self.rect = rotate_from_point(self.ori_image, self.pos, self.inner_pos, self.show_angle)


class Interaction(Generic):
    def __init__(self, cache, pos, size, groups, name):
        surf = pygame.Surface(size)
        super().__init__(cache, pos, surf, groups)
        self.name = name


class Water(Generic):
    def __init__(self, cache, pos, frames, groups):
        # animation setup
        self.frames = frames
        self.frame_index = 0

        # sprite setup
        super().__init__(
            cache=cache,
            pos=pos,
            surf=self.frames[self.frame_index],
            groups=groups,
            z=LAYERS['water'])

    def animate(self):
        self.frame_index += 5 * self.cache.dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def update(self):
        self.animate()


class Decoration(Generic):
    def __init__(self, cache, pos, surf, groups):
        super().__init__(cache, pos, surf, groups)
        self.hitbox = self.rect.copy().inflate(-20, -self.rect.height * 0.9)


class Block(Generic):
    def __init__(self, cache, pos, surf, groups):
        super().__init__(cache, pos, surf, groups)
        self.hitbox = self.rect.copy().inflate(-20, -self.rect.height * 0.9)


class Particle(Generic):
    def __init__(self, cache, pos, surf, groups, z, duration=200):
        super().__init__(cache, pos, surf, groups, z)
        self.start_time = pygame.time.get_ticks()
        self.duration = duration

        # white surface
        mask_surf = pygame.mask.from_surface(self.image)
        new_surf = mask_surf.to_surface()
        new_surf.set_colorkey((0, 0, 0))
        self.image = new_surf

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time > self.duration:
            self.kill()


class Tree(Generic):
    def __init__(self, cache, pos, surf, groups, name, player_add):
        super().__init__(cache, pos, surf, groups)

        # tree attributes
        self.health = 5
        self.alive = True
        stump_path = f'./graphics/stumps/{"small" if name == "Small" else "large"}.png'
        self.stump_surf = pygame.image.load(stump_path).convert_alpha()

        # apples
        # self.apple_surf = pygame.image.load('./graphics/fruit/apple.png')
        # self.apple_pos = APPLE_POS[name]
        # self.apple_sprites = pygame.sprite.Group()
        # self.create_fruit()

        self.player_add = player_add

        # sounds
        self.axe_sound = pygame.mixer.Sound('./audio/axe.mp3')

    def damage(self):

        # damaging the tree
        self.health -= 1

        # play sound
        self.axe_sound.play()

    # remove an apple
    # if len(self.apple_sprites.sprites()) > 0:
    # 	random_apple = choice(self.apple_sprites.sprites())
    # 	Particle(
    # 		pos = random_apple.rect.topleft,
    # 		surf = random_apple.image,
    # 		groups = self.groups()[0],
    # 		z = LAYERS['fruit'])
    # 	self.player_add('apple')
    # 	random_apple.kill()

    def check_death(self):
        if self.health <= 0:
            Particle(self.cache, self.rect.topleft, self.image, self.groups()[0], LAYERS['fruit'], 300)
            self.image = self.stump_surf
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
            self.hitbox = self.rect.copy().inflate(-10, -self.rect.height * 0.6)
            self.alive = False
            self.player_add('wood')

    def update(self):
        if self.alive:
            self.check_death()

# def create_fruit(self):
# 	for pos in self.apple_pos:
# 		if randint(0,10) < 2:
# 			x = pos[0] + self.rect.left
# 			y = pos[1] + self.rect.top
# 			Generic(
# 				pos = (x,y),
# 				surf = self.apple_surf,
# 				groups = [self.apple_sprites,self.groups()[0]],
# 				z = LAYERS['fruit'])
