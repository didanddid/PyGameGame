import pygame


class Player:
    def __init__(self, image: pygame.Surface, start_pos=(100, 100)):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = start_pos

        self.velocity_y = 0
        self.gravity = 0.5
        self.jump_strength = -13

        self.on_ground = False
        self.on_air_platform = False

    def handle_horizontal_input(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= 5
        if keys[pygame.K_RIGHT]:
            self.rect.x += 5

    def try_jump(self, keys):
        if keys[pygame.K_SPACE] and (self.on_ground or self.on_air_platform):
            self.velocity_y = self.jump_strength
            self.on_ground = False
            self.on_air_platform = False

    def apply_gravity(self):
        self.velocity_y += self.gravity
        self.velocity_y = round(self.velocity_y, 2)
        self.rect.y += self.velocity_y

    def resolve_vertical_collisions(self, air_platforms, ground_platform):
        self.on_ground = False
        self.on_air_platform = False

        for platform in air_platforms:
            if self.rect.colliderect(platform):
                if self.velocity_y > 0 and abs(self.rect.bottom - platform.top) <= 20:
                    self.rect.bottom = platform.top
                    self.velocity_y = 0
                    self.on_air_platform = True
                elif self.velocity_y < 0 and self.rect.top >= platform.bottom:
                    self.rect.top = platform.bottom
                    self.velocity_y = 0

        if self.rect.colliderect(ground_platform):
            if self.velocity_y > 0 and self.rect.bottom <= ground_platform.top:
                self.rect.bottom = ground_platform.top
                self.velocity_y = 0
                self.on_ground = True

    def clamp_to_screen(self, screen_width, ground_platform):
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > screen_width:
            self.rect.right = screen_width
        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity_y = 0
        if self.rect.bottom > ground_platform.top:
            self.rect.bottom = ground_platform.top
            self.velocity_y = 0
            self.on_ground = True

    def collect_coins(self, coins):
        collected = 0
        for coin in coins[:]:
            if self.rect.colliderect(coin):
                coins.remove(coin)
                collected += 1
        return collected

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, self.rect)
