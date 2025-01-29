import pygame

# Инициализация Pygame
pygame.init()

# Настройка экрана
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("PGG")

# Загрузка изображения персонажа
player_image = pygame.image.load('assets/player.png')
player_rect = player_image.get_rect()
player_rect.topleft = (100, 100)

# Платформы
platforms = [
    pygame.Rect(100, 500, 200, 20),
    pygame.Rect(400, 400, 200, 20)
]

# Монеты
coins = [
    pygame.Rect(150, 450, 20, 20),
    pygame.Rect(450, 350, 20, 20)
]

# Переменные для управления движением персонажа
is_jumping = False
jump_count = 10
velocity_y = 0
gravity = 1
score = 0

# Основной игровой цикл
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Получение состояния клавиш
    keys = pygame.key.get_pressed()

    # Управление движением персонажа
    if keys[pygame.K_LEFT]:
        player_rect.x -= 5
    if keys[pygame.K_RIGHT]:
        player_rect.x += 5
    if keys[pygame.K_SPACE] and not is_jumping:
        is_jumping = True
        jump_count = 10

    # Реализация прыжка
    if is_jumping:
        if jump_count >= -10:
            neg = 1
            if jump_count < 0:
                neg = -1
            velocity_y = (jump_count ** 2) * 0.5 * neg
            jump_count -= 1
        else:
            is_jumping = False

    player_rect.y -= velocity_y
    velocity_y -= gravity

    # Проверка коллизий с платформами
    for platform in platforms:
        if player_rect.colliderect(platform):
            if player_rect.bottom > platform.top and player_rect.bottom - velocity_y <= platform.top:
                player_rect.bottom = platform.top
                velocity_y = 0
                is_jumping = False

    # Проверка сбора монет
    for coin in coins[:]:
        if player_rect.colliderect(coin):
            coins.remove(coin)
            score += 1

    # Ограничение движения за пределы экрана
    if player_rect.left < 0:
        player_rect.left = 0
    if player_rect.right > screen_width:
        player_rect.right = screen_width
    if player_rect.top < 0:
        player_rect.top = 0
    if player_rect.bottom > screen_height:
        player_rect.bottom = screen_height
        velocity_y = 0
        is_jumping = False

    # Отрисовка фона
    screen.fill((0, 0, 0))

    # Отрисовка платформ
    for platform in platforms:
        pygame.draw.rect(screen, (255, 255, 255), platform)

    # Отрисовка монет
    for coin in coins:
        pygame.draw.rect(screen, (255, 215, 0), coin)

    # Отрисовка персонажа
    screen.blit(player_image, player_rect)

    # Отображение счета
    font = pygame.font.Font(None, 36)
    text = font.render(f'Score: {score}', True, (255, 255, 255))
    screen.blit(text, (10, 10))

    # Обновление экрана
    pygame.display.flip()

    # Ограничение кадров в секунду
    pygame.time.Clock().tick(165)

# Выход из Pygame
pygame.quit()