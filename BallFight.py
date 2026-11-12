import pygame as pg
from Loader import load_image
from pathlib import Path
from random import random, choice, randint
from math import radians, sin, cos

class BallFight:
    def __init__(self, leave_event):
        self.leave_event = leave_event
        if Path("Assets/Text/FontUndertale.ttf").is_file():
            self.main_font = pg.font.Font("Assets/Text/FontUndertale.ttf", 55)
            self.small_font = pg.font.Font("Assets/Text/FontUndertale.ttf", 38)
        else:
            self.main_font = pg.font.SysFont("Arial", 55)
            self.small_font = pg.font.Font("Arial", 30)
        self.has_started = False
        self.player_stats = [["Урон х2: ", 0, 100], ["Размер меча х1.5: ", 0, 270], ["Скорость меча х3: ", 0, 570], ["Размер шарика х0.5: ", 0, 875]]
        self.active_buffs = self.small_font.render("Активные баффы:", True, (255, 255, 255))
        self.can_direct = pg.time.get_ticks() - 10000
        self.direct_text = ["Чтобы начать, наведись и нажми ЛКМ!", None]
        self.direct_text[1] = self.main_font.render(self.direct_text[0], True, (255, 255, 255))
        self.verdict = None
        self.player_w = pg.sprite.Group()
        self.enemy_w = pg.sprite.Group()
        self.buff_group = pg.sprite.Group()
        self.buff_time = pg.time.get_ticks()
        self.player = PlayerFighter(((0, 0, 255), (0, 0, 100)), (235, 435), ((155, 1125), (155, 805)))
        self.enemy = Fighter(((255, 0, 0), (100, 0, 0)), (950, 435), ((155, 1125), (155, 805)))
        self.player.set_display_hp(self.main_font.render("100", True, (255, 255, 255)))
        self.enemy.set_display_hp(self.main_font.render("100", True, (255, 255, 255)))
        self.player_w.add(self.player.weapon)
        self.enemy_w.add(self.enemy.weapon)

    def mouse_input(self, pos):
        if not self.has_started:
            self.has_started = True
            self.player.change_direction(None, pos)
        elif pg.time.get_ticks() - self.can_direct >= 10000 and self.player is not None and self.enemy is not None:
            self.player.change_direction(None, pos)
            self.can_direct = pg.time.get_ticks()

    def update(self, screen):
        pg.draw.rect(screen, (242, 242, 242), (150, 150, 980, 660), 5)
        if self.enemy is None:
            self.player_w.draw(screen)
            screen.blit(self.player.image, self.player.rect)
            screen.blit(self.verdict, (150, 850))
            self.player.move()
            return
        elif self.player is None:
            self.enemy_w.draw(screen)
            screen.blit(self.enemy.image, self.enemy.rect)
            screen.blit(self.verdict, (150, 850))
            self.enemy.move()
            return
        if not self.has_started:
            screen.blit(self.player.image, self.player.rect)
            screen.blit(self.enemy.image, self.enemy.rect)
            screen.blit(self.direct_text[1], (150, 50))
            return

        if pg.time.get_ticks() - self.can_direct >= 10000 and self.direct_text[0] != "Н":
            self.direct_text[0] = "Наведись и нажми ЛКМ, чтобы направить шарик!"
            self.direct_text[1] = self.main_font.render(self.direct_text[0], True, (255, 255, 255))
        elif pg.time.get_ticks() - self.can_direct < 10000:
            i = (9999 - pg.time.get_ticks() + self.can_direct) // 1000 + 1
            if self.direct_text[-1] != str(i)[-1]:
                self.direct_text[0] = f"Секунд до возможности направить шарик: {i}"
                self.direct_text[1] = self.main_font.render(self.direct_text[0], True, (255, 255, 255))
        screen.blit(self.direct_text[1], (150, 50))
        for i in range(4):
            t = self.player_stats[i]
            if t[1] != self.player.buffs[i][0]:
                t[1] = self.player.buffs[i][0]
            if t[1] > 0:
                screen.blit(self.small_font.render(t[0] + str(t[1]), True, (255, 255, 255)), (t[2], 870))
        if any([i[1] for i in self.player_stats]):
            screen.blit(self.active_buffs, (100, 830))
        if pg.time.get_ticks() - self.buff_time >= 10000:
            self.buff_time = pg.time.get_ticks()
            self.spawn_buff()
        self.buff_group.draw(screen)
        self.player_w.draw(screen)
        self.enemy_w.draw(screen)
        screen.blit(self.player.image, self.player.rect)
        screen.blit(self.enemy.image, self.enemy.rect)
        pos_p, pos_e = pg.Vector2(self.player.rect.center), pg.Vector2(self.enemy.rect.center)
        if (pos_p - pos_e).length() <= 100:
            self.reflect(pos_p, pos_e)
        if (pg.sprite.spritecollide(self.player.weapon, self.enemy_w, False, pg.sprite.collide_mask) and
                pg.time.get_ticks() - self.player.w_sf >= 500):
            self.player.w_sf = pg.time.get_ticks()
            self.player.weapon.rotation_speed *= -1
            self.enemy.weapon.rotation_speed *= -1
        if pg.sprite.spritecollide(self.player, self.enemy_w, False, pg.sprite.collide_mask):
            if self.enemy.weapon.contact == 0 and pg.time.get_ticks() - self.enemy.w_sf >= 1000:
                self.player.change_direction((pos_e, self.enemy.weapon.angle))
                self.enemy.w_sf = pg.time.get_ticks()
                self.enemy.weapon.rotation_speed *= -1
            elif self.enemy.weapon.contact > 0 and self.player.hurt_timer(True):
                self.player.hurt(self.enemy.weapon.contact * (2 if self.enemy.buffs[0][0] else 1))
                if self.player.hp <= 0:
                    self.player = None
                    self.enemy.reset()
                    self.verdict = self.main_font.render("(Выход на Escape) Вы проиграли :с",
                                                         True, (255, 255, 255))
                    return
                self.player.change_direction((pos_e, self.enemy.weapon.angle))
                self.enemy.weapon.rotation_speed *= -1
                self.player.speed, self.enemy.speed = 0, 0
        elif pg.sprite.spritecollide(self.enemy, self.player_w, False, pg.sprite.collide_mask):
            if self.player.weapon.contact == 0 and pg.time.get_ticks() - self.player.w_sf >= 1000:
                self.enemy.change_direction((pos_p, self.player.weapon.angle))
                self.player.w_sf = pg.time.get_ticks()
                self.player.weapon.rotation_speed *= -1
            elif self.player.weapon.contact > 0 and self.enemy.hurt_timer(True):
                self.enemy.hurt(self.player.weapon.contact * (2 if self.player.buffs[0][0] else 1))
                if self.enemy.hp <= 0:
                    self.enemy = None
                    self.player.reset()
                    self.verdict = self.main_font.render("(Выход на Escape) Вы победили! :3",
                                                         True, (255, 255, 255))
                    return
                self.enemy.change_direction((pos_p, self.player.weapon.angle))
                self.player.weapon.rotation_speed *= -1
                self.player.speed, self.enemy.speed = 0, 0
        if self.player.hurt_timer(False) and self.player.color_index or self.enemy.hurt_timer(False) and self.enemy.color_index:
            self.player.speed, self.enemy.speed = 7, 7
        if self.player.hurt_timer(True) and self.player.color_index:
            self.player.change_color()
            self.player.set_display_hp(self.main_font.render(f"{self.player.hp}", True, (255, 255, 255)))
        if self.enemy.hurt_timer(True) and self.enemy.color_index:
            self.enemy.change_color()
            self.enemy.set_display_hp(self.main_font.render(f"{self.enemy.hp}", True, (255, 255, 255)))
        for i in pg.sprite.spritecollide(self.player, self.buff_group, True):
            if i.type == 4:
                self.player.hp += 10
                self.player.set_display_hp(self.main_font.render(f"{self.player.hp}", True, (255, 255, 255)))
            else:
                self.player.manage_buffs(i.type)
        for i in pg.sprite.spritecollide(self.enemy, self.buff_group, True):
            if i.type == 4:
                self.enemy.hp += 10
                self.enemy.set_display_hp(self.main_font.render(f"{self.enemy.hp}", True, (255, 255, 255)))
            else:
                self.enemy.manage_buffs(i.type)
        self.player.manage_buffs()
        self.player.move()
        self.enemy.manage_buffs()
        self.enemy.move()

    def spawn_buff(self):
        rand_type = randint(0, 5)
        if rand_type == 5:
            return
        buff = Buff(rand_type, (randint(180, 1100), randint(180, 780)))
        self.buff_group.add(buff)


    def reflect(self, pos_p, pos_e):
        normal = pos_p - pos_e
        distance = normal.length()
        normal.normalize_ip()
        speed = self.enemy.direction.dot(normal) - self.player.direction.dot(normal)
        if speed > 0:
            self.player.direction += speed * normal
            self.player.direction.normalize_ip()
            self.enemy.direction -= speed * normal
            self.enemy.direction.normalize_ip()
        if distance < 100:
            move = normal * ((100 - distance) / 2)
            if 155 <= (self.player.pos + move).x <= 1125 and 155 <= (self.player.pos + move).y <= 805:
                self.player.pos += move
                self.player.rect.topleft = (round(self.player.pos.x), round(self.player.pos.y))
            if 155 <= (self.enemy.pos + move).x <= 1125 and 155 <= (self.enemy.pos + move).y <= 805:
                self.enemy.pos -= move
                self.enemy.rect.topleft = (round(self.enemy.pos.x), round(self.enemy.pos.y))


class Fighter:
    def __init__(self, colors, position, borders):
        self.speed, self.hp, self.sf, self.w_sf, self.not_move_time, self.size_flag = 7, 100, 0, 0, 0, False
        self.buffs = dict([(i, [0, 0]) for i in range(4)])
        self.display_hp = None
        self.image = pg.Surface((100, 100), pg.SRCALPHA)
        self.colors = colors
        self.color_index = 0
        pg.draw.circle(self.image, colors[0], (50, 50), 50)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = position
        self.start = position
        self.pos = pg.math.Vector2(*position)
        self.borders = borders
        self.direction = pg.math.Vector2((random() * choice((-1, 1)), random() * choice((-1, 1)))).normalize()
        self.weapon = Sword((self.rect.x, self.rect.y - 200))

    def move(self):
        if self.speed == 0:
            return
        if (self.rect.left + 10 <= self.borders[0][0] or self.rect.right - 10 >= self.borders[0][1] or
            self.rect.top + 10 <= self.borders[1][0] or self.rect.bottom - 10 >= self.borders[1][1]):
            self.pos = pg.math.Vector2(*self.start)
            self.rect.topleft = (self.pos.x, self.pos.y)
        if self.rect.left <= self.borders[0][0] or self.rect.right >= self.borders[0][1]:
            self.change_direction(0)
        elif self.rect.top <= self.borders[1][0] or self.rect.bottom >= self.borders[1][1]:
            self.change_direction(1)
        self.pos += self.direction * self.speed
        self.rect.topleft = (round(self.pos.x), round(self.pos.y))
        self.weapon.move(pg.Vector2(self.rect.center), 3 if self.buffs[2][0] else 1)

    def reset(self):
        self.image = pg.Surface((100, 100), pg.SRCALPHA)
        pg.draw.circle(self.image, self.colors[0], (50, 50), 50)
        self.weapon.size_flag = False
        self.image.blit(self.display_hp, (13, 20))
        self.rect = self.image.get_rect(center=self.rect.center)
        self.buffs = dict([(i, [0, 0]) for i in range(4)])

    def change_direction(self, new_dir):
        if new_dir == 1:
            self.pos[1] -= 5 if self.direction.y > 0 else -5
            self.direction.y *= -1
        elif new_dir == 0:
            self.pos[0] -= 5 if self.direction.x > 0 else -5
            self.direction.x *= -1
        else:
            dir_vector = (pg.Vector2(self.rect.center) - new_dir[0]).normalize()
            dir_sword = pg.math.Vector2(-sin(radians(new_dir[1])), cos(radians(new_dir[1])))
            final_dir = (dir_vector * 0.7) + (dir_sword * 0.3)
            if final_dir.length() == 0:
                final_dir = dir_vector
            self.direction = final_dir.normalize()

    def set_display_hp(self, value):
        self.display_hp = value
        if not self.color_index:
            if self.size_flag:
                pg.draw.circle(self.image, self.colors[self.color_index], (25, 25), 25)
                self.image.blit(self.display_hp, (0, 7))
            else:
                pg.draw.circle(self.image, self.colors[self.color_index], (50, 50), 50)
                self.image.blit(self.display_hp, (13, 20))

    def hurt(self, damage):
        self.sf, self.not_move_time = pg.time.get_ticks(), pg.time.get_ticks()
        self.hp -= damage
        self.change_color()


    def hurt_timer(self, return_sf):
        if return_sf:
            return pg.time.get_ticks() - self.sf >= 1500
        else:
            return pg.time.get_ticks() - self.not_move_time >= 200

    def change_color(self):
        self.color_index = 1 - self.color_index
        if self.size_flag:
            self.image = pg.Surface((50, 50), pg.SRCALPHA)
            pg.draw.circle(self.image, self.colors[self.color_index], (25, 25), 25)
        else:
            self.image = pg.Surface((100, 100), pg.SRCALPHA)
            pg.draw.circle(self.image, self.colors[self.color_index], (50, 50), 50)

    def resize(self):
        if self.size_flag:
            self.image = pg.Surface((50, 50), pg.SRCALPHA)
            pg.draw.circle(self.image, self.colors[self.color_index], (25, 25), 25)
            self.image.blit(self.display_hp, (0, 7))
            self.rect = self.image.get_rect(center=self.rect.center)
        else:
            self.image = pg.Surface((100, 100), pg.SRCALPHA)
            pg.draw.circle(self.image, self.colors[self.color_index], (50, 50), 50)
            self.image.blit(self.display_hp, (13, 20))
            self.rect = self.image.get_rect(center=self.rect.center)

    def manage_buffs(self, apply=None):
        if apply is not None:
            if apply == 1 and not self.buffs[1][0]:
                self.weapon.size_flag = True
            elif apply == 3 and not self.buffs[3][0]:
                self.size_flag = True
                self.resize()
            self.buffs[apply] = [15, pg.time.get_ticks()]
        else:
            for i in range(4):
                if self.buffs[i][0] > 0 and pg.time.get_ticks() - self.buffs[i][1] >= 1000:
                    self.buffs[i] = [self.buffs[i][0] - 1, pg.time.get_ticks()]
            if not self.buffs[1][0] and self.weapon.size_flag:
                self.weapon.size_flag = False
            if not self.buffs[3][0] and self.size_flag:
                self.size_flag = False
                self.resize()

class PlayerFighter(Fighter):
    def __init__(self, colors, position, borders):
        super().__init__(colors, position, borders)
        pg.draw.circle(self.image, (255, 255, 255), (50, 50), 50, 3)

    def reset(self):
        super().reset()
        pg.draw.circle(self.image, (255, 255, 255), (50, 50), 50, 3)

    def set_display_hp(self, value):
        super().set_display_hp(value)
        if not self.color_index:
            if self.size_flag:
                pg.draw.circle(self.image, (255, 255, 255), (25, 25), 25, 1)
            else:
                pg.draw.circle(self.image, (255, 255, 255), (50, 50), 50, 3)

    def change_color(self):
        super().change_color()
        if self.size_flag:
            pg.draw.circle(self.image, (255, 255, 255), (25, 25), 25, 1)
        else:
            pg.draw.circle(self.image, (255, 255, 255), (50, 50), 50, 3)

    def resize(self):
        super().resize()
        if self.size_flag:
            pg.draw.circle(self.image, (255, 255, 255), (25, 25), 25, 1)
        else:
            pg.draw.circle(self.image, (255, 255, 255), (50, 50), 50, 3)


    def change_direction(self, new_dir, mouse_click=None):
        if mouse_click is not None:
            self.direction = pg.math.Vector2(mouse_click[0] - self.rect.center[0], mouse_click[1] - self.rect.center[1])
            self.direction.normalize_ip()
            return
        super().change_direction(new_dir)

class Sword(pg.sprite.Sprite):
    def __init__(self, pos: tuple[int, int]) -> None:
        super().__init__()
        sprite = load_image("sword.png")
        self.original_image = sprite
        self.original_image_big = pg.transform.scale(self.original_image, (int(sprite.get_width() * 1.5), int(sprite.get_height() * 1.5)))
        self.image = sprite
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
        self.size_flag = False
        self.angle = 0
        self.rotation_speed = 2
        self.offset = pg.Vector2(0, -100)
        self.big_offset = pg.Vector2(0, -200)
        self.contact = 5

    def move(self, pivot: pg.Vector2, k: int) -> None:
        self.angle = (self.angle + self.rotation_speed * k) % 360
        if self.size_flag:
            rotated_offset = self.big_offset.rotate(-self.angle)
            self.rect.center = pivot + rotated_offset
            self.image = pg.transform.rotate(self.original_image_big, self.angle)
            self.rect = self.image.get_rect(center=self.rect.center)
        else:
            rotated_offset = self.offset.rotate(-self.angle)
            self.rect.center = pivot + rotated_offset
            self.image = pg.transform.rotate(self.original_image, self.angle)
            self.rect = self.image.get_rect(center=self.rect.center)

class Buff(pg.sprite.Sprite):
    def __init__(self, typ, position):
        super().__init__() # 0 - +5 урона на 15 сек, 1 - Оружие в 1.5 раза больше на 15 сек, 2 - Оружие вращается в 3
        self.type = typ # раза быстрее на 15 сек, 3 - Ты в 2 раза меньше на 15 сек, 4 - Хил 10 хп
        self.image = pg.Surface((50, 50), pg.SRCALPHA)
        colors = [(255, 100, 100), (255, 255, 0), (200, 200, 200), (0, 255, 255), (0, 255, 0)]
        pg.draw.circle(self.image, colors[typ], (25, 25), 25)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = position