from copy import copy
from datetime import datetime
from random import randint
from typing import Tuple, Any, List, Optional, Union
from mlx import Mlx
from mazegen import PathFinder, MazeGenerator, Maze
from objects import Image, Window, Brick
from colors import themes
from .Draw import Draw
from game.Player import Player
from enums import Key, Arrow, Numpad
from pathlib import Path


def get_usernames_from_home() -> list[str]:
    """Return a list of usernames by scanning /home.

    Scans the `/home` directory and returns names of entries that are
    directories. Currently used to validate in-game intra names (commented).

    Returns:
        list[str]: Directory names under `/home`.
    """
    return [
        p.name
        for p in Path("/home").iterdir()
        if p.is_dir()
    ]


def darken(color: bytes, factor: float) -> bytes:
    """Return an RGBA color darkened by a factor.

    Args:
        color: 4-byte RGBA color.
        factor: Multiplicative factor applied to RGB channels (0.0-1.0).

    Returns:
        bytes: New RGBA color with scaled RGB channels and original alpha.
    """
    r, g, b, a = color
    r = int(r * factor)
    g = int(g * factor)
    b = int(b * factor)
    return bytes([r, g, b, a])


def transparent(color: bytes, level: int) -> bytes:
    """Return an RGBA color with updated alpha level.

    Args:
        color: 4-byte RGBA color.
        level: New alpha value (0-255).

    Returns:
        bytes: RGBA color with modified alpha channel.
    """
    r, g, b, a = color
    return bytes([r, g, b, level])


class MazeVisualizer:
    """Windowed visualizer that connects maze generation to a GUI.

    The visualizer orchestrates maze generation animation, pathfinding
    animation, user interaction (keyboard/mouse), theming and rendering
    primitives (images, bricks) through the `mlx` binding.
    """

    def __init__(
            self, maze: Maze, path_finder: PathFinder):
        """Initialize the visualizer and load resources.

        Args:
            maze: The `Maze` object to visualize.
            path_finder: The `PathFinder` instance used to compute paths and
                provide step-by-step yields for animations.
        """
        self.start_time = datetime.now()
        self.m = Mlx()
        self.mlx = self.m.mlx_init()
        self.win = Window(self.m, self.mlx, "A-Maze-ing")
        self.draw = Draw()
        self.exit = exit
        self.maze = maze
        self.create_player()
        self.x = -2
        self.y = -1
        self.transparency = 100
        self.maze_draw = True
        self.menu_showed = False
        self.brick_visible = False
        self.paused = False
        self.frozen = False
        self.animation = False
        self.path_finding: bool = False
        self.game_mode = False
        self.game_start_time: Optional[datetime] = None
        self.slider_x = 1
        self.theme_idx = 1
        self.path_finder = path_finder
        self.finder = self.path_finder.find_path(maze)
        self.themes = themes.get_themes(self.transparency)
        self.colors = copy(self.themes[self.theme_idx])
        self.palette = themes.get_palette()
        self.img = Image(self.m, self.mlx, self.win, self.maze)
        self.path_img = Image(self.m, self.mlx, self.win, self.maze)
        self.final_path_img = Image(self.m, self.mlx, self.win, self.maze)
        self.offset\
            = (self.img.height - self.maze.height * self.img.scale) // 2 - 8
        self.color_blocks_height_multipliers = [1, 9, 17, 25, 33, 41, 49]
        self.load_images()
        self.create_elements()
        self.create_background_images()
        self.create_blocks()
        self.set_images_and_position()
        self.set_palettes_data()
        # self.usernames = get_usernames_from_home()

    def load_images(self) -> None:
        """Load PNG assets (icons, start/finish) and set icon sizes.

        Uses `mlx.mlx_png_file_to_image` to load UI icons into memory and
        stores the returned image handles and sizes for later blitting.
        """
        self.icon_size = self.get_icon_size()
        self.save: Tuple[Any, int, int]\
            = self.m.mlx_png_file_to_image(self.mlx, "pictures/save.png")
        self.play: Tuple[Any, int, int]\
            = self.m.mlx_png_file_to_image(self.mlx, "pictures/play.png")
        self.pause: Tuple[Any, int, int]\
            = self.m.mlx_png_file_to_image(self.mlx, "pictures/pause.png")
        self.freeze: Tuple[Any, int, int]\
            = self.m.mlx_png_file_to_image(self.mlx, "pictures/freeze.png")
        self.frozen_img: Tuple[Any, int, int]\
            = self.m.mlx_png_file_to_image(self.mlx, "pictures/frozen.png")
        self.load_start_and_finish_imgs()
        self.refresh: Tuple[Any, int, int]\
            = self.m.mlx_png_file_to_image(self.mlx, "pictures/refresh.png")
        self.animate: Tuple[Any, int, int]\
            = self.m.mlx_png_file_to_image(self.mlx, "pictures/animate.png")
        self.animate_on: Tuple[Any, int, int]\
            = self.m.mlx_png_file_to_image(self.mlx, "pictures/animate_on.png")
        self.path_icon: Tuple[Any, int, int]\
            = self.m.mlx_png_file_to_image(self.mlx, "pictures/path.png")
        self.path_on_icon: Tuple[Any, int, int]\
            = self.m.mlx_png_file_to_image(self.mlx, "pictures/path_on.png")
        self.game: Tuple[Any, int, int]\
            = self.m.mlx_png_file_to_image(self.mlx, "pictures/game.png")
        self.game_on: Tuple[Any, int, int]\
            = self.m.mlx_png_file_to_image(self.mlx, "pictures/game_on.png")

    def load_start_and_finish_imgs(self) -> None:
        """Load the start and finish marker images sized to current icon.

        The images are reloaded when `icon_size` changes so they match current
        maze scale.
        """
        self.start: Tuple[Any, int, int]\
            = self.m.mlx_png_file_to_image(
            self.mlx, f"pictures/start{self.icon_size}.png")
        self.finish: Tuple[Any, int, int]\
            = self.m.mlx_png_file_to_image(
            self.mlx, f"pictures/finish{self.icon_size}.png")

    def create_elements(self) -> None:
        """Create UI image elements used by the menu and palette.

        Constructs small `Image` buffers (e.g., slider, corrector) and fills
        them with baseline colors used as UI controls.
        """
        self.create_brick()
        self.corrector = Image(
            self.m, self.mlx, self.win, self.maze,
            self.win.width // 400, self.win.width // 100)
        self.corrector_data = self.m.mlx_get_data_addr(self.corrector.ptr)[0]
        self.corrector_data[:]\
            = bytes([120, 120, 120, 255]) * (len(self.corrector_data) // 4)
        self.slider = Image(
            self.m, self.mlx, self.win, self.maze,
            self.win.width // 20, self.win.width // 400)
        self.slider_data = self.m.mlx_get_data_addr(self.slider.ptr)[0]
        self.slider_data[:]\
            = bytes([255, 255, 255, 255]) * (len(self.slider_data) // 4)
        self.colors_block = Image(
            self.m, self.mlx, self.win, self.maze,
            self.win.width // 16, self.win.height // 64 * 7)
        self.colors_block_data\
            = self.m.mlx_get_data_addr(self.colors_block.ptr)[0]
        self.create_color_palette()

    def create_background_images(self) -> None:
        """Prepare background and overlay images used when rendering menu.

        Sets up `Image` buffers for background, menu and transparency overlay
        and fills them with default colors (often based on the current theme).
        """
        self.strings_background = Image(
            self.m, self.mlx, self.win, self.maze,
            self.win.width // 8, self.win.height // 8)
        self.strings_background.data[:]\
            = bytes([0, 0, 0, 255]) * (len(self.strings_background.data) // 4)
        self.background_img = Image(
            self.m, self.mlx, self.win, self.maze,
            self.win.width // 8 * 7, self.win.height)
        self.background_img.data[:]\
            = bytes([0, 0, 0, 255]) * (len(self.background_img.data) // 4)
        self.menu_img = Image(
            self.m, self.mlx, self.win, self.maze,
            self.win.width // 8, self.win.height)
        self.menu_img.data[:] = darken(
            self.colors['Background'], 0.6) * (len(self.menu_img.data) // 4)

    def create_blocks(self) -> None:
        """Define vertical positions for color palette blocks in the menu.

        Each block maps a palette row to a y-range used for click detection
        inside `mouse_hook`.
        """
        self.blocks = {
            '42': {
                'start': self.win.height // 64,
                'end': self.win.height // 64 + self.colors_block.height,
            },
            'Grid 1': {
                'start': self.win.height // 64 * 9,
                'end': self.win.height // 64 * 9 + self.colors_block.height,
            },
            'Grid 2': {
                'start': self.win.height // 64 * 17,
                'end': self.win.height // 64 * 17 + self.colors_block.height,
            },
            'Block found': {
                'start': self.win.height // 64 * 25,
                'end': self.win.height // 64 * 25 + self.colors_block.height,
            },
            'Block not found': {
                'start': self.win.height // 64 * 33,
                'end': self.win.height // 64 * 33 + self.colors_block.height,
            },
            'Snake': {
                'start': self.win.height // 64 * 41,
                'end': self.win.height // 64 * 41 + self.colors_block.height,
            },
            'Background': {
                'start': self.win.height // 64 * 49,
                'end': self.win.height // 64 * 49 + self.colors_block.height
            }
        }

    def set_images_and_position(self) -> None:
        """Recompute positions and sizes used to place UI images in menu.

        This should be called when window size, theme, or state changes so
        icon placements stay consistent with the layout.
        """
        self.images_with_height_and_width = {
            self.save[0]:
            {
                'width': self.win.width // 64 * 61,
                'height': self.win.height // 64 * 57
            },
            self.refresh[0]:
            {
                'width': self.win.width // 64 * 63,
                'height': self.win.height // 64 * 57
            },
            self.game_on[0] if self.game_mode else self.game[0]:
            {
                'width': self.win.width // 64 * 62,
                'height': self.win.height // 64 * 61
            },
            self.path_on_icon[0] if self.path_finding else self.path_icon[0]:
            {
                'width': self.win.width // 64 * 61,
                'height': self.win.height // 64 * 61
            },
            self.animate_on[0] if self.animation else self.animate[0]:
            {
                'width': self.win.width // 64 * 62,
                'height': self.win.height // 64 * 57
            },
            self.play[0] if self.paused else self.pause[0]:
            {
                'width': self.win.width // 64 * 63,
                'height': self.win.height // 64 * 59
            },
            self.frozen_img[0] if self.frozen else self.freeze[0]:
            {
                'width': self.win.width // 64 * 63,
                'height': self.win.height // 64 * 61
            },
            self.slider.ptr:
            {
                'width': self.win.width // 128 * 119,
                'height': self.win.height // 64 * 59 + self.play[1]//2
            },
            self.corrector.ptr:
            {
                'width': (
                        self.slider_x * self.slider.width // 100
                        + self.win.width // 128 * 119),
                'height': (
                        self.win.height // 64 * 59 + self.play[1]//2
                        - self.corrector.height//2 + self.slider.height//2)
            },
        }

    def set_palettes_data(self) -> None:
        """Define mapping from palette name to display height multiplier.

        The multiplier is used to layout palette descriptions in the menu.
        """
        self.palettes_descriptions_with_height_multiplier = {
            "42": 1,
            "Grid found": 9,
            "Grid not found": 17,
            "Block found": 25,
            "Block not found": 33,
            "Snake": 41,
            "Background": 49
        }

    def set_menu_data(self) -> None:
        """Generates strings to display in the menu."""
        self.menu_data = {
            "Y=" + str(self.maze.height):
                {
                    'width': self.win.width // 64 * 57,
                    'height': self.win.height // 64 * 56
                },
            "X=" + str(self.maze.width):
                {
                    'width': self.win.width // 64 * 57,
                    'height': self.win.height // 64 * 57
                },
            f"S={self.seed}":
                {
                    'width': self.win.width // 64 * 57,
                    'height': self.win.height // 64 * 58
                },
            "(N)ew maze":
                {
                    'width': self.win.width // 64 * 61,
                    'height': self.win.height // 64 * 63
                },
            "Tr=" + str(self.transparency) + "(w/s)":
                {
                    'width': self.win.width // 64 * 57,
                    'height': self.win.height // 64 * 61
                },
            # "Th=" + str(self.theme_idx) + "(a/d)":
            #     {
            #         'width': self.win.width // 64 * 57,
            #         'height': self.win.height // 64 * 62
            #     },
            "Thi=" + str(self.img.thickness) + "(+/-)":
                {
                    'width': self.win.width // 64 * 57,
                    'height': self.win.height // 64 * 63
                },
            f"{self.slider_x}x":
                {
                    'width': self.win.width * 251 // 256,
                    'height': self.win.height * 231 // 256
                }
        }

    def show_enter_and_exit(self) -> None:
        """Blit the start and finish images at maze entry and exit points."""
        self.m.mlx_put_image_to_window(
            self.mlx, self.win.ptr,
            self.start[0], self.enter_x, self.enter_y)
        self.m.mlx_put_image_to_window(
            self.mlx, self.win.ptr,
            self.finish[0], self.exit_x, self.exit_y)

    def show_maze(self) -> None:
        """Blit the maze image buffer to the window at the offset."""
        self.draw.draw_maze(
            self.m, self.mlx, self.maze, self.img,
            self.win, self.found, self.colors,
            self.brick_visible, self.brick, self.offset)

    def show_path(self, animation: bool) -> None:
        """Render the current path onto the maze image buffer."""
        self.draw.draw_path(
                self.m, self.mlx, self.maze, self.img,
                self.path_img, self.final_path_img, self.win,
                self.path, self.colors, self.offset, animation, False)

    def format_seconds(self, seconds: float, precision: int = 1) -> str:
        """Format a floating point number of seconds into HH:MM:SS,ms style.

        Args:
            seconds: Total time in seconds.
            precision: Number of fractional digits for seconds.

        Returns:
            str: Formatted string like "00:01:23,4".
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        secs_formatted = \
            f"{secs:0{2 + 1 + precision}.{precision}f}".replace('.', ',')

        return f"{hours:02d}:{minutes:02d}:{secs_formatted}"

    def draw_ready_maze_to_window(self) -> None:
        """Blit the prepared maze image buffer to the window at the offset."""
        self.m.mlx_put_image_to_window(
            self.mlx, self.win.ptr, self.img.ptr, 0, self.offset)

    def reset_final_path(self) -> None:
        """
        Reset path image buffers and reinitialize the pathfinder generator.
        """
        self.path_img = Image(self.m, self.mlx, self.win, self.maze)
        self.final_path_img = Image(self.m, self.mlx, self.win, self.maze)
        self.final_path_img.data[:] = bytes([0])*len(self.final_path_img.data)
        self.finder = self.path_finder.find_path(self.maze)

    def draw_game(self) -> None:
        """Render the game HUD and player's final path during game mode.

        Displays elapsed time and draws the player's traced path.
        """
        self.draw_ready_maze_to_window()
        self.final_path_img.data[:] = bytes([0])*len(self.final_path_img.data)
        if self.game_start_time is not None:
            self.m.mlx_string_put(
                self.mlx, self.win.ptr, self.win.width // 8 * 7 - 130,
                self.win.height - 30, 0xffffffff,
                self.format_seconds(
                    (datetime.now() - self.game_start_time).total_seconds()))
        self.draw.draw_path(
            self.m, self.mlx, self.maze, self.img,
            self.path_img, self.final_path_img, self.win,
            self.game_path, self.colors, self.offset, False, True)
        self.show_enter_and_exit()

    def create_player(self) -> None:
        """Create the `Player` instance used for interactive game mode."""
        self.game_player = Player(self.maze)
        self.game_path: List[int] = self.game_player.path

    def draw_maze(self, vars: dict) -> None:
        """Main loop hook: advance generator and render maze animation.

        This function is registered with `mlx_loop_hook` and is invoked
        frequently; it advances the maze generator when animating and
        triggers drawing and menu updates.

        Args:
            vars: Arbitrary state forwarded by the mlx hook (contains "m",
                  "mlx" and "win").
        """
        if self.frozen:
            return
        if not self.maze_draw:
            if self.game_mode:
                self.draw_game()
            if self.path_finding:
                self.draw_path()
            return
        try:
            if not self.paused:
                self.found = next(self.generator)
                self.gen.visualisation_tempo = self.slider_x
            self.show_menu()
            if not self.animation:
                self.create_colors(255)
                self.m.mlx_put_image_to_window(
                    self.mlx, self.win.ptr,
                    self.background_img.ptr, 0, 0)
            self.show_maze()
            self.show_enter_and_exit()
            self.time = datetime.now()

        except StopIteration:
            self.create_colors(255)
            self.show_maze()
            self.show_enter_and_exit()
            self.create_colors(self.transparency)
            self.maze_draw = False
            self.create_player()

    def draw_path(self) -> None:
        """Compute and render the current path (instant or animated).

        Uses `PathFinder.find_path_instant` for instant rendering or pulls
        values from the pathfinder generator for animated mode.
        """
        if not self.path_finding:
            return
        try:
            self.create_colors(255)
            if not self.animation:
                self.path = self.path_finder.find_path_instant(self.maze)
            else:
                self.path = next(self.finder)
            self.draw_ready_maze_to_window()
            self.show_menu()
            self.show_path(self.animation)
            self.show_enter_and_exit()
            self.create_colors(255)

        except StopIteration:
            return

    def create_color_palette(self) -> None:
        """Rasterize the 8x8 color palette grid into the palette Image buffer.

        The function builds a byte sequence representing palette swatches
        and writes it into `self.colors_block.data` used for interactive
        palette selection.
        """
        data = self.colors_block_data
        leng = len(data)
        height = self.colors_block.height
        width = self.colors_block.width
        line_size = leng // height
        space_size = 2
        color_block_height = height//10 - 3
        l_size = line_size // 4
        wid = (l_size - 16 * space_size) // 8
        sequence = bytearray()
        background = bytes([0, 0, 0, 0])
        white = bytes([255, 255, 255, 255])
        for i in range(8):
            sequence.extend(
                (
                        background * (l_size * space_size) +  # offset y
                        (
                            # white stripe y
                            (
                                background * space_size +  # offset x
                                white * wid +  # white stripe
                                background * space_size
                            ) * 8 +  # offset x
                            (background * (l_size - 8 * (
                                    space_size * 2 + wid)))  # fill to fullline
                        )
                        +
                        (
                            # blocks
                            (
                                    b''.join(
                                        background * space_size +
                                        white +
                                        self.palette[i * 8 + j] * (wid - 2) +
                                        white +
                                        background * space_size
                                        for j in range(8)
                                    )
                                    +
                                    background * (
                                            l_size - 8 *
                                            (
                                                space_size * 2 + wid))
                            )
                        )
                        * color_block_height +  # rows of pixels for one row
                        (
                            # white stripe y
                            (
                                background * space_size +  # offset x
                                white
                                * wid +  # white stripe
                                background * space_size
                            ) * 8 +  # offset x
                            background * (
                                l_size - 8 * (space_size * 2 + wid)
                            )  # fill to full line
                            ) +
                        background * (l_size * space_size)  # offset y
                ))
        data[:] = (
                bytes(sequence)
                + background * l_size + b'\x00' * len(data))[:leng]
        self.segment_height = self.colors_block.height // 32
        self.segment_width = max(
            1, int((width - 8.5 * self.segment_height) // 8) - 2)

    def put_palettes_descriptions(self) -> None:
        """Render palette color names next to their respective color blocks."""
        for name, multiplier in (
                self.palettes_descriptions_with_height_multiplier.items()
        ):
            self.m.mlx_string_put(
                self.mlx, self.win.ptr, self.win.width // 64 * 57,
                self.win.height // 64 * multiplier, 0xFFFFFFFF, name)

    def show_menu(self) -> None:
        """Render the menu overlay with icons, text and color palette."""
        # for multiplier in self.color_blocks_height_multipliers:
        self.m.mlx_put_image_to_window(
            self.mlx, self.win.ptr, self.colors_block.ptr,
            self.win.width // 64 * 60,
            self.win.height // 64 * 9)
        self.set_images_and_position()
        self.m.mlx_put_image_to_window(
            self.mlx, self.win.ptr, self.strings_background.ptr,
            self.win.width // 64 * 57, self.win.height // 64 * 56)
        self.set_menu_data()

        for name, position in self.menu_data.items():
            self.m.mlx_string_put(
                self.mlx, self.win.ptr,
                position['width'], position['height'],
                0xFFFFFFFF, name)
        for img, position in self.images_with_height_and_width.items():
            if self.theme_changed() or img != self.save[0]:
                self.m.mlx_put_image_to_window(
                    self.mlx, self.win.ptr, img,
                    position['width'], position['height'])
        # self.put_palettes_descriptions()

    def theme_changed(self) -> bool:
        """Return True if the active theme colors differ from `self.colors`."""
        for a, b in zip(
                self.themes[self.theme_idx].values(), self.colors.values()
        ):
            if a[:3] != b[:3]:
                return True
        return False

    def open_window(self, generator: MazeGenerator, seed: int) -> None:
        """Open the visualizer window and start the main event loop."""
        self.gen = generator
        self.seed = seed
        self.show_menu()
        self.vars = {
            'm': self.m,
            'mlx': self.mlx,
            'win': self.win
        }
        self.m.mlx_key_hook(self.win.ptr, self.key_hook, self.vars)
        self.m.mlx_mouse_hook(self.win.ptr, self.mouse_hook, self.vars)
        self.generate_new_maze(False)
        self.m.mlx_loop_hook(self.mlx, self.draw_maze, self.vars)
        self.m.mlx_loop(self.mlx)

    def handle_animation(self) -> None:
        if self.path_finding and self.animation:
            self.reset_final_path()
        if not self.path_finding or self.maze_draw:
            self.generator = (
                self.gen.create_maze(self.maze, self.seed, self.animation))
        if not self.animation:
            self.create_colors(255)
        else:
            self.create_colors(self.transparency)

    def mouse_hook(self, button: int, x: int, y: int, vars: dict) -> None:
        """Handle mouse click events for UI interaction."""
        if self.cursor_over_slider(x, y):
            if button == 1:
                result = ((x - self.win.width // 128 * 119)
                          - self.corrector.width//2)
                result = result * 100 // self.slider.width
                result = result if result <= 100 else 100
                self.slider_x = result if result >= 1 else 1
            if button == 5:
                if self.slider_x > 5:
                    self.slider_x -= 5
                else:
                    self.slider_x = 1
            if button == 4:
                if self.slider_x <= 95:
                    self.slider_x += 5
                else:
                    self.slider_x = 100
            self.gen.visualisation_tempo = self.slider_x
        if self.theme_changed() and self.cursor_over_save_icon(x, y):
            self.themes[self.theme_idx] = copy(self.colors)
        if self.cursor_over_refresh_icon(x, y):
            self.generate_new_maze(False)
        if self.cursor_over_play_or_pause_icon(x, y):
            self.paused = not self.paused
        if self.cursor_over_freeze_icon(x, y):
            self.frozen = not self.frozen
        if self.cursor_over_game_icon(x, y):
            self.game_mode = not self.game_mode
            if self.game_mode:
                self.animation = False
                self.path_finding = False
                self.create_player()
            else:
                self.game_start_time = None

        if self.cursor_over_path_icon(x, y):
            self.path_finding = not self.path_finding
            if self.path_finding:
                self.game_mode = False
            if not self.path_finding:
                self.draw_ready_maze_to_window()
            if self.animation:
                self.reset_final_path()
        if self.cursor_over_animation_icon(x, y):
            self.animation = not self.animation
            self.handle_animation()
        x_start = self.win.width // 64 * 60 + self.segment_height
        x_end = x_start + self.segment_width * 8 + self.segment_height * 16
        block_width = (x_end - x_start)/8
        if x_start < x <= x_end:
            for name, reach_y in self.blocks.items():
                if (
                        reach_y['start'] + self.segment_height / 2
                        <= y <= reach_y['end']):

                    y_rel = y - reach_y['start']
                    x_rel = x - x_start

                    if (
                            0 <= y_rel < block_width * 8
                            and 0 <= x_rel < block_width * 8
                    ):
                        row = int(y_rel // block_width)
                        col = int(x_rel // block_width)
                        self.colors[name] = transparent(
                            self.palette[row*8+col], self.transparency)
        self.time = datetime.now()
        if not self.animation or self.path_finding:
            self.show_maze()
        self.show_enter_and_exit()
        self.maze_draw = True
        self.show_menu()

    def handle_game(self, key_pressed: Union[Key, Arrow]) -> None:
        """Process player movement and check for game completion."""
        self.game_path = self.game_player.move(key_pressed)
        if self.game_start_time is None:
            self.game_start_time = datetime.now()
        if self.game_path[-1] == self.maze.exit:
            self.intra_name_awaiting = True
            game_time = self.format_seconds(
                (datetime.now() - self.game_start_time).total_seconds(), 5)
            self.game_mode = False
            # intra_name = input("Put your intra name: ")
            # while intra_name not in self.usernames:
            #     intra_name = input(
            # "Wrong intra name.\nPut your intra name: ")
            print(
                "time =", game_time,
                "size =", self.maze.width,
                "x", self.maze.height,
                "seed =", self.seed)

    def new_size_maze(self, x: int, y: int) -> None:
        """Adjust maze dimensions and regenerate the maze accordingly."""
        self.maze.set_width(self.maze.width + x)
        self.maze.set_height(self.maze.height + y)
        if self.icon_size is not self.get_icon_size():
            self.icon_size = self.get_icon_size()
        self.generate_new_maze(False)

    def key_hook(self, keycode: int, vars: dict) -> None:
        """Handle keyboard events for UI interaction and game control."""
        m: Mlx = vars['m']
        win: Window = vars['win']
        mlx = vars['mlx']

        if Key.K_BACKSPACE == keycode and self.game_mode:
            self.handle_game(Key.K_BACKSPACE)

        if Key.K_G == keycode:
            self.game_mode = not self.game_mode
            if self.game_mode:
                self.animation = False
                self.path_finding = False
                self.create_player()

            else:
                self.game_start_time = None

        if Key.K_ESCAPE == keycode:
            m.mlx_destroy_window(mlx, win.ptr)
            m.mlx_loop_exit(mlx)

        if Key.K_B == keycode:
            self.brick_visible = not self.brick_visible

        if Key.K_L == keycode:
            if self.brick.bricks_in_row > 1 and self.brick.brick_w > 1:
                self.brick.bricks_in_row -= 1

        if Key.K_J == keycode:
            if self.brick.brick_w > 2:
                self.brick.bricks_in_row += 1

        if Key.K_I == keycode:
            if self.brick.rows_in_block > 2:
                self.brick.rows_in_block -= 1

        if Key.K_K == keycode:
            self.brick.rows_in_block += 1

        if Numpad.EIGHT == keycode:
            self.brick.mortar_thickness_x += 1

        if Numpad.TWO == keycode:
            if self.brick.mortar_thickness_x > 0:
                self.brick.mortar_thickness_x -= 1

        if Numpad.SIX == keycode:
            self.brick.mortar_thickness_y += 1

        if Numpad.FOUR == keycode:
            if self.brick.mortar_thickness_y > 0:
                self.brick.mortar_thickness_y -= 1

        if Key.K_W == keycode:
            self.increase_transparency()

        if Key.K_S == keycode:
            self.decrease_transparency()

        if Key.K_D == keycode:
            if self.theme_idx < 6:
                self.theme_idx += 1
            self.set_theme()

        if Key.K_A == keycode:
            if self.theme_idx > 1:
                self.theme_idx -= 1
            self.set_theme()

        if Key.K_N == keycode:
            self.generate_new_maze(True)

        if Numpad.PLUS == keycode:
            self.img.thickness += 1

        if Numpad.MINUS == keycode:
            if (self.img.thickness > 1):
                self.img.thickness -= 1

        if Arrow.LEFT == keycode:
            if self.game_mode:
                self.handle_game(Arrow.LEFT)
            elif self.maze.width > 9 and not self.maze.heart:
                self.new_size_maze(-1, 0)
            else:
                return

        if Arrow.UP == keycode:
            if self.game_mode:
                self.handle_game(Arrow.UP)
            elif self.maze.height > 7 and not self.maze.heart:
                self.new_size_maze(0, -1)
            else:
                return

        if Arrow.RIGHT == keycode:
            if self.game_mode:
                self.handle_game(Arrow.RIGHT)
            elif not self.maze.heart:
                self.new_size_maze(1, 0)
            else:
                return

        if Arrow.DOWN == keycode:
            if self.game_mode:
                self.handle_game(Arrow.DOWN)
            elif not self.maze.heart:
                self.new_size_maze(0, 1)
            else:
                return

        self.brick.size = self.img.scale
        self.brick.texture_create()
        self.time = datetime.now()
        self.show_menu()
        if keycode not in (Arrow.DOWN, Arrow.LEFT, Arrow.RIGHT, Arrow.UP):
            if not self.animation:
                self.create_colors(255)
            self.show_maze()
            if self.path_finding and not self.animation:
                self.final_path_img = Image(
                    self.m, self.mlx, self.win, self.maze)
                self.draw_path()
            if (
                self.path_finding and self.animation
                    and keycode in (Numpad.PLUS, Numpad.MINUS)):
                self.animation = False
                self.final_path_img = Image(
                    self.m, self.mlx, self.win, self.maze)
                self.draw_path()
                self.animation = True
        self.show_enter_and_exit()
        self.set_images_and_position()

    def decrease_transparency(self) -> None:
        """Decrease transparency level and update colors accordingly."""
        if self.transparency > 5:
            self.transparency -= 5
        elif self.transparency > 0:
            self.transparency -= 1
        self.create_colors()

    def increase_transparency(self) -> None:
        """Increase transparency level and update colors accordingly."""
        if self.transparency < 5:
            self.transparency += 1
        elif self.transparency > 249:
            self.transparency = 255
        elif self.transparency < 255:
            self.transparency += 5
        self.create_colors()

    def set_theme(self) -> None:
        """Apply the selected theme colors to `self.colors`."""
        self.colors = copy(self.themes[self.theme_idx])
        self.create_colors()

    def generate_new_maze(self, new_seed: bool) -> None:
        """Regenerate the maze and reset all related state."""
        self.m.mlx_put_image_to_window(
            self.mlx, self.win.ptr, self.background_img.ptr, 0, 0)
        self.seed = randint(0, 99999) if new_seed else self.seed
        self.generator = (
            self.gen.create_maze(self.maze, self.seed, self.animation))
        self.finder = self.path_finder.find_path(self.maze)
        self.path_img = Image(self.m, self.mlx, self.win, self.maze)
        self.final_path_img = Image(self.m, self.mlx, self.win, self.maze)
        thickness = self.img.thickness
        self.img = Image(self.m, self.mlx, self.win, self.maze)
        self.img.thickness = thickness
        if self.path_finding:
            self.maze_draw = True
        if not self.path_finding:
            self.maze_draw = True
        self.create_brick()
        self.offset \
            = (self.img.height - self.maze.height * self.img.scale) // 2
        self.set_start_and_finish_coordinates()
        self.load_start_and_finish_imgs()
        self.create_player()
        self.game_start_time = None
        self.create_colors(self.transparency)
        self.draw_maze(self.vars)

    def create_brick(self) -> None:
        """Initialize the Brick instance used for brick wall rendering."""
        self.brick = Brick(
            self.img.scale, self.transparency, darken,
            self.colors['Block found'], bytes([30, 30, 30, 30]))

    def set_start_and_finish_coordinates(self) -> None:
        """Compute pixel coordinates for maze entry and exit images."""
        self.enter_x = (
            self.maze.entry % self.maze.width
            ) * self.img.scale + (
                self.img.scale - self.start[1]
                )//3*2
        self.enter_y = (
            self.maze.entry // self.maze.width
            ) * self.img.scale + (
                self.img.scale - self.finish[1]
                )//3*2 + self.offset
        self.exit_x = (
            self.maze.exit % self.maze.width
            ) * self.img.scale + (
                self.img.scale - self.start[2]
                )//2
        self.exit_y = (
            self.maze.exit // self.maze.width
            ) * self.img.scale + (
                self.img.scale - self.finish[2]
                )//3*2 + self.offset

    def create_colors(self, transparency: Optional[int] = None) -> None:
        """Apply transparency to all colors in `self.colors`."""
        for color in self.colors:
            if color != 'name':
                self.colors[color] = (
                    transparent(
                        self.colors[color],
                        transparency if transparency else self.transparency))

    def cursor_over_slider(self, x: int, y: int) -> bool:
        """Return True if cursor is over the speed slider area."""
        return (self.win.width // 128 * 119 < x <
                self.win.width // 128 * 119 + self.slider.width + 10
                and self.win.height // 64 * 59 + self.slider.height < y <
                self.win.height // 64 * 59 + self.corrector.height +
                self.slider.height)

    def cursor_over_save_icon(self, x: int, y: int) -> bool:
        """Return True if cursor is over the save icon area."""
        return (self.win.width // 64 * 61 < x <
                self.win.width // 64 * 61 + self.save[1]
                and self.win.height // 64 * 57 < y <
                self.win.height // 64 * 57 +
                self.save[2])

    def cursor_over_animation_icon(self, x: int, y: int) -> bool:
        """Return True if cursor is over the animation icon area."""
        return (self.win.width // 64 * 62 < x <
                self.win.width // 64 * 62 + self.animate[1]
                and self.win.height // 64 * 57 < y <
                self.win.height // 64 * 57 +
                self.animate[2])

    def cursor_over_path_icon(self, x: int, y: int) -> bool:
        """Return True if cursor is over the path icon area."""
        return (self.win.width // 64 * 61 < x <
                self.win.width // 64 * 61 + self.animate[1]
                and self.win.height // 64 * 61 < y <
                self.win.height // 64 * 61 +
                self.animate[2])

    def cursor_over_game_icon(self, x: int, y: int) -> bool:
        """Return True if cursor is over the game icon area."""
        return (self.win.width // 64 * 62 < x <
                self.win.width // 64 * 62 + self.animate[1]
                and self.win.height // 64 * 61 < y <
                self.win.height // 64 * 61 +
                self.animate[2])

    def cursor_over_refresh_icon(self, x: int, y: int) -> bool:
        """Return True if cursor is over the refresh icon area."""
        return (self.win.width // 64 * 63 < x <
                self.win.width // 64 * 63 + self.refresh[1]
                and self.win.height // 64 * 57 < y <
                self.win.height // 64 * 57 +
                self.refresh[2])

    def cursor_over_play_or_pause_icon(self, x: int, y: int) -> bool:
        """Return True if cursor is over the play/pause icon area."""
        return (self.win.width // 64 * 63 < x <
                self.win.width // 64 * 63 + self.play[1]
                and self.win.height // 64 * 59 < y <
                self.win.height // 64 * 59 +
                self.play[2])

    def cursor_over_freeze_icon(self, x: int, y: int) -> bool:
        """Return True if cursor is over the freeze icon area."""
        return (
                self.win.width // 64 * 63 < x <
                self.win.width // 64 * 63 + self.freeze[1]
                and self.win.height // 64 * 61 < y <
                self.win.height // 64 * 61 +
                self.freeze[2])

    def get_icon_size(self) -> int:
        """Return icon size (in px) based on current cell scale.

        Icons are selected from discrete buckets depending on `self.img.scale`.
        """
        size = (
            10 if self.img.scale < 20 else
            15 if self.img.scale < 30 else
            20 if self.img.scale < 40 else
            30 if self.img.scale < 60 else
            40 if self.img.scale < 80 else
            60 if self.img.scale < 100 else
            80 if self.img.scale < 120 else
            100
        )
        return size
