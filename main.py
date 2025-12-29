import pygame
import random
import sys
import math
import asyncio  # Только это добавлено для PygBag
from enum import Enum

# Инициализация PyGame
pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 1400, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Новогодняя Backend Odyssey 2025: Год прорывов")
clock = pygame.time.Clock()
emoji_surfaces = {}

# Фоновая новогодняя музыка
try:
    pygame.mixer.music.load("assets/new_year.ogg")
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1)
    music_playing = True
except:
    print("Не удалось загрузить фоновую музыку (new_year.ogg)")
    music_playing = False

# Загрузка изображений
try:
    background_image = pygame.image.load("assets/fon.jpg")
    bg_width, bg_height = background_image.get_size()
    scale_x = WIDTH / bg_width
    scale_y = HEIGHT / bg_height
    scale = min(scale_x, scale_y)
    new_width = int(bg_width * scale)
    new_height = int(bg_height * scale)
    background_image = pygame.transform.scale(background_image, (new_width, new_height))
except:
    background_image = None
    print("Не удалось загрузить fon.jpg")

enemy_images = []
# Список имен ваших файлов (проверьте, чтобы названия в папке assets были такими же!)
enemy_filenames = ["assets/grinch2.png", "assets/nastya.jpg", "assets/german.jpg", "assets/kolya.jpg"]


for filename in enemy_filenames:
    try:
        img = pygame.image.load(filename).convert_alpha()
        img = pygame.transform.scale(img, (80, 80))  # под размер obstacle
        enemy_images.append(img)
    except Exception as e:
        print(f"Не удалось загрузить {filename}: {e}")

# Если ни одна картинка не загрузилась, создаем красный квадрат, чтобы игра не вылетела
if not enemy_images:
    fallback = pygame.Surface((80, 80))
    fallback.fill((255, 0, 0))
    enemy_images.append(fallback)


try:
    alina_image = pygame.image.load("assets/alina.png")
    alina_image = pygame.transform.scale(alina_image, (45, 45))
except:
    alina_image = None
    print("Не удалось загрузить alina.png")

try:
    snowflake_image = pygame.image.load("assets/snow.png").convert_alpha()
    snowflake_image = pygame.transform.scale(snowflake_image, (20, 20))
except:
    snowflake_image = None
    print("Не удалось загрузить snow.png")

try:
    artem_image = pygame.image.load("assets/artem.png").convert_alpha()
    artem_image = pygame.transform.scale(artem_image, (45, 45))
except:
    artem_image = None
    print("Не удалось загрузить artem.png")

# Загрузка шрифтов
try:
    title_font = pygame.font.Font("fonts/arial.ttf", 42)
    font_large = pygame.font.Font("fonts/arial.ttf", 36)
    font_medium = pygame.font.Font("fonts/arial.ttf", 28)
    font_small = pygame.font.Font("fonts/arial.ttf", 24)
    font_xsmall = pygame.font.Font("fonts/arial.ttf", 20)
except:
    title_font = pygame.font.Font(None, 42)
    font_large = pygame.font.Font(None, 36)
    font_medium = pygame.font.Font(None, 28)
    font_small = pygame.font.Font(None, 24)
    font_xsmall = pygame.font.Font(None, 20)

# Новогодняя цветовая палитра
COLORS = {
    "background": (10, 20, 30),
    "dark_bg": (20, 30, 45),
    "primary": (220, 20, 60),
    "secondary": (34, 139, 34),
    "success": (255, 215, 0),
    "warning": (255, 140, 0),
    "danger": (178, 34, 34),
    "text": (255, 250, 250),
    "text_secondary": (192, 192, 192),
    "dev1": (220, 20, 60),
    "dev2": (135, 206, 235),
    "ui_bg": (25, 35, 50, 220),
    "obstacle": (178, 34, 34),
    "refactor": (255, 215, 0),
    "automation": (135, 206, 250),
    "feature": (50, 205, 50),
    "snow": (255, 255, 255),
    "star": (255, 215, 0),
    "silver": (192, 192, 192),
}


# Состояния игры
class JumpNotification:
    def __init__(self, x, y, points):
        self.x = x
        self.y = y
        self.points = points
        self.life = 60
        self.start_y = y

    def update(self):
        self.life -= 1
        self.y -= 1

    def draw(self, surface):
        if self.life > 0:
            text_surf = font_medium.render(f"+{self.points}", True, COLORS["success"])
            surface.blit(text_surf, (self.x, self.y))

    def is_dead(self):
        return self.life <= 0


class GameState(Enum):
    MENU = 1
    PLAYING = 2
    ACHIEVEMENT_SHOW = 3
    ACHIEVEMENT_WAIT = 4
    PAUSED = 5
    FINISHED = 6


class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(3, 8)
        self.speed_x = random.uniform(-2, 2)
        self.speed_y = random.uniform(-3, 0)
        self.life = 30
        self.gravity = 0.1
        self.sparkle = random.randint(0, 10)

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.speed_y += self.gravity
        self.life -= 1
        self.size *= 0.95
        self.sparkle = (self.sparkle + 1) % 20

    def draw(self, surface):
        if self.life > 0:
            alpha = int(255 * (self.life / 30))
            if self.sparkle < 15:
                alpha = int(alpha * 0.7)
            s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (self.size, self.size), self.size)
            surface.blit(s, (self.x - self.size, self.y - self.size))

    def is_dead(self):
        return self.life <= 0

class Obstacle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 80
        self.height = 80

        # 🎲 случайный персонаж
        self.image = random.choice(enemy_images) if enemy_images else None

        self.speed = 8

    def update(self):
        self.x -= self.speed

    def draw(self, surface):
        if self.image:
            surface.blit(self.image, (self.x, self.y))
        else:
            pygame.draw.rect(
                surface,
                COLORS["obstacle"],
                (self.x, self.y, self.width, self.height),
                0,
                10
            )

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Developer:
    def __init__(self, x, y, color, name, icon_text):
        self.x = x
        self.y = y
        self.start_y = y
        self.color = color
        self.name = name
        self.icon_text = icon_text
        self.width = 45
        self.height = 70
        self.velocity_y = 0
        self.jumping = False
        self.double_jump = False
        self.collected = []
        self.animation_frame = 0
        self.run_frames = [0, 1, 2, 1]
        self.frame_timer = 0
        self.particles = []
        self.jump_power = 1.0

    def jump(self, power=1.0):
        self.jump_power = power
        if not self.jumping:
            self.velocity_y = -22 * power
            self.jumping = True
            self.create_jump_particles()
        elif self.double_jump:
            self.velocity_y = -18 * power
            self.double_jump = False
            self.create_jump_particles()

    def create_jump_particles(self):
        for _ in range(10):
            self.particles.append(Particle(
                self.x + self.width // 2,
                self.y + self.height,
                self.color
            ))

    def update(self):
        self.velocity_y += 0.8
        self.y += self.velocity_y

        if self.y > self.start_y:
            self.y = self.start_y
            if self.jumping:
                self.create_land_particles()
            self.jumping = False
            self.double_jump = True
            self.velocity_y = 0

        if not self.jumping and self.y == self.start_y:
            self.frame_timer += 1
            if self.frame_timer >= 5:
                self.frame_timer = 0
                self.animation_frame = (self.animation_frame + 1) % len(self.run_frames)

        for particle in self.particles[:]:
            particle.update()
            if particle.is_dead():
                self.particles.remove(particle)

    def create_land_particles(self):
        for _ in range(15):
            self.particles.append(Particle(
                self.x + self.width // 2,
                self.y + self.height,
                (255, 255, 255)
            ))

    def draw(self, surface):
        shadow = pygame.Surface((self.width + 10, 20), pygame.SRCALPHA)
        shadow_alpha = 100 - abs(self.y - self.start_y) * 2
        pygame.draw.ellipse(shadow, (0, 0, 0, max(0, shadow_alpha)),
                            (0, 0, self.width + 10, 20))
        surface.blit(shadow, (self.x - 5, self.start_y + self.height - 5))

        body_rect = pygame.Rect(self.x, self.y, self.width, self.height)

        bounce_offset = 0
        if self.jumping and self.velocity_y > 0:
            bounce_offset = math.sin(pygame.time.get_ticks() * 0.01) * 3

        pygame.draw.rect(surface, self.color, body_rect, 0, 10)

        if self.name == "Артем":
            pygame.draw.rect(surface, COLORS["snow"],
                             (self.x, self.y + self.height - 15, self.width, 15), 0, 5)
            pygame.draw.rect(surface, (139, 69, 19),
                             (self.x, self.y + self.height // 2, self.width, 8))
        else:
            pygame.draw.rect(surface, COLORS["snow"],
                             (self.x, self.y + self.height - 15, self.width, 15), 0, 5)
            pygame.draw.rect(surface, (192, 192, 192),
                             (self.x, self.y + self.height // 2, self.width, 5))
            pygame.draw.rect(surface, COLORS["snow"],
                             (self.x, self.y + 10, self.width, 10), 0, 5)

        head_y = self.y - 20 + bounce_offset
        pygame.draw.circle(surface, (255, 220, 177),
                           (self.x + self.width // 2, head_y), 18)

        shoulder_y = self.y + 15
        left_shoulder_x = self.x + 5
        right_shoulder_x = self.x + self.width - 5
        arm_length = 25
        swing = math.sin(pygame.time.get_ticks() * 0.01) * 10

        pygame.draw.line(surface, self.color,
                         (left_shoulder_x, shoulder_y),
                         (left_shoulder_x - arm_length, shoulder_y + swing), 5)
        pygame.draw.line(surface, self.color,
                         (right_shoulder_x, shoulder_y),
                         (right_shoulder_x + arm_length, shoulder_y - swing), 5)

        if self.name == "Артем":
            hat_offset = math.sin(pygame.time.get_ticks() * 0.005) * 3
            hat_points = [
                (self.x + self.width // 2 - 20, head_y - 10 + hat_offset),
                (self.x + self.width // 2 + 20, head_y - 10 + hat_offset),
                (self.x + self.width // 2, head_y - 50 + hat_offset)
            ]
            pygame.draw.polygon(surface, COLORS["primary"], hat_points)
            pygame.draw.circle(surface, COLORS["snow"],
                               (self.x + self.width // 2, head_y - 50), 6)
        else:
            hat_offset = math.sin(pygame.time.get_ticks() * 0.005) * 3
            hat_points = [
                (self.x + self.width // 2 - 18, head_y - 8 + hat_offset),
                (self.x + self.width // 2 + 18, head_y - 8 + hat_offset),
                (self.x + self.width // 2, head_y - 50 + hat_offset)
            ]
            pygame.draw.polygon(surface, (135, 206, 235), hat_points)
            pygame.draw.arc(surface, COLORS["snow"],
                            (self.x + self.width // 2 - 20, head_y - 15 + hat_offset, 40, 20),
                            0, 3.14, 3)
            pygame.draw.circle(surface, COLORS["snow"],
                               (self.x + self.width // 2, head_y - 50), 4)
            for i in range(3):
                angle = i * 120
                snow_x = self.x + self.width // 2 + math.cos(math.radians(angle)) * 10
                snow_y = head_y - 30 + math.sin(math.radians(angle)) * 10 + hat_offset
                pygame.draw.circle(surface, (192, 192, 192), (int(snow_x), int(snow_y)), 2)

        if self.name == "Алина" and alina_image:
            self.face(alina_image, head_y, surface)
        elif artem_image:
            self.face(artem_image, head_y, surface)

        leg_offset = self.run_frames[self.animation_frame] * 3
        if self.jumping:
            leg_offset = 0

        if self.name == "Алина":
            pygame.draw.rect(surface, (135, 206, 235),
                             (self.x + 5, self.y + self.height - 10, 10, 15 + leg_offset))
            pygame.draw.rect(surface, COLORS["snow"],
                             (self.x + 5, self.y + self.height - 10, 10, 3))
            pygame.draw.rect(surface, (135, 206, 235),
                             (self.x + self.width - 15, self.y + self.height - 10, 10, 15 - leg_offset))
            pygame.draw.rect(surface, COLORS["snow"],
                             (self.x + self.width - 15, self.y + self.height - 10, 10, 3))
        else:
            pygame.draw.rect(surface, self.color,
                             (self.x + 5, self.y + self.height - 10, 10, 15 + leg_offset))
            pygame.draw.rect(surface, self.color,
                             (self.x + self.width - 15, self.y + self.height - 10, 10, 15 - leg_offset))

        name_surf = font_small.render(self.name, True, COLORS["text"])
        surface.blit(name_surf, (self.x - 10, self.y - 50))

        for particle in self.particles:
            particle.draw(surface)

    def face(self, image, head_y, surface):
        face_size = 45
        scaled_face = pygame.transform.smoothscale(image, (face_size, face_size))
        face_x = self.x + self.width // 2 - face_size // 2
        face_y = head_y - face_size // 2

        face_surface = pygame.Surface((face_size, face_size), pygame.SRCALPHA)
        face_surface.blit(scaled_face, (0, 0))

        for x in range(face_size):
            for y in range(face_size):
                distance = ((x - face_size // 2) ** 2 + (y - face_size // 2) ** 2) ** 0.5
                if distance > face_size // 2:
                    face_surface.set_at((x, y), (0, 0, 0, 0))

        surface.blit(face_surface, (face_x, face_y))


class AchievementObstacle:
    def __init__(self, achievement_data, x_offset=0):
        self.y = HEIGHT // 2 - 40
        self.x = WIDTH + 150 + x_offset
        self.width = 80
        self.height = 80
        self.speed = 4
        self.data = achievement_data
        self.collected = False
        self.passed = False
        self.particles = []
        self.rotation = 0
        self.bounce_offset = 0
        self.bounce_speed = random.uniform(0.05, 0.1)
        self.image = random.choice(enemy_images) if enemy_images else None

        self.types = {
            "team": COLORS["success"],
            "deadline": COLORS["warning"],
            "product": COLORS["primary"],
            "refactor": COLORS["refactor"],
            "api": COLORS["obstacle"],
            "config": COLORS["automation"],
            "template": COLORS["feature"],
            "automation": COLORS["secondary"],
            "reuse": COLORS["dev2"]
        }

        self.color = self.types.get(achievement_data.get("type", "product"), COLORS["primary"])

    def update(self):
        self.x -= self.speed
        self.rotation += 2
        self.bounce_offset = math.sin(pygame.time.get_ticks() * self.bounce_speed) * 5

        for particle in self.particles[:]:
            particle.update()
            if particle.is_dead():
                self.particles.remove(particle)

        return self.x < -100

    def create_collect_particles(self):
        for _ in range(25):
            self.particles.append(Particle(
                self.x + self.width // 2,
                self.y + self.height // 2,
                self.color
            ))

    def draw(self, surface):
        current_y = self.y + self.bounce_offset

        if self.image:
            rotated_img = pygame.transform.rotate(self.image, self.rotation)
            rotated_rect = rotated_img.get_rect(
                center=(self.x + self.width // 2,
                        current_y + self.height // 2)
            )
            surface.blit(rotated_img, rotated_rect)
        else:
            if not self.collected:
                glow_size = 20
                for i in range(3, 0, -1):
                    glow_surf = pygame.Surface((self.width + i * glow_size,
                                                self.height + i * glow_size),
                                               pygame.SRCALPHA)
                    alpha = 30 // i
                    pygame.draw.rect(glow_surf, (*self.color, alpha),
                                     (0, 0, self.width + i * glow_size,
                                      self.height + i * glow_size),
                                     0, 15)
                    surface.blit(glow_surf,
                                 (self.x - i * glow_size // 2,
                                  current_y - i * glow_size // 2))

            block_color = self.color if not self.collected else (*self.color, 100)
            block_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(block_surf, block_color, (0, 0, self.width, self.height), 0, 15)
            rotated_surf = pygame.transform.rotate(block_surf, self.rotation)
            rotated_rect = rotated_surf.get_rect(center=(self.x + self.width // 2,
                                                         current_y + self.height // 2))
            surface.blit(rotated_surf, rotated_rect)

            icon_surf = font_medium.render(self.data["icon"], True, COLORS["text"])
            icon_rect = icon_surf.get_rect(center=(self.x + self.width // 2,
                                                   current_y + self.height // 2))
            surface.blit(icon_surf, icon_rect)

        for particle in self.particles:
            particle.draw(surface)

    def check_collision(self, developer):
        if self.collected:
            return False

        dev_center_x = developer.x + developer.width // 2
        dev_center_y = developer.y + developer.height // 2
        obst_center_x = self.x + self.width // 2
        obst_center_y = self.y + self.height // 2 + self.bounce_offset

        distance = math.sqrt((dev_center_x - obst_center_x) ** 2 +
                             (dev_center_y - obst_center_y) ** 2)

        return distance < (developer.width // 2 + self.width // 2)


# Новогодние данные достижений
achievements_data = [
    {
        "icon": "TEAM",
        "title": "Новогодняя команда",
        "text": "В команду пришла ценная помощница Алина, которая выжила в суровых сроках и успешно справлялась с ответственными задачами",
        "stats": "+40% к скорости разработки",
        "type": "team",
        "details": [
            "Новый член команды влился в процессы меньше чем за 2 недели",
            "Взяла на себя ключевые проекты",
            "Помогла с рефакторингом"
        ]
    },
    {
        "icon": "TIME",
        "title": "Новогодние сроки",
        "text": "Все проекты были реализованы в срок или даже раньше дедлайнов до Нового года",
        "stats": "100% соблюдение сроков",
        "type": "deadline",
        "details": [
            "19 проектов завершены вовремя",
            "3 проекта сданы досрочно",
            "0 переносов дедлайнов"
        ]
    },
    {
        "icon": "GIFT",
        "title": "Подарочный продукт",
        "text": "Запущен 'Холодильник Выгоды' - новогодний подарок пользователям с постоянным развитием",
        "stats": "+300% вовлеченности пользователей",
        "type": "product",
        "details": [
            "Архитектура микросервисов",
            "Реализовано 15+ уникальных фич",
            "Еженедельные релизы"
        ]
    },
    {
        "icon": "SNOW",
        "title": "Снежная уборка кода",
        "text": "Провели рефакторинг кодовой базы всех проектов как новогоднюю уборку",
        "stats": "-60% технического долга",
        "type": "refactor",
        "details": [
            "Выделена переиспользуемая библиотека",
            "Улучшена читаемость кода",
            "Сокращено время отладки"
        ]
    },
    {
        "icon": "TREE",
        "title": "Елочка API",
        "text": "Разделили монолитный эндпоинт user на независимые ручки как ветки елки",
        "stats": "+200% скорость ответа API",
        "type": "api",
        "details": [
            "5 независимых эндпоинтов",
            "Упрощено тестирование",
            "Улучшена масштабируемость"
        ]
    },
    {
        "icon": "STAR",
        "title": "Звездная конфигурация",
        "text": "Статические данные валидируются на уровне конфигов как звезды на елке",
        "stats": "-90% продакшн багов",
        "type": "config",
        "details": [
            "Изменение без деплоев",
            "Ускоренное тестирование",
            "Предсказуемое поведение"
        ]
    },
    {
        "icon": "BELL",
        "title": "Колокольчик шаблонов",
        "text": "Создан шаблон для реализации проектов как новогодний колокольчик",
        "stats": "-40% время на старт проекта",
        "type": "template",
        "details": [
            "Стандартизирована структура",
            "Автоматическая настройка",
            "Готовые модули"
        ]
    },
    {
        "icon": "MAGIC",
        "title": "Новогодняя магия автоматизации",
        "text": "Автоматическая отправка аналитики в Telegram как новогодние поздравления",
        "stats": "Ежедневная экономия 2 человеко-часов",
        "type": "automation",
        "details": [
            "Отчеты в реальном времени",
            "Интеграция со всеми проектами",
            "Гибкая настройка метрик"
        ]
    },
    {
        "icon": "CANDY",
        "title": "Сладкое переиспользование",
        "text": "Механизм подбора приза переиспользован в проектах как новогодние конфеты",
        "stats": "Переиспользовано в 5+ проектах",
        "type": "reuse",
        "details": [
            "Универсальное решение",
            "Простая интеграция",
            "Гибкая конфигурация"
        ]
    }
]


class Game:
    def __init__(self):
        self.state = GameState.MENU
        center_x = WIDTH // 2
        center_y = HEIGHT // 2

        self.dev1 = Developer(center_x - 80, center_y, COLORS["dev1"], "Артем", "SANTA")
        self.dev2 = Developer(center_x + 80, center_y, COLORS["dev2"], "Алина", "Snow_Girl")
        self.selected_dev = self.dev1
        self.obstacles = []
        self.current_achievement = 0
        self.achievement_display = None
        self.achievement_method = None
        self.display_timer = 0
        self.score = 0
        self.jump_score = 0
        self.timer = 0
        self.spawn_timer = 0
        self.game_speed = 1.0
        self.particles = []
        self.collected_achievements = []
        self.jump_notifications = []

        self.stars = []
        for _ in range(120):
            self.stars.append([
                random.randint(0, WIDTH),
                random.randint(0, HEIGHT),
                random.uniform(0.3, 1.0),
                random.randint(15, 35)
            ])

    def spawn_obstacle(self):
        if self.current_achievement < len(achievements_data) and self.spawn_timer <= 0:
            obstacle = AchievementObstacle(achievements_data[self.current_achievement],
                                           x_offset=self.current_achievement * 100)
            self.obstacles.append(obstacle)
            self.current_achievement += 1
            self.spawn_timer = random.randint(150, 200)

    def show_achievement(self, achievement, method="collected"):
        self.achievement_display = achievement
        self.achievement_method = method
        self.display_timer = 60

        if method == "collected":
            self.score += 100

        self.create_celebration_particles()

    def create_celebration_particles(self):
        christmas_colors = [
            COLORS["success"],
            COLORS["primary"],
            COLORS["secondary"],
            COLORS["snow"],
            COLORS["warning"]
        ]
        for _ in range(40):
            self.particles.append(Particle(
                random.randint(200, 1000),
                random.randint(100, 200),
                random.choice(christmas_colors)
            ))

    def update(self):
        if self.state not in [GameState.PLAYING, GameState.ACHIEVEMENT_SHOW]:
            return

        self.timer += 1
        self.spawn_timer -= 1

        if self.state == GameState.PLAYING:
            self.dev1.update()
            self.dev2.update()

        for star in self.stars:
            star[1] += star[2] * 3
            star[0] += math.sin(pygame.time.get_ticks() * 0.001 + star[0]) * 0.5
            if star[1] > HEIGHT:
                star[1] = -star[3]
                star[0] = random.randint(0, WIDTH)

        self.spawn_obstacle()

        for obstacle in self.obstacles[:]:
            if obstacle.update():
                self.obstacles.remove(obstacle)
            elif not obstacle.collected and not obstacle.passed:
                collected_by = None
                method = None
                if obstacle.check_collision(self.dev1):
                    obstacle.collected = True
                    obstacle.create_collect_particles()
                    collected_by = self.dev1
                    method = "collected"
                elif obstacle.check_collision(self.dev2):
                    obstacle.collected = True
                    obstacle.create_collect_particles()
                    collected_by = self.dev2
                    method = "collected"

                if not collected_by and obstacle.x + obstacle.width < min(self.dev1.x, self.dev2.x):
                    obstacle.passed = True
                    if abs(self.dev1.x - obstacle.x) < abs(self.dev2.x - obstacle.x):
                        collected_by = self.dev1
                    else:
                        collected_by = self.dev2

                    method = "jumped"

                    self.jump_score += 50
                    self.score += 50

                    notification_x = (self.dev1.x + self.dev2.x) // 2
                    notification_y = min(self.dev1.y, self.dev2.y) - 50
                    self.jump_notifications.append(JumpNotification(notification_x, notification_y, 50))

                    for _ in range(15):
                        self.particles.append(Particle(
                            notification_x,
                            notification_y + 20,
                            COLORS["success"]
                        ))

                if collected_by:
                    self.show_achievement(obstacle.data, method)
                    collected_by.collected.append(obstacle.data)
                    self.collected_achievements.append({
                        "achievement": obstacle.data,
                        "collected_by": collected_by.name,
                        "method": method
                    })
                    self.state = GameState.ACHIEVEMENT_SHOW

        if self.state == GameState.ACHIEVEMENT_SHOW:
            if self.display_timer > 0:
                self.display_timer -= 1
                if self.display_timer <= 0:
                    self.state = GameState.ACHIEVEMENT_WAIT

        for particle in self.particles[:]:
            particle.update()
            if particle.is_dead():
                self.particles.remove(particle)

        for notification in self.jump_notifications[:]:
            notification.update()
            if notification.is_dead():
                self.jump_notifications.remove(notification)

        if (len(self.dev1.collected) + len(self.dev2.collected) >= len(achievements_data) and
                len(self.obstacles) == 0):
            self.state = GameState.FINISHED

    def draw_background(self):
        if background_image:
            scaled_bg = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
            screen.blit(scaled_bg, (0, 0))
        else:
            for y in range(HEIGHT):
                color_value = int(10 + (y / HEIGHT) * 20)
                pygame.draw.line(screen, (color_value, color_value + 5, color_value + 30),
                                 (0, y), (WIDTH, y))

        for x, y, brightness, size in self.stars:
            if snowflake_image:
                scaled_snowflake = pygame.transform.scale(snowflake_image, (size, size))
                screen.blit(scaled_snowflake, (x - size // 2, y - size // 2))
            else:
                alpha = int(200 * brightness)
                s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*COLORS["snow"], alpha), (size, size), size)
                screen.blit(s, (x - size, y - size))

    def draw_ui(self):
        pygame.draw.rect(screen, (*COLORS["ui_bg"][:3], 120), (20, 20, 240, 200), 0, 10)

        title = font_medium.render("Новогодняя Backend", True, COLORS["primary"])
        screen.blit(title, (40, 40))

        title = font_medium.render("Odyssey 2025", True, COLORS["primary"])
        screen.blit(title, (40, 60))

        score_text = font_small.render(f"Общий счет: {self.score}", True, COLORS["text"])
        screen.blit(score_text, (40, 90))

        jump_score_text = font_small.render(f"За прыжки: {self.jump_score}", True, COLORS["success"])
        screen.blit(jump_score_text, (40, 115))

        collected = len(self.dev1.collected) + len(self.dev2.collected)
        total = len(achievements_data)
        progress_text = font_small.render(f"Прогресс: {collected}/{total}", True, COLORS["text"])
        screen.blit(progress_text, (40, 140))

        progress_width = 200
        target_progress = collected / total if total > 0 else 0
        self.display_progress = getattr(self, "display_progress", 0)
        self.display_progress += (target_progress - self.display_progress) * 0.1
        pygame.draw.rect(screen, COLORS["success"],
                         (40, 160, progress_width * self.display_progress, 12), 0, 6)

        controls_y = HEIGHT - 250
        controls = [
            "Управление:",
            "ПРОБЕЛ - Прыжок (оба сразу)",
            "ENTER - Продолжить",
            "R - Рестарт",
            "ESC - Выход",
            "",
            "Очки:",
            "+50 за перепрыгивание",
            "+150 за касание"
        ]

        for i, text in enumerate(controls):
            control_text = font_xsmall.render(text, True, COLORS["text_secondary"])
            screen.blit(control_text, (WIDTH - 300, controls_y + i * 25))

        pygame.draw.rect(screen, (*COLORS["ui_bg"][:3], 120), (WIDTH - 300, 20, 280, 150), 0, 10)
        achievements_title = font_small.render("Последние:", True, COLORS["primary"])
        screen.blit(achievements_title, (WIDTH - 280, 40))

        recent = (self.dev1.collected[-2:] + self.dev2.collected[-2:])[-2:]
        for i, achievement in enumerate(recent[::-1]):
            if i < 2:
                achievement_text = font_xsmall.render(f"• {achievement['title']}",
                                                      True, COLORS["text"])
                screen.blit(achievement_text, (WIDTH - 280, 70 + i * 30))

    def wrap_text(self, text, font, max_width):
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            line_width = font.size(' '.join(current_line))[0]

            if line_width > max_width:
                if len(current_line) == 1:
                    lines.append(' '.join(current_line))
                    current_line = []
                else:
                    current_line.pop()
                    lines.append(' '.join(current_line))
                    current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines

    def draw_achievement_popup(self):
        if not self.achievement_display:
            return

        popup_width = 1200
        popup_height = 400
        popup_x = WIDTH // 2 - popup_width // 2
        popup_y = 50

        s = pygame.Surface((popup_width, popup_height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 220))
        screen.blit(s, (popup_x, popup_y))

        pygame.draw.rect(screen, COLORS["primary"],
                         (popup_x, popup_y, popup_width, popup_height), 3, 10)

        icon = title_font.render(self.achievement_display["icon"], True, COLORS["primary"])
        title_text = self.achievement_display["title"]
        if len(title_text) > 30:
            title_text = title_text[:27] + "..."
        title = title_font.render(title_text, True, COLORS["success"])

        screen.blit(icon, (popup_x + 30, popup_y + 25))
        screen.blit(title, (popup_x + 130, popup_y + 25))

        text_lines = self.wrap_text(self.achievement_display["text"], font_medium, 1000)
        for i, line in enumerate(text_lines[:3]):
            text = font_medium.render(line, True, COLORS["text"])
            screen.blit(text, (popup_x + 30, popup_y + 90 + i * 30))

        stats = font_medium.render(self.achievement_display["stats"], True, COLORS["secondary"])
        screen.blit(stats, (popup_x + 30, popup_y + 200))

        if hasattr(self, 'achievement_method') and self.achievement_method:
            method_text = "Получено касанием (+150 очков)" if self.achievement_method == "collected" else "Получено перепрыгиванием (+50 очков)"
            method_color = COLORS["success"] if self.achievement_method == "collected" else COLORS["warning"]
            method_render = font_small.render(method_text, True, method_color)
            screen.blit(method_render, (popup_x + 30, popup_y + 230))

        if "details" in self.achievement_display:
            details_title = font_medium.render("Детали:", True, COLORS["warning"])
            screen.blit(details_title, (popup_x + 30, popup_y + 260))

            for i, detail in enumerate(self.achievement_display["details"][:2]):
                detail_text = f"• {detail}"
                detail_render = font_small.render(detail_text, True, COLORS["text_secondary"])
                screen.blit(detail_render, (popup_x + 50, popup_y + 290 + i * 25))

        if self.state == GameState.ACHIEVEMENT_WAIT:
            continue_text = font_large.render("Нажмите ENTER для продолжения", True, COLORS["warning"])
            screen.blit(continue_text, (popup_x + popup_width // 2 - continue_text.get_width() // 2,
                                        popup_y + 350))
        else:
            dev1_has = any(ach["title"] == self.achievement_display["title"] for ach in self.dev1.collected)
            dev2_has = any(ach["title"] == self.achievement_display["title"] for ach in self.dev2.collected)

            if dev1_has and dev2_has:
                collected_by = "Оба разработчика"
            elif dev1_has:
                collected_by = "Тимлид"
            else:
                collected_by = "Разработчик"

            collector_text = font_medium.render(f"Собрано: {collected_by}", True, COLORS["text_secondary"])
            screen.blit(collector_text, (popup_x + popup_width // 2 - collector_text.get_width() // 2,
                                         popup_y + 350))

    def draw_menu(self):
        self.draw_background()

        panel_width = 800
        panel_height = 400
        panel_x = WIDTH // 2 - panel_width // 2
        panel_y = HEIGHT // 2 - panel_height // 2 - 50

        pygame.draw.rect(screen, (*COLORS["ui_bg"][:3], 240),
                         (panel_x, panel_y, panel_width, panel_height), 0, 20)
        pygame.draw.rect(screen, COLORS["primary"],
                         (panel_x, panel_y, panel_width, panel_height), 3, 20)

        title = title_font.render("НОВОГОДНЯЯ BACKEND ODYSSEY 2025", True, COLORS["primary"])
        subtitle = font_large.render("Год прорывов и новогодних достижений", True, COLORS["text"])

        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, panel_y + 40))
        screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, panel_y + 100))

        description = [
            "Дед мороз Артем и Снегурочка Алина бегут к новогоднему успеху!",
            "Перепрыгивайте препятствия (+50 очков) или касайтесь их (+150 очков).",
            "После показа достижения нажмите ENTER для продолжения."
        ]

        for i, line in enumerate(description):
            desc_text = font_medium.render(line, True, COLORS["text_secondary"])
            screen.blit(desc_text, (WIDTH // 2 - desc_text.get_width() // 2, panel_y + 160 + i * 35))

        button_rect = pygame.Rect(WIDTH // 2 - 150, panel_y + 320, 300, 50)
        pygame.draw.rect(screen, COLORS["primary"], button_rect, 0, 10)
        pygame.draw.rect(screen, COLORS["text"], button_rect, 2, 10)

        start_text = font_large.render("НАЧАТЬ ПУТЕШЕСТВИЕ", True, COLORS["text"])
        screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, panel_y + 335))

        hint = font_small.render("Нажмите ПРОБЕЛ для начала", True, COLORS["text_secondary"])
        screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, panel_y + 380))

        return button_rect

    def draw_finish_screen(self):
        self.draw_background()

        panel_width = 1300
        panel_height = 700
        panel_x = WIDTH // 2 - panel_width // 2
        panel_y = 20

        pygame.draw.rect(
            screen, (*COLORS["ui_bg"][:3], 240),
            (panel_x, panel_y, panel_width, panel_height), 0, 20
        )
        pygame.draw.rect(
            screen, COLORS["primary"],
            (panel_x, panel_y, panel_width, panel_height), 3, 20
        )

        congrats = title_font.render("🎉 ВСЕ НОВОГОДНИЕ ДОСТИЖЕНИЯ 2025! 🎉", True, COLORS["success"])
        screen.blit(congrats, (WIDTH // 2 - congrats.get_width() // 2, panel_y + 20))

        pygame.draw.line(screen, COLORS["primary"],
                         (panel_x + 50, panel_y + 100),
                         (panel_x + panel_width - 50, panel_y + 100), 2)

        col1_x = panel_x + 60
        col2_x = panel_x + panel_width // 2 + 20
        start_y = panel_y + 120

        achievements_title = font_large.render("Все достижения Backend команды 2025:", True, COLORS["warning"])
        screen.blit(achievements_title, (col1_x, start_y))

        achievements_per_column = (len(achievements_data) + 1) // 2

        for i, achievement in enumerate(achievements_data):
            if i < achievements_per_column:
                x = col1_x
                y = start_y + 40 + (i * 60)
            else:
                x = col2_x
                y = start_y + 40 + ((i - achievements_per_column) * 60)

            achievement_type = achievement.get("type", "product")
            type_colors = {
                "team": COLORS["success"],
                "deadline": COLORS["warning"],
                "product": COLORS["primary"],
                "refactor": COLORS["success"],
                "api": COLORS["danger"],
                "config": COLORS["secondary"],
                "template": COLORS["secondary"],
                "automation": COLORS["secondary"],
                "reuse": COLORS["secondary"]
            }
            icon_color = type_colors.get(achievement_type, COLORS["primary"])

            icon_text = font_medium.render(achievement["icon"], True, icon_color)
            screen.blit(icon_text, (x, y))

            title_text = achievement["title"]
            if len(title_text) > 35:
                title_text = title_text[:32] + "..."
            title_render = font_small.render(title_text, True, COLORS["text"])
            screen.blit(title_render, (x + 80, y))

            stats_render = font_xsmall.render(achievement["stats"], True, COLORS["success"])
            screen.blit(stats_render, (x + 40, y + 20))

        stats_y = panel_y + panel_height - 80
        summary_text = f"Собрано: 9 достижений | Время: 363 дня | Эффективность: 100%"
        summary_render = font_medium.render(summary_text, True, COLORS["text"])
        screen.blit(summary_render, (WIDTH // 2 - summary_render.get_width() // 2, stats_y))

        restart_text = font_large.render("Нажмите R для новой игры или ESC для выхода", True, COLORS["warning"])
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, panel_y + panel_height - 40))

    def draw(self):
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state in [GameState.PLAYING, GameState.ACHIEVEMENT_SHOW, GameState.ACHIEVEMENT_WAIT]:
            self.draw_background()
            for obstacle in self.obstacles:
                obstacle.draw(screen)
            self.dev1.draw(screen)
            self.dev2.draw(screen)

            for particle in self.particles:
                particle.draw(screen)

            for notification in self.jump_notifications:
                notification.draw(screen)

            self.draw_ui()

            if self.achievement_display:
                self.draw_achievement_popup()

            if self.state == GameState.ACHIEVEMENT_WAIT:
                pause_text = font_medium.render("ИГРА ОСТАНОВЛЕНА", True, COLORS["warning"])
                screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT - 80))

        elif self.state == GameState.FINISHED:
            self.draw_finish_screen()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                global music_playing
                if music_playing:
                    pygame.mixer.music.pause()
                    music_playing = False
                else:
                    pygame.mixer.music.unpause()
                    music_playing = True

            elif self.state == GameState.MENU:
                if event.key == pygame.K_SPACE:
                    self.state = GameState.PLAYING

            elif self.state == GameState.PLAYING:
                if event.key == pygame.K_SPACE:
                    self.dev1.jump(1.0)
                    self.dev2.jump(1.0)
                elif event.key == pygame.K_r:
                    self.__init__()
                    self.state = GameState.PLAYING
                elif event.key == pygame.K_ESCAPE:
                    self.state = GameState.MENU

            elif self.state == GameState.ACHIEVEMENT_WAIT:
                if event.key == pygame.K_RETURN:
                    self.state = GameState.PLAYING
                    self.achievement_display = None
                elif event.key == pygame.K_ESCAPE:
                    self.state = GameState.MENU

            elif self.state == GameState.FINISHED:
                if event.key == pygame.K_r:
                    self.__init__()
                    self.state = GameState.PLAYING
                elif event.key == pygame.K_ESCAPE:
                    self.state = GameState.MENU
                elif event.key == pygame.K_RETURN:
                    self.__init__()
                    self.state = GameState.PLAYING

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.state == GameState.MENU:
                button_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 50, 300, 50)
                if button_rect.collidepoint(event.pos):
                    self.state = GameState.PLAYING

            elif self.state == GameState.FINISHED:
                button_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 150, 300, 45)
                if button_rect.collidepoint(event.pos):
                    self.__init__()
                    self.state = GameState.PLAYING


# === АСИНХРОННАЯ ФУНКЦИЯ ДЛЯ PYGbag ===
async def main():
    game = Game()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game.handle_event(event)

        game.update()
        game.draw()

        # Оригинальный FPS
        fps = font_xsmall.render(f"FPS: {int(clock.get_fps())}", True, COLORS["text_secondary"])
        screen.blit(fps, (10, HEIGHT - 30))

        # Ключевое изменение для PygBag
        await asyncio.sleep(0)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


# === ДВОЙНАЯ ТОЧКА ВХОДА ===
if __name__ == "__main__":
    # Для обычного запуска: python main.py
    # Для PygBag: asyncio.run(main())

    # Проверяем, запущен ли через PygBag
    try:
        import pygbag

        # Запускаем асинхронную версию для PygBag
        asyncio.run(main())
    except ImportError:
        # Запускаем обычную синхронную версию
        game = Game()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                game.handle_event(event)

            game.update()
            game.draw()

            fps = font_xsmall.render(f"FPS: {int(clock.get_fps())}", True, COLORS["text_secondary"])
            screen.blit(fps, (10, HEIGHT - 30))

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        sys.exit()