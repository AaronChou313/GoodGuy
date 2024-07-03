import pygame
from settings import *
from support import *
import math
from timer import Timer


class Creature(pygame.sprite.Sprite):
    def __init__(self, cache, pos, group, collision_sprites, active_collision_sprites, species, category = '', z=LAYERS['main'], actions=None):
        super().__init__(group)

        self.HP = 100
        self.MP = 20
        self.ATK = 10
        self.MATK = 0
        self.DEF = 0
        self.MDEF = 0
        self.MOV = 0
        self.WSP = 1

        self.cache = cache
        # 种类名称
        self.species = species
        # 种类所属分支（即贴图子路径）
        self.category = category
        # 状态
        self.status = 'down_idle'
        # 动画帧索引
        self.frame_index = 0
        # 贴图路径
        self.graphics_path = './graphics/creatures/' + self.category + '/' + self.species + '/'
        # 动作列表，默认只有行走和闲置
        if actions is None:
            actions = []
        self.actions = ['walk', 'idle'] + actions
        self.animations = {}
        # 动画列表（方向+动作）
        for action in self.actions:
            for direction in ['up', 'down', 'left', 'right']:
                self.animations[direction + '_' + action] = []
        # 导入贴图
        self.import_assets()
        # 设置初始贴图
        self.image = self.animations[self.status][self.frame_index]
        # 获取显示矩形
        self.rect = self.image.get_rect(center=pos)
        # 显示层
        self.z = z
        # 方向、位置、偏移量
        self.mass = BASIC_MASS
        self.direction = 0
        self.moving_direction = 0
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 100
        self.velocity = 0
        # 碰撞箱
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2, -self.rect.height * 0.2)
        self.hitcircle = Circle(pygame.math.Vector2(self.hitbox.center), self.hitbox.width / 2)
        # 碰撞对象集
        self.collision_sprites = collision_sprites
        self.active_collision_sprites = active_collision_sprites
        # 计时器
        self.timers = {}
        self.test_tick = 0

    def move(self, dt):
        self.active_collision()
        if self.velocity < 0:
            self.velocity = -self.velocity
            self.direction -= 180
        self.velocity -= 50
        if self.velocity < 0:
            self.velocity = 0
        while not (0 <= self.direction < 360):
            if self.direction < 0:
                self.direction += 360
            if self.direction >= 360:
                self.direction -= 360

        # 垂直移动
        self.pos.x += math.cos(math.radians(self.direction)) * self.velocity * dt
        self.hitbox.centerx = round(self.pos.x)
        self.hitcircle.center.x = self.hitbox.centerx
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')

        # 水平移动
        self.pos.y += math.sin(math.radians(self.direction)) * self.velocity * dt
        self.hitbox.centery = round(self.pos.y)
        self.hitcircle.center.y = self.hitbox.centery
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')


    def active_collision(self):
        for sprite in self.active_collision_sprites.sprites():
            if hasattr(sprite, 'hitcircle') and hasattr(sprite, 'mass') and sprite != self:
                if self.hitcircle.center.distance_to(sprite.hitcircle.center) < sprite.hitcircle.radius + self.hitcircle.radius:
                    me_colli_direction = relative_angle(self.hitcircle.center, sprite.hitcircle.center)
                    me_diff_angle = self.direction - me_colli_direction
                    if me_diff_angle < 0:
                        me_diff_angle += 360
                    me_colli_velocity = self.velocity * math.cos(math.radians(me_diff_angle))
                    me_vertical_velocity = self.velocity * math.sin(math.radians(me_diff_angle))

                    you_colli_direction = relative_angle(sprite.hitcircle.center, self.hitcircle.center)
                    you_diff_angle = self.direction - you_colli_direction
                    if you_diff_angle < 0:
                        you_diff_angle += 360
                    you_colli_velocity = sprite.velocity * math.cos(math.radians(you_diff_angle))

                    me_after_velocity = ((self.mass - sprite.mass) * me_colli_velocity +
                                         sprite.mass * 2 * you_colli_velocity) / (sprite.mass + self.mass)
                    self.velocity = math.sqrt(me_after_velocity * me_after_velocity + me_vertical_velocity * me_vertical_velocity)
                    velo_angle = math.degrees(math.atan2(me_vertical_velocity, me_after_velocity))
                    self.direction = me_colli_direction + velo_angle
                    if me_after_velocity < 0:
                        self.direction += 180


    def collision(self, direction):
        for sprite in self.collision_sprites.sprites():
            if hasattr(sprite, 'hitbox'):
                if sprite.hitbox.colliderect(self.hitbox):
                    velocity_x = self.velocity * math.cos(math.radians(self.direction))
                    velocity_y = self.velocity * math.sin(math.radians(self.direction))
                    diff_angle = self.direction % 90
                    if direction == 'vertical':
                        if velocity_y > 0:  # 向下方移动
                            self.hitbox.bottom = sprite.hitbox.top
                            if velocity_x >= 0:
                                self.direction -= diff_angle*2
                            else:
                                self.direction += 180-diff_angle*2
                        if velocity_y < 0:  # 向上方移动
                            self.hitbox.top = sprite.hitbox.bottom
                            if velocity_x >= 0:
                                self.direction += 180-diff_angle*2
                            else:
                                self.direction -= diff_angle*2
                        self.rect.centery = self.hitbox.centery
                        self.hitcircle.center.y = self.hitbox.centery
                        self.pos.y = self.hitbox.centery
                    if direction == 'horizontal':
                        if velocity_x > 0:  # 向右侧移动
                            self.hitbox.right = sprite.hitbox.left
                            if velocity_y >= 0:
                                self.direction += 180-diff_angle*2
                            else:
                                self.direction -= diff_angle*2
                        if velocity_x < 0:  # 向左侧移动
                            self.hitbox.left = sprite.hitbox.right
                            if velocity_y >= 0:
                                self.direction -= diff_angle*2
                            else:
                                self.direction += 180-diff_angle*2
                        self.rect.centerx = self.hitbox.centerx
                        self.hitcircle.center.x = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx

    def import_assets(self):
        for animation in self.animations.keys():
            full_path = self.graphics_path + animation
            self.animations[animation] = import_folder(full_path)

    def animate(self, dt):
        self.frame_index += 4 * dt
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0

        self.image = self.animations[self.status][int(self.frame_index)]

    def get_status(self):
        # idle
        if self.velocity == 0:
            self.status = self.status.split('_')[0] + '_idle'

        for action in self.actions:
            if action != 'walk' and action != 'idle':
                if self.timers[action].active:
                    self.status = self.status.split('_')[0] + '_' + action

    def update_boxs(self):
        self.rect = self.image.get_rect(center=self.pos)
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2, -self.rect.height * 0.2)
        self.hitcircle.center.x = self.hitbox.centerx
        self.hitcircle.center.y = self.hitbox.centery
        self.hitcircle.radius = self.hitbox.width / 2 if self.hitbox.width < self.hitbox.height else self.hitbox.height / 2

    def update(self):
        dura = 200
        if self.test_tick >= dura*8:
            self.test_tick = 0

        if 0 <= self.test_tick < dura:
            self.direction = 0
            self.velocity = 0
        elif dura <= self.test_tick < dura*2:
            self.direction = 0
            self.status = 'right_walk'
            self.velocity = self.speed
        elif dura*2 <= self.test_tick < dura*3:
            self.direction = 90
            self.velocity = 0
        elif dura*3 <= self.test_tick < dura*4:
            self.direction = 90
            self.status = 'down_walk'
            self.velocity = self.speed
        elif dura*4 <= self.test_tick < dura*5:
            self.direction = 180
            self.velocity = 0
        elif dura*5 <= self.test_tick < dura*6:
            self.direction = 180
            self.status = 'left_walk'
            self.velocity = self.speed
        elif dura*6 <= self.test_tick < dura*7:
            self.direction = 270
            self.velocity = 0
        elif dura*7 <= self.test_tick < dura*8:
            self.direction = 270
            self.status = 'up_walk'
            self.velocity = self.speed
        self.test_tick += 1

        self.update_boxs()
        self.get_status()

        self.move(self.cache.dt)
        self.animate(self.cache.dt)
