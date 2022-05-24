import pygame as pg

pg.mixer.pre_init()
pg.init()

TITLE = "GAME"
SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = 560, 480
FPS = 60

FONT_SM = pg.font.Font("assets/fonts/LuckiestGuy.ttf", 32)
FONT_MD = pg.font.Font("assets/fonts/LuckiestGuy.ttf", 64)
FONT_LG = pg.font.Font("assets/fonts/LuckiestGuy.ttf", 72)

BLACK = pg.color.Color(0, 0, 0)
WHITE = pg.color.Color(255, 255, 255)


class Entity(pg.sprite.Sprite):
    def __init__(self, x: float, y: float, image: pg.Surface):
        super().__init__()

        self.image = image
        self.rect = image.get_rect()
        self.x = x
        self.y = y

        self.vx = 0.0
        self.vy = 0.0


def main():
    win = pg.display.set_mode(SCREEN_SIZE)
    pg.display.set_caption(TITLE)
    clock = pg.time.Clock()

    try:
        while True:
            for e in pg.event.get():
                if e.type == pg.QUIT:
                    raise SystemExit

            clock.tick(FPS)

            pg.display.flip()
    except SystemExit:
        pg.quit()
        raise


if __name__ == "__main__":
    main()
