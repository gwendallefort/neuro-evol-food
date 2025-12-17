import numpy as np

# Window Dimensions
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
SIM_WIDTH = 750
GRAPH_PANEL_X = 760
GRAPH_PANEL_WIDTH = 430

# Simulation Settings
CREATURE_COUNT = 25
FOOD_COUNT = 35
GENERATION_TIME = 12
TURBO_STEPS = 50 

# Brain Settings
FOV_ANGLE = np.pi * 0.75 # Field of view in radians (180 degrees)
NUM_SECTORS = 8  # Number of sectors to divide the field of view
SENSOR_RANGE = 200  # Maximum sensing range
BRAIN_LAYERS = [
    NUM_SECTORS * 2 + 2, # 2 inputs per sector (food + creature) + wall + energy
    8,
    2
]  

# Speed Options
SPEED_OPTIONS = [1, 2, 5, 10, 25]

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (0, 100, 200)
GRAY = (240, 240, 240)
DARK_GRAY = (100, 100, 100)
YELLOW = (255, 200, 0)
ORANGE = (255, 140, 0)