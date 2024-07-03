from os import walk
import pygame
import math
from settings import *
from timer import Timer


class Circle(pygame.sprite.Sprite):
	def __init__(self, center, radius):
		pygame.sprite.Sprite.__init__(self)
		self.center = center
		self.radius = radius


class Text(pygame.sprite.Sprite):
	def __init__(self, content, cache, pos, group, color=(255, 255, 255), font='Arial', size=16):
		super().__init__(group)
		self.content = content
		self.cache = cache
		self.pos = pos
		self.color = color
		self.size = size
		self.font = font
		self.fontstyle = pygame.font.SysFont(font, self.size)
		if isinstance(self.content, str):
			self.image = self.fontstyle.render(self.content, True, self.color)
		else:
			self.image = self.content
		self.rect = self.image.get_rect(center=self.pos)

	def show(self):
		self.cache.display_surface.blit(self.image, self.rect)


class Button(pygame.sprite.Sprite):
	def __init__(self, cache, pos, group, title='button', surf=None, width=BUTTON_WIDTH, height=BUTTON_HEIGHT, func=None):
		super().__init__(group)
		self.font = pygame.font.SysFont('Arial', 30)
		self.cache = cache
		self.width = width
		self.height = height
		self.title = title
		if surf is None:
			self.image = self.font.render(self.title, True, (255,255,255))
			self.rect = pygame.rect.Rect(pos[0] - self.width / 2, pos[1] - self.height / 2, self.width, self.height)
		else:
			self.image = surf
			self.rect = self.image.get_rect(center=pos)
		self.func = func
		self.timers = {
			'touched': Timer(400),
		}

	def touched(self):
		if not self.timers['touched'].active:
			if self.cache.mouse_pressed[0] and self.rect.collidepoint(self.cache.mouse_abs_pos):
				return True
			else:
				return False
		else:
			return True

	def show(self):
		self.cache.display_surface.blit(self.image, self.rect)


def import_folder(path):
	surface_list = []

	for _, __, img_files in walk(path):
		for image in img_files:
			full_path = path + '/' + image
			image_surf = pygame.image.load(full_path).convert_alpha()
			surface_list.append(image_surf)

	return surface_list

def import_folder_dict(path):
	surface_dict = {}

	for _, __, img_files in walk(path):
		for image in img_files:
			full_path = path + '/' + image
			image_surf = pygame.image.load(full_path).convert_alpha()
			surface_dict[image.split('.')[0]] = image_surf

	return surface_dict

def relative_angle(posA, posB):
	angle = math.degrees(math.atan2(posB[1] - posA[1], posB[0] - posA[0]))
	angle += 180
	return angle

def rotate_from_point(ori_image, outer_pos, inner_pos, angle):
	# angle是贴图底边与x正方形夹角，应为-180~180
	ori_width = ori_image.get_width()
	ori_height = ori_image.get_height()

	inner_length = math.sqrt(inner_pos[0]*inner_pos[0]+inner_pos[1]*inner_pos[1])
	af_angle = math.atan2(inner_pos[1], inner_pos[0])
	inner_offset_angle = af_angle - math.radians(angle)
	inner_offset_x = inner_length * math.cos(inner_offset_angle)
	inner_offset_y = inner_length * math.sin(inner_offset_angle)

	outer_offset_angle = math.radians(abs(angle) % 90)
	if 0 <= angle < 90:
		outer_offset_angle = math.radians(abs(angle))
		outer_offset_x = 0
		outer_offset_y = ori_width*math.sin(outer_offset_angle)
		res_width = ori_width * math.cos(outer_offset_angle) + ori_height * math.sin(outer_offset_angle)
		res_height = ori_width * math.sin(outer_offset_angle) + ori_height * math.cos(outer_offset_angle)
	elif 90 <= angle <= 180:
		outer_offset_angle = math.radians(abs(angle) - 90)
		outer_offset_x = ori_width*math.sin(outer_offset_angle)
		outer_offset_y = ori_width*math.cos(outer_offset_angle) + ori_height*math.sin(outer_offset_angle)
		res_width = ori_width * math.sin(outer_offset_angle) + ori_height * math.cos(outer_offset_angle)
		res_height = ori_width * math.cos(outer_offset_angle) + ori_height * math.sin(outer_offset_angle)
	elif -180 <= angle <= -90:
		outer_offset_angle = math.radians(180 - abs(angle))
		outer_offset_x = ori_width*math.cos(outer_offset_angle) + ori_height*math.sin(outer_offset_angle)
		outer_offset_y = ori_height*math.cos(outer_offset_angle)
		res_width = ori_width * math.cos(outer_offset_angle) + ori_height * math.sin(outer_offset_angle)
		res_height = ori_width * math.sin(outer_offset_angle) + ori_height * math.cos(outer_offset_angle)
	else:
		outer_offset_angle = math.radians(90 - abs(angle))
		outer_offset_x = ori_height*math.cos(outer_offset_angle)
		outer_offset_y = 0
		res_width = ori_width * math.sin(outer_offset_angle) + ori_height * math.cos(outer_offset_angle)
		res_height = ori_width * math.cos(outer_offset_angle) + ori_height * math.sin(outer_offset_angle)

	res_pos = pygame.math.Vector2(outer_pos[0] - inner_offset_x - outer_offset_x, outer_pos[1] - inner_offset_y - outer_offset_y)

	return pygame.transform.rotate(ori_image, angle), pygame.Rect(res_pos[0], res_pos[1], res_width, res_height)



