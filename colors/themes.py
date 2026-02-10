def get_palette() -> list[bytes]:
    """Return a list of RGBA color bytes for various game elements."""
    return [
            bytes([255, 255, 255, 255]), bytes([192, 192, 192, 255]),
            bytes([255, 192, 192, 255]), bytes([255, 224, 192, 255]),
            bytes([255, 255, 192, 255]), bytes([192, 255, 192, 255]),
            bytes([192, 255, 255, 255]), bytes([192, 192, 255, 255]),

            bytes([224, 224, 224, 255]), bytes([160, 160, 160, 255]),
            bytes([255, 160, 160, 255]), bytes([255, 192, 160, 255]),
            bytes([255, 255, 160, 255]), bytes([160, 255, 160, 255]),
            bytes([160, 255, 255, 255]), bytes([160, 160, 255, 255]),

            bytes([192, 192, 192, 255]), bytes([128, 128, 128, 255]),
            bytes([255, 128, 128, 255]), bytes([255, 160, 128, 255]),
            bytes([255, 255, 128, 255]), bytes([128, 255, 128, 255]),
            bytes([128, 255, 255, 255]), bytes([128, 128, 255, 255]),

            bytes([160, 160, 160, 255]), bytes([96, 96, 96, 255]),
            bytes([255, 96, 96, 255]), bytes([255, 128, 96, 255]),
            bytes([255, 255, 96, 255]), bytes([96, 255, 96, 255]),
            bytes([96, 255, 255, 255]), bytes([96, 96, 255, 255]),

            bytes([128, 128, 128, 255]), bytes([64, 64, 64, 255]),
            bytes([255, 0, 0, 255]), bytes([255, 128, 0, 255]),
            bytes([255, 255, 0, 255]), bytes([0, 255, 0, 255]),
            bytes([0, 255, 255, 255]), bytes([0, 0, 255, 255]),

            bytes([96, 96, 96, 255]), bytes([32, 32, 32, 255]),
            bytes([192, 0, 0, 255]), bytes([192, 96, 0, 255]),
            bytes([192, 192, 0, 255]), bytes([0, 192, 0, 255]),
            bytes([0, 192, 192, 255]), bytes([0, 0, 192, 255]),

            bytes([64, 64, 64, 255]), bytes([0, 0, 0, 255]),
            bytes([128, 0, 0, 255]), bytes([128, 64, 0, 255]),
            bytes([128, 128, 0, 255]), bytes([0, 128, 0, 255]),
            bytes([0, 128, 128, 255]), bytes([0, 0, 128, 255]),

            bytes([32, 32, 32, 255]), bytes([16, 16, 16, 255]),
            bytes([64, 0, 0, 255]), bytes([64, 32, 0, 255]),
            bytes([64, 64, 0, 255]), bytes([0, 64, 0, 255]),
            bytes([0, 64, 64, 255]), bytes([0, 0, 64, 255]),
        ]


def get_themes(transparency: int) -> dict:
    """
    Return a dict of color themes, each containing
    RGBA bytes for various game elements.
    """
    return {
        1: {
            'name': 'dgajowni',
            '42': bytes([0, 0, 255, transparency]),
            'Grid 1': bytes([240, 240, 240, transparency]),
            'Grid 2': bytes([5, 10, 5, transparency]),
            'Block found': bytes([30, 30, 30, transparency]),
            'Block not found': bytes([0, 0, 0, transparency]),
            'Snake': bytes([192, 96, 0, transparency]),
            'Background': bytes([0, 0, 0, transparency]),
        },

        2: {
            'name': 'desert',
            '42': bytes([210, 180, 140, transparency]),
            'Grid 1': bytes([238, 214, 175, transparency]),
            'Grid 2': bytes([189, 154, 122, transparency]),
            'Block found': bytes([160, 82, 45, transparency]),
            'Block not found': bytes([120, 60, 30, transparency]),
            'Snake': bytes([255, 215, 0, transparency]),
            'Background': bytes([80, 50, 20, transparency]),
        },

        3: {
            'name': 'ice',
            '42': bytes([180, 220, 255, transparency]),
            'Grid 1': bytes([220, 240, 255, transparency]),
            'Grid 2': bytes([120, 170, 200, transparency]),
            'Block found': bytes([100, 140, 180, transparency]),
            'Block not found': bytes([50, 80, 120, transparency]),
            'Snake': bytes([0, 255, 255, transparency]),
            'Background': bytes([10, 30, 60, transparency]),
        },

        4: {
            'name': 'mono',
            '42': bytes([255, 255, 255, transparency]),
            'Grid 1': bytes([200, 200, 200, transparency]),
            'Grid 2': bytes([150, 150, 150, transparency]),
            'Block found': bytes([100, 100, 100, transparency]),
            'Block not found': bytes([50, 50, 50, transparency]),
            'Snake': bytes([220, 220, 220, transparency]),
            'Background': bytes([0, 0, 0, transparency]),
        },

        5: {
            'name': 'retro',
            '42': bytes([255, 128, 0, transparency]),
            'Grid 1': bytes([255, 255, 0, transparency]),
            'Grid 2': bytes([0, 128, 128, transparency]),
            'Block found': bytes([128, 0, 128, transparency]),
            'Block not found': bytes([0, 0, 128, transparency]),
            'Snake': bytes([0, 255, 0, transparency]),
            'Background': bytes([0, 0, 0, transparency]),
        },

        6: {
            'name': 'mario',
            '42': bytes([255, 0, 0, transparency]),
            'Grid 1': bytes([255, 255, 255, transparency]),
            'Grid 2': bytes([0, 0, 255, transparency]),
            'Block found': bytes([255, 200, 0, transparency]),
            'Block not found': bytes([0, 0, 0, transparency]),
            'Snake': bytes([0, 200, 0, transparency]),
            'Background': bytes([90, 170, 255, transparency]),
        },
    }
