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
    # Оставляем оригинальный размер, масштабирование будет при отрисовке
except:
    background_image = None
    print("Не удалось загрузить fon.jpg")

try:
    grinch_image = pygame.image.load("grinch.png")
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

# Загрузка шрифтов
try:
    title_font = pygame.font.Font("fonts/arial.ttf", 42)
    font_large = pygame.font.Font("fonts/arial.ttf", 28)
    font_medium = pygame.font.Font("fonts/arial.ttf", 22)
    font_small = pygame.font.Font("fonts/arial.ttf", 18)
    font_xsmall = pygame.font.Font("fonts/arial.ttf", 16)
except:
    title_font = pygame.font.Font(None, 42)
    font_large = pygame.font.Font(None, 28)
    font_medium = pygame.font.Font(None, 22)
    font_small = pygame.font.Font(None, 18)
    font_xsmall = pygame.font.Font(None, 16)

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
class JumpNotification:
    def __init__(self, x, y, points):
        self.x = x
        self.y = y
        self.points = points
        self.life = 60  # 1 секунда при 60 FPS
        self.start_y = y
        
    def update(self):
        self.life -= 1
        self.y -= 1  # Поднимается вверх
        
    def draw(self, surface):
        if self.life > 0:
            alpha = int(255 * (self.life / 60))
            color = (*COLORS["success"], alpha)
            
            # Создаем поверхность с альфа-каналом
            text_surf = font_medium.render(f"+{self.points}", True, COLORS["success"])
            alpha_surf = pygame.Surface(text_surf.get_size(), pygame.SRCALPHA)
            alpha_surf.fill((*COLORS["success"], alpha))
            alpha_surf.blit(text_surf, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)
            
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

        # Новогодняя шапка
        if self.name == "Артем":  # Шапка Санты
            # Красная шапка
            hat_points = [
                (self.x + self.width // 2 - 15, head_y - 10),
                (self.x + self.width // 2 + 15, head_y - 10),
                (self.x + self.width // 2 + 20, head_y - 25),
                (self.x + self.width // 2 + 5, head_y - 30)
            ]
            pygame.draw.polygon(surface, COLORS["primary"], hat_points)
            # Белый помпон
            pygame.draw.circle(surface, COLORS["snow"],
                               (self.x + self.width // 2 + 5, head_y - 30), 5)
        else:  # Шапка эльфа
            # Зеленая остроконечная шапка
            hat_points = [
                (self.x + self.width // 2 - 12, head_y - 8),
                (self.x + self.width // 2 + 12, head_y - 8),
                (self.x + self.width // 2, head_y - 35)
            ]
            pygame.draw.polygon(surface, COLORS["secondary"], hat_points)
            # Колокольчик
            pygame.draw.circle(surface, COLORS["warning"],
                               (self.x + self.width // 2, head_y - 35), 3)

        # Лицо персонажа
        if self.name == "Алина" and alina_image:  # Для эльфа используем фото Алины
            # Создаем круглую маску для фото
            face_size = 28
            face_x = self.x + self.width // 2 - face_size // 2
            face_y = head_y - face_size // 2

            # Масштабируем изображение под размер лица с сглаживанием
            scaled_alina = pygame.transform.smoothscale(alina_image, (face_size, face_size))

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
        self.x = WIDTH + 150 + x_offset
        self.y = HEIGHT - 160  # Немного выше для лучшего выравнивания с персонажами
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

    def is_passed_by_developers(self, dev1, dev2):
        """Проверяет, прошло ли препятствие мимо разработчиков"""
        # Препятствие считается пройденным, если его правый край прошел левый край персонажей
        return (self.x + self.width < min(dev1.x, dev2.x) and 
                not self.collected and not self.passed)

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
            # Поворот изображения
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


# Основной класс игры
class Game:
    def __init__(self):
        self.state = GameState.MENU
        self.dev1 = Developer(150, HEIGHT - 170, COLORS["dev1"], "Артем", "SANTA")
        self.dev2 = Developer(300, HEIGHT - 170, COLORS["dev2"], "Алина", "ELF")
        self.selected_dev = self.dev1
        self.obstacles = []
        self.current_achievement = 0
        self.achievement_display = None
        self.achievement_method = None
        self.display_timer = 0
        self.score = 0
        self.jump_score = 0  # Очки за прыжки
        self.timer = 0
        self.spawn_timer = 0
        self.game_speed = 1.0
        self.particles = []
        self.collected_achievements = []
        
        # Система уведомлений о прыжках
        self.jump_notifications = []

        # Фоновые элементы (обновляем для нового размера экрана)
        self.stars = []
        for _ in range(80):  # Больше снежинок для большего экрана
            self.stars.append([
                random.randint(0, WIDTH),
                random.randint(0, HEIGHT),
                random.uniform(0.1, 0.5)
            ])

    def spawn_obstacle(self):
        if self.current_achievement < len(achievements_data) and self.spawn_timer <= 0:
            obstacle = AchievementObstacle(achievements_data[self.current_achievement])
            self.obstacles.append(obstacle)
            self.current_achievement += 1
            # УВЕЛИЧЕННЫЙ ТАЙМЕР ДЛЯ ЗАМЕДЛЕНИЯ
            self.spawn_timer = random.randint(150, 200)

    def show_achievement(self, achievement, method="collected"):
        self.achievement_display = achievement
        self.achievement_method = method  # Сохраняем способ получения
        self.display_timer = 60  # Укороченный таймер для быстрого перехода к ожиданию
        
        # Начисляем дополнительные очки только за касание (сбор)
        if method == "collected":
            self.score += 100  # Дополнительные очки за касание
        
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

        # Обновление звезд
        for star in self.stars:
            star[0] -= star[2] * 0.5
            if star[0] < -10:
                star[0] = WIDTH + 10
                star[1] = random.randint(0, HEIGHT)

        # Спавн препятствий
        self.spawn_obstacle()

        # Обновление препятствий
        for obstacle in self.obstacles[:]:
            if obstacle.update():
                self.obstacles.remove(obstacle)
            elif not obstacle.collected and not obstacle.passed:
                # Проверяем столкновения (касание для сбора)
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

                # Проверяем, прошли ли препятствие (перепрыгивание)
                if not collected_by and obstacle.x + obstacle.width < min(self.dev1.x, self.dev2.x):
                    obstacle.passed = True
                    # Определяем кто перепрыгнул (ближайший персонаж)
                    if abs(self.dev1.x - obstacle.x) < abs(self.dev2.x - obstacle.x):
                        collected_by = self.dev1
                    else:
                        collected_by = self.dev2
                    
                    method = "jumped"
                    
                    # Очки за перепрыгивание
                    self.jump_score += 50
                    self.score += 50
                    
                    # Создаем уведомление о прыжке
                    notification_x = (self.dev1.x + self.dev2.x) // 2
                    notification_y = min(self.dev1.y, self.dev2.y) - 50
                    self.jump_notifications.append(JumpNotification(notification_x, notification_y, 50))
                    
                    # Создаем частицы успеха
                    for _ in range(15):
                        self.particles.append(Particle(
                            notification_x,
                            notification_y + 20,
                            COLORS["success"]
                        ))

                # Если достижение получено (касанием или перепрыгиванием)
                if collected_by:
                    self.show_achievement(obstacle.data, method)
                    collected_by.collected.append(obstacle.data)
                    self.collected_achievements.append({
                        "achievement": obstacle.data,
                        "collected_by": collected_by.name,
                        "method": method
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
                
        # Обновление уведомлений о прыжках
        for notification in self.jump_notifications[:]:
            notification.update()
            if notification.is_dead():
                self.jump_notifications.remove(notification)

        # Проверка завершения
        if (len(self.dev1.collected) + len(self.dev2.collected) >= len(achievements_data) and
                len(self.obstacles) == 0):
            self.state = GameState.FINISHED

    def draw_background(self):
        # Используем фоновое изображение если доступно
        if background_image:
            # Масштабируем изображение на весь экран
            scaled_bg = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
            screen.blit(scaled_bg, (0, 0))
        else:
            # Новогодний градиентный фон (запасной вариант)
            for y in range(HEIGHT):
                color_value = int(10 + (y / HEIGHT) * 20)
                # Добавляем синий оттенок для зимней атмосферы
                pygame.draw.line(screen, (color_value, color_value + 5, color_value + 30),
                                 (0, y), (WIDTH, y))

        # Падающие снежинки
        for x, y, brightness in self.stars:
            alpha = int(200 * brightness)
            snow_size = brightness * 3
            s = pygame.Surface((snow_size * 2, snow_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*COLORS["snow"], alpha),
                               (snow_size, snow_size), snow_size)
            screen.blit(s, (x - snow_size, y - snow_size))

    def draw_text_with_shadow(self, surface, text, font, color, x, y, shadow_color=(0, 0, 0)):
        """Отрисовка текста с тенью для лучшей читаемости"""
        # Рисуем тень
        shadow_surf = font.render(text, True, shadow_color)
        surface.blit(shadow_surf, (x + 1, y + 1))
        # Рисуем основной текст
        text_surf = font.render(text, True, color)
        surface.blit(text_surf, (x, y))
        return text_surf

    def draw_ui(self):
        # Левый сайдбар - статистика (полупрозрачный фон)
        pygame.draw.rect(screen, (*COLORS["ui_bg"][:3], 120), (20, 20, 240, 200), 0, 10)

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
        progress = collected / total if total > 0 else 0
        pygame.draw.rect(screen, (50, 50, 70), (40, 160, progress_width, 12), 0, 6)
        pygame.draw.rect(screen, COLORS["success"],
                         (40, 160, progress_width * progress, 12), 0, 6)

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
            "+50 за перепрыгивание",
            "+150 за касание (+50 прыжок + 100 бонус)"
        ]

        for i, text in enumerate(controls):
            control_text = font_xsmall.render(text, True, COLORS["text_secondary"])
            screen.blit(control_text, (WIDTH - 300, controls_y + i * 25))

        # Последние достижения (полупрозрачный фон)
        pygame.draw.rect(screen, (*COLORS["ui_bg"][:3], 120), (WIDTH - 300, 20, 280, 150), 0, 10)
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

        # Увеличенное окно для отображения всех данных с большими шрифтами
        popup_width = 1200
        popup_height = 400  # Увеличена высота для больших шрифтов
        popup_x = WIDTH // 2 - popup_width // 2
        popup_y = 50  # Немного ниже

        # Полупрозрачный фон
        s = pygame.Surface((popup_width, popup_height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 220))
        screen.blit(s, (popup_x, popup_y))

        # Рамка
        pygame.draw.rect(screen, COLORS["primary"],
                         (popup_x, popup_y, popup_width, popup_height), 3, 10)

        # Иконка и заголовок (увеличенные шрифты)
        icon = title_font.render(self.achievement_display["icon"], True, COLORS["primary"])
        title_text = self.achievement_display["title"]
        if len(title_text) > 30:  # Уменьшаем лимит из-за большего шрифта
            title_text = title_text[:27] + "..."
        title = title_font.render(title_text, True, COLORS["success"])

        screen.blit(icon, (popup_x + 30, popup_y + 25))
        screen.blit(title, (popup_x + 130, popup_y + 25))

        # Основной текст с переносами (увеличенный шрифт)
        text_lines = self.wrap_text(self.achievement_display["text"], font_medium, 1000)
        for i, line in enumerate(text_lines[:3]):  # Максимум 3 строки из-за большего шрифта
            text = font_medium.render(line, True, COLORS["text"])
            screen.blit(text, (popup_x + 30, popup_y + 90 + i * 30))

        # Статистика (увеличенный шрифт)
        stats = font_medium.render(self.achievement_display["stats"], True, COLORS["secondary"])
        screen.blit(stats, (popup_x + 30, popup_y + 200))
        
        # Способ получения (увеличенный шрифт)
        if hasattr(self, 'achievement_method') and self.achievement_method:
            method_text = "Получено касанием (+150 очков)" if self.achievement_method == "collected" else "Получено перепрыгиванием (+50 очков)"
            method_color = COLORS["success"] if self.achievement_method == "collected" else COLORS["warning"]
            method_render = font_small.render(method_text, True, method_color)
            screen.blit(method_render, (popup_x + 30, popup_y + 230))

        # Детали достижения (увеличенный шрифт)
        if "details" in self.achievement_display:
            details_title = font_medium.render("Детали:", True, COLORS["warning"])
            screen.blit(details_title, (popup_x + 30, popup_y + 260))

            for i, detail in enumerate(self.achievement_display["details"][:2]):  # Максимум 2 детали из-за большего шрифта
                detail_text = f"• {detail}"
                detail_render = font_small.render(detail_text, True, COLORS["text_secondary"])
                screen.blit(detail_render, (popup_x + 50, popup_y + 290 + i * 25))

        # Клавиша для продолжения
        if self.state == GameState.ACHIEVEMENT_WAIT:
            continue_text = font_large.render("Нажмите ENTER для продолжения", True, COLORS["warning"])
            screen.blit(continue_text, (popup_x + popup_width // 2 - continue_text.get_width() // 2,
                                        popup_y + 350))
        else:
            # Индикатор сбора
            # Проверяем, у кого из разработчиков есть это достижение
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
            "Санта Артем и Эльф Алина бегут к новогоднему успеху!",
            "Перепрыгивайте препятствия (+50 очков) или касайтесь их (+150 очков).",
            "В любом случае вы получите достижение и покажется его описание.",
            "После показа достижения нажмите ENTER для продолжения."
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
        # Фон
        self.draw_background()

        # Центральная панель (увеличена для отображения всех достижений)
        panel_width = 1300
        panel_height = 700
        panel_x = WIDTH // 2 - panel_width // 2
        panel_y = 20

        pygame.draw.rect(screen, (*COLORS["ui_bg"][:3], 240),
                         (panel_x, panel_y, panel_width, panel_height), 0, 20)
        pygame.draw.rect(screen, COLORS["primary"],
                         (panel_x, panel_y, panel_width, panel_height), 3, 20)

        # Заголовок
        congrats = title_font.render("🎉 ВСЕ НОВОГОДНИЕ ДОСТИЖЕНИЯ 2025! 🎉", True, COLORS["success"])
        screen.blit(congrats, (WIDTH // 2 - congrats.get_width() // 2, panel_y + 20))

        # Финальный счет
        final_score = font_large.render(f"Финальный счет: {self.score}", True, COLORS["primary"])
        screen.blit(final_score, (WIDTH // 2 - final_score.get_width() // 2, panel_y + 60))

        # Разделитель
        pygame.draw.line(screen, COLORS["primary"],
                         (panel_x + 50, panel_y + 100),
                         (panel_x + panel_width - 50, panel_y + 100), 2)

        # Отображение всех достижений в две колонки
        col1_x = panel_x + 30
        col2_x = panel_x + panel_width // 2 + 20
        start_y = panel_y + 120
        
        # Заголовок достижений
        achievements_title = font_large.render("Все достижения Backend команды 2025:", True, COLORS["warning"])
        screen.blit(achievements_title, (col1_x, start_y))
        
        # Отображаем все достижения из achievements_data
        achievements_per_column = (len(achievements_data) + 1) // 2
        
        for i, achievement in enumerate(achievements_data):
            # Определяем колонку и позицию
            if i < achievements_per_column:
                x = col1_x
                y = start_y + 40 + (i * 60)
            else:
                x = col2_x
                y = start_y + 40 + ((i - achievements_per_column) * 60)
            
            # Цвет иконки в зависимости от типа достижения
            achievement_type = achievement.get("type", "product")
            type_colors = {
                "team": COLORS["success"],      # Золотой
                "deadline": COLORS["warning"],  # Оранжевый
                "product": COLORS["primary"],   # Красный
                "refactor": COLORS["success"],  # Золотой
                "api": COLORS["danger"],        # Темно-красный
                "config": COLORS["secondary"],  # Голубой
                "template": COLORS["secondary"], # Зеленый
                "automation": COLORS["secondary"], # Зеленый
                "reuse": COLORS["secondary"]    # Зеленый эльфа
            }
            icon_color = type_colors.get(achievement_type, COLORS["primary"])
            
            # Иконка и название
            icon_text = font_medium.render(achievement["icon"], True, icon_color)
            screen.blit(icon_text, (x, y))
            
            title_text = achievement["title"]
            if len(title_text) > 35:
                title_text = title_text[:32] + "..."
            title_render = font_small.render(title_text, True, COLORS["text"])
            screen.blit(title_render, (x + 40, y))
            
            # Статистика достижения
            stats_render = font_xsmall.render(achievement["stats"], True, COLORS["success"])
            screen.blit(stats_render, (x + 40, y + 20))
            
            # Индикатор сбора (кто собрал это достижение)
            collected_by = []
            if any(ach["title"] == achievement["title"] for ach in self.dev1.collected):
                collected_by.append("Санта")
            if any(ach["title"] == achievement["title"] for ach in self.dev2.collected):
                collected_by.append("Эльф")
            
            if collected_by:
                collector_text = f"✓ {', '.join(collected_by)}"
                collector_color = COLORS["secondary"]
            else:
                collector_text = "✗ Не собрано"
                collector_color = COLORS["danger"]
                
            collector_render = font_xsmall.render(collector_text, True, collector_color)
            screen.blit(collector_render, (x + 40, y + 35))

        # Итоговая статистика внизу
        total_collected = len(self.dev1.collected) + len(self.dev2.collected)
        stats_y = panel_y + panel_height - 80
        
        summary_text = f"Собрано: {total_collected}/{len(achievements_data)} достижений | Время: {self.timer // 60} сек | Эффективность: {int((total_collected / len(achievements_data)) * 100)}%"
        summary_render = font_medium.render(summary_text, True, COLORS["text"])
        screen.blit(summary_render, (WIDTH // 2 - summary_render.get_width() // 2, stats_y))

        # Кнопка рестарта
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

            # Частицы
            for particle in self.particles:
                particle.draw(screen)
                
            # Уведомления о прыжках
            for notification in self.jump_notifications:
                notification.draw(screen)

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