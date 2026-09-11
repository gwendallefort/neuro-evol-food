"""Browser/pygbag helpers used by the simulation (no-ops on desktop)."""

from .platform import IS_WEB, configure_web_display, quit_pygame, yield_frame

__all__ = ["IS_WEB", "configure_web_display", "quit_pygame", "yield_frame"]
