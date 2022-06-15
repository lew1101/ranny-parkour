import pygame as pg
import yaml
from enum import IntEnum

from . import *
from .misc import load_image, SpriteSheet
from .widgets import Text

# welcome, adventurer, to the land of spagetti code

PLAYER_WIDTH = BLOCK_SIZE
PLAYER_HEIGHT = 1.8*BLOCK_SIZE

# ranny idle
PLAYER_IDLE_IMAGE_RIGHT = pg.transform.scale(pg.image.load(
    BASE_PATH+"assets/sprites/ranny_silouette.png"), (PLAYER_WIDTH, PLAYER_HEIGHT)).convert_alpha()
PLAYER_IDLE_IMAGE_LEFT = pg.transform.flip(
    PLAYER_IDLE_IMAGE_RIGHT, 1, 0).convert_alpha()

# ranny walking
RANNY_SHEET_1 = SpriteSheet(BASE_PATH + "assets/sprites/ranny_spritesheet_1.png")  # noqa

PLAYER_WALKING_IMAGES_RIGHT = list(map(
    lambda image: pg.transform.scale(
        image, (PLAYER_WIDTH, PLAYER_HEIGHT)).convert_alpha(),
    RANNY_SHEET_1.load_strip(pg.Rect(512, 0, 512, 1024), 4))
)

PLAYER_WALKING_IMAGES_LEFT = [pg.transform.flip(
    s, 1, 0).convert_alpha() for s in PLAYER_WALKING_IMAGES_RIGHT]

# ranny jumping
RANNY_SHEET_2 = SpriteSheet(BASE_PATH + "assets/sprites/ranny_spritesheet_2.png")  # noqa

PLAYER_JUMPING_IMAGE_RIGHT = pg.transform.scale(
    RANNY_SHEET_2.image_at(pg.Rect(512, 0, 256, 510)), (PLAYER_WIDTH, PLAYER_HEIGHT)).convert_alpha()
PLAYER_JUMPING_IMAGE_LEFT = pg.transform.flip(
    PLAYER_JUMPING_IMAGE_RIGHT, 1, 0).convert_alpha()

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
        super().__init__(x, y, self.block_type, image or self.image)


class Dirtblock(Block):
    block_type = Block.BlockType.DIRT
    image = load_image(BASE_PATH + "assets/sprites/dirt_block.png")

    def __init__(self, x: int, y: int, image: pg.Surface = None):
        super().__init__(x, y, self.block_type, image or self.image)


class Lavablock(Block):
    block_type = Block.BlockType.LAVA
    image = load_image(BASE_PATH + "assets/sprites/lava_block.png")

    def __init__(self, x: int, y: int, image: pg.Surface = None):
        super().__init__(x, y, self.block_type, image or self.image)


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
        None,
    ]
    return constructors[block_type](x, y, image)

# ==================


class Coin(Entity):
    image = load_image(BASE_PATH + "assets/sprites/coin.png")

    def __init__(self, x: float, y: float, image: pg.Surface = None):
        super().__init__(x, y, image or self.image)
        self.val = 1


class Endpoint(Entity):
    image = load_image(BASE_PATH+"assets/sprites/pride.png")

    def __init__(self, x: int, y: int, image: pg.Surface = None):
        super().__init__(x, y, image or self.image)


# ==================
# Level
# ==================

class Level:
    @staticmethod
    def from_file(path: str):
        with open(path, 'r') as f:
            level_data = yaml.load(f, yaml.Loader)
            return Level(level_data)

    def __init__(self, data: dict):
        self.completed = False

        self.name = data.get("name")

        level_data = data.get("data", {})
        # player
        player_args = level_data.get("player", {})
        self.player_starting_pos = tuple(
            [v * BLOCK_SIZE for v in player_args.get("starting-pos", (0, 0))])
        self.player_respawn_pos = tuple(
            [v * BLOCK_SIZE for v in player_args.get("respawn-pos", (0, 0))])
        self.player_speed = player_args.get("speed")
        self.player_lives = player_args.get("lives")
        self.player_jump_power = player_args.get("jump-power")

        # world
        world_args = level_data.get("world", {})
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
        self.total_coins = 0

        # define layers
        self.starting_blocks = []
        self.starting_coins = []
        self.starting_endpoints = []

        self.blocks = pg.sprite.Group()
        self.coins = pg.sprite.Group()
        self.endpoints = pg.sprite.Group()

        self.active_sprites = pg.sprite.Group()
        self.static_sprites = pg.sprite.Group()

        block_str = world_args.get("blocks")

        # check block_str is string
        assert isinstance(block_str, str), \
            "block string needs to be an instance of string"

        block_str = block_str.replace("\n", "")

        # check length of block_str is correct
        assert len(block_str) == self.rows * self.cols, \
            f"length of block string {len(block_str)} does not match given \
            row {self.rows} and col {self.cols} attributes"

        for y in range(self.rows):
            for x in range(self.cols):
                idx = y * self.cols + x
                cell = block_str[idx]
                block_x, block_y = x * BLOCK_SIZE, y * BLOCK_SIZE

                if cell == "0":
                    # empty
                    continue
                elif cell.isdigit() and Block.BlockType.has_value((block_type := int(cell))):
                    # block
                    self.starting_blocks.append(
                        BlockFactory(block_x, block_y, block_type))
                elif cell == "C":
                    # coin
                    self.starting_coins.append(
                        Coin(block_x, block_y))
                    self.total_coins += 1
                elif cell == "F":
                    # endpoint
                    self.starting_endpoints.append(
                        Endpoint(block_x, block_y)
                    )
                else:
                    # invalid value
                    raise Exception(
                        f"value “{cell}” in level {self.name} on cell ({x}, {y}) is invalid")

        self.blocks.add(self.starting_blocks)
        self.coins.add(self.starting_coins)
        self.endpoints.add(self.starting_endpoints)

        self.active_sprites.add(self.coins, self.starting_endpoints)
        self.static_sprites.add(self.blocks)

        # is this a good idea?
        self.background_layer = pg.Surface(self.size, pg.SRCALPHA, COLOR_DEPTH)
        self.blocks_layer = pg.Surface(self.size, pg.SRCALPHA, COLOR_DEPTH)
        self.active_layer = pg.Surface(self.size, pg.SRCALPHA, COLOR_DEPTH)

        if self.background_color:
            self.background_layer.fill(pg.Color(*self.background_color))

        if hasattr(self, "background_image"):
            pg.transform.scale(self.background_image, SCREEN_SIZE)
            self.background_image.blit(self.background_layer, (0, 0))

        self.static_sprites.draw(self.blocks_layer)

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

    def __init__(self, game: 'Game'):
        self.game = game
        self.level = game.level
        x, y = self.level.player_starting_pos
        super().__init__(x, y, PLAYER_IDLE_IMAGE_RIGHT)

        self.coins_collected = 0
        self.lives = self.level.player_lives
        self.speed = self.level.player_speed
        self.jump_power = self.level.player_jump_power

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
        self.process_coins()
        self.process_endpoints()
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
        if self.vx != 0:
            new_state = Player.State.WALKING
        else:
            new_state = Player.State.IDLE

        if not self.grounded and (self.vy < 0 or self.state == Player.State.JUMPING):
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
        self.game.flags |= Game.Flags.WIN

    def respawn(self):
        pass

    def process_coins(self):
        collide_list = pg.sprite.spritecollide(self, self.level.coins, False)
        for coin in collide_list:
            coin.kill()
            self.coins_collected += 1

    def process_endpoints(self):
        collide_list = pg.sprite.spritecollide(
            self, self.level.endpoints, False)
        if len(collide_list) > 0:
            self.win()

        # ==================
        # Game
        # ==================


class Game:
    class Flags(IntEnum):
        WIN = 1

    def __init__(self):
        self.game_over = False
        self.flags = 0

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
            if self.player.state != Player.State.JUMPING:
                self.player.stop()

    def calculate_offset(self):
        x = -self.player.rect.centerx + SCREEN_WIDTH / 2

        if self.player.rect.centerx < SCREEN_WIDTH / 2:
            x = 0
        elif self.player.rect.centerx > self.level.width - SCREEN_WIDTH / 2:
            x = -self.level.width + SCREEN_WIDTH

        return x, 0

    def render(self, surf: pg.Surface):
        self.level.active_layer.fill(TRANSPARENT)
        self.level.active_sprites.draw(self.level.active_layer)

        blit_coords = self.calculate_offset()
        surf.blits([
            (self.level.background_layer, blit_coords),
            (self.level.blocks_layer, blit_coords),
            (self.level.active_layer, blit_coords)
        ])
        self.show_level_text(surf)
        self.show_score(surf)
        self.show_win_text(surf)

    def reset(self):
        self.flags = 0
        self.start()
        self.load_level(self.curr_level)

    def load_level(self, level_index: int):
        try:
            self.level = Level.from_file(LEVELS[level_index])
            self.player = Player(self)
            self.curr_level = level_index
            return 0
        except IndexError:
            return -1

    # the methods below need to be moved out of here (too lazy)
    def show_level_text(self, surf: pg.Surface):
        if not hasattr(self, "prev_level") or self.prev_level != self.curr_level:
            self.level_text = Text(
                f"{self.curr_level+1}. {self.level.name}", FONT_SM)
            self.level_text.rect.x = 15
            self.level_text.rect.y = 15
        self.level_text.draw(surf)
        self.prev_level = self.curr_level

    def show_win_text(self, surf: pg.Surface):
        if self.flags & Game.Flags.WIN:
            text = Text(END_GAME_TEXT, FONT_LG)
            text.rect.center = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
            text.draw(surf)

    def show_score(self, surf: pg.Surface):
        if not hasattr(self, "prev_score") or self.prev_score != self.player.coins_collected:
            image = Coin.image.copy()
            image_rect = image.get_rect(x=0, y=-10)

            text = Text(f"{self.player.coins_collected}/{self.level.total_coins}",
                        FONT_MD)
            text.rect.left = image_rect.right
            text.rect.y = 15
            self.score_surf = pg.Surface(
                (image_rect.width+text.rect.width, max(image_rect.height, text.rect.height)), pg.SRCALPHA, COLOR_DEPTH)
            self.r = self.score_surf.get_rect(right=SCREEN_WIDTH-15, top=0)

            self.score_surf.blit(image, image_rect)
            text.draw(self.score_surf)
        surf.blit(self.score_surf, self.r)
        self.prev_score = self.player.coins_collected
