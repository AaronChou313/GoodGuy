import pygame
from settings import *
from support import *
from timer import Timer
from lives import Creature
import math

class Player(Creature):
	def __init__(self, pos, group, collision_sprites, active_collision_sprites, tree_sprites, interaction, soil_layer, toggle_shop, cache):
		super().__init__(
				cache = cache,
				pos = pos,
				group = group,
				collision_sprites = collision_sprites,
				active_collision_sprites= active_collision_sprites,
				species = 'Alice',
				category = 'player',
				actions = ['tool'])
		# 质量
		self.mass = 20
		self.speed = 500
		# 计时器
		self.timers.update({
			'tool': Timer(400, self.use_tool),
			'tool switch': Timer(200),
			'seed use': Timer(350, self.use_seed),
			'seed switch': Timer(200),
		})

		# tools
		self.tools = self.cache.tools
		self.tool_index = 0
		self.selected_tool = self.tools[self.tool_index]

		self.pointing_direction = 0

		# seeds
		self.seeds = ['corn', 'tomato']
		self.seed_index = 0
		self.selected_seed = self.seeds[self.seed_index]

		# inventory
		self.item_inventory = {
			'wood': 20,
			'apple': 20,
			'corn': 20,
			'tomato': 20
		}
		self.seed_inventory = {
			'corn': 5,
			'tomato': 5
		}
		self.money = 200

		# interaction
		self.tree_sprites = tree_sprites
		self.interaction = interaction
		self.sleep = False
		self.soil_layer = soil_layer
		self.toggle_shop = toggle_shop

		# sound
		self.watering = pygame.mixer.Sound('./audio/water.mp3')
		self.watering.set_volume(0.2)

	def use_tool(self):
		if self.selected_tool == 'hoe':
			self.soil_layer.get_hit(self.target_pos)

		if self.selected_tool == 'axe':
			for tree in self.tree_sprites.sprites():
				if tree.rect.collidepoint(self.cache.mouse_pos):
					tree.damage()

		if self.selected_tool == 'water':
			self.soil_layer.water(self.target_pos)
			self.watering.play()

	def get_target_pos(self):
		self.target_pos = self.rect.center + PLAYER_TOOL_OFFSET[self.status.split('_')[0]]

	def use_seed(self):
		if self.seed_inventory[self.selected_seed] > 0:
			self.soil_layer.plant_seed(self.target_pos, self.selected_seed)
			self.seed_inventory[self.selected_seed] -= 1

	def input(self):
		keys = pygame.key.get_pressed()
		self.cache.mouse_pos = pygame.mouse.get_pos() + self.cache.offset
		self.cache.mouse_pressed = pygame.mouse.get_pressed()
		self.cache.mouse_wheel = self.cache.mouse_wheel
		# 鼠标方向
		self.pointing_direction = -math.degrees(math.atan2(self.cache.mouse_pos[1] - self.rect.centery,
														   self.cache.mouse_pos[0] - self.rect.centerx))

		# 只有当不在使用工具时才能走动和使用工具
		if not self.sleep:
			# 方向
			if (keys[pygame.K_UP] or keys[pygame.K_w]) and (keys[pygame.K_RIGHT] or keys[pygame.K_d]):
				self.direction = 315
				self.status = 'up_walk'
				self.velocity = self.speed
			elif (keys[pygame.K_UP] or keys[pygame.K_w]) and (keys[pygame.K_LEFT] or keys[pygame.K_a]):
				self.direction = 225
				self.status = 'up_walk'
				self.velocity = self.speed
			elif (keys[pygame.K_DOWN] or keys[pygame.K_s]) and (keys[pygame.K_RIGHT] or keys[pygame.K_d]):
				self.direction = 45
				self.status = 'right_walk'
				self.velocity = self.speed
			elif (keys[pygame.K_DOWN] or keys[pygame.K_s]) and (keys[pygame.K_LEFT] or keys[pygame.K_a]):
				self.direction = 135
				self.status = 'left_walk'
				self.velocity = self.speed
			elif keys[pygame.K_UP] or keys[pygame.K_w]:
				self.direction = 270
				self.status = 'up_walk'
				self.velocity = self.speed
			elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
				self.direction = 90
				self.status = 'down_walk'
				self.velocity = self.speed
			elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
				self.direction = 0
				self.status = 'right_walk'
				self.velocity = self.speed
			elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
				self.direction = 180
				self.status = 'left_walk'
				self.velocity = self.speed
			# 当正在使用工具时不允许进行交互操作
			if not self.timers['tool'].active:
				# 使用工具
				if self.cache.mouse_pressed[0]:
					self.timers['tool'].activate()
					self.frame_index = 0

				# 切换工具
				if keys[pygame.K_q] and not self.timers['tool switch'].active:
					self.timers['tool switch'].activate()
					self.tool_index += 1
					self.tool_index = self.tool_index if self.tool_index < len(self.tools) else 0
					self.selected_tool = self.tools[self.tool_index]

				if self.cache.mouse_wheel == 'down':
					self.tool_index += 1
					self.tool_index = self.tool_index if self.tool_index < len(self.tools) else 0
					self.selected_tool = self.tools[self.tool_index]

				if self.cache.mouse_wheel == 'up':
					self.tool_index -= 1
					self.tool_index = self.tool_index if self.tool_index >= 0 else (len(self.tools) - 1)
					self.selected_tool = self.tools[self.tool_index]

				for i in range(1, 9):
					if keys[eval('pygame.K_'+str(i))] and i - 1 < len(self.tools) and not self.timers['tool switch'].active:
						self.timers['tool switch'].activate()
						self.tool_index = i - 1
						self.selected_tool = self.tools[self.tool_index]

				self.cache.update_mouse_wheel('none')

				# seed use
				if keys[pygame.K_LCTRL]:
					self.timers['seed use'].activate()
					self.frame_index = 0

				# change seed
				if keys[pygame.K_e] and not self.timers['seed switch'].active:
					self.timers['seed switch'].activate()
					self.seed_index += 1
					self.seed_index = self.seed_index if self.seed_index < len(self.seeds) else 0
					self.selected_seed = self.seeds[self.seed_index]

				if keys[pygame.K_RETURN]:
					collided_interaction_sprite = pygame.sprite.spritecollide(self, self.interaction, False)
					if collided_interaction_sprite:
						if collided_interaction_sprite[0].name == 'Trader':
							self.toggle_shop()
						else:
							self.status = 'left_idle'
							self.sleep = True

	def update_timers(self):
		for timer in self.timers.values():
			timer.update()

	def update(self):
		self.cache.offset = pygame.math.Vector2(self.pos[0] - SCREEN_WIDTH / 2, self.pos[1] - SCREEN_HEIGHT / 2)
		self.input()
		self.get_status()
		self.update_timers()
		self.get_target_pos()

		self.move(self.cache.dt)
		self.animate(self.cache.dt)
