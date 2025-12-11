import pygame
import random
from settings import *
from entities import Creature, Food
from genetics import create_new_generation
from stats import Statistics
from ui import SpeedController, ScrollablePanel, draw_ui_panel, draw_status_indicators

def simulation_step(creatures, foods, dt, speed_multiplier=1):
    """Run one simulation step"""
    for creature in creatures:
        creature.update(foods, creatures, dt, speed_multiplier)
        creature.eat(foods)
    
    while len(foods) < FOOD_COUNT:
        foods.append(Food())

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Evolution Simulation")
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
    foods = [Food() for _ in range(FOOD_COUNT)]
    
    stats = Statistics()
    speed_controller = SpeedController()
    scrollable_panel = ScrollablePanel(SIM_WIDTH, 0, WINDOW_WIDTH - SIM_WIDTH, WINDOW_HEIGHT)
    
    generation = 1
    gen_timer = 0
    graph_surface = None

    running = True
    paused = False
    show_fov = False
    
    while running:
        real_dt = clock.tick(60) / 1000
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle scrollable panel events first
            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                scrollable_panel.handle_mouse_event(event)
                
            if event.type == pygame.KEYDOWN:
                # Pause
                if event.key == pygame.K_SPACE:
                    paused = not paused
                    
                # Reset
                # elif event.key == pygame.K_r:
                #     creatures = [
                #         Creature(
                #             random.uniform(50, SIM_WIDTH - 50),
                #             random.uniform(50, WINDOW_HEIGHT - 50)
                #         )
                #         for _ in range(CREATURE_COUNT)
                #     ]
                #     foods = [Food() for _ in range(FOOD_COUNT)]
                #     stats = Statistics()
                #     generation = 1
                #     gen_timer = 0
                #     graph_surface = None
                    
                # Speed controls
                elif event.key in (pygame.K_UP, pygame.K_PLUS, pygame.K_EQUALS):
                    speed_controller.increase_speed()
                elif event.key in (pygame.K_DOWN, pygame.K_MINUS):
                    speed_controller.decrease_speed()
                    
                # Preset speeds (1-6 keys)
                elif event.key == pygame.K_1:
                    speed_controller.set_speed(0)
                elif event.key == pygame.K_2:
                    speed_controller.set_speed(1)
                elif event.key == pygame.K_3:
                    speed_controller.set_speed(2)
                elif event.key == pygame.K_4:
                    speed_controller.set_speed(3)
                elif event.key == pygame.K_5:
                    speed_controller.set_speed(4)
                    
                # Turbo mode
                elif event.key == pygame.K_t:
                    speed_controller.toggle_turbo()
                
                # Toggle FOV visualization
                elif event.key == pygame.K_v:
                    show_fov = not show_fov

        # =========================
        # SIMULATION UPDATE
        # =========================
        if not paused:
            if speed_controller.turbo_mode:
                # Turbo: run many steps, skip rendering
                for _ in range(TURBO_STEPS):
                    sim_dt = 1/60
                    gen_timer += sim_dt
                    simulation_step(creatures, foods, sim_dt, speed_controller.current_speed)
                    
                    # Check generation end
                    if gen_timer >= GENERATION_TIME or all(not c.alive for c in creatures):
                        stats.record_generation(generation, creatures, gen_timer)
                        creatures = create_new_generation(creatures)
                        foods = [Food() for _ in range(FOOD_COUNT)]
                        generation += 1
                        gen_timer = 0
                        graph_surface = stats.render_graphs(GRAPH_PANEL_WIDTH, 380)
            else:
                # Normal speed
                sim_dt = real_dt * speed_controller.current_speed
                gen_timer += sim_dt
                simulation_step(creatures, foods, sim_dt, speed_controller.current_speed)
                
                # Check generation end
                if gen_timer >= GENERATION_TIME or all(not c.alive for c in creatures):
                    stats.record_generation(generation, creatures, gen_timer)
                    creatures = create_new_generation(creatures)
                    foods = [Food() for _ in range(FOOD_COUNT)]
                    generation += 1
                    gen_timer = 0
                    graph_surface = stats.render_graphs(GRAPH_PANEL_WIDTH, 380)

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

        # Right panel with scrolling
        draw_ui_panel(screen, scrollable_panel, font, small_font, clock, generation, creatures, gen_timer, stats, speed_controller, graph_surface)

        # Status indicators
        draw_status_indicators(screen, font, paused, speed_controller, show_fov)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()