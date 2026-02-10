from random import Random, randint
from typing import List, Union, Set, Generator, Optional, Tuple
from .Direction import Direction
from .Maze import Maze


class MazeGenerator:
    """
    A class for generating random mazes using Wilson's algorithm.
    """
    def _prepare_data(self, seed: int, width: int, height: int,
                      is_perfect: bool, heart: bool,
                      entry: int, exit: int) -> None:
        """
        Initialize the generator's internal state.

        Args:
            seed (int): Random number generator seed.
            width (int): Maze width.
            height (int): Maze height.
            is_perfect (bool): Whether the maze should be perfect.
            heart (bool): Whether to mask the maze with a heart shape.
            entry (int): Entry cell index.
            exit (int): Exit cell index.
        """
        self.maze_random = Random()
        self.maze_random.seed(seed)
        self.maze_map: List[Union[bool, int]] = [False] * (width * height)
        self.available_cells: Set[int] = {x for x in range(width * height)}

        self.width = width
        self.height = height
        self.found: Set[int] = set()
        self.seed = seed
        self.is_perfect = is_perfect
        self.visualisation_tempo = 1
        self.heart = heart

        if self.heart:
            self._generate_heart_shape()
        if not (height > 6 and width > 8):
            raise ValueError("Maze is to small for the '42' sign.")
        self._set_42()
        self._is_entry_exit_valid(entry, exit)
        self._populate_neighbor_links()
        self._clear_pattern_from_available()
        if self.heart:
            self._remove_maze_artifacts()

    def _is_entry_exit_valid(self, entry: int, exit: int) -> None:
        """
        Check if the entry and exit points are valid within the generated
            layout.

        Args:
            entry (int): Entry cell index.
            exit (int): Exit cell index.

        Raises:
            ValueError: If entry or exit coordinates are invalid
                (e.g., inside an obstacle).
        """
        if self.maze_map[entry] == 0xF or self.maze_map[entry] == 1:
            raise ValueError("Invalid start coordinates.")
        if self.maze_map[exit] == 0xF or self.maze_map[exit] == 1:
            raise ValueError("Invalid end coordinates.")

    def _set_42(self) -> None:
        """
        Carve a '42' pattern into the center of the maze.
        """
        x = self.width // 2
        y = self.height // 2

        central_cell = y * self.width + x

        self.maze_map[central_cell - 1] = 0xF
        self.maze_map[central_cell - 2] = 0xF
        self.maze_map[central_cell - 3] = 0xF
        self.maze_map[central_cell - 3 - self.width] = 0xF
        self.maze_map[central_cell - 3 - self.width * 2] = 0xF
        self.maze_map[central_cell - 1 + self.width] = 0xF
        self.maze_map[central_cell - 1 + self.width * 2] = 0xF
        self.maze_map[central_cell + 1] = 0xF
        self.maze_map[central_cell + 2] = 0xF
        self.maze_map[central_cell + 3] = 0xF
        self.maze_map[central_cell + 3 - self.width] = 0xF
        self.maze_map[central_cell + 3 - self.width * 2] = 0xF
        self.maze_map[central_cell + 2 - self.width * 2] = 0xF
        self.maze_map[central_cell + 1 - self.width * 2] = 0xF
        self.maze_map[central_cell + 1 + self.width] = 0xF
        self.maze_map[central_cell + 1 + self.width * 2] = 0xF
        self.maze_map[central_cell + 2 + self.width * 2] = 0xF
        self.maze_map[central_cell + 3 + self.width * 2] = 0xF

    def _populate_neighbor_links(self) -> None:
        """
        Pre-calculate the adjacency list for the maze grid.
        """
        self.neighbors: List[List[int]] = [[] for _ in range(self.width *
                                                             self.height)]

        for y in range(self.height):
            for x in range(self.width):
                c = y * self.width + x
                if (x > 0 and self.maze_map[c - 1] != 0xF
                        and self.maze_map[c - 1] != 1):
                    self.neighbors[c].append(c - 1)
                if (x < self.width - 1 and self.maze_map[c + 1] != 0xF
                        and self.maze_map[c + 1] != 1):
                    self.neighbors[c].append(c + 1)
                if (y > 0 and self.maze_map[c - self.width] != 0xF
                        and self.maze_map[c - self.width] != 1):
                    self.neighbors[c].append(c - self.width)
                if (y < self.height - 1
                    and self.maze_map[c + self.width] != 0xF
                        and self.maze_map[c + self.width] != 1):
                    self.neighbors[c].append(c + self.width)

    def _clear_pattern_from_available(self) -> None:
        """
        Remove cells occupied by the '42' pattern (or other obstacles) from
            the usable set.
        """
        for i, cell in enumerate(self.maze_map):
            if cell == 0xF or cell == 1:
                self.available_cells.remove(i)

    def create_maze_instant(
            self, maze: Maze, seed: Optional[int] = None) -> str:
        """
        Generate the maze instantly without visualization steps.

        Args:
            maze (Maze): The Maze object to populate.
            seed (Optional[int]): The random seed. If None, a random one
                is generated.

        Returns:
            str: A string representation of the generated maze.
        """
        if seed is None:
            seed = randint(0, 10000000000)
        self._prepare_data(seed, maze.width, maze.height,
                           maze.is_perfect, maze.heart,
                           maze.entry, maze.exit)

        end = self._choose_random_cell()
        self.maze_map[end] = 0b1111
        self.found.add(end)
        path_found: bool = False
        path: List[int] = []
        i: int = 0

        while self.available_cells:
            start = self._choose_random_cell()
            path.append(start)

            self.maze_map[start] = 16
            current_pos = start

            path_found = False
            while not path_found:
                current_pos = self._select_random_neighbor(current_pos, path)
                if self.maze_map[current_pos] == -1:
                    self.maze_map[current_pos] = 16
                    self._earase_loop(current_pos, path)
                elif self.maze_map[current_pos] != 16:
                    path_found = True

                maze.map = self.maze_map
                i += 1

            self._store_valid_path(path)
            path.clear()

        if not self.is_perfect:
            self._create_non_perfect_maze()

        maze.map = self.maze_map
        return self.get_maze_str()

    def create_maze(self, maze: Maze, seed: Optional[int] = None,
                    visualize: Optional[bool] = False) -> Generator[
                        Tuple[set[int], List[int]], None, None]:
        """
        Generate the maze step-by-step for visualization.

        Args:
            maze (Maze): The Maze object to populate.
            seed (Optional[int]): The random seed. If None, a random one
                is generated.
            visualize (bool, optional): If True, yields intermediate states.

        Yields:
            Tuple[set[int], List[int]]: Current set of found cells and the
                current random path being carved.
        """
        if seed is None:
            seed = randint(0, 10000000000)
        self._prepare_data(seed, maze.width, maze.height,
                           maze.is_perfect, maze.heart,
                           maze.entry, maze.exit)

        end = self._choose_random_cell()
        self.maze_map[end] = 0b1111
        self.found.add(end)
        path_found: bool = False
        path: List[int] = []
        i: int = 0

        while self.available_cells:
            start = self._choose_random_cell()
            path.append(start)

            self.maze_map[start] = 16
            current_pos = start

            path_found = False
            while not path_found:
                current_pos = self._select_random_neighbor(current_pos, path)
                if self.maze_map[current_pos] == -1:
                    self.maze_map[current_pos] = 16
                    self._earase_loop(current_pos, path)
                elif self.maze_map[current_pos] != 16:
                    path_found = True
                maze.map = self.maze_map

                i += 1
                if visualize and i % self.visualisation_tempo == 0:
                    yield self.found, path

            self._store_valid_path(path)
            path.clear()

        if not self.is_perfect:
            self._create_non_perfect_maze()

        maze.map = self.maze_map
        yield self.found, path

    def _create_non_perfect_maze(self) -> None:
        """
        Remove some walls to create loops in the maze (making it non-perfect).
        """
        end_blocks: Set[int] = {0b0111, 0b1011, 0b1101, 0b1110}

        for i, cell in enumerate(self.maze_map):
            if cell in end_blocks:
                new_connection = self.maze_random.choice(self.neighbors[i])
                direction = self._derive_path_directions(
                    [i, new_connection])[0]
                self._update_walls_for_passage(i, new_connection, direction)

    def get_maze_str(self) -> str:
        """
        Convert the maze map to a hex string representation.

        Returns:
            str: The string representation of the maze map data.
        """
        lines = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                cell = y * self.width + x
                row.append(f"{self.maze_map[cell]:X}")
            lines.append("".join(row))

        return "\n".join(lines)

    def _store_valid_path(self, path: List[int]) -> None:
        """
        Commit a valid random walk path to the maze structure.

        Args:
            path (List[int]): The path of cells to add to the maze.
        """
        self.maze_map[path[0]] = 0xF
        directions = self._derive_path_directions(path)

        current = path[0]

        i: int = 0
        for direction in directions:
            previous = current
            i += 1
            current = path[i]
            self._update_walls_for_passage(previous, current, direction)

        for cell in path:
            self.found.add(cell)

    def _derive_path_directions(self, path: List[int]) -> List[Direction]:
        """
        Determine the directions of movement along a path of cells.

        Args:
            path (List[int]): List of cell indices.

        Returns:
            List[Direction]: List of directions corresponding to moves between
                cells.
        """
        directions: List[Direction] = []

        previous: Optional[int] = None
        for cell in path:
            if previous is None:
                previous = cell
                continue

            if previous + 1 == cell:
                directions.append(Direction.EAST)
            elif previous - 1 == cell:
                directions.append(Direction.WEST)
            elif previous + self.width == cell:
                directions.append(Direction.SOUTH)
            elif previous - self.width == cell:
                directions.append(Direction.NORTH)
            previous = cell

        return directions

    def _update_walls_for_passage(self, previous: int,
                                  current: int,
                                  direction: Direction) -> None:
        """
        Knock down walls between two cells to create a passage.

        Args:
            previous (int): Index of the previous cell.
            current (int): Index of the current cell.
            direction (Direction): Direction of movement from previous to
                current.
        """

        previous_cell = self.maze_map[previous]
        previous_cell = previous_cell & ~(1 << direction.value)
        self.maze_map[previous] = previous_cell

        current_cell = (0b1111 if self.maze_map[current] == 16
                        else self.maze_map[current])
        current_cell = current_cell & ~(1 << direction.opposite.value)
        self.maze_map[current] = current_cell

    def _earase_loop(self, current_pos: int,
                     path: List[int]) -> None:
        """
        Backtrack and erase the current path creation attempt
            (loop eradication).

        Args:
            current_pos (int): The current cell index causing the loop.
            path (List[int]): The current path being built.
        """
        i = len(path) - 1
        while len(path) != 0 and path[-1] != current_pos:
            cell = path.pop()
            self.maze_map[cell] = False
            self.available_cells.add(cell)
            i -= 1

    def _select_random_neighbor(self, current_pos: int,
                                path: List[int]) -> int:
        """
        Choose a random neighbor to move to for the random walk.

        Args:
            current_pos (int): The current cell index.
            path (List[int]): The current random path.

        Returns:
            int: The new current cell index.
        """
        current_pos = self.maze_random.choice(self.neighbors[current_pos])

        if not self.maze_map[current_pos]:
            path.append(current_pos)
            self.maze_map[current_pos] = 16
            self.available_cells.remove(current_pos)

        elif self.maze_map[current_pos] == 16:
            self.maze_map[current_pos] = -1

        else:
            path.append(current_pos)

        return (current_pos)

    def _choose_random_cell(self) -> int:
        """
        Pick a random cell from the available (unvisited) cells.

        Returns:
            int: The index of the chosen cell.
        """
        cell = self.maze_random.choice(list(self.available_cells))
        self.available_cells.remove(cell)
        return (cell)

    def _generate_heart_shape(self) -> None:
        """
        Create a heart mask on the grid where cells outside the heart are
            marked as walls.
        """
        heart_map = []

        for y in range(self.height):
            py = (self.height / 2 - y) / (self.height / 2.5)

            for x in range(self.width):
                px = (x - self.width / 2) / (self.width / 2.5)
                y_adj = py + 0.2

                equation = (px**2 + y_adj**2 - 1)**3 - (px**2 * y_adj**3)

                if equation <= 0:
                    heart_map.append(0)  # Inside the heart
                else:
                    heart_map.append(1)  # Background

        self.maze_map = heart_map

    def _remove_maze_artifacts(self) -> None:
        """
        Clean up outline artifacts for heart shaped mazes.
        """
        for i, cell in enumerate(self.maze_map):
            if cell == 1:
                self.maze_map[i] = 0
