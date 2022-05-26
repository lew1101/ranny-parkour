import pygame.image
import pygame.transform

from .game import BLOCK_SIZE


def load_image(path: str, width: BLOCK_SIZE, height: BLOCK_SIZE):
    image = pygame.image.load(path)
    image = pygame.transform.scale(image, (width, height))
    return
