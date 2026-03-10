import pygame


class Level:
    def __init__(self, screen_width, screen_height):
        self.air_platforms = [
            pygame.Rect(100, 450, 200, 20),
            pygame.Rect(400, 350, 200, 20),
        ]

        self.ground_platform = pygame.Rect(0, screen_height - 20, screen_width, 20)

        self.coins = [
            pygame.Rect(150, 400, 20, 20),
            pygame.Rect(450, 300, 20, 20),
        ]

    def draw(self, screen: pygame.Surface):
        for platform in self.air_platforms:
            pygame.draw.rect(screen, (255, 255, 255), platform)

        pygame.draw.rect(screen, (255, 255, 255), self.ground_platform)

        for coin in self.coins:
            pygame.draw.rect(screen, (255, 215, 0), coin)
