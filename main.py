import pygame
import sys
import os

# Функция для получения пути к ресурсам
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in sys._MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Инициализация Pygame
pygame.init()

# Настройка экрана
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("PGG")

# Загрузка изображения персонажа
player_image = pygame.image.load(resource_path('assets/player.png'))
player_rect = player_image.get_rect()
player_rect.topleft = (100, 100)

# Платформы в воздухе
air_platforms = [
    pygame.Rect(100, 450, 200, 20),
    pygame.Rect(400, 350, 200, 20)
]

# Самая нижняя платформа (земля)
ground_platform = pygame.Rect(0, screen_height - 20, screen_width, 20)

# Монеты
coins = [
    pygame.Rect(150, 400, 20, 20),
    pygame.Rect(450, 300, 20, 20)
]

# Переменные для управления движением персонажа
velocity_y = 0
gravity = 0.5  # Гравитация
jump_strength = -13  # Сила прыжка
score = 0

# Флаги для проверки, стоит ли персонаж на платформе или на земле
on_ground = False
on_air_platform = False

# Основной игровой цикл
running = True
clock = pygame.time.Clock()

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

    # Условие для прыжка
    if keys[pygame.K_SPACE] and (on_ground or on_air_platform):
        velocity_y = jump_strength  # Начальная скорость прыжка
        on_ground = False  # Сбрасываем флаг "на земле" при прыжке
        on_air_platform = False  # Сбрасываем флаг "на воздушной платформе" при прыжке

    # Применяем гравитацию
    velocity_y += gravity
    velocity_y = round(velocity_y, 2)  # Округляем velocity_y до 2 знаков после запятой

    # Обновляем позицию игрока
    player_rect.y += velocity_y

    # Проверка коллизий с платформами и землей
    on_ground = False  # Предполагаем, что персонаж не на земле
    on_air_platform = False  # Предполагаем, что персонаж не на воздушной платформе
    for platform in air_platforms:
        if player_rect.colliderect(platform):
            if velocity_y > 0 and abs(player_rect.bottom - platform.top) <= 20:  # Падает сверху
                player_rect.bottom = platform.top
                velocity_y = 0
                on_air_platform = True
            elif velocity_y < 0 and player_rect.top >= platform.bottom:  # Ударяется снизу
                player_rect.top = platform.bottom
                velocity_y = 0

    # Проверка коллизий с землей
    if player_rect.colliderect(ground_platform):
        if velocity_y > 0 and player_rect.bottom <= ground_platform.top:  # Падает сверху
            player_rect.bottom = ground_platform.top
            velocity_y = 0
            on_ground = True

    # Ограничение движения за пределы экрана
    if player_rect.left < 0:
        player_rect.left = 0
    if player_rect.right > screen_width:
        player_rect.right = screen_width
    if player_rect.top < 0:
        player_rect.top = 0
        velocity_y = 0
    if player_rect.bottom > ground_platform.top:
        player_rect.bottom = ground_platform.top
        velocity_y = 0
        on_ground = True

    # Проверка сбора монет
    for coin in coins[:]:
        if player_rect.colliderect(coin):
            coins.remove(coin)
            score += 1

    # Отладочные сообщения
    print(f"Velocity Y: {velocity_y}, On Ground: {on_ground}, On Air Platform: {on_air_platform}")

    # Отрисовка фона
    screen.fill((0, 0, 0))

    # Отрисовка платформ
    for platform in air_platforms:
        pygame.draw.rect(screen, (255, 255, 255), platform)

    # Отрисовка земли
    pygame.draw.rect(screen, (255, 255, 255), ground_platform)

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
    clock.tick(100)

# Выход из Pygame
pygame.quit()