import pygame as pg

from . import *
from .widgets import Page, Text, FONT_LG
from .game import Game


class App:
    def __init__(self):
        self.win = pg.display.get_surface()
        self.clock = pg.time.Clock()

        self.main_page = Page(hidden=True)
        t = Text("bruh", pos={"center": (SCREEN_WIDTH //
                                         2, SCREEN_HEIGHT // 2)}, font=FONT_LG)
        self.main_page.add(t)
        self.main_page.hidden = True

        self.game = Game()
        self.done = False

    def run_loop(self):
        self.game.start()

        while not self.done:
            self.clock.tick(FPS)

            for e in pg.event.get():
                if e.type == pg.QUIT:
                    return self.quit()
                elif e.type == pg.KEYDOWN:
                    if e.key == pg.K_n:
                        self.game.reset()

            keys = pg.key.get_pressed()
            self.game.process_keypresses(keys)

            self.game.tick()
            self.game.render(self.win)

            if not self.main_page.hidden:
                self.main_page.render(self.win)

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
