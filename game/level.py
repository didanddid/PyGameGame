import json
from pathlib import Path

import pygame


class Level:
    def __init__(
        self,
        screen_width,
        screen_height,
        air_platforms,
        coins,
        player_start=(100, 100),
        ground_height=20,
        spikes=None,
        moving_platforms=None,
    ):
        self.player_start = tuple(player_start)
        self.static_air_platforms = [pygame.Rect(*platform) for platform in air_platforms]
        self.ground_platform = pygame.Rect(0, screen_height - ground_height, screen_width, ground_height)
        self.coins = [pygame.Rect(*coin) for coin in coins]
        self.spikes = [pygame.Rect(*spike) for spike in (spikes or [])]

        self.moving_platforms = []
        for platform in moving_platforms or []:
            rect = pygame.Rect(*platform['rect'])
            self.moving_platforms.append(
                {
                    'rect': rect,
                    'min_x': platform['min_x'],
                    'max_x': platform['max_x'],
                    'speed': platform['speed'],
                    'direction': 1,
                }
            )

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
            spikes=data.get('spikes', []),
            moving_platforms=data.get('moving_platforms', []),
        )

    @staticmethod
    def validate(data):
        required = ('air_platforms', 'coins')
        for key in required:
            if key not in data:
                raise ValueError(f"Level JSON missing required key: {key}")

        for key in ('air_platforms', 'coins', 'spikes'):
            if key in data:
                if not isinstance(data[key], list):
                    raise ValueError(f"{key} must be a list")
                for item in data[key]:
                    if not (isinstance(item, list) and len(item) == 4):
                        raise ValueError(f"Each item in {key} must be [x, y, w, h]")

        if 'moving_platforms' in data:
            if not isinstance(data['moving_platforms'], list):
                raise ValueError('moving_platforms must be a list')
            for item in data['moving_platforms']:
                if not isinstance(item, dict):
                    raise ValueError('Each moving platform must be an object')
                for field in ('rect', 'min_x', 'max_x', 'speed'):
                    if field not in item:
                        raise ValueError(f"Moving platform missing field: {field}")
                if not (isinstance(item['rect'], list) and len(item['rect']) == 4):
                    raise ValueError("Moving platform 'rect' must be [x, y, w, h]")

    def update(self, dt_ms):
        dt_factor = dt_ms / 16.67
        for platform in self.moving_platforms:
            rect = platform['rect']
            rect.x += platform['speed'] * platform['direction'] * dt_factor

            if rect.x <= platform['min_x']:
                rect.x = platform['min_x']
                platform['direction'] = 1
            elif rect.x >= platform['max_x']:
                rect.x = platform['max_x']
                platform['direction'] = -1

    def get_air_platforms(self):
        moving_rects = [platform['rect'] for platform in self.moving_platforms]
        return self.static_air_platforms + moving_rects

    def hits_spike(self, player_rect):
        return any(player_rect.colliderect(spike) for spike in self.spikes)

    def draw(self, screen: pygame.Surface):
        for platform in self.static_air_platforms:
            pygame.draw.rect(screen, (255, 255, 255), platform)

        for moving in self.moving_platforms:
            pygame.draw.rect(screen, (100, 200, 255), moving['rect'])

        pygame.draw.rect(screen, (255, 255, 255), self.ground_platform)

        for coin in self.coins:
            pygame.draw.rect(screen, (255, 215, 0), coin)

        for spike in self.spikes:
            pygame.draw.rect(screen, (220, 60, 60), spike)
