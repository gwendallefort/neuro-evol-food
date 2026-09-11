import argparse
import os
import random
import secrets
import time

import numpy as np
from settings import SIMULATION_SEED
from web import seed_from_url

# UI-only RNG so pressing N / interacting does not desync the simulation seed.
ui_rng = random.Random()


def _fresh_seed():
    """
    Pick an unpredictable seed for a new run.

    On desktop, Python's ``random`` module is auto-seeded from OS entropy.
    Under pygbag/Emscripten the default ``random`` state is often identical on
    every page load, so ``random.randint`` would always return the same seed.
    Prefer ``secrets`` / ``os.urandom``, then fall back to time-based entropy.
    """
    try:
        return secrets.randbelow(2**31)
    except Exception:
        pass
    try:
        return int.from_bytes(os.urandom(4), "big") & 0x7FFFFFFF
    except Exception:
        pass
    # Last resort: mix wall-clock time (enough to differ across refreshes).
    return int(time.time_ns() % (2**31))


def resolve_seed(explicit_seed=None):
    """Pick the seed for this run: CLI/URL > settings > random."""
    if explicit_seed is not None:
        return int(explicit_seed)
    if SIMULATION_SEED is not None:
        return int(SIMULATION_SEED)
    return _fresh_seed()


def seed_simulation(seed):
    """Seed every RNG used by the simulation."""
    random.seed(seed)
    np.random.seed(seed)


def parse_seed_arg(argv=None):
    """
    Resolve and apply the simulation seed.

    Priority: ``--seed`` (CLI) > ``?seed=`` (web URL) > ``SIMULATION_SEED`` > random.
    """
    parser = argparse.ArgumentParser(description="Neuro-evolution food simulation")
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="RNG seed for a reproducible simulation (overrides SIMULATION_SEED / URL)",
    )
    args, _ = parser.parse_known_args(argv)
    explicit = args.seed if args.seed is not None else seed_from_url()
    seed = resolve_seed(explicit)
    seed_simulation(seed)
    # Separate entropy so UI picks (e.g. N) stay non-deterministic on web too.
    ui_rng.seed(_fresh_seed())
    return seed
