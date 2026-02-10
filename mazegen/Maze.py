from typing import List, Tuple, Union


class Maze:
    """
    Represents a maze structure with dimensions, entry/exit points, and layout.
    """
    def __init__(self, width: int, height: int,
                 entry: Tuple[int, int], exit: Tuple[int, int],
                 is_perfect: bool, heart: bool = False) -> None:
        """
        Initialize a Maze object.

        Args:
            width (int): The width of the maze.
            height (int): The height of the maze.
            entry (Tuple[int, int]): The (x, y) coordinates of the entry point.
            exit (Tuple[int, int]): The (x, y) coordinates of the exit point.
            is_perfect (bool): True if the maze should be perfect (no loops),
                False otherwise.
            heart (bool, optional): True if the maze involves a heart shape.
                Defaults to False.
        """
        self.height = height
        self.width = width
        self.entry = entry[1] * width + entry[0]
        self.exit = exit[1] * width + exit[0]
        self.is_perfect = is_perfect
        self.heart = heart
        self.map: List[Union[int, bool]] = []

    def set_height(self, new_height: int) -> None:
        """
        Set a new height for the maze and reset entry/exit points.

        Args:
            new_height (int): The new height of the maze.
        """
        if new_height != self.height:
            self.height = new_height
            self.entry = 0
            self.exit = (self.height - 1) * self.width + self.width - 1

    def set_width(self, new_width: int) -> None:
        """
        Set a new width for the maze and reset entry/exit points.

        Args:
            new_width (int): The new width of the maze.
        """
        if new_width != self.width:
            self.width = new_width
            self.entry = 0
            self.exit = (self.height - 1) * self.width + self.width - 1
