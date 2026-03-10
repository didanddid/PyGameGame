import pygame


class UI:
    def __init__(self):
        self.font = pygame.font.Font(None, 36)

    def draw_score(self, screen: pygame.Surface, score: int):
        text = self.font.render(f'Score: {score}', True, (255, 255, 255))
        screen.blit(text, (10, 10))
