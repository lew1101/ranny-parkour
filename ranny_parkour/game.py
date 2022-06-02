import pygame as pg
import yaml
from enum import IntEnum, Flag

from . import *
from .misc import load_image, SpriteSheet


RANNY_SHEET_1 = SpriteSheet(BASE_PATH + "assets/sprites/ranny_spritesheet_1.png")  # noqa

PLAYER_IDLE_SPRITE_RIGHT, *PLAYER_WALKING_SPRITES_RIGHT = map(
    lambda image: pg.transform.scale(image, (51, 102)),
    RANNY_SHEET_1.load_strip(pg.Rect(0, 0, 512, 1024), 5)
)

PLAYER_IDLE_SPRITE_LEFT = pg.transform.flip(
    PLAYER_IDLE_SPRITE_RIGHT, 1, 0)

PLAYER_WALKING_SPRITES_LEFT = [pg.transform.flip(
    s, 1, 0) for s in PLAYER_WALKING_SPRITES_RIGHT]

PLAYER_JUMPING_SPRITES_RIGHT = []
PLAYER_JUMPING_SPRITES_LEFT = [pg.transform.flip(
    s, 1, 0) for s in PLAYER_JUMPING_SPRITES_RIGHT]

COINS_SPRITE = load_image(BASE_PATH + "assets/sprites/coin.png")
BLOCK_SPRITES = [
    None,
    load_image(BASE_PATH + "assets/sprites/grass_block.png"),
    load_image(BASE_PATH + "assets/sprites/lava_block.png"),
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    load_image(BASE_PATH + "assets/sprites/coin.png"),
]


# ==================
# Base Classes
# ==================


class Entity(pg.sprite.Sprite):
    def __init__(self, x: float, y: float, image: pg.Surface):
        super().__init__()
        self.image = image
        self.rect = image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.vx = 0.0
        self.vy = 0.0

    def apply_gravity(self, gravity: float, terminal_vel: float):
        self.vy = min(self.vy + gravity, terminal_vel)


class Block(pg.sprite.Sprite):
    class BlockType(IntEnum):
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
        self.player_starting_pos = tuple(
            [v * BLOCK_SIZE for v in player_args.get("starting-pos", (0, 0))])

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
        self.background_color = world_args.get("background-color")

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
                if cell == "0":
                    pass
                elif cell.isdigit() and Block.BlockType.has_value((block_type := int(cell))):
                    self.starting_blocks.append(Block(blit_x, blit_y, block_type,
                                                      BLOCK_SPRITES[block_type]))
                # check cell is a coin
                elif cell == "C":
                    self.starting_coins.append(
                        Coin(blit_x, blit_y, COINS_SPRITE))
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
            pg.transform.scale(self.background_image, SCREEN_SIZE)
            self.background_image.blit(self.background_layer, (0, 0))

        self.inactive_sprites.draw(self.inactive_layer)

    @staticmethod
    def from_file(path: str):
        with open(path, 'r') as f:
            data = yaml.load(f, yaml.Loader)["data"]
            return Level(data)

    def reset(self):
        pass


# ==================
# Player
# ==================


class Player(Entity):
    image_interval = 20  # update anim every x frames
    images = [
        [[PLAYER_IDLE_SPRITE_LEFT], [PLAYER_IDLE_SPRITE_RIGHT]],
        [PLAYER_WALKING_SPRITES_LEFT, PLAYER_WALKING_SPRITES_RIGHT],
        [PLAYER_JUMPING_SPRITES_LEFT, PLAYER_JUMPING_SPRITES_RIGHT]
    ]

    class State(IntEnum):
        STANDING = 0
        WALKING = 1
        JUMPING = 2

    def __init__(self, x: float, y: float, lives: int):
        self.state = self.State.WALKING
        self.steps = 0
        self.image_index = 0

        self.lives = lives
        self.speed = 5
        self.facing_right = True
        self.grounded = True
        super().__init__(x, y, PLAYER_IDLE_SPRITE_RIGHT)

    def tick(self):
        if self.steps == 0:
            self.update_image()
        self.steps = (self.steps + 1) % self.image_interval

    def update_image(self):
        images = self.images[self.state][1 if self.facing_right else 0]
        self.image = images[self.image_index]
        self.image_index = (self.image_index + 1) % len(images)

    def stop(self):
        self.vx = 0.0

    def move_left(self):
        self.rect.x -= self.speed
        self.facing_right = False

    def move_right(self):
        self.rect.x += self.speed
        self.facing_right = True

    def jump(self):
        if not self.grounded:
            return -1

        # ==================
        # Game
        # ==================


class Game:
    class Flags(Flag):
        pass

    def __init__(self):
        self.game_over = False
        self.flags = 0
        self.reset()

    def start(self):
        pass

    def tick(self):
        self.player.tick()

    def process_keypresses(self, keys: list[pg.event.Event]):
        if not self.player:
            return
        if keys[pg.K_a] or keys[pg.K_LEFT]:
            self.player.move_left()
        if keys[pg.K_d] or keys[pg.K_RIGHT]:
            self.player.move_right()
        if keys[pg.K_w] or keys[pg.K_UP]:
            self.player.jump()

    def render(self, surf: pg.Surface, coords=(0, 0)):
        self.level.active_layer.fill(TRANSPARENT)
        self.level.active_sprites.draw(self.level.active_layer)

        surf.blits([
            (self.level.background_layer, coords),
            (self.level.active_layer, coords),
            (self.level.inactive_layer, coords)
        ])

    def reset(self):
        self.load_level(0)
        self.start()

    def load_level(self, level_index: int):
        self.curr_level = level_index
        self.level = Level.from_file(LEVELS[level_index])

        player_x, player_y = self.level.player_starting_pos
        self.player = Player(player_x, player_y, self.level.player_lives)
        self.level.active_sprites.add(self.player)
