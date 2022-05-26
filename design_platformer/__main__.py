import pygame as pg

from . import *

pg.mixer.pre_init()
pg.init()


FONT_SM = pg.font.Font("assets/fonts/LuckiestGuy.ttf", 32)
FONT_MD = pg.font.Font("assets/fonts/LuckiestGuy.ttf", 64)
FONT_LG = pg.font.Font("assets/fonts/LuckiestGuy.ttf", 72)

BLACK = pg.color.Color(0, 0, 0)
WHITE = pg.color.Color(255, 255, 255)


def main():
    win = pg.display.set_mode(SCREEN_SIZE)
    pg.display.set_caption(TITLE)
    clock = pg.time.Clock()

    try:
        while True:
            for e in pg.event.get():
                if e.type == pg.QUIT:
                    raise SystemExit

            pg.display.flip()

            clock.tick(FPS)
    except SystemExit:
        pg.quit()
        raise


if __name__ == "__main__":
    main()
