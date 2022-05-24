import pygame as pg
import yaml

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

LEVELS = [
    "levels/world-1.yaml"
]


class Level:
    def __init__(self, **kwargs):
        pass

    @staticmethod
    def from_file(path: str):
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
            return Level(**data)


class Entity(pg.sprite.Sprite):
    def __init__(self, x: float, y: float, image: pg.Surface):
        super().__init__()

        self.image = image
        self.rect = image.get_rect()
        self.x = x
        self.y = y

        self.vx = 0.0
        self.vy = 0.0

    def apply_gravity(self, gravity: float, terminal_vel: float):
        self.vy = min(self.vy + gravity, terminal_vel)


class Block(pg.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.rect = image.get_rect()
        self.x = x
        self.y = y


class Player(Entity):
    def __init__(self, x: float, y: float, image: pg.Surface):
        super().__init__(x, y, image)


class Game(pg.Surface):
    class Flags:
        pass

    def __init__(self, *args):
        super.__init__(*args)
        self.flags = 0
        self.reset()

    def start(self):
        pass

    def reset(self):
        self.player = Player()
        self.curr_level = 0
        self.start()

    def tick(self):
        pass


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
