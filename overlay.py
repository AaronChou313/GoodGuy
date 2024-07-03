import pygame
from settings import *

# 置顶显示层（工具栏、状态栏等）
class Overlay:
	def __init__(self,player,graphics):

		# 获取屏幕和玩家
		self.display_surface = pygame.display.get_surface()
		self.player = player
		self.graphics = graphics

		# 导入工具贴图
		overlay_inventory_path = './graphics/overlay/inventory/'
		self.inventory_surf = pygame.image.load(f'{overlay_inventory_path}inventory.png').convert_alpha()
		self.inventory_item_box_surf = pygame.image.load(f'{overlay_inventory_path}inventory_item.png').convert_alpha()
		self.tools_surf = graphics.tools_surf
		# self.seeds_surf = {seed: pygame.image.load(f'{overlay_path}{seed}.png').convert_alpha() for seed in player.seeds}
		self.tools_list = list(self.tools_surf.keys())

	def display(self):
		# 显示物品栏
		inventory_rect = self.inventory_surf.get_rect(bottomleft=INVENTORY_OUTER_POSITION)
		self.display_surface.blit(self.inventory_surf, inventory_rect)

		# 显示物品
		for index, tool_surf in enumerate(self.tools_surf.values()):
			tool_rect = tool_surf.get_rect(bottomleft= \
				(INVENTORY_INNER_POSITION[0] + INVENTORY_ITEM_SIZE * index, INVENTORY_INNER_POSITION[1]))
			self.display_surface.blit(tool_surf, tool_rect)

		# 显示物品栏选中框
		selected_index = self.tools_list.index(self.player.selected_tool)
		inventory_item_box_rect = self.inventory_item_box_surf.get_rect(bottomleft= \
			(INVENTORY_OUTER_POSITION[0] + INVENTORY_ITEM_SIZE * selected_index, INVENTORY_OUTER_POSITION[1]))
		self.display_surface.blit(self.inventory_item_box_surf, inventory_item_box_rect)