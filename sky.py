import pygame 
from settings import *
from support import import_folder
from sprites import Generic
from random import randint, choice

class Sky:
	def __init__(self, cache):
		self.display_surface = pygame.display.get_surface()
		self.cache = cache
		self.full_surf = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
		self.start_color = (255,255,255)
		self.current_color = [255,255,255]
		self.end_color = (38,101,189)
		self.status = DARKEN

	def display(self):
		change = 0
		if self.status:
			for index, value in enumerate(self.end_color):
				if self.current_color[index] > value:
					self.current_color[index] -= 2 * self.cache.dt
				else:
					change += 1
		else:
			for index, value in enumerate(self.start_color):
				if self.current_color[index] < value:
					self.current_color[index] += 2 * self.cache.dt
				else:
					change += 1
		if change == 3:
			self.status = 0 if self.status else 1

		self.full_surf.fill(self.current_color)
		self.display_surface.blit(self.full_surf, (0, 0), special_flags = pygame.BLEND_RGBA_MULT)


class Drop(Generic):
	def __init__(self, cache, surf, pos, moving, groups, z):
		
		# general setup
		super().__init__(cache, pos, surf, groups, z)
		self.lifetime = randint(400,500)
		self.start_time = pygame.time.get_ticks()

		# moving 
		self.moving = moving
		if self.moving:
			self.pos = pygame.math.Vector2(self.rect.topleft)
			self.direction = pygame.math.Vector2(-2,4)
			self.speed = randint(200,250)

	def update(self):
		# movement
		if self.moving:
			self.pos += self.direction * self.speed * self.cache.dt
			self.rect.topleft = (round(self.pos.x), round(self.pos.y))

		# timer
		if pygame.time.get_ticks() - self.start_time >= self.lifetime:
			self.kill()


class Rain:
	def __init__(self, cache, all_sprites):
		self.cache = cache
		self.all_sprites = all_sprites
		self.rain_drops = import_folder('./graphics/rain/drops/')
		self.rain_floor = import_folder('./graphics/rain/floor/')
		self.floor_w, self.floor_h = pygame.image.load('./graphics/world/ground.png').get_size()

	def create_floor(self):
		Drop(
			cache = self.cache,
			surf = choice(self.rain_floor), 
			pos = (randint(0,self.floor_w),randint(0,self.floor_h)), 
			moving = False, 
			groups = self.all_sprites, 
			z = LAYERS['rain floor'])

	def create_drops(self):
		Drop(
			cache=self.cache,
			surf = choice(self.rain_drops), 
			pos = (randint(0,self.floor_w),randint(0,self.floor_h)), 
			moving = True, 
			groups = self.all_sprites, 
			z = LAYERS['rain drops'])

	def update(self):
		self.create_floor()
		self.create_drops()