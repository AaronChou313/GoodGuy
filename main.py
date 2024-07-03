import pygame, sys
from settings import *
from level import Level
from cache import Cache
from pages import Page, Pages, Level, WelcomePage, GamePage


class Game:
	def __init__(self):
		pygame.init()
		self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
		pygame.display.set_caption('Good Guy：好家伙')
		self.clock = pygame.time.Clock()
		self.cache = Cache()
		self.pages = Pages(self.cache)
		self.page_list = {
			'welcome': WelcomePage(self.cache, self.pages),
			'game': GamePage(self.cache, self.pages)
		}

		self.page_list['welcome'].activate()

	def run(self):
		while True:
			# 处理游戏事件
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == pygame.MOUSEWHEEL:
					if event.y > 0:
						self.cache.update_mouse_wheel('up')
					else:
						self.cache.update_mouse_wheel('down')
			# 监听切换页面请求
			if self.cache.change_page != 'none':
				self.page_list[self.cache.change_page].activate()
				self.cache.change_page = 'none'
			# 更新cache和鼠标数据
			self.cache.dt = self.clock.tick() / 1000
			self.cache.mouse_abs_pos = pygame.mouse.get_pos()
			self.cache.mouse_pressed = pygame.mouse.get_pressed()
			# 更新页面
			self.pages.update_page()
			self.pages.run()

			pygame.display.update()


if __name__ == '__main__':
	game = Game()
	game.run()
