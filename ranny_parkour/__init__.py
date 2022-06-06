import pygame as pg
import sys
import os.path


def find_base_path():
    if getattr(sys, 'frozen', False):
        datadir = os.path.dirname(sys.executable)
    else:
        datadir = os.path.dirname(__file__)
    return datadir + "/"


pg.mixer.pre_init()
pg.init()

BLOCK_SIZE = 64
SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = 12*BLOCK_SIZE, 10*BLOCK_SIZE
COLOR_DEPTH = 32
FPS = 45
TITLE = "Ranny Parkour"
BASE_PATH = find_base_path()
LEVELS = [
    BASE_PATH + "levels/world-1.yaml"
]

FONT_SM = pg.font.Font(BASE_PATH + "assets/fonts/LuckiestGuy.ttf", 32)
FONT_MD = pg.font.Font(BASE_PATH + "assets/fonts/LuckiestGuy.ttf", 50)
FONT_LG = pg.font.Font(BASE_PATH + "assets/fonts/LuckiestGuy.ttf", 102)

BLACK = pg.color.Color(0, 0, 0)
WHITE = pg.color.Color(255, 255, 255)
TRANSPARENT = pg.color.Color(0, 0, 0, 0)

pg.display.set_mode(SCREEN_SIZE)
pg.display.set_caption(TITLE)
pg.display.set_icon(pg.image.load(BASE_PATH + "assets/icons/icon.png"))
