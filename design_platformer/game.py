import pygame as pg
import yaml
from enum import Flag

from . import *

BLOCK_SIZE = 64
LEVELS = [
    "levels/world-1.yaml"
]

PLAYER_STANDING_SPRITE = ""
PLAYER_WALKING_SPRITES = []
PLAYER_JUMPING_SPRITES = []

COINS_SPRITES = []
BLOCK_SPRITES = {

}


# ==================
# Base Classes
# ==================

class Entity(pg.sprite.Sprite):
    def __init__(self, x: float, y: float, image: pg.Surface):
        self.image = image
        self.rect = image.get_rect()
        self.x = x
        self.y = y

        self.vx = 0.0
        self.vy = 0.0

    def apply_gravity(self, gravity: float, terminal_vel: float):
        self.vy = min(self.vy + gravity, terminal_vel)


class Block(pg.sprite.Sprite):
    class BlockType(Flag):
        AIR = 0
        GRASS = 1
        LAVA = 2
        ENDPOINT = 9

    def __init__(self, x: int, y: int, block_type: int, image: pg.Surface):
        self.block_type = block_type
        self.image = image
        self.rect = image.get_rect()
        self.x = x
        self.y = y


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
        player_args = data.get("player", {})
        self.player_starting_pos = player_args.get("starting-pos")
        self.player_lives = player_args.get("lives")

        world_args = data.get("world", {})
        self.biome = world_args.get("biome", "default")
        self.background_image = world_args.get("background-image", None)
        self.background_color = world_args.get("background_color")
        self.rows = world_args.get("rows")
        self.cols = world_args.get("cols")
        self.gravity = world_args.get("gravity", 1.0),
        self.terminal_velocity = world_args.get("terminal-velocity", 32.0)

        self.starting_blocks = []
        self.starting_coins = []

        self.blocks = pg.sprite.Group()
        self.coins = pg.sprite.Group()

        block_str = world_args.get("blocks", "")
        for y in range(self.rows):
            for x in range(self.cols):
                idx = y * self.cols + x
                val = block_str[idx]
                blit_x, blit_y = x * BLOCK_SIZE, y*BLOCK_SIZE

                if (block_type := int(val)) in Block.BlockType:
                    self.starting_blocks.append(Block(blit_x, blit_y, int(val), block_type,
                                                      BLOCK_SPRITES[block_type]))
                elif val == "C":
                    self.starting_coins.append(
                        Coin(blit_x, blit_y, COINS_SPRITES))

        self.blocks.add(self.starting_blocks)
        self.coins.add(self.starting_coins)

        self.background_layer = pg.Surface(SCREEN_SIZE, pg.SRCALPHA, 32)

    @staticmethod
    def from_file(path: str):
        with open(path, 'r') as f:
            data = yaml.load(f)["data"]
            return Level(data)

    def render(self, surf: pg.Surface):
        pass

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

    def reset(self):
        self.player = Player()
        self.load_level(0)
        self.start()

    def load_level(self, level: int):
        self.curr_level = level
        self.level = Level.from_file(LEVELS[level])
