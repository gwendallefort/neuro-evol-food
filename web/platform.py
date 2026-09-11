"""Desktop vs pygbag/web runtime helpers.

Imported by the simulation on both platforms; web-only calls are no-ops on desktop.
"""

from __future__ import annotations

import asyncio
import sys
from urllib.parse import parse_qs

IS_WEB = sys.platform in ("emscripten", "wasi")


def seed_from_url() -> int | None:
    """Read ``?seed=`` from the browser URL; return None on desktop or if unset/invalid."""
    if not IS_WEB:
        return None

    import platform

    try:
        search = str(getattr(platform.window.location, "search", "") or "")
    except Exception:
        return None

    values = parse_qs(search.lstrip("?")).get("seed")
    if not values:
        return None
    try:
        return int(values[0])
    except (TypeError, ValueError):
        return None


def post_seed_to_parent(seed: int) -> None:
    """Notify the embedding page of the active simulation seed via postMessage."""
    if not IS_WEB:
        return

    import json
    import platform

    payload = {"type": "ne-food-seed", "seed": int(seed)}
    try:
        # Build a plain JS object.
        message = platform.window.JSON.parse(json.dumps(payload))
        targets = []
        parent = getattr(platform.window, "parent", None)
        top = getattr(platform.window, "top", None)
        if parent is not None:
            targets.append(parent)
        if top is not None and top is not parent:
            targets.append(top)
        for target in targets:
            target.postMessage(message, "*")
        print(f"post_seed_to_parent: sent {payload}")
    except Exception as exc:
        print(f"post_seed_to_parent failed: {exc!r}")


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
