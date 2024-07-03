import pygame
from settings import *
from support import *
from level import Level, GameLevel
from sprites import Generic


def button_activate_page(cache, page_name):
    cache.change_page = page_name


class Pages(pygame.sprite.Group):
    def __init__(self, cache):
        super().__init__()
        self.cache = cache

    def update_page(self):
        target_page = None
        for index, sprite in enumerate(self.sprites()):
            if sprite.activate_request:
                target_page = index
                sprite.activate_request = False
        if target_page is not None:
            for index, sprite in enumerate(self.sprites()):
                if index == target_page:
                    sprite.active = True
                elif sprite.active:
                    sprite.active = False

    def run(self):
        for sprite in self.sprites():
            if sprite.active:
                sprite.run()


class Page(pygame.sprite.Sprite):
    def __init__(self, cache, pages):
        super().__init__(pages)
        self.cache = cache
        self.all_components = pygame.sprite.Group()
        self.all_buttons = pygame.sprite.Group()
        self.active = False
        self.activate_request = False

    def activate(self):
        self.activate_request = True

    def update(self):
        pass

    def run(self):
        self.update()
        self.cache.display_surface.fill('black')
        for component in self.all_components:
            component.show()


class WelcomePage(Page):
    def __init__(self, cache, pages):
        super().__init__(cache, pages)
        Generic(
            cache=self.cache,
            pos=(0, 0),
            surf=pygame.image.load('./graphics/overlay/welcome_background.png').convert_alpha(),
            groups=self.all_components,
            z=LAYERS['ground'])

        self.title_path = './graphics/overlay/main_title.png'
        self.title_surf = pygame.image.load(self.title_path).convert_alpha()
        self.title = Text(self.title_surf, self.cache, (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 9 * 2), self.all_components, color=(255, 255, 255))

        self.button_path = {
            'start': './graphics/overlay/start.png',
            'multiplay': './graphics/overlay/multiplay.png',
            'setting': './graphics/overlay/setting.png',
            'exit': './graphics/overlay/exit.png'
        }
        self.start_button_surf = pygame.image.load(self.button_path['start']).convert_alpha()
        self.multiplay_button_surf = pygame.image.load(self.button_path['multiplay']).convert_alpha()
        self.setting_button_surf = pygame.image.load(self.button_path['setting']).convert_alpha()
        self.exit_button_surf = pygame.image.load(self.button_path['exit']).convert_alpha()

        self.buttons = {
            'game': Button(self.cache, (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 9 * 5), self.all_components,'Start', self.start_button_surf),
            'multi': Button(self.cache, (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 9 * 6), self.all_components,'Multiplay',self.multiplay_button_surf),
            'setting': Button(self.cache, (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 9 * 7), self.all_components,'Setting',self.setting_button_surf),
            'exit': Button(self.cache, (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 9 * 8), self.all_components, 'exit',self.exit_button_surf)
        }

    def update(self):
        for key, value in self.buttons.items():
            if value.touched():
                button_activate_page(self.cache, key)


class ChoosingPage(Page):
    def __init__(self, cache, pages):
        super().__init__(cache, pages)
        Generic(
            cache=self.cache,
            pos=(0, 0),
            surf=pygame.image.load('./graphics/overlay/choosing_background.png').convert_alpha(),
            groups=self.all_components,
            z=LAYERS['ground'])


class GamePage(Page):
    def __init__(self, cache, pages):
        super().__init__(cache, pages)
        self.main_layer = GameLevel(self.cache, self.all_components)
