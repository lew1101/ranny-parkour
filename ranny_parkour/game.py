import pygame as pg
import yaml
from enum import IntEnum, Flag

from . import *
from .misc import load_image, SpriteSheet

# ranny idle
PLAYER_IDLE_IMAGE_RIGHT = pg.transform.scale(pg.image.load(
    BASE_PATH+"assets/sprites/ranny_silouette.png"), (51, 102)).convert_alpha()
PLAYER_IDLE_IMAGE_LEFT = pg.transform.flip(
    PLAYER_IDLE_IMAGE_RIGHT, 1, 0).convert_alpha()

# ranny walking
RANNY_SHEET_1 = SpriteSheet(BASE_PATH + "assets/sprites/ranny_spritesheet_1.png")  # noqa

PLAYER_WALKING_IMAGES_RIGHT = list(map(
    lambda image: pg.transform.scale(image, (51, 102)).convert_alpha(),
    RANNY_SHEET_1.load_strip(pg.Rect(512, 0, 512, 1024), 4))
)

PLAYER_WALKING_IMAGES_LEFT = [pg.transform.flip(
    s, 1, 0).convert_alpha() for s in PLAYER_WALKING_IMAGES_RIGHT]

# ranny jumping
RANNY_SHEET_2 = SpriteSheet(BASE_PATH + "assets/sprites/ranny_spritesheet_2.png")  # noqa

PLAYER_JUMPING_IMAGE_RIGHT = pg.transform.scale(
    RANNY_SHEET_2.image_at(pg.Rect(512, 0, 256, 510)), (51, 102)).convert_alpha()
PLAYER_JUMPING_IMAGE_LEFT = pg.transform.flip(
    PLAYER_JUMPING_IMAGE_RIGHT, 1, 0).convert_alpha()

COINS_SPRITE = load_image(BASE_PATH + "assets/sprites/coin.png")

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

    def apply_gravity(self, gravity: float = 1.0, terminal_vel: float = 32.0):
        self.vy = min(self.vy + gravity, terminal_vel)


class Block(pg.sprite.Sprite):
    class BlockType(IntEnum):
        GRASS = 1
        DIRT = 2
        LAVA = 3
        ENDPOINT = 9

        @ classmethod
        def has_value(cls, value):
            return value in cls._value2member_map_

    def __init__(self, x: int, y: int, block_type: int, image: list[pg.Surface]):
        super().__init__()
        self.block_type = block_type
        self.image = image
        self.rect = image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Grassblock(Block):
    block_type = Block.BlockType.GRASS
    image = load_image(BASE_PATH + "assets/sprites/grass_block.png")

    def __init__(self, x: int, y: int, image: pg.Surface = None):
        image = image or self.image
        super().__init__(x, y, self.block_type, image)


class Dirtblock(Block):
    block_type = Block.BlockType.DIRT
    image = load_image(BASE_PATH + "assets/sprites/dirt_block.png")

    def __init__(self, x: int, y: int, image: pg.Surface = None):
        image = image or self.image
        super().__init__(x, y, self.block_type, image)


class Lavablock(Block):
    block_type = Block.BlockType.LAVA
    image = load_image(BASE_PATH + "assets/sprites/lava_block.png")

    def __init__(self, x: int, y: int, image: pg.Surface = None):
        image = image or self.image
        super().__init__(x, y, self.block_type, image)


class Endpoint(Block):
    block_type = Block.BlockType.ENDPOINT
    images = [load_image(BASE_PATH + "assets/sprites/lava_block.png")]

    def __init__(self, x: int, y: int, images: pg.Surface = None):
        self.images = images or self.images
        self.steps = 0
        super().__init__(x, y, self.block_type, self.images[0])


def BlockFactory(x, y, block_type=Block.BlockType.GRASS, image=None):
    constructors: list[None | Block] = [
        None,
        Grassblock,
        Dirtblock,
        Lavablock,
        None,
        None,
        None,
        None,
        None,
        Endpoint
    ]
    return constructors[block_type](x, y, image)

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
        self.player_respawn_pos = tuple(
            [v * BLOCK_SIZE for v in player_args.get("respawn-pos", (0, 0))])
        self.player_speed = player_args.get("speed")
        self.player_lives = player_args.get("lives")
        self.player_jump_power = player_args.get("jump-power")

        # world
        world_args = data.get("world", {})
        self.biome = world_args.get("biome", "default")
        self.rows = world_args.get("rows")
        self.cols = world_args.get("cols")

        self.width = self.cols * BLOCK_SIZE
        self.height = self.rows * BLOCK_SIZE
        self.size = (self.width, self.height)

        self.gravity = world_args.get("gravity", 1.0)
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
        self.static_sprites = pg.sprite.Group()

        block_str = world_args.get("blocks")

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
                    self.starting_blocks.append(
                        BlockFactory(blit_x, blit_y, block_type))
                # check cell is a coin
                elif cell == "C":
                    self.starting_coins.append(
                        Coin(blit_x, blit_y, COINS_SPRITE))
                else:
                    raise Exception(F"{cell} on ({x}, {y}) is invalid")

        self.blocks.add(self.starting_blocks)
        self.coins.add(self.starting_coins)

        self.active_sprites.add(self.coins)
        self.static_sprites.add(self.blocks)

        self.background_layer = pg.Surface(self.size, pg.SRCALPHA, COLOR_DEPTH)
        self.blocks_layer = pg.Surface(self.size, pg.SRCALPHA, COLOR_DEPTH)

        if self.background_color:
            self.background_layer.fill(pg.Color(*self.background_color))

        if hasattr(self, "background_image"):
            pg.transform.scale(self.background_image, SCREEN_SIZE)
            self.background_image.blit(self.background_layer, (0, 0))

        self.static_sprites.draw(self.blocks_layer)

    @ staticmethod
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
    class State(IntEnum):
        IDLE = 0
        WALKING = 1
        JUMPING = 2

    image_interval = 10  # update anim every x frames
    images = [
        [PLAYER_IDLE_IMAGE_LEFT, PLAYER_IDLE_IMAGE_RIGHT],
        [PLAYER_WALKING_IMAGES_LEFT, PLAYER_WALKING_IMAGES_RIGHT],
        [PLAYER_JUMPING_IMAGE_LEFT, PLAYER_JUMPING_IMAGE_RIGHT],
    ]

    def __init__(self, level: Level):
        x, y = level.player_starting_pos
        super().__init__(x, y, PLAYER_IDLE_IMAGE_RIGHT)

        self.level = level
        self.lives = level.player_lives
        self.speed = level.player_speed
        self.jump_power = level.player_jump_power

        self.grounded = False
        self.facing_right = True
        self.state = Player.State.IDLE
        self.anim_steps = 0
        self.image_index = 0

        self.level.active_sprites.add(self)

    def tick(self):
        self.apply_gravity(self.level.gravity,
                           self.level.terminal_velocity)
        self.move_and_process_blocks()
        self.check_world_boundaries()
        # update player anim stage
        self.update_state()
        if self.anim_steps == 0:
            self.update_image()
        self.anim_steps = (self.anim_steps + 1) % self.image_interval

    def update_image(self):
        if self.state == Player.State.WALKING:
            images = Player.images[Player.State.WALKING][1 if self.facing_right else 0]
            self.image = images[self.image_index]
            self.image_index = (self.image_index + 1) % len(images)
        else:
            self.image = Player.images[self.state][1 if self.facing_right else 0]

    def update_state(self):
        new_state = None
        if self.grounded:
            if self.vx != 0:
                new_state = Player.State.WALKING
            else:
                new_state = Player.State.IDLE
        else:
            new_state = Player.State.JUMPING

        if self.state != new_state:
            self.state = new_state
            self.image_index = 0
            self.steps = 0

    def check_world_boundaries(self):
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > self.level.width:
            self.rect.right = self.level.width

    def stop(self):
        self.vx = 0.0

    def move_left(self):
        self.vx = -self.speed
        self.facing_right = False

    def move_right(self):
        self.vx = self.speed
        self.facing_right = True

    def jump(self):
        self.grounded = False
        self.vy = -self.jump_power

    def move_and_process_blocks(self):
        blocks = self.level.blocks
        self.rect.x += self.vx
        collide_list = pg.sprite.spritecollide(
            self, blocks, False)

        for block in collide_list:
            if self.vx > 0:
                self.rect.right = block.rect.left
            elif self.vx < 0:
                self.rect.left = block.rect.right

        self.grounded = False
        self.rect.y += self.vy
        collide_list = pg.sprite.spritecollide(
            self, blocks, False)

        for block in collide_list:
            # special actions
            if block.block_type == Block.BlockType.LAVA:
                return self.die()
            elif block.block_type == Block.BlockType.ENDPOINT:
                return self.win()

            if self.vy > 0:
                self.rect.bottom = block.rect.top
                self.vy = 0.0
                self.grounded = True
            elif self.vy < 0:
                self.rect.top = block.rect.bottom
                self.vy = 0.0

    def die(self):
        self.lives -= 1
        self.rect.x, self.rect.y = self.level.player_respawn_pos

    def win(self):
        print("win")

    def respawn(self):
        pass

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

    def process_keypresses(self, keys: list[bool]):
        if not self.player:
            return

        if keys[pg.K_w] or keys[pg.K_UP]:
            if self.player.grounded:
                self.player.jump()

        if keys[pg.K_a] or keys[pg.K_LEFT]:
            self.player.move_left()
        elif keys[pg.K_d] or keys[pg.K_RIGHT]:
            self.player.move_right()
        else:
            if self.player.grounded:
                self.player.stop()

    def render(self, surf: pg.Surface, coords=(0, 0)):
        surf.blits([
            (self.level.background_layer, coords),
            (self.level.blocks_layer, coords)
        ])
        self.level.active_sprites.draw(surf)

    def reset(self):
        self.load_level(0)
        self.start()

    def load_level(self, level_index: int):
        self.curr_level = level_index
        self.level = Level.from_file(LEVELS[level_index])
        self.player = Player(self.level)
