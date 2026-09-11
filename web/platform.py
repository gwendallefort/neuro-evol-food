"""Desktop vs pygbag/web runtime helpers.

Imported by the simulation on both platforms; web-only calls are no-ops on desktop.
"""

from __future__ import annotations

import asyncio
import sys

IS_WEB = sys.platform in ("emscripten", "wasi")


def configure_web_display() -> None:
    """Restore full-width canvas sizing and dismiss the loading shell."""
    if not IS_WEB:
        return

    import platform

    platform.window.config.gui_divider = 1
    platform.window.window_resize()
    platform.window.canvas.style.visibility = "visible"

    # dismiss custom loading overlay.
    transfer = getattr(platform.window, "transfer", None)
    if transfer is not None:
        transfer.hidden = True
        # Inline style beats the template's `#transfer { display: flex }`.
        transfer.style.display = "none"


async def yield_frame() -> None:
    """Yield to the browser event loop (required each frame under pygbag)."""
    await asyncio.sleep(0)


def quit_pygame() -> None:
    """Call pygame.quit() on desktop; skip under pygbag (keeps the runtime alive)."""
    if IS_WEB:
        return
    import pygame
    pygame.quit()
