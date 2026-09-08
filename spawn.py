import random
from settings import SIM_WIDTH, WINDOW_HEIGHT


def random_spawn_position(margin=50):
    """Return a random (x, y) inside the simulation area with margin from edges."""
    return (
        random.uniform(margin, SIM_WIDTH - margin),
        random.uniform(margin, WINDOW_HEIGHT - margin),
    )
