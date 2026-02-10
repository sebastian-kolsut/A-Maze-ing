*This project has been created as part of the 42 curriculum by Dawid Gajownik (dgajowni) and Sebastian Kolsut (skolsut)*

# mazegen Package Documentation

The `mazegen` package is a standalone module designed for generating and solving mazes. It provides a flexible API for creating randomized mazes with customizable parameters and finding solutions.

## Installation

To install the package, you can use the provided wheel file or the source distribution:

```bash
# Install using wheel
pip install mazegen-1.0.0-py3-none-any.whl

# Or install using source distribution
pip install mazegen-1.0.0.tar.gz
```

## Usage

Here is a comprehensive example of how to use the `mazegen` package to generate a maze and find a path through it.

```python
from mazegen import MazeGenerator, PathFinder, Maze

# 1. Instantiate the Maze object
# Define dimensions (width, height)
width = 15
height = 15
# Define Start (0,0) and End (14,14) coordinates
entry_coord = (0, 0)
exit_coord = (14, 14)
# Configuration flags
is_perfect = True  # True for a perfect maze (no loops)
heart_shape = False # True for heart shaped maze

maze = Maze(width, height, entry_coord, exit_coord, is_perfect, heart_shape)

# 2. Generate the Maze
# Initialize the generator
generator = MazeGenerator()
seed = 123456  # Optional seed for reproducibility

# This populates the maze.map with the generated structure
generator.create_maze_instant(maze, seed)

# 3. Access the Structure
# The maze structure is stored in maze.map as a flat list
# Each integer represents a cell and its wall configuration
print(f"Maze Map: {maze.map}")

# 4. Get String Representation
# You can also get a hex string representation of the maze
maze_str = generator.get_maze_str()
print(f"Maze String: \n{maze_str}")

# 5. Solve the Maze
# Initialize the pathfinder
finder = PathFinder()

# Find the shortest path (returns a list of cell indices)
solution_path = finder.find_path_instant(maze)
print(f"Solution Path: {solution_path}")

# 6. Get Path as Directions
# Convert the solution path to a string of directions (N, S, E, W)
path_str = finder.get_str_path(solution_path)
print(f"Path String: {path_str}")
```

## Parameters

The `MazeGenerator` and `Maze` classes support the following custom parameters:

-   **width** (`int`): The width of the maze grid.
-   **height** (`int`): The height of the maze grid.
-   **entry** (`Tuple[int, int]`): The starting coordinates (x, y) of the maze.
-   **exit** (`Tuple[int, int]`): The ending coordinates (x, y) of the maze.
-   **is_perfect** (`bool`): If `True`, generates a perfect maze where exactly one path exists between any two points. If `False`, the maze may contain loops.
-   **heart** (`bool`): If `True`, creates a heart-shaped pattern within the maze (experimental feature).
-   **seed** (`int`): An integer seed passed to the generator to ensure deterministic and reproducible maze generation.

## Structure Access

-   **Maze Structure**: Use `maze.map` to access the generated grid. It is a one-dimensional list of integers where each index corresponds to `y * width + x`. The integer value encodes the state of the cell (walls, visited status, etc.).
-   **Solution**: The `find_path_instant` method returns a list of integers, where each integer represents the index of a cell in the path from the entry to the exit.

## API Reference

### `class Maze`
The data structure representing the maze.

*   `__init__(width: int, height: int, entry: Tuple[int, int], exit: Tuple[int, int], is_perfect: bool, heart: bool = False)`
    *   Initializes the maze grid.
*   `set_width(new_width: int)` / `set_height(new_height: int)`
    *   Updates dimensions and resets entry/exit points.

### `class MazeGenerator`
The algorithmic core for generating maze structures.

*   `create_maze_instant(maze: Maze, seed: Optional[int] = None) -> str`
    *   Generates a maze instantly using the given seed (optional) and populates the `maze` object. Returns the maze structure as a string.
*   `create_maze(maze: Maze, seed: Optional[int] = None, visualize: bool = False) -> Generator`
    *   A generator version of the creation process. Yields intermediate states `(found_cells, current_path)` for visualization purposes.
*   `get_maze_str() -> str`
    *   Returns the hex string representation of the generated maze.

### `class PathFinder`
The solver engine.

*   `find_path_instant(maze: Maze) -> List[int]`
    *   Solves the maze instantly (BFS) and returns the solution path as a list of cell indices.
*   `find_path(maze: Maze) -> Generator`
    *   A generator version of the solver. Yields visited cells during search and eventually yields the solution path.
*   `get_str_path(path: List[int]) -> str`
    *   Converts a list of path cell indices into a string of cardinal directions ('N', 'S', 'E', 'W').

## Technical Details

### Algorithm: Wilson's Algorithm
The `mazegen` package implements **Wilson's Algorithm** for maze generation.

- **Unbiased Distribution:** It generates a "Uniform Spanning Tree," ensuring that all possible perfect mazes of a given size are equally likely to be generated.
- **Loop-Erased Random Walks:** The algorithm relies on loop-erased random walks to populate the maze structure.
