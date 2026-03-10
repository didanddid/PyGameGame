import pygame


class Player:
    def __init__(self, image: pygame.Surface, start_pos=(100, 100)):
        self.image = image
        self.start_pos = start_pos
        self.rect = self.image.get_rect()
        self.rect.topleft = start_pos

        self.velocity_y = 0
        self.gravity = 0.5
        self.jump_strength = -13

        self.on_ground = False
        self.on_air_platform = False

        self.coyote_time_ms = 100
        self.jump_buffer_ms = 120
        self.coyote_timer_ms = 0
        self.jump_buffer_timer_ms = 0
        self.prev_jump_pressed = False
        self.jump_triggered = False

    def set_start_position(self, start_pos):
        self.start_pos = tuple(start_pos)

    def reset(self):
        self.rect.topleft = self.start_pos
        self.velocity_y = 0
        self.on_ground = False
        self.on_air_platform = False
        self.coyote_timer_ms = 0
        self.jump_buffer_timer_ms = 0
        self.prev_jump_pressed = False
        self.jump_triggered = False

    def handle_horizontal_input(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= 5
        if keys[pygame.K_RIGHT]:
            self.rect.x += 5

    def process_jump_input(self, keys, dt_ms):
        self.jump_triggered = False
        jump_pressed = keys[pygame.K_SPACE]

        if jump_pressed and not self.prev_jump_pressed:
            self.jump_buffer_timer_ms = self.jump_buffer_ms

        if not jump_pressed and self.prev_jump_pressed and self.velocity_y < 0:
            self.velocity_y *= 0.5

        self.prev_jump_pressed = jump_pressed

        self.jump_buffer_timer_ms = max(0, self.jump_buffer_timer_ms - dt_ms)
        self.coyote_timer_ms = max(0, self.coyote_timer_ms - dt_ms)

        self.consume_buffered_jump()

    def consume_buffered_jump(self):
        if self.jump_buffer_timer_ms > 0 and self.can_jump():
            self.velocity_y = self.jump_strength
            self.on_ground = False
            self.on_air_platform = False
            self.coyote_timer_ms = 0
            self.jump_buffer_timer_ms = 0
            self.jump_triggered = True
            return True
        return False

    def can_jump(self):
        return self.on_ground or self.on_air_platform or self.coyote_timer_ms > 0

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

    def refresh_grounding_timers(self):
        if self.on_ground or self.on_air_platform:
            self.coyote_timer_ms = self.coyote_time_ms

    def collect_coins(self, coins):
        collected = 0
        for coin in coins[:]:
            if self.rect.colliderect(coin):
                coins.remove(coin)
                collected += 1
        return collected

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, self.rect)
