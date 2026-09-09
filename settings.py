import math

# Window Dimensions
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
SIM_WIDTH = 750
GRAPH_PANEL_X = 760
GRAPH_PANEL_WIDTH = 430
GRAPH_PANEL_HEIGHT = 500

# Simulation Settings
CREATURE_COUNT = 25
MAX_FOOD = 30
FOOD_SPAWN_INTERVAL = 0.1  # Time in seconds between food spawns
GENERATION_TIME = 12

# Set to an int for a reproducible run, or None to pick a random seed each launch.
# You can also pass --seed on the command line (overrides this value).
SIMULATION_SEED = None

# Generation Settings
REPRODUCTION_RATE = 1.5

# Brain Settings
FOV_ANGLE = math.pi * 0.75  # Field of view in radians
NUM_SECTORS = 8  # Number of sectors to divide the field of view
SENSOR_RANGE = 200  # Maximum sensing range
BRAIN_LAYERS = [
    NUM_SECTORS * 2 + 2, # 2 inputs per sector (food + creature) + wall + energy
    8,
    2  # 2 outputs: angle change, speed
]

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (0, 100, 200)
PURPLE = (100, 0, 100)
GRAY = (240, 240, 240)
DARK_GRAY = (100, 100, 100)
YELLOW = (255, 200, 0)
ORANGE = (255, 140, 0)