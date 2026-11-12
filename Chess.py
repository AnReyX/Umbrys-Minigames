import pygame as pg
import json
from pathlib import Path
from random import randint
from Loader import load_sprite_sheet, load_image


class Chess:
    def __init__(self, leave_event):
        self.leave_event = leave_event
        if Path("Assets/Text/FontUndertale.ttf").is_file():
            self.main_font = pg.font.Font("Assets/Text/FontUndertale.ttf", 55)
            self.small_font = pg.font.Font("Assets/Text/FontUndertale.ttf", 25)
        else:
            self.main_font = pg.font.SysFont("Arial", 55)
            self.small_font = pg.font.Font("Arial", 25)
        self.colors = [(184, 136, 103), (242, 222, 193), (255, 142, 142), (255, 255, 142)]
        self.problem_params = [0, str(randint(0, 4))]  # Сложность (0-изи, 1-нормал, 2-хард), айди задачи
        self.board = [[[pg.Rect((20 + i * 85, 260 + j * 85, 85, 85)), []] for i in range(8)] for j in range(8)]
        self.active = []
        self.tip = []
        self.mistake = [0, 0, 0] # Таймер на ошибку, номер сообщения ошибки, сколько всего ошибок за задачу
        self.answered = False
        self.board_active = False
        self.numeration = [(self.small_font.render(i, True, (255, 255, 255)),
                            self.small_font.render(chr(96 + int(i)), True, (255, 255, 255))) for i in "12345678"]
        self.talk_icons, self.pieces_icons, self.current_icon = {}, {}, "normal"
        icons = load_sprite_sheet("UmbryIcon")
        for i in icons[1].keys():
            s = pg.Surface((240, 240), pg.SRCALPHA)
            x, y = icons[1][i]["x"], icons[1][i]["y"]
            s.blit(icons[0], (0, 0), (x, y, x + 240, y + 240))
            self.talk_icons[i] = s
        pieces = load_sprite_sheet("Pieces")
        for j in pieces[1].keys():
            s = pg.Surface((85, 85), pg.SRCALPHA)
            x, y = pieces[1][j]["x"], pieces[1][j]["y"]
            s.blit(pieces[0], (0, 0), (x, y, x + 85, y + 85))
            self.pieces_icons[j] = s
        self.problem = self.load_problems(0)
        self.arrange_pieces(self.problem[self.problem_params[1]]["pieces"])
        self.UI = {"text": [[[self.main_font.render(f"Задачка {i + 1}.", True, (255, 255, 255)),
                              self.main_font.render(f"Уровень: {("Легко", "Средне", "Сложно")[i]}", True, (255, 255, 255))] for i in range(3)],
                            [self.main_font.render(i, True, (255, 255, 255)) for i in
                             self.problem[self.problem_params[1]]["desc_0"]],
                            [self.main_font.render(i, True, (255, 255, 255)) for i in
                             self.problem[self.problem_params[1]]["desc_1"]],
                            [self.main_font.render(i, True, (255, 255, 255)) for i in
                             ("Нет, не правильно...", "Хмм, всё же ответ другой...", "Ничего, попробуй ещё раз.")],
                            self.main_font.render("Ты прошёл все задачи, поздравляю!!", True, (255, 255, 255))],
                   "button": [Button((880, 760, 300, 100), self.main_font.render("К задаче!", True, (255, 255, 255))),
                              Button((100, 760, 300, 100), self.main_font.render("Выйти", True, (255, 255, 255))),
                              Button((850, 840, 300, 100), self.main_font.render("Далее", True, (255, 255, 255))),
                              Button((850, 558, 300, 100), self.main_font.render("Подсказка", True, (255, 255, 255)))]}
        self.UI["text"][0][2] += [self.main_font.render(("Внимание! Эти задачки реально сложные.", "Поэтому можно выйти сейчас, если не хочешь решать.",
                                                         "Миниигра всё равно засчитается :3")[i], True, (255, 255, 255)) for i in range(3)]
        for i in range(2, 4):
            self.UI["button"][i].switch()

    def load_problems(self, difficulty):
        if Path(f"Assets/ChessProblems/{difficulty}.json").is_file():
            with open(f"Assets/ChessProblems/{difficulty}.json", encoding='utf-8') as f:
                return json.load(f)
        return self.main_font.render("Ошибка, файл с задачами не найден, переустанавливай игру :с",True, (242, 242, 242))

    def arrange_pieces(self, pieces):
        self.active = []
        for i in pieces:
            data = i.split()
            piece, y, x = data[0][:2], int(data[0][2]), int(data[0][3])
            self.board[y][x][1].append(self.pieces_icons[data[0][:2]])
            if len(data) > 0:
                data = [(int(i[0]), int(i[1])) for i in data[1:]]
                self.board[y][x][1].extend(data)

    def clear_board(self):
        for i in self.board:
            for j in i:
                j[1] = []

    def update(self, screen):
        pg.draw.rect(screen, (56, 52, 52), (0, 0, 1280, 960))
        if not isinstance(self.problem, dict):
            screen.blit(self.problem, (100, 480))
            return
        if self.board_active:
            pg.draw.rect(screen, (0, 0, 0), (20, 0, 1240, 260))
            pg.draw.rect(screen, (255, 255, 255), (20, 0, 1240, 260), 5)
            if pg.time.get_ticks() - self.mistake[0] > 3000:
                for ind, i in enumerate(self.UI["text"][2 if self.answered else 1]):
                    screen.blit(i, (280, 50 + ind * 50))
                if self.current_icon == "annoyed":
                    self.current_icon = "normal"
            else:
                screen.blit(self.UI["text"][3][self.mistake[1]], (280, 50))
            color_index = 1
            for y in range(8):
                for x in range(8):
                    c = self.board[y][x]
                    pg.draw.rect(screen, self.colors[2 if self.active == [y, x] else color_index], c[0])
                    if self.tip == [y, x] and self.active != [y, x]:
                        pg.draw.rect(screen, self.colors[3], c[0])
                    if c[1]:
                        screen.blit(c[1][0], (c[0].x, c[0].y))
                    if self.active and (y, x) in self.board[self.active[0]][self.active[1]][1][1:]:
                        pg.draw.circle(screen, (135, 135, 135), c[0].center, 10)
                    color_index = 1 - color_index
                screen.blit(self.numeration[y][1], ((85 + 85 * y) if self.problem[self.problem_params[1]]["move"] == "W" else (680 - 85 * y), 935))
                screen.blit(self.numeration[y][0], (705, (310 + 85 * y) if self.problem[self.problem_params[1]]["move"] == "B" else (905 - 85 * y)))
                color_index = 1 - color_index
            screen.blit(self.talk_icons[self.current_icon], (20, 0))
        else:
            if self.problem_params is not None:
                for ind, i in enumerate(self.UI["text"][0][self.problem_params[0]]):
                    screen.blit(i, (640 - i.get_width() // 2, 100 + ind * 50))
            else:
                screen.blit(self.UI["text"][4], (280, 100))
        for i in self.UI["button"]:
            i.update(screen)


    def mouse_input(self, pos):
        if self.UI["button"][0].work(pos):
            self.board_active = True
            self.current_icon = "normal"
            for i in self.UI["button"]:
                i.switch()
            self.UI["button"][2].switch()
            return
        elif self.UI["button"][1].work(pos):
            pg.event.post(self.leave_event)
            return
        elif self.UI["button"][2].work(pos):
            self.board_active = False
            for i in self.UI["button"]:
                i.switch()
            if self.problem_params[0] + 1 == 3:
                self.problem_params = None
                self.UI["button"][0].switch()
            else:
                self.problem_params = [self.problem_params[0] + 1, str(randint(0, 4))]
                self.problem = self.load_problems(self.problem_params[0])
                self.clear_board()
                self.arrange_pieces(self.problem[self.problem_params[1]]["pieces"])
                self.UI["text"][1] = [self.main_font.render(i, True, (255, 255, 255)) for i in
                             self.problem[self.problem_params[1]]["desc_0"]]
                self.UI["text"][2] = [self.main_font.render(i, True, (255, 255, 255)) for i in
                                      self.problem[self.problem_params[1]]["desc_1"]]
                self.answered = False
        elif self.UI["button"][3].work(pos):
            self.tip = [int(i) for i in self.problem[self.problem_params[1]]["answer"][:2]]
        if self.board_active and not self.answered:
            for i in range(8):
                for j in range(8):
                    if self.board[i][j][0].collidepoint(pos):
                        if len(self.board[i][j][1]) > 1:
                            self.active = [i, j]
                            return
                        elif self.active and (i, j) in self.board[self.active[0]][self.active[1]][1][1:]:
                            answer = f"{self.active[0]}{self.active[1]}{i}{j}"
                            if answer == self.problem[self.problem_params[1]]["answer"]:
                                self.answered = True
                                self.board[i][j][1] = self.board[self.active[0]][self.active[1]][1]
                                self.board[self.active[0]][self.active[1]][1] = []
                                self.mistake = [0, 0, self.mistake[2]]
                                self.tip = []
                                self.UI["button"][2].switch()
                                self.current_icon = ("glad", "happy", "surprised")[self.problem_params[0]]
                            else:
                                self.mistake = [pg.time.get_ticks(), randint(0, 2), self.mistake[2]]
                                self.current_icon = "annoyed"
                            self.active = []
                            return
            self.active = []


class Button:
    def __init__(self, dims, text):
        self.dims = dims
        self.text = text
        self.rect = self.text.get_rect()
        self.rect.center = (self.dims[0] + self.dims[2] // 2, self.dims[1] + self.dims[3] // 2)
        self.is_activated = True

    def update(self, screen):
        if not self.is_activated:
            return
        else:
            pg.draw.rect(screen, (0, 0, 0), self.dims)
            pg.draw.rect(screen, (255, 255, 255), self.dims, 5)
            screen.blit(self.text, self.rect.topleft)

    def switch(self):
        self.is_activated = not self.is_activated

    def work(self, pos):
        if not self.is_activated:
            return False
        if self.dims[0] < pos[0] < self.dims[0] + self.dims[2] and self.dims[1] < pos[1] < self.dims[1] + self.dims[3]:
            return True
        return False