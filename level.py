import pygame
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic, Water, Decoration, Block, Tool, Tree, Interaction, Particle, Text
from pytmx.util_pygame import load_pygame
from support import *
from transition import Transition
from soil import SoilLayer
from sky import Rain, Sky
from random import randint
from menu import Menu
from lives import Creature
import numpy as np


class Level:
	def __init__(self, cache):
		self.cache = cache
		self.all_components = pygame.sprite.Group()

	def run(self):
		for sprite in self.all_components:
			self.cache.display_surface.blit(sprite.image, sprite.rect)
			pygame.draw.rect(self.cache.display_surface, 'red', sprite.rect, 5)


class GameLevel(pygame.sprite.Sprite):
	def __init__(self, cache, group):
		super().__init__(group)
		# 缓存区
		self.cache = cache
		# 鼠标
		self.pointing_direction = 0

		# sprite groups
		self.all_sprites = CameraGroup(self.cache)  # 渲染组
		self.collision_sprites = pygame.sprite.Group()  # 碰撞组
		self.active_collision_sprites = pygame.sprite.Group()  # 运动碰撞组
		self.tree_sprites = pygame.sprite.Group()  # 树
		self.interaction_sprites = pygame.sprite.Group()  # 交互

		self.soil_layer = SoilLayer(self.all_sprites, self.collision_sprites)
		self.setup()
		self.overlay = Overlay(self.player, self.cache)
		self.transition = Transition(self.reset, self.player)

		# self.texts = {
		# 	'sky': Text(self.cache, self.player, self.all_sprites, 1),
		# 	'player direction': Text(self.cache, self.player, self.all_sprites, 2),
		# 	'player velocity': Text(self.cache, self.player, self.all_sprites, 3),
		# 	'player status': Text(self.cache, self.player, self.all_sprites, 4),
		# 	'player position': Text(self.cache, self.player, self.all_sprites, 5),
		# 	'alice direction': Text(self.cache, self.player, self.all_sprites, 6),
		# 	'alice velocity': Text(self.cache, self.player, self.all_sprites, 7),
		# 	'alice status': Text(self.cache, self.player, self.all_sprites, 8),
		# 	'alice position': Text(self.cache, self.player, self.all_sprites, 9),
		# 	'pointing direction': Text(self.cache, self.player, self.all_sprites, 10),
		# }

		# 手持工具
		self.tool = Tool(self.cache, self.all_sprites, self.player, LAYERS['tool'])

		# sky
		self.rain = Rain(self.cache, self.all_sprites)
		self.raining = randint(0, 10) > 7
		self.soil_layer.raining = self.raining
		self.sky = Sky(self.cache)

		# shop
		self.menu = Menu(self.player, self.toggle_shop)
		self.shop_active = False

		# music
		self.success = pygame.mixer.Sound('./audio/success.wav')
		self.success.set_volume(0.3)
		self.music = pygame.mixer.Sound('./audio/music.mp3')

	# self.music.play(loops=-1)

	def setup(self):
		tmx_data = load_pygame('./datas/map.tmx')

		# house
		for layer in ['House_floor', 'House_decoration']:
			for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
				Generic(self.cache, (x * TILE_SIZE, y * TILE_SIZE), surf, [self.all_sprites, self.collision_sprites],
						LAYERS['main'])

		for layer in ['House_top']:
			for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
				Generic(self.cache, (x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, LAYERS['house top'])

		# Fence
		for x, y, surf in tmx_data.get_layer_by_name('Fence').tiles():
			Generic(self.cache, (x * TILE_SIZE, y * TILE_SIZE), surf, [self.all_sprites, self.collision_sprites])

		# water
		water_frames = import_folder('./graphics/water')
		for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
			Water(self.cache, (x * TILE_SIZE, y * TILE_SIZE), water_frames, self.all_sprites)

		# trees
		for obj in tmx_data.get_layer_by_name('Trees'):
			Tree(
				cache=self.cache,
				pos=(obj.x, obj.y),
				surf=obj.image,
				groups=[self.all_sprites, self.collision_sprites, self.tree_sprites],
				name=obj.name,
				player_add=self.player_add)

		# Decorations
		for x, y, surf in tmx_data.get_layer_by_name('Decorations').tiles():
			Generic(self.cache, (x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites)

		# Blocks
		for x, y, surf in tmx_data.get_layer_by_name('Blocks').tiles():
			Generic(self.cache, (x * TILE_SIZE, y * TILE_SIZE), surf, [self.all_sprites, self.collision_sprites])

		# collision tiles
		for x, y, surf in tmx_data.get_layer_by_name('Collision').tiles():
			Generic(self.cache, (x * TILE_SIZE, y * TILE_SIZE), pygame.Surface((TILE_SIZE, TILE_SIZE)),
					self.collision_sprites)

		# Player
		for obj in tmx_data.get_layer_by_name('Player'):
			if obj.name == 'Start':
				self.player = Player(
					pos=(obj.x, obj.y),
					group=[self.all_sprites, self.active_collision_sprites],
					collision_sprites=self.collision_sprites,
					active_collision_sprites=self.active_collision_sprites,
					tree_sprites=self.tree_sprites,
					interaction=self.interaction_sprites,
					soil_layer=self.soil_layer,
					toggle_shop=self.toggle_shop,
					cache=self.cache)

			if obj.name == 'Bed':
				Interaction(self.cache, (obj.x, obj.y), (obj.width, obj.height), self.interaction_sprites, obj.name)

			if obj.name == 'Trader':
				Interaction(self.cache, (obj.x, obj.y), (obj.width, obj.height), self.interaction_sprites, obj.name)

		for obj in tmx_data.get_layer_by_name('Creatures'):
			self.Alice = Creature(cache=self.cache,
								  pos=(obj.x, obj.y),
								  group=[self.all_sprites, self.active_collision_sprites],
								  collision_sprites=self.collision_sprites,
								  active_collision_sprites=self.active_collision_sprites,
								  species='pig',
								  category='animal', )

		Generic(
			cache=self.cache,
			pos=(0, 0),
			surf=pygame.image.load('./graphics/world/ground.png').convert_alpha(),
			groups=self.all_sprites,
			z=LAYERS['ground'])

	def player_add(self, item):

		self.player.item_inventory[item] += 1
		self.success.play()

	def toggle_shop(self):

		self.shop_active = not self.shop_active

	def reset(self):
		# plants
		self.soil_layer.update_plants()

		# soil
		self.soil_layer.remove_water()
		self.raining = randint(0, 10) > 7
		self.soil_layer.raining = self.raining
		if self.raining:
			self.soil_layer.water_all()

		# apples on the trees
		for tree in self.tree_sprites.sprites():
			for apple in tree.apple_sprites.sprites():
				apple.kill()
			tree.create_fruit()

		# sky
		self.sky.start_color = [255, 255, 255]

	def plant_collision(self):
		if self.soil_layer.plant_sprites:
			for plant in self.soil_layer.plant_sprites.sprites():
				if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
					self.player_add(plant.plant_type)
					plant.kill()
					Particle(plant.rect.topleft, plant.image, self.all_sprites, z=LAYERS['main'])
					self.soil_layer.grid[plant.rect.centery // TILE_SIZE][plant.rect.centerx // TILE_SIZE].remove('P')

	def show(self):
		# 将屏幕填充为黑色，防止闪帧（偶然看见上一帧）
		self.cache.display_surface.fill('black')
		# 绘制所有精灵
		self.all_sprites.custom_draw()
		# pygame.draw.line(self.cache.display_surface, (0, 0, 0), self.player.pos-self.cache.offset,self.Alice.pos-self.cache.offset)

		# # text
		# self.texts['sky'].get_content('Sky: ' + ','.join(map(str, np.around(self.sky.current_color, decimals=2))))
		# self.texts['player direction'].get_content('Player direction: ' + '{:.2f}'.format(self.player.direction))
		# self.texts['player velocity'].get_content('Player velocity: ' + '{:.2f}'.format(self.player.velocity))
		# self.texts['player status'].get_content('Player status: ' + self.player.status)
		# self.texts['player position'].get_content('Player position: ' + str(self.player.pos))
		# self.texts['alice direction'].get_content('Alice direction: ''{:.2f}'.format(self.Alice.direction))
		# self.texts['alice velocity'].get_content('Alice velocity: ''{:.2f}'.format(self.Alice.velocity))
		# self.texts['alice position'].get_content('Alice position: ' + str(self.Alice.pos))
		# self.texts['alice status'].get_content('Alice status: ' + self.Alice.status)
		# self.texts['pointing direction'].get_content(
		# 	'Pointing direction: ''{:.2f}'.format(self.player.pointing_direction))

		# updates
		if self.shop_active:
			self.menu.update()
		else:
			self.all_sprites.update()
			self.plant_collision()

		# weather
		self.overlay.display()
		if self.raining and not self.shop_active:
			self.rain.update()
		self.sky.display()

		# transition overlay
		if self.player.sleep:
			self.transition.play()


class CameraGroup(pygame.sprite.Group):
	def __init__(self, cache):
		super().__init__()
		self.cache = cache

	def custom_draw(self):

		for layer in LAYERS.values():
			for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
				if sprite.z == layer:
					offset_rect = sprite.rect.copy()
					offset_rect.center -= self.cache.offset
					self.cache.display_surface.blit(sprite.image, offset_rect)
					# analytics
					# if hasattr(sprite, 'mass'):
					# 	pygame.draw.rect(self.cache.display_surface, 'red', offset_rect, 5)
					# 	hitbox_rect = sprite.hitbox.copy()
					# 	hitbox_rect.center -= self.cache.offset
					# 	pygame.draw.rect(self.cache.display_surface, 'green', hitbox_rect, 5)
					# 	pygame.draw.circle(self.cache.display_surface, 'blue', sprite.hitcircle.center - self.cache.offset,
					# 					   sprite.hitcircle.radius, 5)
					#
					# 	# target_pos = offset_rect.center + PLAYER_TOOL_OFFSET[player.status.split('_')[0]]
					# 	# pygame.draw.circle(self.display_surface,'blue',target_pos,5)
					#
					# 	pygame.draw.circle(self.cache.display_surface, 'blue', self.cache.mouse_pos - self.cache.offset, 5)
