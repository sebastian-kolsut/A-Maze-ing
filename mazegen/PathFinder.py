from typing import Dict, List, Deque, Set, Generator
from .Direction import Direction
from collections import deque
from .Maze import Maze
from typing import Any, Optional


class PathFinder:
    """
    A class used to find paths within a maze.
    """
    def _prepare_data(self, maze: Maze) -> None:
        """
        Extract necessary data from the Maze object.

        Args:
            maze (Maze): The Maze object to extract data from.
        """
        self.entry: int = maze.entry
        self.exit: int = maze.exit
        self.height: int = maze.height
        self.width: int = maze.width
        self.maze: list[Any] = maze.map

    def find_path_instant(self, maze: Maze) -> List[int]:
        """
        Find the shortest path from entry to exit in the maze instantly (BFS).

        Args:
            maze (Maze): The maze to solve.

        Returns:
            list[int]: The path from entry to exit as a list of cell indices.
        """
        self._prepare_data(maze)

        maze_connections: Dict[int, int] = {}
        queue: Deque[int] = deque([self.entry])
        current: int = self.entry
        visited: Set[int] = {self.entry}

        while queue:
            current = queue.popleft()

            if current == self.exit:
                break

            for neighbor in self._collect_accessible_neighbors(current):
                if neighbor not in visited:
                    queue.append(neighbor)
                    visited.add(neighbor)
                    maze_connections[neighbor] = current

        path: List[int] = []

        while current != self.entry:
            path.append(current)
            current = maze_connections[current]

        path.append(self.entry)
        path.reverse()

        return path

    def find_path(
            self, maze: Maze
            ) -> Generator[List[int], None, None]:
        """
        Find the shortest path and yield intermediate steps for visualization.

        Args:
            maze (Maze): The maze to solve.

        Yields:
            int | list[int]: Visited cells during search, and finally the
                complete path.

        Returns:
            str: A string representation of the directions (N, S, E, W) for
                the path.
        """
        self._prepare_data(maze)

        maze_connections: Dict[int, int] = {}
        queue: Deque[int] = deque([self.entry])
        current: int = self.entry
        visited: Set[int] = {self.entry}

        while queue:
            current = queue.popleft()
            yield [current]

            if current == self.exit:
                break

            for neighbor in self._collect_accessible_neighbors(current):
                if neighbor not in visited:
                    queue.append(neighbor)
                    visited.add(neighbor)
                    maze_connections[neighbor] = current

        path: List[int] = []

        while current != self.entry:
            path.append(current)
            current = maze_connections[current]

        path.append(self.entry)
        path.reverse()
        yield path

    def _collect_accessible_neighbors(self, current: int) -> Generator[int,
                                                                       None,
                                                                       None]:
        """
        Find valid neighbors for a given cell.

        Args:
            current (int): The index of the current cell.

        Yields:
            int: The index of a valid neighbor cell.
        """
        val = self.maze[current]

        if not (val & (1 << Direction.NORTH.value)):
            yield current - self.width
        if not (val & (1 << Direction.SOUTH.value)):
            yield current + self.width
        if not (val & (1 << Direction.EAST.value)):
            yield current + 1
        if not (val & (1 << Direction.WEST.value)):
            yield current - 1

    def get_str_path(self, path: List[int]) -> str:
        """
        Convert a list of cell indices into a string of cardinal directions.

        Args:
            path (List[int]): The path as a list of cell indices.

        Returns:
            str: A string composed of 'N', 'S', 'E', 'W' characters.
        """
        directions: List[str] = []

        previous: Optional[int] = None

        for cell in path:
            if previous is None:
                previous = cell
                continue

            if previous + 1 == cell:
                directions.append("E")
            elif previous - 1 == cell:
                directions.append("W")
            elif previous + self.width == cell:
                directions.append("S")
            elif previous - self.width == cell:
                directions.append("N")
            previous = cell

        str_path: str = "".join(directions)

        return str_path
