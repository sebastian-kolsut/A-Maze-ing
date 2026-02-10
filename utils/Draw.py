from typing import Any, Union, List
from mlx import Mlx
from objects import Image, Window, Brick
from mazegen import Maze, Direction


def _put_block(
        i: int, j: int, img: Image,
        color: bytes, thickness: int) -> None:
    """Paint a filled square block representing a single cell.

    Args:
        i: Cell x index.
        j: Cell y index.
        img: Target `Image` to modify.
        color: RGBA color bytes used to fill the block.
        thickness: Wall thickness offset applied inside the cell.
    """
    start_x = i * img.scale + thickness//2 + img.thickness
    start_y = j * img.scale + thickness//2 + img.thickness
    size = img.scale - thickness

    row = color * size

    for y in range(start_y, start_y + size):
        offset = (y * img.width + start_x) * 4
        img.data[offset: offset + size * 4] = row


def _put_brick(
        i: int, j: int, img: Image, thickness: int,
        brick: Brick) -> None:
    """Paint a textured brick cell using the `Brick` helper.

    A pseudo-random row selection produces a non-uniform brick texture.

    Args:
        i: Cell x index.
        j: Cell y index.
        img: Image to draw into.
        thickness: Inner wall thickness offset.
        brick: Brick helper that provides texture rows.
    """
    start_x = i * img.scale + thickness
    start_y = j * img.scale + thickness
    size = img.scale

    for y in range(start_y, start_y + size):
        idx = y % (brick.lines_amount-1)
        brick_even = brick.rows_even[idx]
        brick_odd = brick.rows_odd[idx]
        offset = (y * img.width + start_x) * 4
        img.data[offset: offset + size * 4]\
            = brick.mortar if y % brick.brick_h\
            < brick.mortar_thickness_y else\
            brick_even if (y // brick.brick_h) % 2 == 0\
            else brick_odd


def _put_up(color: bytes, i: int, j: int, img: Image, wall_range: tuple,
            thickness: int) -> None:
    """Paint a horizontal wall segment at the top edge of a cell.

    Args:
        color: RGBA bytes for the wall.
        i: Cell x index.
        j: Cell y index.
        img: Target image buffer.
        wall_range: Tuple indicating horizontal span relative to cell.
        thickness: Vertical thickness in pixels.
    """

    start_y = j * img.scale + thickness
    start_x = i * img.scale + thickness - 1

    y_start = start_y + (-thickness if j == 0 else 0)
    y_end = start_y + thickness

    x0 = start_x + wall_range[0]
    x1 = start_x + wall_range[1]

    x0 = max(0, x0)
    x1 = min(img.width, x1)

    if x0 >= x1:
        return

    pixels = x1 - x0
    line = color * pixels
    line_len = pixels * 4

    for y in range(y_start, y_end):
        if 0 <= y < img.height:
            offset = (y * img.width + x0) * 4
            img.data[offset:offset + line_len] = line


def _put_down(color: bytes,
              i: int, j: int, img: Image, maze: Maze, w_range: tuple,
              thickness: int
              ) -> None:
    """Paint a horizontal wall segment at the bottom edge of a cell.

    Args:
        color: RGBA wall color.
        i: Cell x index.
        j: Cell y index.
        img: Image buffer to modify.
        maze: Maze reference (used for bounds in some cases).
        w_range: Horizontal span to paint relative to cell.
        thickness: Vertical thickness in pixels.
    """

    start_x = i * img.scale + thickness - 1

    y_start = ((j + 1) * img.scale)
    y_end = y_start + thickness

    x0 = start_x + w_range[0]
    x1 = start_x + w_range[1]

    x0 = max(0, x0)
    x1 = min(img.width, x1)

    if x0 >= x1:
        return

    pixels = x1 - x0
    line = color * pixels
    line_len = pixels * 4

    for y in range(y_start, y_end):
        if 0 <= y < img.height:
            offset = (y * img.width + x0) * 4
            img.data[offset:offset + line_len] = line


def _put_left(color: bytes, i: int, j: int, img: Image, w_range: tuple,
              thickness: int) -> None:
    """Paint a vertical wall segment on the left side of a cell.

    Args:
        color: Wall color as RGBA bytes.
        i: Cell x index.
        j: Cell y index.
        img: Target `Image` buffer.
        w_range: Vertical range to paint relative to the cell.
        thickness: Horizontal thickness in pixels.
    """
    start_y = j * img.scale + thickness - 1
    x_base = i * img.scale + thickness

    data = img.data
    width = img.width
    height = img.height

    y0 = start_y + w_range[0]
    y1 = start_y + w_range[1]

    pixels = thickness
    line = color * pixels

    y0 = max(0, y0)
    y1 = min(height, y1)

    if y0 >= y1:
        return

    for y in range(y0, y1):
        offset = (y * width + x_base) * 4
        data[offset:offset + pixels*4] = line


def _put_right(color: bytes,
               i: int, j: int, img: Image, w_range: tuple,
               thickness: int
               ) -> None:
    """Paint a vertical wall on the right side of a cell.

    Args:
        color: RGBA bytes for the wall.
        i: Cell x index.
        j: Cell y index.
        img: Image target where pixels are written.
        w_range: Vertical range tuple relative to cell.
        thickness: Horizontal thickness in pixels.
    """
    start_y = j * img.scale + thickness - 1
    x_base = (i+1) * img.scale

    data = img.data
    width = img.width
    height = img.height

    y0 = start_y + w_range[0]
    y1 = start_y + w_range[1]

    pixels = thickness
    line = color * pixels
    y0 = max(0, y0)
    y1 = min(height, y1)

    if y0 >= y1:
        return
    for y in range(y0, y1):
        offset = (y * width + x_base) * 4
        data[offset:offset + pixels*4] = line


def _put_road_block(
        i: int, j: int, img: Image, color: bytes,
        thickness: int, path: list, idx: int, width: int
        ) -> None:
    """Paint a path segment (road) inside a cell connecting neighboring cells.

    Args:
        i, j: Cell coordinates.
        img: Destination `Image`.
        color: RGBA color for the path fill.
        thickness: Stroke thickness used for path padding.
        path: List of linear cell indices representing the path.
        idx: Index of current cell inside `path`.
        width: Maze width (for neighbor comparisons).
    """

    x_m = thickness if idx == 0 or path[idx - 1] - path[idx] != -1 else 0
    x_p = thickness if path[idx - 1] - path[idx] == 1 else 0
    y_m = thickness if path[idx - 1] - path[idx] != -width else 0
    y_p = thickness if path[idx - 1] - path[idx] == width else 0

    start_x = i * img.scale + img.thickness + x_m * 2 - 1
    start_y = j * img.scale + img.thickness + y_m * 2 - 1
    size_x = img.scale - img.thickness - x_m * 2 + 1 + x_p * 2
    size_y = img.scale - img.thickness - y_m * 2 + 1 + y_p * 2

    row = color * size_x

    for y in range(start_y, start_y + size_y):
        offset = (y * img.width + start_x) * 4
        img.data[offset: offset + size_x * 4] = row


def left_wall_painted(found: List[int], idx: int) -> bool:
    """Return True if the left wall is considered painted for the snake/path.

    Args:
        found: Sequence of linear indices representing visited path.
        idx: Index within the `found` list to check.

    Returns:
        bool: True if left wall should be rendered as painted.
    """
    return (
        idx > 0 and (found[idx - 1] - found[idx] != -1) and (
            idx < len(found) - 1 and found[idx + 1] - found[idx] != -1
            ) or (
                idx == len(
                    found) - 1 and found[idx] - found[idx - 1] != 1
                    ) or (idx == 0 and found[1] - found[0] != -1))


def right_wall_painted(found: List[int], idx: int) -> bool:
    """Return True if the right wall should be painted for the path.

    Args:
        found: List of visited cell indices.
        idx: Position inside `found` to inspect.
    """
    return (
        idx > 0 and (found[idx - 1] - found[idx] != 1) and (
            idx < len(found) - 1 and found[idx + 1] - found[idx] != 1
            ) or (
                idx == len(
                    found) - 1 and found[idx] - found[idx - 1] != -1
                    ) or (idx == 0 and found[1] - found[0] != 1))


def upper_wall_painted(found: List[int], idx: int, maze: Maze) -> bool:
    """Return True if the upper wall should be painted for the path.

    Args:
        found: Path as a list of cell indices.
        idx: Index inside `found`.
        maze: Maze object (for width information).
    """
    return (
        idx > 0 and (found[idx-1] - found[idx] != -maze.width) and (
            idx < len(found)-1 and found[idx+1] - found[idx] != -maze.width
            ) or (
                idx == len(
                    found) - 1 and found[idx] - found[idx - 1] != maze.width
                    ) or (idx == 0 and found[1] - found[0] != -maze.width))


def down_wall_painted(found: List[int], idx: int, maze: Maze) -> bool:
    """Return True if the bottom wall should be painted for the path."""
    return (
        idx > 0 and (found[idx-1] - found[idx] != maze.width) and (
            idx < len(found)-1 and found[idx+1] - found[idx] != maze.width
            ) or (
                idx == len(
                    found) - 1 and found[idx] - found[idx - 1] != -maze.width
                ) or (idx == 0 and found[1] - found[0] != maze.width))


def _paint_snake(
        maze: Maze, colors: dict, img: Image,
        wall_range: tuple, x: int, y: int, found: List[int]) -> None:
    """Paint a snake (animated path) fragment inside cell (x,y).

    This function draws the snake body and ensures connecting walls are
    painted appropriately depending on neighboring path segments.
    """
    _put_block(x, y, img, colors['Snake'], 0)
    idx = found.index(y * maze.width + x)
    if left_wall_painted(found, idx):
        _put_left(colors['Grid 1'], x, y, img, wall_range, img.thickness)
        _put_right(colors['Grid 1'], x-1, y, img, wall_range, img.thickness)
    if right_wall_painted(found, idx):
        _put_right(colors['Grid 1'], x, y, img, wall_range, img.thickness)
        _put_left(colors['Grid 1'], x+1, y, img, wall_range, img.thickness)
    if upper_wall_painted(found, idx, maze):
        _put_up(colors['Grid 1'], x, y, img, wall_range, img.thickness)
        _put_down(
            colors['Grid 1'], x, y-1, img, maze, wall_range, img.thickness)
    if down_wall_painted(found, idx, maze):
        _put_down(colors['Grid 1'], x, y, img, maze, wall_range, img.thickness)
        _put_up(colors['Grid 1'], x, y + 1, img, wall_range, img.thickness)
    if not left_wall_painted(found, idx):
        if (y - 1) * maze.width + x in found:
            idx_upper = found.index((y - 1) * maze.width + x)
            if left_wall_painted(found, idx_upper):
                _put_left(
                    colors['Grid 1'], x, y - 1,
                    img, wall_range, img.thickness)
                _put_right(
                    colors['Grid 1'], x - 1, y - 1,
                    img, wall_range, img.thickness)
        try:
            if not upper_wall_painted(found, idx, maze):
                if (y * maze.width + x - 1) in found:
                    idx_left = found.index(y * maze.width + x - 1)
                    if upper_wall_painted(found, idx_left, maze):
                        _put_up(
                            colors['Grid 1'], x - 1, y,
                            img, wall_range, img.thickness)
                        _put_down(
                            colors['Grid 1'], x - 1, y - 1,
                            img, maze, wall_range, img.thickness)
        except IndexError:
            return


def _is_found(
        x: int, y: int, maze: Maze,
        found: Union[list[int], set[int]]) -> bool:
    """Return True if the cell (x,y) is present in `found` set/list."""
    return (y * maze.width + x) in found


def _is_forty_two(x: int, y: int, maze: Maze) -> bool:
    """Return True if cell encodes the special '42' carved block (0xF)."""
    return maze.map[y * maze.width + x] == 15


def _south_wall_closed(x: int, y: int, maze: Maze) -> bool:
    """Return True if the SOUTH wall bit is set for the cell (x,y)."""
    return bool(
        maze.map[y * maze.width + x] & (1 << Direction.SOUTH.value))


def _north_wall_closed(x: int, y: int, maze: Maze) -> bool:
    """Return True if the NORTH wall bit is set for the cell (x,y)."""
    return bool(
        maze.map[y * maze.width + x] & (1 << Direction.NORTH.value))


def _west_wall_closed(x: int, y: int, maze: Maze) -> bool:
    """Return True if the WEST wall bit is set for the cell (x,y)."""
    return bool(
        maze.map[y * maze.width + x] & (1 << Direction.WEST.value))


def _east_wall_closed(x: int, y: int, maze: Maze) -> bool:
    """Return True if the EAST wall bit is set for the cell (x,y)."""
    return bool(
        maze.map[y * maze.width + x] & (1 << Direction.EAST.value))


def _left_block_north_wall_closed(x: int, y: int, maze: Maze) -> bool:
    """Return True if the north wall of the left neighbor is closed."""
    return bool(
        maze.map[y * maze.width + x - 1] & (1 << Direction.NORTH.value))


def _upper_block_west_wall_closed(x: int, y: int, maze: Maze) -> bool:
    """Return True if the west wall of the upper neighbor is closed."""
    return bool(
        maze.map[(y - 1) * maze.width + x] & (1 << Direction.WEST.value))


def _paint_forty_two(
        img: Image, maze: Maze, colors: dict,
        wall_range: tuple[int, int], x: int, y: int) -> None:
    """Paint the special '42' block."""
    _put_block(x, y, img, colors['42'], img.thickness)
    _put_down(colors['Grid 1'], x, y-1, img, maze, wall_range, img.thickness)
    _put_up(colors['Grid 1'], x, y+1, img, wall_range, img.thickness)
    _put_left(colors['Grid 1'], x+1, y, img, wall_range, img.thickness)


def _paint_south_wall(
        img: Image, maze: Maze, colors: dict,
        wall_range: tuple[int, int], x: int, y: int) -> None:
    """Paint the SOUTH wall of cell (x,y)."""
    _put_down(colors['Grid 1'], x, y, img, maze, wall_range, img.thickness)
    _put_up(colors['Grid 1'], x, y + 1, img, wall_range, img.thickness)


def _paint_north_wall(
        img: Image, maze: Maze, colors: dict,
        wall_range: tuple[int, int], x: int, y: int) -> None:
    """Paint the NORTH wall of cell (x,y)."""
    _put_up(colors['Grid 1'], x, y, img, wall_range, img.thickness)
    _put_down(colors['Grid 1'], x, y-1, img, maze, wall_range, img.thickness)


def _paint_west_wall(
        img: Image, maze: Maze, colors: dict,
        wall_range: tuple[int, int], x: int, y: int) -> None:
    """Paint the WEST wall of cell (x,y)."""
    _put_left(colors['Grid 1'], x, y, img, wall_range, img.thickness)
    _put_right(colors['Grid 1'], x-1, y, img, wall_range, img.thickness)


def _paint_east_wall(
        img: Image, maze: Maze, colors: dict,
        wall_range: tuple[int, int], x: int, y: int) -> None:
    """Paint the EAST wall of cell (x,y)."""
    _put_right(colors['Grid 1'], x, y, img, wall_range, img.thickness)
    _put_left(colors['Grid 1'], x+1, y, img, wall_range, img.thickness)


def _repaint_left_block_north_wall(
        img: Image, maze: Maze, colors: dict,
        wall_range: tuple[int, int], x: int, y: int) -> None:
    """Repaint the north wall of the left neighbor of cell (x,y)."""
    _put_up(colors['Grid 1'], x - 1, y, img, wall_range, img.thickness)
    _put_down(
        colors['Grid 1'], x - 1, y-1, img, maze, wall_range, img.thickness)


def _repaint_upper_block_west_wall(
        img: Image, maze: Maze, colors: dict,
        wall_range: tuple[int, int], x: int, y: int) -> None:
    """Repaint the west wall of the upper neighbor of cell (x,y)."""
    _put_left(colors['Grid 1'], x, y - 1, img, wall_range, img.thickness)
    _put_right(colors['Grid 1'], x - 1, y - 1, img, wall_range, img.thickness)


class Draw():
    """Rendering helper for maze and path drawing.

    Provides low-level pixel operations to paint maze walls, filled cells,
    bricks and animated path segments into `Image` buffers.
    """

    def draw_path(
            cls, m: Mlx, mlx: Any, maze: Maze, img: Image,
            path_img: Image, final_path_img: Image, win: Window,
            path_list: List[int], colors: dict, offset: int,
            animation: bool, game_mode: bool
    ) -> None:
        """Draw a path or a single path cell to the window.

        Args:
            m: The `mlx` binding instance.
            mlx: mlx connection pointer.
            maze: Maze object (for width/height).
            img: Temporary path image buffer.
            path_img: Small buffer used when single-cell path is shown.
            final_path_img: Accumulating buffer for full path rendering.
            win: Window to draw to.
            path_list: List of linear indices forming the path.
            colors: Theme colors mapping.
            offset: Vertical offset for the maze image in the window.
            animation: If True, blit after each path segment to animate.
        """
        if len(path_list) == 1 and not game_mode:
            x = path_list[0] % maze.width
            y = path_list[0] // maze.width
            _put_block(x, y, path_img, colors['Snake'][:3] + bytes([40]), 0)
            m.mlx_put_image_to_window(mlx, win.ptr, path_img.ptr, 0, offset)
        else:
            for idx, path in enumerate(path_list):
                x = path % maze.width
                y = path // maze.width
                _put_road_block(
                    x, y, final_path_img, colors['Snake'][:3] + bytes([255]),
                    img.thickness, path_list, idx, maze.width)
                if animation:
                    m.mlx_put_image_to_window(
                        mlx, win.ptr, final_path_img.ptr, 0, offset)
                    m.mlx_pixel_put(mlx, win.ptr, 0, 0, 0xFF000000)
            if not animation:
                m.mlx_put_image_to_window(
                    mlx, win.ptr, final_path_img.ptr, 0, offset)

    def draw_maze(
            cls, m: Mlx, mlx: Any, maze: Maze, img: Image,
            win: Window, found: tuple[set[int], List[int]], colors: dict,
            brick_visible: bool,
            brick: Brick, offset: int
            ) -> None:
        """Render the entire maze into `img` and blit to `win`.

        Args:
            cls: Unused - method kept static-style.
            m, mlx, win: MLX bindings and window.
            maze: Maze instance to render.
            img: Target `Image` buffer where maze pixels are written.
            found: Tuple of (found_set, found_list) used to draw animation.
            colors: Theme color mapping.
            brick_visible: If True draw brick textures instead of flat fill.
            brick: Brick helper to draw bricks.
            offset: Vertical offset for blitting to the window.
        """

        row = img.size_line // 4
        maze_width = maze.width * img.scale
        rest = row - maze_width
        rest_lines = (
            len(img.data) - img.size_line * maze.height * img.scale) // 4
        img.data[:] = (
            colors['Background'] * maze_width + bytes([0, 0, 0, 255]) * rest
            ) * maze.height * img.scale + (bytes([0, 0, 0, 255]) * rest_lines)
        wall_range = (-img.thickness+1, img.scale + img.thickness)
        for y in range(maze.height):
            for x in range(maze.width):
                if len(maze.map) > 0:
                    if _is_found(x, y, maze, found[0]):
                        if brick_visible:
                            _put_brick(x, y, img, 0, brick)
                        else:
                            _put_block(
                                x, y, img, colors['Block found'],
                                max(1, img.thickness//2))
                    if _is_forty_two(x, y, maze):
                        _paint_forty_two(img, maze, colors, wall_range, x, y)
                    if _is_found(x, y, maze, found[1]):
                        _paint_snake(
                            maze, colors, img, wall_range, x, y, found[1])
                    if _south_wall_closed(x, y, maze):
                        _paint_south_wall(img, maze, colors, wall_range, x, y)
                    if _north_wall_closed(x, y, maze):
                        _paint_north_wall(img, maze, colors, wall_range, x, y)
                    if _west_wall_closed(x, y, maze):
                        _paint_west_wall(img, maze, colors, wall_range, x, y)
                    if _east_wall_closed(x, y, maze):
                        _paint_east_wall(img, maze, colors, wall_range, x, y)
                    if _left_block_north_wall_closed(x, y, maze):
                        _repaint_left_block_north_wall(
                            img, maze, colors, wall_range, x, y)
                    if _upper_block_west_wall_closed(x, y, maze):
                        _repaint_upper_block_west_wall(
                            img, maze, colors, wall_range, x, y)
        m.mlx_put_image_to_window(mlx, win.ptr, img.ptr, 0, offset)
