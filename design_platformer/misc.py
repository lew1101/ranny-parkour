import pygame as pg

from . import *


def load_image(path: str, width=BLOCK_SIZE, height=BLOCK_SIZE):
    image = pg.image.load(path)
    image = pg.transform.scale(image, (width, height))
    return image.convert_alpha()


class SpriteSheet:
    def __init__(self, image_path: str):
        self.sheet = pg.image.load(image_path)

    def image_at(self, rect: pg.Rect):
        image = pg.Surface(rect.size)
        image.blit(self.sheet, (0, 0), rect)
        return image.convert_alpha()

    def images_at(self, rects: list[pg.Rect]):
        return [self.image_at(rect) for rect in rects]

    def load_strip(self, rect: pg.Rect, image_count):
        rects = [rect.copy().move(rect.width*i, 0) for i in range(image_count)]
        return self.images_at(rects)
