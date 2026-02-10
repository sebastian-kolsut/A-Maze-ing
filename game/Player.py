from mazegen import Maze
from enums import Arrow, Key
from mazegen import Direction
from typing import List, Union


class Player:
    """
    Represents a player navigating through a maze.
    """
    def __init__(self, maze: Maze) -> None:
        """
        Initialize the player with the given maze.

        Args:
            maze (Maze): The maze object the player will navigate.
        """
        self.current_position = maze.entry
        self.taret_position = maze.exit
        self.maze_map = maze.map
        self.width = maze.width
        self.path: List[int] = [maze.entry]

    def move(self, key_pressed: Union[Key, Arrow]) -> List[int]:
        """
        Update the player's position based on the key pressed.

        Args:
            key_pressed (Union[Key, Arrow]): The key or arrow pressed by
                the user.

        Returns:
            List[int]: The current path of the player as a list of cell
                indices.
        """
        direction = self._get_direction(key_pressed)

        if direction is not None and self._is_valid_move(direction):
            self._get_next_cell(direction)
            if self.current_position in self.path:
                self._remove_loop()
            else:
                self.path.append(self.current_position)

        elif key_pressed == Key.K_BACKSPACE and len(self.path) > 1:
            self.path.pop()
            self.current_position = self.path[-1]

        return self.path

    @staticmethod
    def _get_direction(
            key_pressed: Union[Key, Arrow]) -> Union[Direction, None]:
        """
        Convert a key press into a directional enum.

        Args:
            key_pressed (Union[Key, Arrow]): The input key.

        Returns:
            Union[Direction, None]: The corresponding Direction if valid,
                else None.
        """
        direction: Union[Direction, None] = None

        if key_pressed == Arrow.UP:
            direction = Direction.NORTH
        elif key_pressed == Arrow.RIGHT:
            direction = Direction.EAST
        elif key_pressed == Arrow.DOWN:
            direction = Direction.SOUTH
        elif key_pressed == Arrow.LEFT:
            direction = Direction.WEST

        return direction

    def _is_valid_move(self, direction: Direction) -> bool:
        """
        Check if moving in the given direction is possible (i.e., no wall).

        Args:
            direction (Direction): The direction to check.

        Returns:
            bool: True if the move is valid, False otherwise.
        """
        val = self.maze_map[self.current_position]

        return not (val & (1 << direction.value))

    def _get_next_cell(self, direction: Direction) -> None:
        """
        Calculate and update the new position based on the direction.

        Args:
            direction (Direction): The direction of movement.
        """
        if direction == Direction.NORTH:
            self.current_position -= self.width
        if direction == Direction.SOUTH:
            self.current_position += self.width
        if direction == Direction.EAST:
            self.current_position += 1
        if direction == Direction.WEST:
            self.current_position -= 1

    def _remove_loop(self) -> None:
        """
        Remove the loop from the current path when the player backtracks.
        """
        while len(self.path) != 0 and self.path[-1] != self.current_position:
            self.path.pop()
