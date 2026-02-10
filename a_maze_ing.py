from random import randint
from mazegen import MazeGenerator, PathFinder, Maze
from utils import MazeVisualizer
from typing import Dict, Tuple, Set
from sys import argv


def check_entry_exit_coordinates(entry: Tuple[int, int], exit: Tuple[int, int],
                                 width: int, height: int) -> None:
    """
    Validate that entry and exit coordinates are within
    maze bounds and distinct.

    Args:
        entry (Tuple[int, int]): The (x, y) coordinates of the entry point.
        exit (Tuple[int, int]): The (x, y) coordinates of the exit point.
        width (int): The width of the maze.
        height (int): The height of the maze.

    Raises:
        ValueError: If coordinates are out of bounds or entry equals exit.
    """
    if (entry[0] < 0 or entry[0] > width - 1
        or entry[1] < 0 or entry[1] > height - 1
        or exit[0] < 0 or exit[0] > width - 1
        or exit[1] < 0 or exit[1] > height - 1
            or (entry[0] == exit[0] and entry[1] == exit[1])):
        raise ValueError("Invalid (start, end) coordinates.")


def check_true_false(key: str, config: Dict[str, str]) -> None:
    """
    Verify that a configuration key's value is a boolean string
    ('True' or 'False').

    Args:
        key (str): The dictionary key to check.
        config (Dict[str, str]): The configuration dictionary.

    Raises:
        ValueError: If the value associated with the key is not 'True'
            or 'False'.
    """
    if not (config[key].lower() == "true"
            or config[key].lower() == "false"):
        raise ValueError(f"{key}: Diffrent from 'True' or 'False'.")


def check_output_file_type(file_name: str) -> None:
    """
    Ensure that the output filename ends with '.txt'.

    Args:
        file_name (str): The filename to validate.

    Raises:
        ValueError: If the filename does not end with '.txt'.
    """
    if file_name[-4:] != ".txt":
        raise ValueError("Invalid output file type. ('*.txt' required)")


def check_if_key_is_valid(key: str) -> None:
    """
    Check if the configuration key is one of the allowed keys.

    Args:
        key (str): The configuration key to validate.

    Raises:
        KeyError: If the key is not in the set of valid keys.
    """
    keys: Set[str] = {
        "WIDTH", "HEIGHT", "ENTRY", "EXIT",
        "OUTPUT_FILE", "PERFECT", "HEART", "SEED"
        }

    if key not in keys:
        raise KeyError(f"Invalid key: '{key}'")


def main() -> None:
    """
    Main function to load config, generate maze, save output, and
    verify visualization.

    Reads configuration from a file specified in command line arguments,
    validates parameters, generates the maze and solution, writes to an
    output file, and launches the visualizer.
    """
    try:
        config = {}
        with open(argv[1]) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                key, value = line.split("=", 1)
                check_if_key_is_valid(key)
                config[key.strip()] = value.strip()
    except FileNotFoundError:
        print(f"Invalid file name: '{argv[1]}'")
        return
    except ValueError as e:
        print(f"Invalid line in '{argv[1]}'. {e}")
        return
    except KeyError as e:
        print(e)
        return

    try:
        width = int(config["WIDTH"])
        height = int(config["HEIGHT"])
        entry_str = str((config["ENTRY"])).split(",")
        exit_str = str((config["EXIT"])).split(",")
        if len(entry_str) != 2 or len(exit_str) != 2:
            raise ValueError("entry, exit accepts (x,y).")
        entry = (int(entry_str[0]), int(entry_str[1]))
        exit = (int(exit_str[0]), int(exit_str[1]))

        check_entry_exit_coordinates(entry, exit, width, height)

        check_output_file_type(config['OUTPUT_FILE'])
        output = config["OUTPUT_FILE"]

        check_true_false('PERFECT', config)
        perfect = config["PERFECT"].lower() == "true"

        heart: bool = False
        if 'HEART' in config.keys():
            check_true_false('HEART', config)
            heart = config['HEART'].lower() == "true"

        maze = Maze(width, height, entry, exit, perfect, heart)
        seed = (int(config['SEED']) if 'SEED' in list(config.keys())
                else randint(1, 9999))

        generator = MazeGenerator()
        finder = PathFinder()
        maze_map_hex = generator.create_maze_instant(maze, seed)
        path = finder.find_path_instant(maze)
        path_str = finder.get_str_path(path)

        with open(output, "w") as file:
            file.write(maze_map_hex)
            file.write(f"\n\n{entry[0]},{entry[1]}\n")
            file.write(f"{exit[0]},{exit[1]}\n")
            file.write(f"{path_str}\n")

        visualizer = MazeVisualizer(maze, finder)
        visualizer.open_window(generator, seed)

    except KeyError as e:
        print(f"Key missing from '{argv[1]}': {e}")
    except ValueError as e:
        print(e)


if __name__ == "__main__":
    main()
