import pygame


class Cache:
    def __init__(self):
        self.root_path = './graphics/items/'

        self.tools_path = self.root_path + 'tools/'
        self.tools = ['hoe', 'axe', 'water']
        self.tools_surf = self.import_assets(self.tools_path, self.tools)

        self.offset = pygame.math.Vector2()
        self.mouse_pos = pygame.mouse.get_pos() + self.offset
        self.mouse_abs_pos = pygame.mouse.get_pos()
        self.mouse_pressed = pygame.mouse.get_pressed()

        self.mouse_wheel = 'none'

        self.display_surface = pygame.display.get_surface()

        self.dt = 0

        self.game_start = False
        self.game_running = False

        self.change_page = 'none'

    def import_assets(self, items_path, items):
        item_surf = {item: pygame.image.load(f'{items_path}{item}.png').convert_alpha() for item in items}
        return item_surf

    def update_mouse_wheel(self, mouse_wheel):
        self.mouse_wheel = mouse_wheel
