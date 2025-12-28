import pygame
import random
import sys
import math
from enum import Enum

# Инициализация PyGame
pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 1200, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Backend Odyssey 2025: Год прорывов")
clock = pygame.time.Clock()

# Загрузка изображений
try:
    background_image = pygame.image.load("fon.jpg")
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
except:
    background_image = None
    print("Не удалось загрузить fon.jpg")

try:
    grinch_image = pygame.image.load("grinch.png")
    grinch_image = pygame.transform.scale(grinch_image, (80, 80))
except:
    grinch_image = None
    print("Не удалось загрузить grinch.png")

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

# Цветовая палитра
COLORS = {
    "background": (10, 20, 30),
    "dark_bg": (20, 30, 45),
    "primary": (0, 184, 148),
    "secondary": (255, 159, 67),
    "success": (46, 204, 113),
    "warning": (241, 196, 15),
    "danger": (231, 76, 60),
    "text": (220, 240, 255),
    "text_secondary": (150, 170, 190),
    "dev1": (52, 152, 219),
    "dev2": (155, 89, 182),
    "ui_bg": (25, 35, 50, 220),
    "obstacle": (86, 98, 246),
    "refactor": (156, 136, 255),
    "automation": (72, 219, 251),
    "feature": (29, 209, 161)
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

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.speed_y += self.gravity
        self.life -= 1
        self.size *= 0.95

    def draw(self, surface):
        if self.life > 0:
            alpha = int(255 * (self.life / 30))
            s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (self.size, self.size), self.size)
            surface.blit(s, (self.x - self.size, self.y - self.size))

    def is_dead(self):
        return self.life <= 0



class Developer:
    def __init__(self, x, y, color, name, icon):
        self.x = x
        self.y = y
        self.start_y = y
        self.color = color
        self.name = name
        self.icon = icon
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

        # Рисуем разработчика
        pygame.draw.rect(surface, self.color, body_rect, 0, 10)

        # Голова
        head_y = self.y - 20 + bounce_offset
        pygame.draw.circle(surface, self.color,
                           (self.x + self.width // 2, head_y), 18)

        # Иконка
        icon_surf = font_large.render(self.icon, True, COLORS["text"])
        surface.blit(icon_surf, (self.x + self.width // 2 - 10, head_y - 12))

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
        surface.blit(name_surf, (self.x - 10, self.y - 45))

        # Частицы
        for particle in self.particles:
            particle.draw(surface)


# Препятствие-достижение
class AchievementObstacle:
    def __init__(self, achievement_data, x_offset=0):
        self.x = WIDTH + 150 + x_offset
        self.y = HEIGHT - 140
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

            # Иконка достижения
            icon_surf = font_large.render(self.data["icon"], True, COLORS["text"])
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


# Данные достижений
achievements_data = [
    {
        "icon": "👩‍💻",
        "title": "Усиление команды",
        "text": "В команду пришла ценная помощница, которая выжила в суровых сроках и успешно справлялась с ответственными задачами",
        "stats": "+40% к скорости разработки",
        "type": "team",
        "details": [
            "Новый член команды влился в процессы за 2 недели",
            "Взяла на себя ключевые проекты",
            "Помогла наладить процессы код-ревью"
        ]
    },
    {
        "icon": "⏱️",
        "title": "Соблюдение сроков",
        "text": "Все проекты были реализованы в срок или даже раньше дедлайнов",
        "stats": "100% соблюдение сроков",
        "type": "deadline",
        "details": [
            "12 проектов завершены вовремя",
            "3 проекта сданы досрочно",
            "0 переносов дедлайнов"
        ]
    },
    {
        "icon": "🚀",
        "title": "Прорывной продукт",
        "text": "Запущен 'Холодильник Выгоды' - бесконечный продукт с постоянным развитием",
        "stats": "+300% вовлеченности пользователей",
        "type": "product",
        "details": [
            "Архитектура микросервисов",
            "Реализовано 15+ уникальных фич",
            "Еженедельные релизы"
        ]
    },
    {
        "icon": "🧹",
        "title": "Масштабный рефакторинг",
        "text": "Провели рефакторинг кодовой базы всех проектов",
        "stats": "-60% технического долга",
        "type": "refactor",
        "details": [
            "Выделена переиспользуемая библиотека",
            "Улучшена читаемость кода",
            "Сокращено время отладки"
        ]
    },
    {
        "icon": "🔀",
        "title": "Декомпозиция API",
        "text": "Разделили монолитный эндпоинт user на независимые ручки",
        "stats": "+200% скорость ответа API",
        "type": "api",
        "details": [
            "5 независимых эндпоинтов",
            "Упрощено тестирование",
            "Улучшена масштабируемость"
        ]
    },
    {
        "icon": "⚙️",
        "title": "Конфигурационная валидация",
        "text": "Статические данные валидируются на уровне конфигов",
        "stats": "-90% продакшн багов",
        "type": "config",
        "details": [
            "Изменение без деплоев",
            "Ускоренное тестирование",
            "Предсказуемое поведение"
        ]
    },
    {
        "icon": "📐",
        "title": "Базовый шаблон",
        "text": "Создан шаблон для реализации проектов",
        "stats": "-40% время на старт проекта",
        "type": "template",
        "details": [
            "Стандартизирована структура",
            "Автоматическая настройка",
            "Готовые модули"
        ]
    },
    {
        "icon": "🤖",
        "title": "Автоматизация аналитики",
        "text": "Автоматическая отправка аналитики в Telegram",
        "stats": "Ежедневная экономия 2 человеко-часов",
        "type": "automation",
        "details": [
            "Отчеты в реальном времени",
            "Интеграция со всеми проектами",
            "Гибкая настройка метрик"
        ]
    },
    {
        "icon": "🎰",
        "title": "Механизм переиспользования",
        "text": "Механизм подбора приза переиспользован в проектах",
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
        self.dev1 = Developer(150, HEIGHT - 170, COLORS["dev1"], "Артем", "👑")
        self.dev2 = Developer(300, HEIGHT - 170, COLORS["dev2"], "Алина", "💻")
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

        # Фоновые элементы
        self.stars = []
        for _ in range(50):
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

    def show_achievement(self, achievement):
        self.achievement_display = achievement
        self.display_timer = 60  # Укороченный таймер для быстрого перехода к ожиданию
        self.score += 100
        self.create_celebration_particles()

    def create_celebration_particles(self):
        for _ in range(30):
            self.particles.append(Particle(
                random.randint(200, 1000),
                random.randint(100, 200),
                random.choice([COLORS["success"], COLORS["warning"],
                               COLORS["primary"], COLORS["secondary"]])
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
            screen.blit(background_image, (0, 0))
        else:
            # Градиентный фон (запасной вариант)
            for y in range(HEIGHT):
                color_value = int(10 + (y / HEIGHT) * 20)
                pygame.draw.line(screen, (color_value, color_value + 10, color_value + 20),
                                 (0, y), (WIDTH, y))

            # Звезды
            for x, y, brightness in self.stars:
                alpha = int(150 * brightness)
                star_size = brightness * 2
                s = pygame.Surface((star_size * 2, star_size * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (255, 255, 255, alpha),
                                   (star_size, star_size), star_size)
                screen.blit(s, (x - star_size, y - star_size))

            # "Дорожка"
            pygame.draw.rect(screen, (40, 50, 70), (0, HEIGHT - 100, WIDTH, 100))

            # Разметка на дорожке
            for i in range(0, WIDTH, 60):
                dash_length = 40
                pygame.draw.rect(screen, (80, 110, 140),
                                 (i - int(self.timer * 0.5) % 60,
                                  HEIGHT - 50, dash_length, 5))

        # Боковые панели (полупрозрачные поверх фона)
        pygame.draw.rect(screen, (*COLORS["ui_bg"][:3], 180), (0, 0, 280, HEIGHT))
        pygame.draw.rect(screen, (*COLORS["ui_bg"][:3], 180), (WIDTH - 320, 0, 320, HEIGHT))

    def draw_ui(self):
        # Левый сайдбар - статистика
        pygame.draw.rect(screen, (*COLORS["ui_bg"][:3], 180), (20, 20, 240, 200), 0, 10)

        # Заголовок
        title = font_medium.render("Backend Odyssey 2025", True, COLORS["primary"])
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
        dev1_text = font_xsmall.render(f"👑 Тимлид: {len(self.dev1.collected)}",
                                       True, self.dev1.color)
        dev2_text = font_xsmall.render(f"💻 Разработчик: {len(self.dev2.collected)}",
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

        # Окно в ВЕРХНЕЙ ЧАСТИ экрана
        popup_width = 1000
        popup_height = 240  # Уменьшена высота
        popup_x = WIDTH // 2 - popup_width // 2
        popup_y = 30  # ПЕРЕМЕЩЕНО ВВЕРХ

        # Полупрозрачный фон
        s = pygame.Surface((popup_width, popup_height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 220))
        screen.blit(s, (popup_x, popup_y))

        # Рамка
        pygame.draw.rect(screen, COLORS["primary"],
                         (popup_x, popup_y, popup_width, popup_height), 3, 10)

        # Иконка и заголовок
        icon = font_large.render(self.achievement_display["icon"], True, COLORS["primary"])
        title_text = self.achievement_display["title"]
        if len(title_text) > 40:
            title_text = title_text[:37] + "..."
        title = font_large.render(title_text, True, COLORS["success"])

        screen.blit(icon, (popup_x + 30, popup_y + 25))
        screen.blit(title, (popup_x + 80, popup_y + 25))

        # Основной текст с переносами
        text_lines = self.wrap_text(self.achievement_display["text"], font_small, 800)
        for i, line in enumerate(text_lines[:3]):  # Максимум 3 строки
            text = font_small.render(line, True, COLORS["text"])
            screen.blit(text, (popup_x + 30, popup_y + 70 + i * 25))

        # Статистика
        stats = font_small.render(self.achievement_display["stats"], True, COLORS["secondary"])
        screen.blit(stats, (popup_x + 30, popup_y + 155))

        # Клавиша для продолжения
        if self.state == GameState.ACHIEVEMENT_WAIT:
            continue_text = font_medium.render("Нажмите ENTER для продолжения", True, COLORS["warning"])
            screen.blit(continue_text, (popup_x + popup_width // 2 - continue_text.get_width() // 2,
                                        popup_y + 185))
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

            collector_text = font_small.render(f"Собрано: {collected_by}", True, COLORS["text_secondary"])
            screen.blit(collector_text, (popup_x + popup_width - 200, popup_y + 155))

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
        title = title_font.render("BACKEND ODYSSEY 2025", True, COLORS["primary"])
        subtitle = font_large.render("Год прорывов и достижений", True, COLORS["text"])

        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, panel_y + 40))
        screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, panel_y + 100))

        # Описание
        description = [
            "Два разработчика бегут к успеху, собирая достижения года.",
            "Управляйте прыжками (ПРОБЕЛ) и собирайте все препятствия.",
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
        # Фон
        self.draw_background()

        # Центральная панель
        panel_width = 1000
        panel_height = 500
        panel_x = WIDTH // 2 - panel_width // 2
        panel_y = 100

        pygame.draw.rect(screen, (*COLORS["ui_bg"][:3], 240),
                         (panel_x, panel_y, panel_width, panel_height), 0, 20)
        pygame.draw.rect(screen, COLORS["primary"],
                         (panel_x, panel_y, panel_width, panel_height), 3, 20)

        # Заголовок
        congrats = title_font.render("🎉 ВСЕ ДОСТИЖЕНИЯ ГОДА СОБРАНЫ! 🎉", True, COLORS["success"])
        screen.blit(congrats, (WIDTH // 2 - congrats.get_width() // 2, panel_y + 30))
        
        # Финальный счет
        final_score = font_large.render(f"Финальный счет: {self.score}", True, COLORS["primary"])
        screen.blit(final_score, (WIDTH // 2 - final_score.get_width() // 2, panel_y + 80))
        
        jump_score_final = font_medium.render(f"Очки за прыжки: {self.jump_score}", True, COLORS["success"])
        screen.blit(jump_score_final, (WIDTH // 2 - jump_score_final.get_width() // 2, panel_y + 110))

        # Разделитель
        pygame.draw.line(screen, COLORS["primary"],
                         (panel_x + 50, panel_y + 140),
                         (panel_x + panel_width - 50, panel_y + 140), 2)

        # Колонки с достижениями
        col1_x = panel_x + 50
        col2_x = panel_x + panel_width // 2 + 20
        y_offset = panel_y + 170

        # Тимлид
        dev1_title = font_large.render("👑 Тимлид собрал:", True, COLORS["dev1"])
        screen.blit(dev1_title, (col1_x, y_offset))

        for i, achievement in enumerate(self.dev1.collected):
            ach_text = font_small.render(f"• {achievement['title']}", True, COLORS["text"])
            screen.blit(ach_text, (col1_x + 20, y_offset + 40 + i * 25))

        # Разработчик
        dev2_title = font_large.render("💻 Разработчик собрал:", True, COLORS["dev2"])
        screen.blit(dev2_title, (col2_x, y_offset))

        for i, achievement in enumerate(self.dev2.collected):
            ach_text = font_small.render(f"• {achievement['title']}", True, COLORS["text"])
            screen.blit(ach_text, (col2_x + 20, y_offset + 40 + i * 25))

        # Совместные достижения (если есть) - ИСПРАВЛЕННАЯ ВЕРСИЯ
        # Используем заголовки для сравнения
        dev1_titles = [ach["title"] for ach in self.dev1.collected]
        dev2_titles = [ach["title"] for ach in self.dev2.collected]

        # Находим общие заголовки
        common_titles = set(dev1_titles) & set(dev2_titles)

        if common_titles:
            y_common = y_offset + max(len(self.dev1.collected), len(self.dev2.collected)) * 25 + 70

            common_title = font_large.render("Совместные достижения:", True, COLORS["primary"])
            screen.blit(common_title, (col1_x, y_common))

            for i, title in enumerate(list(common_titles)[:4]):
                ach_text = font_small.render(f"• {title}", True, COLORS["text_secondary"])
                screen.blit(ach_text, (col1_x + 20, y_common + 40 + i * 25))

        # Итоговая статистика
        total_collected = len(self.dev1.collected) + len(self.dev2.collected)
        stats_y = panel_y + panel_height - 120

        stats = [
            f"Всего достижений: {total_collected} из {len(achievements_data)}",
            f"Тимлид: {len(self.dev1.collected)} достижений",
            f"Разработчик: {len(self.dev2.collected)} достижений",
            f"Итоговый счет: {self.score}",
            f"Время прохождения: {self.timer // 60} сек."
        ]

        for i, stat in enumerate(stats):
            stat_text = font_medium.render(stat, True, COLORS["text"])
            screen.blit(stat_text, (col2_x, stats_y + i * 30))

        # Кнопка рестарта
        button_rect = pygame.Rect(WIDTH // 2 - 150, panel_y + panel_height - 50, 300, 45)
        pygame.draw.rect(screen, COLORS["primary"], button_rect, 0, 10)
        restart_text = font_medium.render("ИГРАТЬ ЕЩЕ РАЗ", True, COLORS["text"])
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2,
                                   panel_y + panel_height - 40))

        # Подсказка
        hint = font_small.render("Нажмите R для рестарта или ESC для выхода в меню",
                                 True, COLORS["text_secondary"])
        screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, panel_y + panel_height + 20))

        return button_rect

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