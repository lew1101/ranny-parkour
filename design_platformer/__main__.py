import pygame as pg

from . import *
from .widgets import Page, Text, FONT_LG
from .game import Game


def main():
    win = pg.display.get_surface()
    clock = pg.time.Clock()

    main_page = Page(hidden=True)
    t = Text("bruh", pos={"center": (SCREEN_WIDTH //
             2, SCREEN_HEIGHT // 2)}, font=FONT_LG)
    main_page.add(t)
    main_page.hidden = True

    game = Game()
    game.start()
    # loop
    done = True

    while done:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                done = False

        keys = pg.key.get_pressed()
        game.process_keypresses(keys)

        game.tick()
        game.render(win)

        if not main_page.hidden:
            main_page.render(win)

        pg.display.flip()
        clock.tick(FPS)

    pg.quit()
    raise SystemExit


if __name__ == "__main__":
    main()
