from mlx import Mlx
from typing import Any, Tuple


class Window:
    """Simple wrapper for an MLX window with default sizing.

    The wrapper queries the display resolution and creates a window that
    is slightly smaller than the screen to leave margins. The created
    `ptr` is the window handle used by MLX calls.
    """

    def __init__(self, mlx: Mlx, mlx_ptr: Any, desc: str):
        """Create a new window sized relative to the host screen.

        Args:
            mlx: MLX binding instance.
            mlx_ptr: MLX connection pointer.
            desc: Window title/description.
        """
        screen_size: Tuple[Any, int, int] = mlx.mlx_get_screen_size(mlx_ptr)
        *_, self.width, self.height = screen_size
        self.height -= 100
        self.width -= 100
        self.desc = desc
        self.ptr = mlx.mlx_new_window(
            mlx_ptr, self.width, self.height, self.desc)
