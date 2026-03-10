import json
from pathlib import Path

import pygame


class Level:
    def __init__(self, screen_width, screen_height, air_platforms, coins, player_start=(100, 100), ground_height=20):
        self.player_start = tuple(player_start)
        self.air_platforms = [pygame.Rect(*platform) for platform in air_platforms]
        self.ground_platform = pygame.Rect(0, screen_height - ground_height, screen_width, ground_height)
        self.coins = [pygame.Rect(*coin) for coin in coins]

    @classmethod
    def from_json_file(cls, level_path, screen_width, screen_height):
        data = json.loads(Path(level_path).read_text(encoding='utf-8'))
        cls.validate(data)
        return cls(
            screen_width=screen_width,
            screen_height=screen_height,
            air_platforms=data['air_platforms'],
            coins=data['coins'],
            player_start=data.get('player_start', [100, 100]),
            ground_height=data.get('ground_height', 20),
        )

    @staticmethod
    def validate(data):
        required = ('air_platforms', 'coins')
        for key in required:
            if key not in data:
                raise ValueError(f"Level JSON missing required key: {key}")

        for key in ('air_platforms', 'coins'):
            if not isinstance(data[key], list):
                raise ValueError(f"{key} must be a list")
            for item in data[key]:
                if not (isinstance(item, list) and len(item) == 4):
                    raise ValueError(f"Each item in {key} must be [x, y, w, h]")

    def draw(self, screen: pygame.Surface):
        for platform in self.air_platforms:
            pygame.draw.rect(screen, (255, 255, 255), platform)

        pygame.draw.rect(screen, (255, 255, 255), self.ground_platform)

        for coin in self.coins:
            pygame.draw.rect(screen, (255, 215, 0), coin)
