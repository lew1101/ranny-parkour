import pygame as pg

pg.mixer.pre_init()
pg.init()

BLOCK_SIZE = 64
SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = 12*BLOCK_SIZE, 10*BLOCK_SIZE
COLOR_DEPTH = 32
FPS = 60
TITLE = "Ranny Parkour"
BASE_PATH = "ranny_parkour/"
LEVELS = [
    BASE_PATH + "levels/world-1.yaml"
]

FONT_SM = pg.font.Font(BASE_PATH + "assets/fonts/LuckiestGuy.ttf", 32)
FONT_MD = pg.font.Font(BASE_PATH + "assets/fonts/LuckiestGuy.ttf", 64)
FONT_LG = pg.font.Font(BASE_PATH + "assets/fonts/LuckiestGuy.ttf", 72)

BLACK = pg.color.Color(0, 0, 0)
WHITE = pg.color.Color(255, 255, 255)
TRANSPARENT = pg.color.Color(0, 0, 0, 0)

pg.display.set_mode(SCREEN_SIZE)
pg.display.set_caption(TITLE)
pg.display.set_icon(pg.image.load(BASE_PATH + "assets/icons/icon.png"))
