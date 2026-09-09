"""Shared desktop vs pygbag/web runtime helpers."""

import asyncio
import sys

IS_WEB = sys.platform in ("emscripten", "wasi")


def configure_web_display():
    """Restore full-width canvas sizing under pygbag's default template."""
    if not IS_WEB:
        return
    import platform
    platform.window.config.gui_divider = 1
    platform.window.window_resize()


async def yield_frame():
    """Yield to the browser event loop (required each frame under pygbag)."""
    await asyncio.sleep(0)
