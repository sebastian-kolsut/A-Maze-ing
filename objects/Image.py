from mlx import Mlx
from .Window import Window
from mazegen import Maze
from typing import Any


class Image():
    """Image buffer wrapper for MLX-backed pixel operations.

    The `Image` class encapsulates an MLX image pointer and provides a
    simple pixel buffer (`data`) plus computed `scale` / `thickness` used
    by the drawing helpers. Width/height default to layout-derived values
    when omitted.

    Args:
        mlx: MLX binding instance used to create images.
        mlx_ptr: MLX connection pointer.
        win: Window used to derive default dimensions.
        maze: Maze used to compute cell scale when not explicitly provided.
        width: Optional explicit image width.
        height: Optional explicit image height.
    """
    def __init__(self, mlx: Mlx, mlx_ptr: Any, win: Window, maze: Maze,
                 width: int | None = None,
                 height: int | None = None
                 ):
        self.height = win.height - 64
        self.width = win.width // 8 * 7
        self.set_scale(maze)
        self.height = height if height else maze.height * self.scale
        self.width = width if width else maze.width * self.scale
        self.height = height if height else win.height
        self.width = width if width else win.width // 8 * 7

        self.ptr = mlx.mlx_new_image(mlx_ptr, self.width, self.height)
        (self.data, self.bits_per_pixel, self.size_line,
            self.theformat) = mlx.mlx_get_data_addr(self.ptr)
        self.thickness = 1
        self.prev_thickness = None
        self.prev_scale = None
        self.data[:] = bytes([0]) * len(self.data)

    def set_scale(self, maze: Maze) -> None:
        """Compute a best-fit `scale` in pixels per cell for this image.

        The scale is chosen as the min of width/maze.width and
        height/maze.height so that the full maze fits into the image.

        Args:
            maze: Maze used to compute the scale.
        """
        self.scale = min(
            self.width // maze.width,
            self.height // maze.height
        )
