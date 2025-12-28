import pygame
import random
import sys
import math
from enum import Enum

# Инициализация PyGame
pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 1400, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Новогодняя Backend Odyssey 2025: Год прорывов")
clock = pygame.time.Clock()

# Загрузка изображений
try:
    background_image = pygame.image.load("fon.jpg")
    # Масштабируем изображение, сохраняя пропорции
    bg_width, bg_height = background_image.get_size()
    scale_x = WIDTH / bg_width
    scale_y = HEIGHT / bg_height
    scale = min(scale_x, scale_y)  # Используем меньший масштаб для сохранения пропорций
    new_width = int(bg_width * scale)
    new_height = int(bg_height * scale)
    background_image = pygame.transform.scale(background_image, (new_width, new_height))
except:
    background_image = None
    print("Не удалось загрузить fon.jpg")

try:
    grinch_image = pygame.image.load("grinch2.png").convert_alpha()
    grinch_image = pygame.transform.scale(grinch_image, (80, 80))
except:
    grinch_image = None
    print("Не удалось загрузить grinch.png")

try:
    alina_image = pygame.image.load("alina.png")
except:
    alina_image = None
    print("❌ Не удалось загрузить alina.png")

try:
    alina_image = pygame.image.load("alina.png")
    alina_image = pygame.transform.scale(alina_image, (45, 45))  # Размер лица персонажа
except:
    alina_image = None
    print("Не удалось загрузить alina.png")
try:
    snowflake_image = pygame.image.load("snow.png").convert_alpha()
    snowflake_image = pygame.transform.scale(snowflake_image, (20, 20))
except:
    snowflake_image = None
    print("Не удалось загрузить snow.png")
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
    "primary": (220, 20, 60),  # Красный новогодний
    "secondary": (34, 139, 34),  # Зеленый елочный
    "success": (255, 215, 0),  # Золотой
    "warning": (255, 140, 0),  # Оранжевый мандариновый
    "danger": (178, 34, 34),  # Темно-красный
    "text": (255, 250, 250),  # Снежно-белый
    "text_secondary": (192, 192, 192),  # Серебристый
    "dev1": (220, 20, 60),  # Красный Санта
    "dev2": (34, 139, 34),  # Зеленый эльф
    "ui_bg": (25, 35, 50, 220),
    "obstacle": (178, 34, 34),  # Темно-красный
    "refactor": (255, 215, 0),  # Золотой
    "automation": (135, 206, 250),  # Голубой снежный
    "feature": (50, 205, 50),  # Лайм-зеленый
    "snow": (255, 255, 255),  # Белый снег
    "star": (255, 215, 0)  # Золотая звезда
}


# Состояния игры
class GameState(Enum):
    MENU = 1
    PLAYING = 2
    ACHIEVEMENT_SHOW = 3
    ACHIEVEMENT_WAIT = 4
    PAUSED = 5
    FINISHED = 6


# Частицы для эффектов
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
        self.sparkle = random.randint(0, 10)  # Для мерцания

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
            # Добавляем мерцание для новогоднего эффекта
            if self.sparkle < 15:
                alpha = int(alpha * 0.7)
            s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (self.size, self.size), self.size)
            surface.blit(s, (self.x - self.size, self.y - self.size))

    def is_dead(self):
        return self.life <= 0


class Developer:
    def __init__(self, x, y, color, name, icon_text):
        self.x = x
        self.y = y
        self.start_y = y
        self.color = color
        self.name = name
        self.icon_text = icon_text  # Текстовая иконка вместо эмодзи
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
            # УВЕЛИЧЕННАЯ СИЛА ПРЫЖКА
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
        # Гравитация
        self.velocity_y += 0.8
        self.y += self.velocity_y

        # Ограничение по земле
        if self.y > self.start_y:
            self.y = self.start_y
            if self.jumping:
                self.create_land_particles()
            self.jumping = False
            self.double_jump = True
            self.velocity_y = 0

        # Анимация бега
        if not self.jumping and self.y == self.start_y:
            self.frame_timer += 1
            if self.frame_timer >= 5:
                self.frame_timer = 0
                self.animation_frame = (self.animation_frame + 1) % len(self.run_frames)

        # Обновление частиц
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
        # Тень
        shadow = pygame.Surface((self.width + 10, 20), pygame.SRCALPHA)
        shadow_alpha = 100 - abs(self.y - self.start_y) * 2
        pygame.draw.ellipse(shadow, (0, 0, 0, max(0, shadow_alpha)),
                            (0, 0, self.width + 10, 20))
        surface.blit(shadow, (self.x - 5, self.start_y + self.height - 5))

        # Тело
        body_rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # Эффект отскока при приземлении
        bounce_offset = 0
        if self.jumping and self.velocity_y > 0:
            bounce_offset = math.sin(pygame.time.get_ticks() * 0.01) * 3

        # Рисуем разработчика с новогодним стилем
        pygame.draw.rect(surface, self.color, body_rect, 0, 10)

        # Новогодние украшения на теле
        if self.name == "Артем":  # Санта
            # Белая отделка
            pygame.draw.rect(surface, COLORS["snow"],
                             (self.x, self.y + self.height - 15, self.width, 15), 0, 5)
            # Пояс
            pygame.draw.rect(surface, (139, 69, 19),
                             (self.x, self.y + self.height // 2, self.width, 8))
        else:  # Эльф
            # Полоски на костюме
            for i in range(0, self.height, 15):
                pygame.draw.rect(surface, COLORS["warning"],
                                 (self.x, self.y + i, self.width, 3))

        # Голова
        head_y = self.y - 20 + bounce_offset
        pygame.draw.circle(surface, (255, 220, 177),  # Цвет кожи
                           (self.x + self.width // 2, head_y), 18)
        # --- Руки ---
        # Координаты плеч
        shoulder_y = self.y + 15
        left_shoulder_x = self.x + 5
        right_shoulder_x = self.x + self.width - 5

        # Длина рук
        arm_length = 25

        # Анимация движения рук при беге
        swing = math.sin(pygame.time.get_ticks() * 0.01) * 10  # колебание +-10

        # Левая рука
        pygame.draw.line(surface, self.color,
                         (left_shoulder_x, shoulder_y),
                         (left_shoulder_x - arm_length, shoulder_y + swing), 5)
        # Правая рука
        pygame.draw.line(surface, self.color,
                         (right_shoulder_x, shoulder_y),
                         (right_shoulder_x + arm_length, shoulder_y - swing), 5)
        # Новогодняя шапка
        if self.name == "Артем":  # Шапка Санты
            # Красная треугольная шапка
            hat_offset = math.sin(pygame.time.get_ticks() * 0.005) * 3  # покачивание
            hat_points = [
                (self.x + self.width // 2 - 20, head_y - 10 + hat_offset),  # левый край
                (self.x + self.width // 2 + 20, head_y - 10 + hat_offset),  # правый край
                (self.x + self.width // 2, head_y - 50 + hat_offset)  # вершина
            ]
            pygame.draw.polygon(surface, COLORS["primary"], hat_points)
            # Белый помпон
            pygame.draw.circle(surface, COLORS["snow"],
                               (self.x + self.width // 2, head_y - 50), 6)
        else:  # Шапка эльфа
            # Зеленая остроконечная шапка
            hat_offset = math.sin(pygame.time.get_ticks() * 0.005) * 3
            hat_points = [
                (self.x + self.width // 2 - 18, head_y - 8 + hat_offset),  # ширина увеличена
                (self.x + self.width // 2 + 18, head_y - 8 + hat_offset),
                (self.x + self.width // 2, head_y - 50 + hat_offset)  # высота увеличена
            ]
            pygame.draw.polygon(surface, COLORS["secondary"], hat_points)
            # Колокольчик
            pygame.draw.circle(surface, COLORS["warning"],
                               (self.x + self.width // 2, head_y - 50), 4)
            # Лицо персонажа
        if self.name == "Алина" and alina_image:  # Для эльфа используем фото Алины
            # Создаем круглую маску для фото
            face_size = 45  # было 28
            scaled_alina = pygame.transform.smoothscale(alina_image, (face_size, face_size))

            # Позиция лица
            face_x = self.x + self.width // 2 - face_size // 2
            face_y = head_y - face_size // 2

            # Масштабируем изображение под размер лица с сглаживанием

            # Создаем круглую маску
            face_surface = pygame.Surface((face_size, face_size), pygame.SRCALPHA)
            face_surface.blit(scaled_alina, (0, 0))

            # Применяем круглую маску
            for x in range(face_size):
                for y in range(face_size):
                    distance = ((x - face_size // 2) ** 2 + (y - face_size // 2) ** 2) ** 0.5
                    if distance > face_size // 2:
                        face_surface.set_at((x, y), (0, 0, 0, 0))

            surface.blit(face_surface, (face_x, face_y))
        else:
            # Текстовая иконка роли для Санты или если нет изображения Алины
            icon_surf = font_medium.render(self.icon_text, True, COLORS["text"])
            surface.blit(icon_surf, (self.x + self.width // 2 - 8, head_y - 5))

        # Ноги (анимация бега)
        leg_offset = self.run_frames[self.animation_frame] * 3
        if self.jumping:
            leg_offset = 0

        pygame.draw.rect(surface, self.color,
                         (self.x + 5, self.y + self.height - 10, 10, 15 + leg_offset))
        pygame.draw.rect(surface, self.color,
                         (self.x + self.width - 15, self.y + self.height - 10, 10, 15 - leg_offset))

        # Имя
        name_surf = font_small.render(self.name, True, COLORS["text"])
        surface.blit(name_surf, (self.x - 10, self.y - 50))

        # Частицы
        for particle in self.particles:
            particle.draw(surface)


# Препятствие-достижение
class AchievementObstacle:
    def __init__(self, achievement_data, x_offset=0):
        self.y = HEIGHT // 2 - 40
        self.x = WIDTH + 150 + x_offset
        self.width = 80
        self.height = 80
        # ЗАМЕДЛЕННАЯ СКОРОСТЬ
        self.speed = 4  # Было 6
        self.data = achievement_data
        self.collected = False
        self.passed = False  # Новое поле для отслеживания прохождения
        self.particles = []
        self.rotation = 0
        self.bounce_offset = 0
        self.bounce_speed = random.uniform(0.05, 0.1)

        self.types = {
            "team": COLORS["success"],  # Золотой
            "deadline": COLORS["warning"],  # Оранжевый
            "product": COLORS["primary"],  # Красный
            "refactor": COLORS["refactor"],  # Золотой
            "api": COLORS["obstacle"],  # Темно-красный
            "config": COLORS["automation"],  # Голубой
            "template": COLORS["feature"],  # Зеленый
            "automation": COLORS["secondary"],  # Зеленый
            "reuse": COLORS["dev2"]  # Зеленый эльфа
        }

        self.color = self.types.get(achievement_data.get("type", "product"), COLORS["primary"])

    def update(self):
        self.x -= self.speed
        self.rotation += 2
        self.bounce_offset = math.sin(pygame.time.get_ticks() * self.bounce_speed) * 5

        # Обновление частиц
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

        # Если есть изображение Гринча, используем его
        if grinch_image:
            rotated_grinch = pygame.transform.rotate(grinch_image, self.rotation)
            rotated_rect = rotated_grinch.get_rect(center=(self.x + self.width // 2,
                                                           current_y + self.height // 2))
            surface.blit(rotated_grinch, rotated_rect)
        else:
            # Свечение (если нет изображения)
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

            # Основной блок с поворотом
            block_color = self.color if not self.collected else (*self.color, 100)

            block_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(block_surf, block_color, (0, 0, self.width, self.height), 0, 15)

            # Вращение
            rotated_surf = pygame.transform.rotate(block_surf, self.rotation)
            rotated_rect = rotated_surf.get_rect(center=(self.x + self.width // 2,
                                                         current_y + self.height // 2))
            surface.blit(rotated_surf, rotated_rect)

            # Иконка достижения (текстовая)
            icon_surf = font_medium.render(self.data["icon"], True, COLORS["text"])
            icon_rect = icon_surf.get_rect(center=(self.x + self.width // 2,
                                                   current_y + self.height // 2))
            surface.blit(icon_surf, icon_rect)

        # Частицы
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
        "icon": "TEAM  ",
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

# Основной класс игры
class Game:
    def __init__(self):
        self.state = GameState.MENU
        center_x = WIDTH // 2
        center_y = HEIGHT // 2

        # Девелоперы в центре
        self.dev1 = Developer(center_x - 80, center_y, COLORS["dev1"], "Артем", "SANTA")
        self.dev2 = Developer(center_x + 80, center_y, COLORS["dev2"], "Алина", "ELF")
        self.selected_dev = self.dev1
        self.obstacles = []
        self.current_achievement = 0
        self.achievement_display = None
        self.display_timer = 0
        self.score = 0
        self.jump_score = 0  # Очки за прыжки
        self.timer = 0
        self.spawn_timer = 0
        self.game_speed = 1.0
        self.particles = []
        self.collected_achievements = []

        # Фоновые элементы (обновляем для нового размера экрана)
        self.stars = []
        for _ in range(120):  # Количество снежинок
            self.stars.append([
                random.randint(0, WIDTH),
                random.randint(0, HEIGHT),
                random.uniform(0.3, 1.0),  # Яркость / масштаб снежинки
                random.randint(15, 35)  # Размер снежинки (больше!)
            ])

    def spawn_obstacle(self):
        if self.current_achievement < len(achievements_data) and self.spawn_timer <= 0:
            obstacle = AchievementObstacle(achievements_data[self.current_achievement],
                                           x_offset=self.current_achievement * 100)
            self.obstacles.append(obstacle)
            self.current_achievement += 1
            # УВЕЛИЧЕННЫЙ ТАЙМЕР ДЛЯ ЗАМЕДЛЕНИЯ
            self.spawn_timer = random.randint(150, 200)

    def show_achievement(self, achievement):
        self.achievement_display = achievement
        self.display_timer = 60  # Укороченный таймер для быстрого перехода к ожиданию
        self.score += 100
        self.create_celebration_particles()

    def create_celebration_particles(self):
        # Новогодние цвета для частиц
        christmas_colors = [
            COLORS["success"],  # Золотой
            COLORS["primary"],  # Красный
            COLORS["secondary"],  # Зеленый
            COLORS["snow"],  # Белый
            COLORS["warning"]  # Оранжевый
        ]
        for _ in range(40):  # Больше частиц для праздника
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

        # Обновление разработчиков - ТЕПЕРЬ СИНХРОННО
        if self.state == GameState.PLAYING:
            self.dev1.update()
            self.dev2.update()

        # Обновление снежинок
        for star in self.stars:
            star[1] += star[2] * 3
            star[0] += math.sin(pygame.time.get_ticks() * 0.001 + star[0]) * 0.5
            if star[1] > HEIGHT:
                star[1] = -star[3]
                star[0] = random.randint(0, WIDTH)

        # Спавн препятствий
        self.spawn_obstacle()

        # Обновление препятствий
        for obstacle in self.obstacles[:]:
            if obstacle.update():
                self.obstacles.remove(obstacle)
            elif not obstacle.collected:
                # Проверяем, прошли ли препятствие (для начисления очков за прыжок)
                if not obstacle.passed and obstacle.x + obstacle.width < min(self.dev1.x, self.dev2.x):
                    obstacle.passed = True
                    self.jump_score += 50  # Очки за успешный прыжок
                    self.score += 50
                    # Создаем частицы успеха
                    for _ in range(10):
                        self.particles.append(Particle(
                            obstacle.x + obstacle.width // 2,
                            obstacle.y + obstacle.height // 2,
                            COLORS["success"]
                        ))

                # Проверяем столкновения
                collected_by = None
                if obstacle.check_collision(self.dev1):
                    obstacle.collected = True
                    obstacle.create_collect_particles()
                    collected_by = self.dev1
                elif obstacle.check_collision(self.dev2):
                    obstacle.collected = True
                    obstacle.create_collect_particles()
                    collected_by = self.dev2

                if collected_by:
                    self.show_achievement(obstacle.data)
                    collected_by.collected.append(obstacle.data)
                    self.collected_achievements.append({
                        "achievement": obstacle.data,
                        "collected_by": collected_by.name
                    })
                    # Переходим в состояние показа достижения
                    self.state = GameState.ACHIEVEMENT_SHOW

        # Обновление таймера отображения
        if self.state == GameState.ACHIEVEMENT_SHOW:
            if self.display_timer > 0:
                self.display_timer -= 1
                if self.display_timer <= 0:
                    # После показа переходим в состояние ожидания нажатия C
                    self.state = GameState.ACHIEVEMENT_WAIT

        # Обновление частиц
        for particle in self.particles[:]:
            particle.update()
            if particle.is_dead():
                self.particles.remove(particle)

        # Проверка завершения
        if (len(self.dev1.collected) + len(self.dev2.collected) >= len(achievements_data) and
                len(self.obstacles) == 0):
            self.state = GameState.FINISHED

    def draw_background(self):
        # Используем фоновое изображение если доступно
        if background_image:
            # Центрируем изображение
            bg_x = (WIDTH - background_image.get_width()) // 2
            bg_y = (HEIGHT - background_image.get_height()) // 2
            screen.blit(background_image, (bg_x, bg_y))
        else:
            # Новогодний градиентный фон (запасной вариант)
            for y in range(HEIGHT):
                color_value = int(10 + (y / HEIGHT) * 20)
                # Добавляем синий оттенок для зимней атмосферы
                pygame.draw.line(screen, (color_value, color_value + 5, color_value + 30),
                                 (0, y), (WIDTH, y))


        # Падающие снежинки с PNG
        for x, y, brightness, size in self.stars:
            if snowflake_image:
                # Масштабируем PNG под размер снежинки
                scaled_snowflake = pygame.transform.scale(snowflake_image, (size, size))
                screen.blit(scaled_snowflake, (x - size // 2, y - size // 2))
            else:
                # fallback: белый кружок
                alpha = int(200 * brightness)
                s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*COLORS["snow"], alpha), (size, size), size)
                screen.blit(s, (x - size, y - size))
        # Боковые панели (полупрозрачные поверх фона)
        pygame.draw.rect(screen, (*COLORS["ui_bg"][:3], 180), (0, 0, 280, HEIGHT))
        pygame.draw.rect(screen, (*COLORS["ui_bg"][:3], 180), (WIDTH - 320, 0, 320, HEIGHT))


    def draw_ui(self):

        # Левый сайдбар - статистика

        pygame.draw.rect(screen, (*COLORS["ui_bg"][:3], 180), (20, 20, 240, 200), 0, 10)

        # Заголовок
        title = font_medium.render("Новогодняя Backend Odyssey 2025", True, COLORS["primary"])
        screen.blit(title, (40, 40))

        # Счет
        score_text = font_small.render(f"Общий счет: {self.score}", True, COLORS["text"])
        screen.blit(score_text, (40, 80))

        # Очки за прыжки
        jump_score_text = font_small.render(f"За прыжки: {self.jump_score}", True, COLORS["success"])
        screen.blit(jump_score_text, (40, 105))

        # Прогресс
        collected = len(self.dev1.collected) + len(self.dev2.collected)
        total = len(achievements_data)
        progress_text = font_small.render(f"Прогресс: {collected}/{total}", True, COLORS["text"])
        screen.blit(progress_text, (40, 130))

        # Прогресс-бар
        progress_width = 200
        # Плавное заполнение прогресс-бара
        target_progress = collected / total if total > 0 else 0
        self.display_progress = getattr(self, "display_progress", 0)
        self.display_progress += (target_progress - self.display_progress) * 0.1  # интерполяция
        pygame.draw.rect(screen, COLORS["success"],
                         (40, 160, progress_width * self.display_progress, 12), 0, 6)
        # Статистика разработчиков
        dev1_text = font_xsmall.render(f"SANTA Санта: {len(self.dev1.collected)}",
                                       True, self.dev1.color)
        dev2_text = font_xsmall.render(f"ELF Эльф: {len(self.dev2.collected)}",
                                       True, self.dev2.color)
        screen.blit(dev1_text, (40, 190))
        screen.blit(dev2_text, (40, 215))

        # Правый сайдбар - управление
        controls_y = HEIGHT - 250
        controls = [
            "Управление:",
            "ПРОБЕЛ - Прыжок (оба сразу)",
            "ENTER - Продолжить после достижения",
            "R - Рестарт",
            "ESC - Выход",
            "",
            "Очки:",
            "+50 за успешный прыжок",
            "+100 за сбор достижения"
        ]

        for i, text in enumerate(controls):
            control_text = font_xsmall.render(text, True, COLORS["text_secondary"])
            screen.blit(control_text, (WIDTH - 300, controls_y + i * 25))

        # Последние достижения
        pygame.draw.rect(screen, (*COLORS["ui_bg"][:3], 180), (WIDTH - 300, 20, 280, 150), 0, 10)
        achievements_title = font_small.render("Последние:", True, COLORS["primary"])
        screen.blit(achievements_title, (WIDTH - 280, 40))

        recent = (self.dev1.collected[-2:] + self.dev2.collected[-2:])[-2:]
        for i, achievement in enumerate(recent[::-1]):
            if i < 2:  # Показываем только 2 последних
                achievement_text = font_xsmall.render(f"• {achievement['title']}",
                                                      True, COLORS["text"])
                screen.blit(achievement_text, (WIDTH - 280, 70 + i * 30))


    def wrap_text(self, text, font, max_width):
        """Перенос текста на несколько строк"""
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
        popup_height = 350
        popup_x = WIDTH // 2 - popup_width // 2
        popup_y = 50

        # Полупрозрачный фон
        s = pygame.Surface((popup_width, popup_height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 220))
        screen.blit(s, (popup_x, popup_y))

        # Рамка
        pygame.draw.rect(screen, COLORS["primary"],
                         (popup_x, popup_y, popup_width, popup_height), 3, 10)

        # Иконка
        icon = font_large.render(self.achievement_display["icon"], True, COLORS["primary"])
        icon_x = popup_x + 30
        icon_y = popup_y + 25
        screen.blit(icon, (icon_x, icon_y))

        # Отступ для текста
        icon_width = 50
        icon_margin = 30
        content_x = icon_x + icon_width + icon_margin

        # Заголовок
        title_text = self.achievement_display["title"]
        if len(title_text) > 50:
            title_text = title_text[:47] + "..."
        title = font_large.render(title_text, True, COLORS["success"])
        screen.blit(title, (content_x, icon_y))

        # Основной текст
        text_lines = self.wrap_text(self.achievement_display["text"], font_small, 1000)
        for i, line in enumerate(text_lines[:4]):
            text = font_small.render(line, True, COLORS["text"])
            screen.blit(text, (content_x, popup_y + 70 + i * 22))

        # Статистика
        stats = font_small.render(self.achievement_display["stats"], True, COLORS["secondary"])
        screen.blit(stats, (content_x, popup_y + 170))

        # Детали
        if "details" in self.achievement_display:
            details_title = font_small.render("Детали:", True, COLORS["warning"])
            screen.blit(details_title, (content_x, popup_y + 200))
            for i, detail in enumerate(self.achievement_display["details"][:3]):
                detail_text = f"• {detail}"
                detail_render = font_small.render(detail_text, True, COLORS["text_secondary"])
                screen.blit(detail_render, (content_x + 20, popup_y + 225 + i * 20))

        # Продолжение / индикатор
        if self.state == GameState.ACHIEVEMENT_WAIT:
            continue_text = font_medium.render("Нажмите ENTER для продолжения", True, COLORS["warning"])
            screen.blit(continue_text, (popup_x + popup_width // 2 - continue_text.get_width() // 2, popup_y + 300))
        else:
            dev1_has = any(ach["title"] == self.achievement_display["title"] for ach in self.dev1.collected)
            dev2_has = any(ach["title"] == self.achievement_display["title"] for ach in self.dev2.collected)

            if dev1_has and dev2_has:
                collected_by = "Оба разработчика"
            elif dev1_has:
                collected_by = "Тимлид"
            else:
                collected_by = "Разработчик"

            collector_text = font_small.render(f"Собрано: {collected_by}", True, COLORS["text_secondary"])
            screen.blit(collector_text, (popup_x + popup_width // 2 - collector_text.get_width() // 2, popup_y + 300))

    def draw_menu(self):
        # Фон меню
        self.draw_background()

        # Центральная панель
        panel_width = 800
        panel_height = 400
        panel_x = WIDTH // 2 - panel_width // 2
        panel_y = HEIGHT // 2 - panel_height // 2 - 50

        pygame.draw.rect(screen, (*COLORS["ui_bg"][:3], 240),
                         (panel_x, panel_y, panel_width, panel_height), 0, 20)
        pygame.draw.rect(screen, COLORS["primary"],
                         (panel_x, panel_y, panel_width, panel_height), 3, 20)

        # Заголовок
        title = title_font.render("НОВОГОДНЯЯ BACKEND ODYSSEY 2025", True, COLORS["primary"])
        subtitle = font_large.render("Год прорывов и новогодних достижений", True, COLORS["text"])

        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, panel_y + 40))
        screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, panel_y + 100))

        # Описание
        description = [
            "Санта и Эльф бегут к новогоднему успеху, собирая достижения года.",
            "Управляйте прыжками (ПРОБЕЛ) и собирайте все новогодние препятствия.",
            "Получайте очки за успешные прыжки (+50) и сбор достижений (+100).",
            "После сбора достижения нажмите ENTER для продолжения."
        ]

        for i, line in enumerate(description):
            desc_text = font_medium.render(line, True, COLORS["text_secondary"])
            screen.blit(desc_text, (WIDTH // 2 - desc_text.get_width() // 2, panel_y + 160 + i * 35))

        # Кнопка старта
        button_rect = pygame.Rect(WIDTH // 2 - 150, panel_y + 320, 300, 50)
        pygame.draw.rect(screen, COLORS["primary"], button_rect, 0, 10)
        pygame.draw.rect(screen, COLORS["text"], button_rect, 2, 10)

        start_text = font_large.render("НАЧАТЬ ПУТЕШЕСТВИЕ", True, COLORS["text"])
        screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, panel_y + 335))

        # Подсказка
        hint = font_small.render("Нажмите ПРОБЕЛ для начала", True, COLORS["text_secondary"])
        screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, panel_y + 380))

        return button_rect

    def draw_finish_screen(self):
        self.draw_background()

        # ---------- Панель ----------
        panel_width = 1200
        panel_height = 650
        panel_x = WIDTH // 2 - panel_width // 2
        panel_y = 40

        pygame.draw.rect(
            screen, (*COLORS["ui_bg"][:3], 240),
            (panel_x, panel_y, panel_width, panel_height), 0, 20
        )
        pygame.draw.rect(
            screen, COLORS["primary"],
            (panel_x, panel_y, panel_width, panel_height), 3, 20
        )

        # ---------- Заголовок ----------
        y = panel_y + 30
        congrats = title_font.render(
            "🎉 ВСЕ НОВОГОДНИЕ ДОСТИЖЕНИЯ СОБРАНЫ! 🎉",
            True, COLORS["success"]
        )
        screen.blit(congrats, (WIDTH // 2 - congrats.get_width() // 2, y))

        y += 50
        final_score = font_large.render(f"Финальный счет: {self.score}", True, COLORS["primary"])
        screen.blit(final_score, (WIDTH // 2 - final_score.get_width() // 2, y))

        y += 35
        jump_score = font_medium.render(f"Очки за прыжки: {self.jump_score}", True, COLORS["success"])
        screen.blit(jump_score, (WIDTH // 2 - jump_score.get_width() // 2, y))

        # ---------- Разделитель ----------
        y += 40
        pygame.draw.line(
            screen, COLORS["primary"],
            (panel_x + 40, y),
            (panel_x + panel_width - 40, y), 2
        )

        # ---------- Константы верстки ----------
        COL_TOP = y + 30
        LINE_TITLE = 32
        LINE_TEXT = 28
        ACH_BLOCK = 64

        col1_x = panel_x + 50
        col2_x = panel_x + panel_width // 2 + 20

        # ---------- Санта ----------
        screen.blit(
            font_large.render("🎅 SANTA собрал:", True, COLORS["dev1"]),
            (col1_x, COL_TOP)
        )

        for i, ach in enumerate(self.dev1.collected[:6]):
            base_y = COL_TOP + LINE_TITLE + i * ACH_BLOCK

            title = font_small.render(f"• {ach['title']}", True, COLORS["text"])
            stats = font_xsmall.render(ach["stats"], True, COLORS["text_secondary"])

            screen.blit(title, (col1_x + 20, base_y))
            screen.blit(stats, (col1_x + 40, base_y + LINE_TEXT))

        # ---------- Эльф ----------
        screen.blit(
            font_large.render("🧝 ELF собрал:", True, COLORS["dev2"]),
            (col2_x, COL_TOP)
        )

        for i, ach in enumerate(self.dev2.collected[:6]):
            base_y = COL_TOP + LINE_TITLE + i * ACH_BLOCK

            title = font_small.render(f"• {ach['title']}", True, COLORS["text"])
            stats = font_xsmall.render(ach["stats"], True, COLORS["text_secondary"])

            screen.blit(title, (col2_x + 20, base_y))
            screen.blit(stats, (col2_x + 40, base_y + LINE_TEXT))

        # ---------- Совместные достижения ----------
        dev1_titles = {a["title"] for a in self.dev1.collected}
        dev2_titles = {a["title"] for a in self.dev2.collected}
        common = list(dev1_titles & dev2_titles)

        max_rows = max(len(self.dev1.collected[:6]), len(self.dev2.collected[:6]))
        y_common = COL_TOP + LINE_TITLE + max_rows * ACH_BLOCK + 30

        if common:
            screen.blit(
                font_large.render("🤝 Совместные достижения:", True, COLORS["primary"]),
                (col1_x, y_common)
            )

            for i, title in enumerate(common[:3]):
                txt = font_small.render(f"• {title}", True, COLORS["text_secondary"])
                screen.blit(txt, (col1_x + 20, y_common + 40 + i * 30))

            y_common += 40 + len(common[:3]) * 30

        # ---------- Итоговая статистика ----------
        stats_y = y_common + 20
        total = len(self.dev1.collected) + len(self.dev2.collected)

        stats = [
            f"Всего достижений: {total} / {len(achievements_data)}",
            f"SANTA: {len(self.dev1.collected)}",
            f"ELF: {len(self.dev2.collected)}",
            f"Время игры: {self.timer // 60} сек",
            f"Эффективность: {int(total / len(achievements_data) * 100)}%"
        ]

        for i, stat in enumerate(stats):
            line = font_medium.render(stat, True, COLORS["text"])
            screen.blit(line, (WIDTH // 2 - line.get_width() // 2, stats_y + i * 28))

        # ---------- Кнопка ----------
        restart = font_medium.render(
            "Нажмите R — новая игра | ESC — выход",
            True, COLORS["warning"]
        )
        screen.blit(
            restart,
            (WIDTH // 2 - restart.get_width() // 2, panel_y + panel_height - 35)
        )
    def draw(self):
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state in [GameState.PLAYING, GameState.ACHIEVEMENT_SHOW, GameState.ACHIEVEMENT_WAIT]:
            self.draw_background()
            for obstacle in self.obstacles:
                obstacle.draw(screen)
            self.dev1.draw(screen)
            self.dev2.draw(screen)

            # Частицы
            for particle in self.particles:
                particle.draw(screen)

            self.draw_ui()

            if self.achievement_display:
                self.draw_achievement_popup()

            # Индикатор состояния
            if self.state == GameState.ACHIEVEMENT_WAIT:
                pause_text = font_medium.render("ИГРА ОСТАНОВЛЕНА", True, COLORS["warning"])
                screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT - 80))

        elif self.state == GameState.FINISHED:
            self.draw_finish_screen()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.state == GameState.MENU:
                if event.key == pygame.K_SPACE:
                    self.state = GameState.PLAYING

            elif self.state == GameState.PLAYING:
                if event.key == pygame.K_SPACE:
                    # ПРЫЖОК ОБОИХ РАЗРАБОТЧИКОВ ОДНОВРЕМЕННО
                    self.dev1.jump(1.0)
                    self.dev2.jump(1.0)
                elif event.key == pygame.K_r:
                    self.__init__()
                    self.state = GameState.PLAYING
                elif event.key == pygame.K_ESCAPE:
                    self.state = GameState.MENU

            elif self.state == GameState.ACHIEVEMENT_WAIT:
                # ПРОДОЛЖЕНИЕ ПОСЛЕ НАЖАТИЯ ENTER
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


def main():
    game = Game()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            game.handle_event(event)

        game.update()
        game.draw()

        # Отображение FPS
        fps = font_xsmall.render(f"FPS: {int(clock.get_fps())}", True, COLORS["text_secondary"])
        screen.blit(fps, (10, HEIGHT - 30))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()