import pygame
import random
from settings import *
from entities import Creature, Food
from genetics import create_new_generation
from stats import Statistics
from ui import ScrollablePanel, draw_ui_panel, draw_status_indicators
from seed import parse_seed_arg, ui_rng


def simulation_step(creatures, foods, dt):
    """Run one simulation step"""
    for creature in creatures:
        creature.update(foods, creatures, dt)
        creature.eat(foods)


def main():
    seed = parse_seed_arg()
    print(f"Simulation seed: {seed}")

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(f"Evolution Simulation (seed={seed})")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    small_font = pygame.font.Font(None, 20)

    # Initialize
    creatures = [
        Creature(
            random.uniform(50, SIM_WIDTH - 50),
            random.uniform(50, WINDOW_HEIGHT - 50)
        )
        for _ in range(CREATURE_COUNT)
    ]
    foods = [Food() for _ in range(MAX_FOOD)]

    stats = Statistics()
    scrollable_panel = ScrollablePanel(SIM_WIDTH, 0, WINDOW_WIDTH - SIM_WIDTH, WINDOW_HEIGHT)

    generation = 1
    gen_timer = 0
    food_spawn_timer = 0  # Timer for constant food spawning
    graph_surface = None
    selected_creature = None

    running = True
    paused = False
    show_fov = False

    while running:
        clock.tick(60)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Handle scrollable panel events first
            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                # Check if click is in simulation area (not panel)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if mouse_x < SIM_WIDTH:  # Click is in simulation area
                        # Find clicked creature
                        selected_creature = None
                        for creature in creatures:
                            dx = mouse_x - creature.x
                            dy = mouse_y - creature.y
                            if dx * dx + dy * dy < creature.radius * creature.radius:
                                selected_creature = creature
                                break
                    else:
                        # Let panel handle the event
                        scrollable_panel.handle_mouse_event(event)
                else:
                    scrollable_panel.handle_mouse_event(event)

            if event.type == pygame.KEYDOWN:
                # Pause
                if event.key == pygame.K_SPACE:
                    paused = not paused

                # Toggle FOV visualization
                elif event.key == pygame.K_v:
                    show_fov = not show_fov

                elif event.key == pygame.K_n:
                    selected_creature = ui_rng.choice(creatures) if creatures else None

        # =========================
        # SIMULATION UPDATE
        # =========================
        if not paused:
            # Fixed timestep so results do not depend on real FPS
            fixed_dt = 1 / 60
            food_spawn_timer += fixed_dt

            # Spawn food at constant rate
            while food_spawn_timer >= FOOD_SPAWN_INTERVAL and len(foods) < MAX_FOOD:
                foods.append(Food())
                food_spawn_timer -= FOOD_SPAWN_INTERVAL

            gen_timer += fixed_dt
            simulation_step(creatures, foods, fixed_dt)

            # Check generation end
            if gen_timer >= GENERATION_TIME or all(not c.alive for c in creatures):
                selected_creature = None

                if creatures:
                    stats.record_generation(generation, creatures, gen_timer)

                creatures = create_new_generation(creatures)
                if creatures is None:
                    print(
                        f"Simulation ended at generation {generation}: "
                        "not enough population to create a new generation."
                    )
                    running = False
                    continue

                foods = [Food() for _ in range(MAX_FOOD)]
                generation += 1
                gen_timer = 0
                food_spawn_timer = 0  # Reset food spawn timer on new generation
                graph_surface = stats.render_graphs(GRAPH_PANEL_WIDTH, GRAPH_PANEL_HEIGHT)

        # =========================
        # RENDERING
        # =========================
        screen.fill(WHITE)
        pygame.draw.rect(screen, WHITE, (0, 0, SIM_WIDTH, WINDOW_HEIGHT))

        # Draw simulation
        for food in foods:
            food.draw(screen)
        for creature in creatures:
            creature.draw(screen, show_fov)

        # Highlight selected creature
        if selected_creature and selected_creature.alive:
            pygame.draw.circle(screen, YELLOW, (int(selected_creature.x), int(selected_creature.y)),
                             selected_creature.radius + 3, 3)

        # Right panel with scrolling
        draw_ui_panel(
            screen, scrollable_panel, font, small_font, clock, generation, creatures,
            gen_timer, stats, graph_surface, selected_creature, foods,
            seed=seed,
        )

        # Status indicators
        draw_status_indicators(screen, font, paused, show_fov)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
