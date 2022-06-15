import pygame as pg

from . import *

# below you will find classes have never been used
# definitely had plans that was too ambitious lol


class UIELement(pg.sprite.Sprite):
    def __init__(self, images: list[pg.Surface], pos: dict = None):
        super().__init__()
        self.images = images
        self.rects = [image.get_rect(**(pos or {})) for image in self.images]
        self.state = 0

    @property
    def image(self):
        return self.images[self.state]

    @property
    def rect(self):
        return self.rects[self.state]


class Text(pg.sprite.Sprite):
    def __init__(self, text: str, font: pg.font.Font, antialias=True, color=BLACK, *args, **kwargs) -> pg.Surface:
        super().__init__()
        self.image = font.render(text, antialias, color, *args)
        self.rect = self.image.get_rect()

    def draw(self, surf: pg.Surface):
        surf.blit(self.image, self.rect)


class Button(UIELement):
    def __init__(self, default_image: pg.Surface, on_hover_image: pg.Surface = None, pos: dict = None, ):
        self.default_image = default_image
        self.on_hover_image = on_hover_image if on_hover_image is not None else default_image
        self.images = [self.default_image, self.on_hover_image]
        super().__init__(self.images, pos)

    def check_mouse_over(self, mouse_pos):
        self.state = 1 if self.rect.collidepoint(mouse_pos) else 0


class Page:
    def __init__(self, hidden, **kwargs):
        self.__c = pg.sprite.Group()
        self.hidden = hidden
        self.background_color = kwargs.get("background_color")
        self.background_image = kwargs.get("background_image")
        if self.background_image:
            self.background_image = pg.transform.scale(
                self.background_image, SCREEN_SIZE)

    def add(self, elem: UIELement):
        self.__c.add(elem)

    def render(self, source: pg.Surface):
        if self.hidden:
            return
        if self.background_color:
            source.fill(self.background_color)
        if self.background_image:
            source.blit(self.background_image)

        return self.__c.draw(source)
