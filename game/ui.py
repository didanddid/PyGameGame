import pygame


class UI:
    def __init__(self):
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 64)

    def draw_score(self, screen: pygame.Surface, score: int):
        text = self.font.render(f'Score: {score}', True, (255, 255, 255))
        screen.blit(text, (10, 10))

    def draw_timer(self, screen: pygame.Surface, remaining_ms: int):
        seconds = max(0, remaining_ms // 1000)
        text = self.font.render(f'Time: {seconds}', True, (255, 255, 255))
        screen.blit(text, (10, 45))

    def draw_level(self, screen: pygame.Surface, current_level: int, total_levels: int):
        text = self.font.render(f'Level: {current_level}/{total_levels}', True, (255, 255, 255))
        screen.blit(text, (10, 80))

    def draw_audio_state(self, screen: pygame.Surface, muted: bool):
        label = "Audio: Mute" if muted else "Audio: On"
        text = self.font.render(label, True, (255, 255, 255))
        screen.blit(text, (10, 115))

    def draw_menu_screen(self, screen: pygame.Surface):
        self._draw_overlay(screen, "PGG", "Enter - Start | 1..9 - Select Level | M - Mute | Esc - Quit")

    def draw_pause_screen(self, screen: pygame.Surface):
        self._draw_overlay(screen, "Paused", "P/Esc - Resume | R - Restart Level | M - Mute")

    def draw_end_screen(self, screen: pygame.Surface, title: str, subtitle: str):
        self._draw_overlay(screen, title, subtitle)

    def _draw_overlay(self, screen: pygame.Surface, title: str, subtitle: str):
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        screen.blit(overlay, (0, 0))

        title_surface = self.title_font.render(title, True, (255, 255, 255))
        subtitle_surface = self.font.render(subtitle, True, (220, 220, 220))

        title_rect = title_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 20))
        subtitle_rect = subtitle_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 30))

        screen.blit(title_surface, title_rect)
        screen.blit(subtitle_surface, subtitle_rect)
