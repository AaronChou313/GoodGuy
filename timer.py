import pygame 

class Timer:
	"""
	计时器，接收属性duration和func，duration为计时器持续时间，func为计时器结束后执行的函数
	从激活时开始计时，到达持续时间时自动停止计时并复位
	"""
	def __init__(self,duration,func = None):
		self.duration = duration
		self.func = func
		self.start_time = 0
		self.active = False
	# 激活计时器
	def activate(self):
		self.active = True
		self.start_time = pygame.time.get_ticks()
	# 停止计时器
	def deactivate(self):
		self.active = False
		self.start_time = 0
	# 更新计时器
	def update(self):
		current_time = pygame.time.get_ticks()	# 获取当前时间
		if current_time - self.start_time >= self.duration: # 如果当前时间大于等于持续时间
			# start_time不为0，说明计时器已经激活过，此时若func不为空，则执行func
			if self.func and self.start_time != 0:
				self.func()
			# 然后停止计时器
			self.deactivate()