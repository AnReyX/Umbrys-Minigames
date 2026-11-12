import pygame as pg
import json

def load_image(name):
    fullname = f"Assets/Images/{name}"
    try:
        im = pg.image.load(fullname).convert_alpha()
        return im
    except FileNotFoundError:
        placeholder = pg.Surface((50, 50))
        placeholder.fill("White")
        return placeholder

def load_sound(name):
    fullname = f"Assets/SFX/{name}"
    try:
        so = pg.mixer.Sound(fullname)
        return so
    except FileNotFoundError:
        sample_rate = 44100
        n_samples = int(sample_rate * 0.1)
        t = np.linspace(0, 0.1, n_samples, False)
        wave = np.sin(440.0 * t * 2 * np.pi)
        audio = wave * (2 ** 15 - 1) * 0.3
        audio = audio.astype(np.int16)
        stereo_audio = np.column_stack((audio, audio))

        return pg.mixer.Sound(buffer=stereo_audio)

def load_sprite_sheet(name):
    name = f"Assets/SpriteSheets/{name}"
    try:
        with open(name + ".json", encoding='utf-8') as f:
            data = json.load(f)
        im = pg.image.load(name + ".png").convert_alpha()
        return im, data
    except FileNotFoundError:
        placeholder = pg.Surface((50, 50))
        placeholder.fill("White")
        return placeholder, {"": {"width": 50, "height": 50, "x": 0, "y": 0}}