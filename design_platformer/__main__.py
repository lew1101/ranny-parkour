import pygame as pg

from . import *
from .game import Game

pg.mixer.pre_init()
pg.init()


FONT_SM = pg.font.Font("design_platformer/assets/fonts/LuckiestGuy.ttf", 32)
FONT_MD = pg.font.Font("design_platformer/assets/fonts/LuckiestGuy.ttf", 64)
FONT_LG = pg.font.Font("design_platformer/assets/fonts/LuckiestGuy.ttf", 72)

BLACK = pg.color.Color(0, 0, 0)
WHITE = pg.color.Color(255, 255, 255)


def main():
    win = pg.display.set_mode(SCREEN_SIZE)
    pg.display.set_caption(TITLE)
    clock = pg.time.Clock()

    game = Game()
    game.start()

    # loop
    running = True

    while running:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                running = False

        game.tick()
        game.render(win)

        pg.display.flip()
        clock.tick(FPS)

    pg.quit()
    raise SystemExit


if __name__ == "__main__":
    main()
