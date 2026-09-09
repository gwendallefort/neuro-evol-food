# /// script
# dependencies = [
#   "numpy",
# ]
# ///
"""Neuro-evolution food simulation (desktop + pygbag/web)."""

import asyncio

import numpy as np  # noqa: F401 — must be imported early for pygbag dependency detection
import pygame

from settings import *
from entities import Creature, Food
from genetics import create_new_generation
from stats import Statistics
from ui import ScrollablePanel, draw_ui_panel, draw_status_indicators
from seed import parse_seed_arg, ui_rng
from spawn import random_spawn_position
from render_entities import draw_creature, draw_food
from web_platform import IS_WEB, configure_web_display, yield_frame


def simulation_step(creatures, foods, dt):
    """Run one simulation step"""
    for creature in creatures:
        creature.update(foods, creatures, dt)
        creature.eat(foods)


def pick_creature_at(x, y, creatures):
    """Return the first creature under (x, y), or None."""
    for creature in creatures:
        dx = x - creature.x
        dy = y - creature.y
        if dx * dx + dy * dy < creature.radius * creature.radius:
            return creature
    return None


def handle_events(scrollable_panel, creatures, state):
    """Process pygame events. Mutates state dict; returns False if quit requested."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if mouse_x < SIM_WIDTH:
                    state['selected_creature'] = pick_creature_at(mouse_x, mouse_y, creatures)
                else:
                    scrollable_panel.handle_mouse_event(event)
            else:
                scrollable_panel.handle_mouse_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                state['paused'] = not state['paused']
            elif event.key == pygame.K_v:
                state['show_fov'] = not state['show_fov']
            elif event.key == pygame.K_n:
                state['selected_creature'] = ui_rng.choice(creatures) if creatures else None

    return True


def maybe_spawn_food(foods, food_spawn_timer, dt):
    """Spawn food at a constant rate. Returns updated timer."""
    food_spawn_timer += dt
    while food_spawn_timer >= FOOD_SPAWN_INTERVAL and len(foods) < MAX_FOOD:
        foods.append(Food())
        food_spawn_timer -= FOOD_SPAWN_INTERVAL
    return food_spawn_timer


def advance_generation(creatures, foods, stats, generation, gen_timer):
    """
    End the current generation and create the next one.

    Returns (creatures, foods, generation, gen_timer, graph_surface, ended).
    ended is True if the simulation should stop.
    """
    if creatures:
        stats.record_generation(generation, creatures, gen_timer)

    creatures = create_new_generation(creatures)
    if creatures is None:
        print(
            f"Simulation ended at generation {generation}: "
            "not enough population to create a new generation."
        )
        return None, foods, generation, gen_timer, None, True

    foods = [Food() for _ in range(MAX_FOOD)]
    generation += 1
    graph_surface = stats.render_graphs(GRAPH_PANEL_WIDTH, GRAPH_PANEL_HEIGHT)
    return creatures, foods, generation, 0, graph_surface, False


def render_frame(screen, foods, creatures, selected_creature, show_fov,
                 scrollable_panel, font, small_font, clock, generation,
                 gen_timer, stats, graph_surface, paused, seed):
    screen.fill(WHITE)
    pygame.draw.rect(screen, WHITE, (0, 0, SIM_WIDTH, WINDOW_HEIGHT))

    for food in foods:
        draw_food(screen, food)
    for creature in creatures:
        draw_creature(screen, creature, show_fov)

    if selected_creature and selected_creature.alive:
        pygame.draw.circle(
            screen, YELLOW,
            (int(selected_creature.x), int(selected_creature.y)),
            selected_creature.radius + 3, 3,
        )

    draw_ui_panel(
        screen, scrollable_panel, font, small_font, clock, generation, creatures,
        gen_timer, stats, graph_surface, selected_creature, foods,
        seed=seed,
    )
    draw_status_indicators(screen, font, paused, show_fov)
    pygame.display.flip()


async def main():
    seed = parse_seed_arg()
    print(f"Simulation seed: {seed}")

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(f"Evolution Simulation (seed={seed})")

    # Pygbag's default template leaves gui_divider=2 (half-width canvas) until
    # main() returns. Our loop never returns, so restore full-width sizing here.
    configure_web_display()

    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    small_font = pygame.font.Font(None, 20)

    creatures = [Creature(*random_spawn_position()) for _ in range(CREATURE_COUNT)]
    foods = [Food() for _ in range(MAX_FOOD)]

    stats = Statistics()
    scrollable_panel = ScrollablePanel(SIM_WIDTH, 0, WINDOW_WIDTH - SIM_WIDTH, WINDOW_HEIGHT)

    generation = 1
    gen_timer = 0
    food_spawn_timer = 0
    graph_surface = None

    state = {
        'selected_creature': None,
        'paused': False,
        'show_fov': False,
    }

    running = True
    while running:
        clock.tick(60)

        running = handle_events(scrollable_panel, creatures, state)
        if not running:
            break

        if not state['paused']:
            fixed_dt = 1 / 60
            food_spawn_timer = maybe_spawn_food(foods, food_spawn_timer, fixed_dt)
            gen_timer += fixed_dt
            simulation_step(creatures, foods, fixed_dt)

            if gen_timer >= GENERATION_TIME or all(not c.alive for c in creatures):
                state['selected_creature'] = None
                creatures, foods, generation, gen_timer, graph_surface, ended = advance_generation(
                    creatures, foods, stats, generation, gen_timer,
                )
                food_spawn_timer = 0
                if ended:
                    running = False
                    continue

        render_frame(
            screen, foods, creatures, state['selected_creature'], state['show_fov'],
            scrollable_panel, font, small_font, clock, generation,
            gen_timer, stats, graph_surface, state['paused'], seed,
        )

        await yield_frame()

    if not IS_WEB:
        pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
