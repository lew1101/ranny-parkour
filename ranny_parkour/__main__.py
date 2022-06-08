import pygame as pg

from . import *
from .widgets import Page, Text, FONT_LG
from .game import Game


class App:
    def __init__(self):
        self.win = pg.display.get_surface()
        self.clock = pg.time.Clock()

        self.game = Game()
        self.done = False

    def run_loop(self):
        self.game.load_level(0)
        self.game.start()

        while not self.done:
            self.clock.tick(FPS)

            for e in pg.event.get():
                if e.type == pg.QUIT:
                    return self.quit()
                elif e.type == pg.KEYDOWN:
                    if e.key == pg.K_n:
                        self.game.reset()
                    elif e.key in range(pg.K_1, pg.K_9):
                        level_index = e.key - pg.K_1  # hack
                        self.game.load_level(level_index)

            keys = pg.key.get_pressed()
            self.game.process_keypresses(keys)

            self.game.tick()
            self.game.render(self.win)

            pg.display.flip()

    def quit(self):
        self.done = True
        pg.quit()
        raise SystemExit


def main():
    app = App()
    app.run_loop()


if __name__ == "__main__":
    main()
