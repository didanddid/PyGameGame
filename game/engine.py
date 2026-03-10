import os
import sys

import pygame

from game.level import Level
from game.player import Player
from game.ui import UI


class GameEngine:
    def __init__(self, dev_mode: bool = False):
        pygame.init()

        self.dev_mode = dev_mode
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("PGG")

        player_image = pygame.image.load(self.resource_path('assets/player.png'))
        self.player = Player(player_image)

        self.level = Level(self.screen_width, self.screen_height)
        self.ui = UI()

        self.score = 0
        self.running = True
        self.clock = pygame.time.Clock()

    @staticmethod
    def resource_path(relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller."""
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        keys = pygame.key.get_pressed()

        self.player.handle_horizontal_input(keys)
        self.player.try_jump(keys)

        self.player.apply_gravity()
        self.player.resolve_vertical_collisions(self.level.air_platforms, self.level.ground_platform)
        self.player.clamp_to_screen(self.screen_width, self.level.ground_platform)

        self.score += self.player.collect_coins(self.level.coins)
        self.log_debug_state()

    def log_debug_state(self):
        if not self.dev_mode:
            return

        print(
            f"Velocity Y: {self.player.velocity_y}, "
            f"On Ground: {self.player.on_ground}, "
            f"On Air Platform: {self.player.on_air_platform}"
        )

    def render(self):
        self.screen.fill((0, 0, 0))

        self.level.draw(self.screen)
        self.player.draw(self.screen)
        self.ui.draw_score(self.screen, self.score)

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(100)

        pygame.quit()
