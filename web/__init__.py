"""Browser/pygbag helpers used by the simulation (no-ops on desktop)."""

from .platform import IS_WEB, configure_web_display, quit_pygame, seed_from_url, yield_frame

__all__ = [
    "IS_WEB",
    "configure_web_display",
    "quit_pygame",
    "seed_from_url",
    "yield_frame",
]
