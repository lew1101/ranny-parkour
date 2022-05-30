import pygame as pg
import yaml
from enum import Enum, Flag

from . import *
from .misc import load_image


BASE_PATH = "design_platformer/"

LEVELS = [
    BASE_PATH + "levels/world-1.yaml"
]

PLAYER_STANDING_SPRITE = load_image(BASE_PATH + "assets/icons/icon.png")
PLAYER_WALKING_SPRITES = []
PLAYER_JUMPING_SPRITES = []

COINS_SPRITES = []
BLOCK_SPRITES = [
    load_image(BASE_PATH + "assets/icons/icon.png"),
    load_image(BASE_PATH + "assets/icons/icon.png"),
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    load_image(BASE_PATH + "assets/icons/icon.png"),
]

# ==================
# Base Classes
# ==================


class Entity(pg.sprite.Sprite):
    def __init__(self, x: float, y: float, image: pg.Surface):
        self.image = image
        self.rect = image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.vx = 0.0
        self.vy = 0.0

    def apply_gravity(self, gravity: float, terminal_vel: float):
        self.vy = min(self.vy + gravity, terminal_vel)


class Block(pg.sprite.Sprite):
    class BlockType(Enum):
        GRASS = 1
        LAVA = 2
        ENDPOINT = 9

        @classmethod
        def has_value(cls, value):
            return value in cls._value2member_map_

    def __init__(self, x: int, y: int, block_type: int, image: pg.Surface):
        super().__init__()
        self.block_type = block_type
        self.image = image
        self.rect = image.get_rect()
        self.rect.x = x
        self.rect.y = y

# ==================


class Coin(Entity):
    def __init__(self, x: float, y: float, image: pg.Surface):
        super().__init__(x, y, image)
        self.val = 1


# ==================
# Level
# ==================


class Level:
    def __init__(self, data: dict):
        self.completed = False

        # player
        player_args = data.get("player", {})
        self.player_starting_pos = player_args.get("starting-pos")
        self.player_lives = player_args.get("lives")

        # world
        world_args = data.get("world", {})
        self.biome = world_args.get("biome", "default")
        self.rows = world_args.get("rows")
        self.cols = world_args.get("cols")

        self.width = self.cols * BLOCK_SIZE
        self.height = self.rows * BLOCK_SIZE
        self.size = (self.width, self.height)

        self.gravity = world_args.get("gravity", 1.0),
        self.terminal_velocity = world_args.get("terminal-velocity", 32.0)

        if (background_image := world_args.get("background-image")):
            self.background_image = pg.image.load(
                background_image).convert_alpha()
        self.background_color = world_args.get("background_color")
        self.background_repeat_x = world_args.get("background-repeat-x", True)
        self.background_fill_y = world_args.get("background-fill-x", False)

        # define layers
        self.starting_blocks = []
        self.starting_coins = []

        self.blocks = pg.sprite.Group()
        self.coins = pg.sprite.Group()

        self.active_sprites = pg.sprite.Group()
        self.inactive_sprites = pg.sprite.Group()

        block_str = world_args.get("blocks")
        print(block_str)

        if not isinstance(block_str, str):
            raise Exception("block string needs to be an instance of string")

        block_str = block_str.replace("\n", "")
        if len(block_str) != self.rows * self.cols:
            raise Exception(
                f"length of block string {len(block_str)} does not match given \
                row {self.row} and col {self.cols} attributes")

        for y in range(self.rows):
            for x in range(self.cols):
                idx = y * self.cols + x
                cell = block_str[idx]
                blit_x, blit_y = x * BLOCK_SIZE, y * BLOCK_SIZE

                # check cell is a block
                if cell.isdigit() and Block.BlockType.has_value((block_type := int(cell))):
                    self.starting_blocks.append(Block(blit_x, blit_y, block_type,
                                                      BLOCK_SPRITES[block_type]))
                # check cell is a coin
                elif cell == "C":
                    self.starting_coins.append(
                        Coin(blit_x, blit_y, COINS_SPRITES))
                else:
                    raise Exception(F"{cell} on ({x}, {y}) is invalid")

        self.blocks.add(self.starting_blocks)
        self.coins.add(self.starting_coins)

        self.inactive_sprites.add(self.blocks, self.coins)

        self.background_layer = pg.Surface(self.size, pg.SRCALPHA, COLOR_DEPTH)
        self.active_layer = pg.Surface(self.size, pg.SRCALPHA, COLOR_DEPTH)
        self.inactive_layer = pg.Surface(self.size, pg.SRCALPHA, COLOR_DEPTH)

        if self.background_color:
            self.background_layer.fill(pg.Color(*self.background_color))

        if hasattr(self, "background_image"):
            if self.background_fill_y:
                w = int(self.background_image.get_width() *
                        SCREEN_HEIGHT / self.background_image.get_height())
                self.background_image = pg.transform.scale(
                    self.background_image, (w, SCREEN_HEIGHT))

            if self.background_repeat_x:
                for x in range(0, self.width, self.background_image.get_width()):
                    self.background_layer.blit(self.background_image, (x, 0))
            else:
                self.background_layer.blit(self.background_image, (0, 0))

        for sprites in (self.active_sprites, self.inactive_sprites):
            for s in sprites:
                s.image.convert()

        self.inactive_sprites.draw(self.inactive_layer)

    @staticmethod
    def from_file(path: str):
        with open(path, 'r') as f:
            data = yaml.load(f, yaml.Loader)["data"]
            return Level(data)

    def render(self, surf: pg.Surface):
        blit_coord = (0, 0)
        surf.blits([
            (self.background_layer, blit_coord),
            (self.active_layer, blit_coord),
            (self.inactive_layer, blit_coord)
        ])

    def reset(self):
        pass


# ==================
# Player
# ==================


class Player(Entity):
    def __init__(self, x: float, y: float, image: pg.Surface):
        super().__init__(x, y, image)


# ==================
# Game
# ==================

class Game:
    class Flags(Flag):
        pass

    def __init__(self):
        self.flags = 0
        self.reset()

    def start(self):
        pass

    def tick(self):
        pass

    def render(self, surf: pg.Surface):
        self.level.render(surf)

    def reset(self):
        self.load_level(0)
        self.start()

    def load_level(self, level_index: int):
        self.curr_level = level_index
        self.level = Level.from_file(LEVELS[level_index])
