import pygame as pg
import pygame_menu as pgm
from pathlib import Path
import sys
from Game import Game

pg.init()

width, height, fps = 1280, 960, 60
if Path("Assets/Text/FontUndertale.ttf").is_file():
    main_font = pg.font.Font("Assets/Text/FontUndertale.ttf", 64)
else:
    main_font = pg.font.SysFont("Arial", 64)
if Path("Assets/Images/BackGround.png").is_file():
    main_bg = pgm.BaseImage("Assets/Images/BackGround.png")
else:
    main_bg = (41, 39, 54)
screen = pg.display.set_mode((width, height))
clock = pg.time.Clock()

LEAVE_GAME = pg.event.custom_type()
LEAVE_GAME_EVENT = pg.event.Event(LEAVE_GAME)
LEAVE_MINIGAME = pg.event.custom_type()
LEAVE_MINIGAME_EVENT = pg.event.Event(LEAVE_MINIGAME)
game_manager = None
game_state = 0
fade_in = [pg.Surface((width, height), pg.SRCALPHA), 0, 10, 0, True, True] # Чёрный экран, таймер для проверки,
# коэффициент скорости, таймер для паузы, чернеет ли чёрный экран?, #Начали ли игру с нуля?

if Path("Assets/Images/Icon.png").is_file():
    pg.display.set_icon(pg.image.load("Assets/Images/Icon.png"))
pg.display.set_caption("Umbry's Minigames!")

pg.mixer.init()
volume = [0.5, 0, False] # Значение громкости, когда последний раз нажали +/-, показывается ли звук на экране
volume_text = None
pg.mixer.music.set_volume(volume[0])
pg.mixer.set_num_channels(32)

def terminate() -> None:
    pg.quit()
    sys.exit()

def continue_game() -> None:
    global fade_in
    if not fade_in[1]:
        fade_in = fade_in = [pg.Surface((width, height), pg.SRCALPHA), pg.time.get_ticks(), 4, 0, True, False]

def start_game() -> None:
    global fade_in
    if not fade_in[1]:
        fade_in = fade_in = [pg.Surface((width, height), pg.SRCALPHA), pg.time.get_ticks(), 10, 0, True, True]

game_theme = pgm.Theme(background_color=(0, 0, 0), widget_font_size=70, title=False, selection_color=(255, 255, 255))
main_theme = pgm.Theme(background_color=main_bg, widget_font_size=70, title=False, selection_color=(255, 255, 255))
main_theme.widget_selection_effect = pgm.widgets.HighlightSelection(border_width=0)
if Path("Assets/Text/FontUndertale.ttf").is_file():
    main_theme.widget_font = "Assets/Text/FontUndertale.ttf"
    main_theme.title_font = "Assets/Text/FontUndertale.ttf"
game_menu = pgm.Menu('', width, height, theme=game_theme)
main_menu = pgm.Menu('', width, height, theme=main_theme)
main_menu.add.vertical_margin(220)
play = main_menu.add.button("Новая Игра", start_game, margin=(-330, 0))
main_menu.add.vertical_margin(80)
settings = main_menu.add.button("Продолжить", continue_game, margin=(-330, 0))
main_menu.add.vertical_margin(85)
exit = main_menu.add.button("Выйти", terminate, margin=(-330, 0))

main_menu.enable()
while True:
    events = pg.event.get()
    for event in events:
        if event.type == pg.QUIT:
            terminate()
        elif event.type == LEAVE_GAME:
            game_state = 0
            game_manager = None
            main_menu.reset(1)
        elif event.type == LEAVE_MINIGAME:
            game_manager.leave_minigame()
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_MINUS and 0 <= round(volume[0] - 0.05, 2):
                volume = [round(volume[0] - 0.05, 2), pg.time.get_ticks(), True]
                volume_text = main_font.render(f"Громкость: {(volume[0] * 100):.0f}%", True, (255, 255, 255))
                pg.mixer.music.set_volume(volume[0])
                if game_state:
                    game_manager.change_sfx_volume(volume[0])
            if event.key == pg.K_EQUALS and 1 >= round(volume[0] + 0.05, 2):
                volume = [round(volume[0] + 0.05, 2), pg.time.get_ticks(), True]
                volume_text = main_font.render(f"Громкость: {(volume[0] * 100):.0f}%", True, (255, 255, 255))
                pg.mixer.music.set_volume(volume[0])
                if game_state:
                    game_manager.change_sfx_volume(volume[0])
            if event.key == pg.K_0:
                if pg.mixer.music.get_volume() != 0:
                    volume = [volume[0], pg.time.get_ticks(), True]
                    volume_text = main_font.render(f"Громкость: ВЫКЛ", True, (255, 255, 255))
                    pg.mixer.music.set_volume(0)
                    if game_state:
                        game_manager.change_sfx_volume(0)
                elif volume[0] > 0:
                    volume = [volume[0], pg.time.get_ticks(), True]
                    volume_text = main_font.render(f"Громкость: {(volume[0] * 100):.0f}%", True, (255, 255, 255))
                    pg.mixer.music.set_volume(volume[0])
                    if game_state:
                        game_manager.change_sfx_volume(volume[0])

        if game_state:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                game_manager.mouse_handler(event.pos)
            if event.type == pg.KEYUP:
                game_manager.key_handler(event.key)
                if event.key == pg.K_ESCAPE:
                    if game_manager.is_in_minigame():
                        game_manager.leave_minigame()
                    else:
                        game_state = 0
                        game_manager = None
                        main_menu.reset(1)

    if main_menu.is_enabled():
        main_menu.update(events)
        main_menu.draw(screen)

    if game_state:
        # game_manager.mouse_handler(pg.mouse.get_pos(), False)
        game_manager.update(screen)

    if fade_in[1]:
        if fade_in[4]:
            if fade_in[3]:
                if pg.time.get_ticks() - fade_in[3] >= 1000:
                    fade_in[1] = pg.time.get_ticks() + 255 * fade_in[2]
                    fade_in[4] = False
                    game_state = 1
                    game_manager = Game(LEAVE_MINIGAME_EVENT)
                    game_manager.change_sfx_volume(volume[0])
                    main_menu._open(game_menu)
                screen.blit(fade_in[0], (0, 0))
            else:
                a = (pg.time.get_ticks() - fade_in[1]) // fade_in[2]
                if a >= 255:
                    fade_in[3] = pg.time.get_ticks()
                    screen.blit(fade_in[0], (0, 0))
                else:
                    fade_in[0].fill((0, 0, 0, a))
                    screen.blit(fade_in[0], (0, 0))
        else:
            a = (fade_in[1] - pg.time.get_ticks()) // fade_in[2]
            if a <= 0:
                screen.blit(fade_in[0], (0, 0))
                fade_in[1] = 0
                game_manager.is_enabled = True
                if fade_in[5]:
                    game_manager.raise_dialogue(0, 8)
            else:
                fade_in[0].fill((0, 0, 0, a))
                screen.blit(fade_in[0], (0, 0))

    if volume[2]:
        if pg.time.get_ticks() - volume[1] >= 2000:
            volume[2] = False
        pg.draw.rect(screen, (0, 0, 0), (400, 0, 435, 75))
        screen.blit(volume_text, (420, 10))
    clock.tick(fps)
    pg.display.flip()