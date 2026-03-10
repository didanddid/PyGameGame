import os
import sys

import pygame

from game.audio import AudioManager
from game.level import Level
from game.player import Player
from game.ui import UI
from game.telemetry import TelemetryStore


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
        self.audio = AudioManager(self.resource_path)
        self.running = True
        self.clock = pygame.time.Clock()
        self.telemetry = TelemetryStore()

        self.default_time_limit_ms = 60_000
        self.level_paths = [
            self.resource_path('data/levels/level_1.json'),
            self.resource_path('data/levels/level_2.json'),
            self.resource_path('data/levels/level_3.json'),
        ]
        self.current_level_index = 0

        self.load_level(self.current_level_index)
        self.game_state = "menu"

    @staticmethod
    def resource_path(relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller."""
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def load_level(self, level_index):
        if not (0 <= level_index < len(self.level_paths)):
            raise IndexError(f"Level index out of range: {level_index}")

        self.current_level_index = level_index
        level_path = self.level_paths[self.current_level_index]
        self.level = Level.from_json_file(level_path, self.screen_width, self.screen_height)

        self.player.set_start_position(self.level.player_start)
        self.player.reset()

        self.score = 0
        self.level_elapsed_ms = 0
        self.remaining_time_ms = self.default_time_limit_ms
        self.game_state = "playing"

    def restart_level(self):
        self.load_level(self.current_level_index)

    def load_next_level(self):
        if self.current_level_index + 1 < len(self.level_paths):
            self.load_level(self.current_level_index + 1)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_state == "playing":
                        self.game_state = "paused"
                    elif self.game_state == "paused":
                        self.game_state = "playing"
                    elif self.game_state == "menu":
                        self.running = False
                elif event.key == pygame.K_RETURN and self.game_state == "menu":
                    self.restart_level()
                elif event.key == pygame.K_p and self.game_state in ("playing", "paused"):
                    self.game_state = "paused" if self.game_state == "playing" else "playing"
                elif event.key == pygame.K_r and self.game_state in ("victory", "game_over", "paused"):
                    self.restart_level()
                elif event.key == pygame.K_n and self.game_state == "victory":
                    self.load_next_level()
                elif event.key == pygame.K_m:
                    self.audio.toggle_mute()
                elif pygame.K_1 <= event.key <= pygame.K_9:
                    requested_level = event.key - pygame.K_1
                    if requested_level < len(self.level_paths):
                        was_menu = self.game_state == "menu"
                        self.load_level(requested_level)
                        if was_menu:
                            self.game_state = "menu"

    def update(self, dt_ms):
        if self.game_state != "playing":
            return

        previous_state = self.game_state
        keys = pygame.key.get_pressed()

        self.player.handle_horizontal_input(keys)
        self.player.process_jump_input(keys, dt_ms)
        if self.player.jump_triggered:
            self.audio.play('jump')

        self.level.update(dt_ms)

        self.player.apply_gravity()
        self.player.resolve_vertical_collisions(self.level.get_air_platforms(), self.level.ground_platform)
        self.player.clamp_to_screen(self.screen_width, self.level.ground_platform)
        self.player.refresh_grounding_timers()
        self.player.consume_buffered_jump()

        collected = self.player.collect_coins(self.level.coins)
        if collected:
            self.audio.play('coin')
        self.score += collected

        self.remaining_time_ms = max(0, self.remaining_time_ms - dt_ms)
        self.level_elapsed_ms += dt_ms

        self.telemetry.update_best_score(self.score)

        if self.level.hits_spike(self.player.rect):
            self.game_state = "game_over"

        self.update_game_state()

        if previous_state == 'playing' and self.game_state in ('victory', 'game_over'):
            self.audio.play(self.game_state)
            if self.game_state == 'victory':
                self.telemetry.update_best_time(self.level_elapsed_ms)

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
            f"Level: {self.current_level_index + 1}, "
            f"Velocity Y: {self.player.velocity_y}, "
            f"On Ground: {self.player.on_ground}, "
            f"On Air Platform: {self.player.on_air_platform}, "
            f"State: {self.game_state}, "
            f"Time Left: {self.remaining_time_ms}, "
            f"Muted: {self.audio.muted}"
        )

    def render(self):
        self.screen.fill((0, 0, 0))

        self.level.draw(self.screen)
        self.player.draw(self.screen)
        self.ui.draw_score(self.screen, self.score)
        self.ui.draw_timer(self.screen, self.remaining_time_ms)
        self.ui.draw_level(self.screen, self.current_level_index + 1, len(self.level_paths))
        self.ui.draw_audio_state(self.screen, self.audio.muted)
        self.ui.draw_records(self.screen, self.telemetry.best_score, self.telemetry.best_time_ms)

        if self.game_state == "menu":
            self.ui.draw_menu_screen(self.screen)
        elif self.game_state == "paused":
            self.ui.draw_pause_screen(self.screen)
        elif self.game_state == "victory":
            subtitle = "Press R to restart"
            if self.current_level_index + 1 < len(self.level_paths):
                subtitle += " | Press N for next level"
            self.ui.draw_end_screen(self.screen, "Victory!", subtitle)
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
