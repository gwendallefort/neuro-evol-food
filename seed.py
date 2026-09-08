import argparse
import random
import numpy as np
from settings import SIMULATION_SEED

# UI-only RNG so pressing N / interacting does not desync the simulation seed.
ui_rng = random.Random()


def resolve_seed(cli_seed=None):
    """Pick the seed for this run: CLI > settings > random."""
    if cli_seed is not None:
        return int(cli_seed)
    if SIMULATION_SEED is not None:
        return int(SIMULATION_SEED)
    return random.randint(0, 2**31 - 1)


def seed_simulation(seed):
    """Seed every RNG used by the simulation."""
    random.seed(seed)
    np.random.seed(seed)


def parse_seed_arg(argv=None):
    """Parse --seed from the command line and return the resolved seed."""
    parser = argparse.ArgumentParser(description="Neuro-evolution food simulation")
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="RNG seed for a reproducible simulation (overrides SIMULATION_SEED)",
    )
    args, _ = parser.parse_known_args(argv)
    seed = resolve_seed(args.seed)
    seed_simulation(seed)
    return seed
