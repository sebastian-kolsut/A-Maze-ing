from random import randint
from typing import Callable, Optional


class Brick:
    """Brick texture generator used to render wall interiors.

    The class generates a procedural brick texture represented as byte
    rows (`rows_even`, `rows_odd`) and a `mortar` line used by the
    renderer. It is parametrized by scale (`size`), transparency and
    color helpers.

    Args:
        size: Cell size in pixels used to compute brick subdivisions.
        transparency: Alpha level (0-255) applied to bricks/mortar.
        darken: Callable that darkens a base color by a float factor.
        color: Optional base RGB(A) bytes for bricks.
        mortar_color: Optional RGBA bytes for mortar.
    """

    def __init__(
            self, size: int, transparency: int,
            darken: Callable[[bytes, float], bytes],
            color: Optional[bytes] = None,
            mortar_color: Optional[bytes] = None):
        self.mortar_thickness_y = 1
        self.mortar_thickness_x = 2
        self.bricks_in_row = 2
        self.rows_in_block = 5
        self.darken = darken
        self.size = size
        self.transparency = transparency
        color = None
        mortar_color = None
        self.color = bytes([28, 53, 116, 255])\
            if not color else color[:3] + bytes([255])
        self.mortar_color = bytes([30, 30, 30, 255])\
            if not mortar_color else mortar_color[:3] + bytes([255])
        self.lines_amount = 21
        self.texture_create()

    def texture_create(self) -> None:
        """Build internal texture rows (`rows_even`, `rows_odd`) and mortar.

        This computes brick width/height, populates `rows_odd` and
        `rows_even` with bytearrays representing horizontal lines of the
        texture and prepares `self.mortar` for fast fills.
        """
        self.brick_w = (self.size // self.bricks_in_row
                        - self.mortar_thickness_x)
        self.brick_h = self.size // self.rows_in_block
        while (
                self.size -
                (
                        (self.brick_w + self.mortar_thickness_x)
                * self.bricks_in_row
                ) > self.brick_w
                + self.mortar_thickness_x):
            self.bricks_in_row += 1

        self.half_brick_w = self.brick_w // 2

        sum_row_1 = ((self.brick_w + self.mortar_thickness_x)
                     * (self.bricks_in_row - 1) + self.brick_w)
        sum_row_3 = (self.half_brick_w + self.mortar_thickness_x
                     + (self.brick_w + self.mortar_thickness_x)
                     * (self.bricks_in_row - 1))

        self.rows_odd = [bytearray() for _ in range(self.lines_amount)]
        self.rows_even = [bytearray() for _ in range(self.lines_amount)]
        a = 6
        b = 9

        for row in self.rows_odd:
            for _ in range(self.bricks_in_row - 1):
                for _ in range(self.brick_w):
                    row.extend(self.darken(self.color, randint(a, b)/10))
                for _ in range(self.mortar_thickness_x):
                    row.extend(self.mortar_color)
            for _ in range(self.brick_w):
                row.extend(self.darken(self.color, randint(a, b)/10))
            for _ in range(self.size - sum_row_1):
                row.extend(self.mortar_color)

        for row in self.rows_even:
            for i in range(self.half_brick_w):
                row.extend(self.darken(self.color, randint(a, b) / 10))
            for i in range(self.mortar_thickness_x):
                row.extend(self.mortar_color)
            for _ in range(self.bricks_in_row - 1):
                for i in range(self.brick_w):
                    row.extend(self.darken(self.color, randint(a, b) / 10))
                for i in range(self.mortar_thickness_x):
                    row.extend(self.mortar_color)
            for i in range(self.size - sum_row_3):
                row.extend(self.darken(self.color, randint(a, b) / 10))

        self.mortar = self.mortar_color * self.size
