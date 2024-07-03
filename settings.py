from pygame.math import Vector2
# 窗口
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
# 画面
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
CENTER_POSITION = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2)
TILE_SIZE = 64

BUTTON_WIDTH = 100
BUTTON_HEIGHT = 50

# sky的参数
DARKEN = 1
BRIGHTEN = 0

# 物品栏参数
INVENTORY_MAXNUM = 8
INVENTORY_ITEM_SIZE = 72
INVENTORY_BORDER_WIDTH = 4
INVENTORY_WIDTH = INVENTORY_MAXNUM * INVENTORY_ITEM_SIZE + 2*INVENTORY_BORDER_WIDTH
INVENTORY_HEIGHT = INVENTORY_ITEM_SIZE + 2*INVENTORY_BORDER_WIDTH
INVENTORY_OUTER_POSITION = ((SCREEN_WIDTH - INVENTORY_WIDTH)/2, SCREEN_HEIGHT - 10)
INVENTORY_INNER_POSITION = (INVENTORY_OUTER_POSITION[0] + INVENTORY_BORDER_WIDTH,
							INVENTORY_OUTER_POSITION[1] - INVENTORY_BORDER_WIDTH)
INVENTORY_BORDER_WIDTH = 2

TOOL_ITEM_SIZE = INVENTORY_ITEM_SIZE

# 生物属性
BASIC_MASS = 10

PLAYER_TOOL_OFFSET = {
	'left': Vector2(-50,40),
	'right': Vector2(50,40),
	'up': Vector2(0,-10),
	'down': Vector2(0,50)
}

LEVELS = {
	'main': 0,
	'text': 1,
	'button': 2
}

LAYERS = {
	'water': 0,
	'ground': 1,
	'soil': 2,
	'soil water': 3,
	'rain floor': 4,
	'house bottom': 5,
	'ground plant': 6,
	'main': 7,
	'tool': 8,
	'house top': 9,
	'fruit': 10,
	'rain drops': 11,
	'text': 12
}

APPLE_POS = {
	'Small': [(18,17), (30,37), (12,50), (30,45), (20,30), (30,10)],
	'Large': [(30,24), (60,65), (50,50), (16,40),(45,50), (42,70)]
}

GROW_SPEED = {
	'corn': 1,
	'tomato': 0.7
}

SALE_PRICES = {
	'wood': 4,
	'apple': 2,
	'corn': 10,
	'tomato': 20
}
PURCHASE_PRICES = {
	'corn': 4,
	'tomato': 5
}