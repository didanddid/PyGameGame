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

        self.ui = UI()
        self.running = True
        self.clock = pygame.time.Clock()

        self.time_limit_ms = 60_000
        self.restart_level()

    @staticmethod
    def resource_path(relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller."""
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def restart_level(self):
        self.level = Level(self.screen_width, self.screen_height)
        self.player.reset()
        self.score = 0
        self.remaining_time_ms = self.time_limit_ms
        self.game_state = "playing"

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                if self.game_state in ("victory", "game_over"):
                    self.restart_level()

    def update(self, dt_ms):
        if self.game_state != "playing":
            return

        keys = pygame.key.get_pressed()

        self.player.handle_horizontal_input(keys)
        self.player.process_jump_input(keys, dt_ms)

        self.player.apply_gravity()
        self.player.resolve_vertical_collisions(self.level.air_platforms, self.level.ground_platform)
        self.player.clamp_to_screen(self.screen_width, self.level.ground_platform)
        self.player.refresh_grounding_timers()
        self.player.consume_buffered_jump()

        self.score += self.player.collect_coins(self.level.coins)
        self.remaining_time_ms = max(0, self.remaining_time_ms - dt_ms)

        self.update_game_state()
        self.log_debug_state()

    def update_game_state(self):
        if not self.level.coins:
            self.game_state = "victory"
        elif self.remaining_time_ms <= 0:
            self.game_state = "game_over"

    def log_debug_state(self):
        if not self.dev_mode:
            return

        print(
            f"Velocity Y: {self.player.velocity_y}, "
            f"On Ground: {self.player.on_ground}, "
            f"On Air Platform: {self.player.on_air_platform}, "
            f"State: {self.game_state}, "
            f"Time Left: {self.remaining_time_ms}"
        )

    def render(self):
        self.screen.fill((0, 0, 0))

        self.level.draw(self.screen)
        self.player.draw(self.screen)
        self.ui.draw_score(self.screen, self.score)
        self.ui.draw_timer(self.screen, self.remaining_time_ms)

        if self.game_state == "victory":
            self.ui.draw_end_screen(self.screen, "Victory!", "Press R to restart")
        elif self.game_state == "game_over":
            self.ui.draw_end_screen(self.screen, "Game Over", "Press R to restart")

        pygame.display.flip()

    def run(self):
        while self.running:
            dt_ms = self.clock.tick(100)
            self.handle_events()
            self.update(dt_ms)
            self.render()

        pygame.quit()
