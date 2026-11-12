import pygame as pg
import json
from pathlib import Path
from Loader import load_image, load_sound, load_sprite_sheet
from BallFight import BallFight
from Chess import Chess
from GuessChar import GuessChar
from Clicker import Clicker


class Game:
    def __init__(self, leave_minigame_event):
        self.leave_minigame_event = leave_minigame_event
        self.writing_speed, self.letter_time = 45, 0 # Скорость в мс для букв, Когда поставили последнюю букву
        self.pointer = load_image("heart.png")
        self.all_sprites = pg.sprite.Group()
        if Path("Assets/Text/FontUndertale.ttf").is_file():
            self.main_font = pg.font.Font("Assets/Text/FontUndertale.ttf", 42)
            self.big_font = pg.font.Font("Assets/Text/FontUndertale.ttf", 55)
        else:
            self.main_font = pg.font.SysFont("Arial", 42)
            self.big_font = pg.font.SysFont("Arial", 55)
        self.sfx = {"text": load_sound("Text.wav")}
        self.borders = [pg.Rect(0, 100, 1280, 60), pg.Rect(0, 160, 40, 600), pg.Rect(1240, 160, 40, 600),
                        pg.Rect(0, 760, 440, 100), pg.Rect(840, 760, 440, 100), pg.Rect(340, 860, 100, 100),
                        pg.Rect(840, 860, 100, 100)]
        self.activation_tiles = [pg.Rect(140, 560, 100, 100), pg.Rect(340, 160, 100, 100),
                                 pg.Rect(840, 160, 100, 100), pg.Rect(1040, 560, 100, 100)]
        self.games_text = {
            0: [self.big_font.render("Миниигра: Битва шариков. Нажми Z для подробностей", True, (255, 255, 255)), True],
            1: [self.big_font.render("Миниигра: Шахматные задачи. Нажми Z для подробностей", True, (255, 255, 255)),
                True],
            2: [self.big_font.render("Миниигра: Угадай персонажа. Нажми Z для подробностей", True, (255, 255, 255)),
                True],
            3: [self.big_font.render("Миниигра: Кликер. Нажми Z для подробностей", True, (255, 255, 255)), True]}

        self.talk_icons = {}
        icons = load_sprite_sheet("UmbryIcon")
        for i in icons[1].keys():
            s = pg.Surface((240, 240), pg.SRCALPHA)
            x, y = icons[1][i]["x"], icons[1][i]["y"]
            s.blit(icons[0], (0, 0), (x, y, x + 240, y + 240))
            self.talk_icons[i] = s

        self.current_icon = None
        self.is_enabled = False # True для статичного изображения на экране
        self.minigame_choice = -1 # На какой по номеру плитке выбора мини-игры мы сейчас стоим

        self.minigame_handler = None
        self.player = Player(load_sprite_sheet("Umbry"), (568, 480))
        self.all_sprites.add(self.player)

        self.is_question = None # Выбор ответа пользователя: Номер выбранной строки, Варианты ответа
        self.writing = [0, 0, 0, False, None] # Какую строку читаем, До какой читаем, По какую букву срез,
        try: # Можно нажать z?, Строка, которую читаем
            with open("Assets/Text/Texts.json", encoding='utf-8') as f:
                self.all_text = json.load(f)
        except FileNotFoundError:
            self.all_text = dict([(str(i), "Ошибка, нет файла Texts.json") for i in range(100)])

    def is_in_minigame(self):
        return self.minigame_handler is not None

    def leave_minigame(self):
        self.minigame_handler = None

    def change_sfx_volume(self, volume):
        for i in self.sfx.keys():
            self.sfx[i].set_volume(volume)

    def set_icon_and_text(self, line):
        if len(line[0]) == 1:
            if "#" in line:
                self.current_icon, self.writing[4] = line.split("#")
            else:
                self.current_icon, self.writing[4] = None, line
        else:
            if "#" in line[0]:
                self.current_icon = line[0].split("#")[0]
                self.writing[4] = [line[0].split("#")[1]]
                self.writing[4].extend(line[1:])
            else:
                self.current_icon, self.writing[4] = None, line

    def raise_dialogue(self, start, end):
        self.writing = [start, end, 0, False, None]
        self.set_icon_and_text(self.all_text[str(start)])

    def key_handler(self, key: int):
        if self.is_in_minigame():
            return
        if key == pg.K_F1:
            self.raise_dialogue(0, len(self.all_text) - 1)
        if key in (pg.K_s, pg.K_DOWN) and self.is_question is not None:
            self.is_question[0] = (self.is_question[0] + 1) % 3
        elif key in (pg.K_w, pg.K_UP) and self.is_question is not None:
            self.is_question[0] = self.is_question[0] - 1 if self.is_question[0] > 0 else 2
        if key == pg.K_z:
            if self.writing[1] and not self.writing[3]:
                return
            if self.writing[3]:
                if self.writing[0] == self.writing[1]: # Закончили диалог вообще
                    self.writing = [0, 0, 0, False, "", None]
                    if self.minigame_choice != -1:
                        self.is_question = [0, self.big_font.render("Повторить обьяснение", True, (255, 255, 255)),
                                            self.big_font.render("Начать миниигру", True, (255, 255, 255)),
                                            self.big_font.render("Выйти", True, (255, 255, 255)), pg.time.get_ticks()]
                else:
                    self.writing = [self.writing[0] + 1, self.writing[1], 0, False, "", None]
                    self.set_icon_and_text(self.all_text[str(self.writing[0])])
                    self.letter_time = pg.time.get_ticks() - self.writing_speed
            elif self.is_question is not None:
                if pg.time.get_ticks() - self.is_question[4] < 300:
                    return
                if self.is_question[0] == 0:
                    self.raise_dialogue({0: 9, 1: 21, 2: 32, 3: 41}[self.minigame_choice],
                                        {0: 20, 1: 31, 2: 40, 3: 46}[self.minigame_choice])
                elif self.is_question[0] == 1:
                    print(f"Начали миниигру под индексом {self.minigame_choice}")
                    if self.minigame_choice == 0: self.minigame_handler = BallFight(self.leave_minigame_event)
                    elif self.minigame_choice == 1: self.minigame_handler = Chess(self.leave_minigame_event)
                    elif self.minigame_choice == 2: self.minigame_handler = GuessChar(self.leave_minigame_event)
                    elif self.minigame_choice == 3: self.minigame_handler = Clicker(self.leave_minigame_event)
                self.is_question = None
            elif self.minigame_choice != -1:
                self.player.to_viewer()
                if self.games_text[self.minigame_choice][1]:
                    self.raise_dialogue({0: 9, 1: 21, 2: 32, 3: 41}[self.minigame_choice],
                                        {0: 20, 1: 31, 2: 40, 3: 46}[self.minigame_choice])
                    self.games_text[self.minigame_choice][1] = False
                else:
                    self.is_question = [0, self.big_font.render("Повторить обьяснение", True, (255, 255, 255)),
                                        self.big_font.render("Начать миниигру", True,(255, 255, 255)),
                                        self.big_font.render("Выйти", True,(255, 255, 255)), pg.time.get_ticks()]
        if key == pg.K_x and self.writing[1] and not self.writing[3]:
            self.writing[2] = len("".join(self.writing[4]))
            self.writing[3] = True
            self.letter_time = pg.time.get_ticks()

    def mouse_handler(self, pos: tuple):
        if self.is_in_minigame():
            self.minigame_handler.mouse_input(pos)

    def update(self, screen: pg.Surface):
        if self.is_in_minigame():
            self.minigame_handler.update(screen)
            return
        # Карта
        pg.draw.rect(screen, (167, 167, 167), (40, 160, 1200, 600))
        pg.draw.rect(screen, (167, 167, 167), (440, 760, 400, 200))
        for i in self.activation_tiles:
            pg.draw.rect(screen, (167, 242, 167), i)

        if self.is_enabled and not (self.writing[1] or self.is_question): # Игрок и его движение
            move = pg.math.Vector2(0, 0)
            keys = pg.key.get_pressed()
            if keys[pg.K_w] or keys[pg.K_UP]:
                move.y -= 1
                self.player.change_dir("up")
            elif keys[pg.K_s] or keys[pg.K_DOWN]:
                move.y += 1
                self.player.change_dir("down")
            if keys[pg.K_a] or keys[pg.K_LEFT]:
                move.x -= 1
                self.player.change_dir("left")
            elif keys[pg.K_d] or keys[pg.K_RIGHT]:
                move.x += 1
                self.player.change_dir("right")
            if move.length_squared() > 0:
                move = move.normalize()
            if move.x:
                self.player.move([move.x, 0])
                if self.player.hit_box.collidelist(self.borders) != -1:
                    self.player.move([-move.x, 0])
            if move.y:
                self.player.move([0, move.y])
                if self.player.hit_box.collidelist(self.borders) != -1:
                    self.player.move([0, -move.y])
            if move.length_squared() == 0 and self.player.movement_data[1]:
                self.player.reset_sprite()

        self.all_sprites.draw(screen)
        if self.is_question is not None:
            pg.draw.rect(screen, (0, 0, 0), (140, 710, 1000, 250))
            pg.draw.rect(screen, (255, 255, 255), (140, 710, 1000, 250), 5)
            for i in range(1, 4):
                screen.blit(self.is_question[i], (300, 655 + 75 * i))
            screen.blit(self.pointer, (175, 730 + 75 * self.is_question[0]))

        if self.writing[1]: # Диалоги
            if not self.writing[3]:
                if pg.time.get_ticks() >= self.letter_time + (5 * self.writing_speed if ''.join(self.writing[4])[self.writing[2] - 1:self.writing[2] + 1] in (", ", "- ", ": ") else self.writing_speed):
                    self.letter_time = pg.time.get_ticks()
                    self.writing[2] += 1
                    if ''.join(self.writing[4])[self.writing[2] - 1] != " ":
                        self.sfx["text"].play()
                if self.writing[2] >= len("".join(self.writing[4])):
                    self.writing[3] = True
            pg.draw.rect(screen, (0, 0, 0),(140, 710, 1000, 250))
            pg.draw.rect(screen, (255, 255, 255), (140, 710, 1000, 250), 5)
            if isinstance(self.writing[4], str):
                line = self.main_font.render(self.writing[4][:self.writing[2]], True, (255, 255, 255))
                screen.blit(line, (420, 750) if self.current_icon is not None else (200, 750))
            else:
                st = []
                w = self.writing[2]
                for i in self.writing[4]:
                    if w <= 0:
                        break
                    st += [i[:min(len(i), w)]]
                    w -= len(i)
                for ind, i in enumerate(st):
                    line = self.main_font.render(i, True, (255, 255, 255))
                    screen.blit(line, (420, 750 + 50 * ind) if self.current_icon is not None else (200, 750 + 50 * ind))
            if self.current_icon is not None:
                screen.blit(self.talk_icons[self.current_icon], (150, 710))
        elif self.is_question is None: # Превью миниигры
            minigame_show_index = self.player.hit_box.collidelist(self.activation_tiles)
            if minigame_show_index != -1:
                pg.draw.rect(screen, (0, 0, 0), (40, 800, 1100, 340))
                pg.draw.rect(screen, (255, 255, 255), (40, 800, 1200, 340), 5)
                screen.blit(self.games_text[minigame_show_index][0], (55, 850))
                if self.minigame_choice == -1:
                    self.minigame_choice = minigame_show_index
            elif self.minigame_choice != -1:
                self.minigame_choice = -1


class Player(pg.sprite.Sprite):
    def __init__(self, sprite_sheet, position) -> None:
        super().__init__()
        self.sprites = {"down": [], "left": [], "right": [], "up": []}
        for i in self.sprites.keys():
            for j in sprite_sheet[1][i]:
                image = pg.Surface((j["width"], j["height"]), pg.SRCALPHA)
                image.blit(sprite_sheet[0],(0, 0), (j["x"] * j["width"], j["y"] * j["height"], j["width"], j["height"]))
                self.sprites[i] += [image]
        self.image = self.sprites["down"][0]
        self.dir = "down"
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = position
        self.hit_box = pg.Rect(self.rect.left + 22, self.rect.bottom - 50, 100, 50)
        self.pos = pg.math.Vector2(*position)
        self.speed = 5
        self.movement_data = [0, 0, 150] # Последнее изменение, индекс спрайта, скорость изменения

    def move(self, base):
        direction = pg.math.Vector2(base[0], base[1])
        self.pos += direction * self.speed
        self.rect.topleft = (round(self.pos.x), round(self.pos.y))
        self.hit_box.topleft = (round(self.pos.x + 22), round(self.pos.y + 238))
        if pg.time.get_ticks() - self.movement_data[0] >= self.movement_data[2]:
            self.movement_data[0] = pg.time.get_ticks()
            self.movement_data[1] = (self.movement_data[1] + 1) % 4
            self.image = self.sprites[self.dir][self.movement_data[1]]

    def change_dir(self, new_dir):
        self.dir = new_dir

    def to_viewer(self):
        self.dir, self.movement_data[0], self.movement_data[1] = "down", pg.time.get_ticks(), 0
        self.image = self.sprites["down"][0]

    def reset_sprite(self):
        self.image = self.sprites[self.dir][0]
        self.movement_data[1] = 0