from enum import Enum


class Direction(int, Enum):
    """
    Enum representing the four cardinal directions.

    Attributes:
        NORTH (int): 0
        EAST (int): 1
        SOUTH (int): 2
        WEST (int): 3
    """
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

    @property
    def opposite(self) -> "Direction":
        """
        Get the opposite direction.

        Returns:
            Direction: The opposite direction.
        """
        match self:
            case Direction.NORTH:
                return Direction.SOUTH
            case Direction.SOUTH:
                return Direction.NORTH
            case Direction.EAST:
                return Direction.WEST
            case Direction.WEST:
                return Direction.EAST
