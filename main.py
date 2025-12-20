import pygame
import random
import os
from datetime import datetime
from tkinter import filedialog
import tkinter as tk
from settings import *
from entities import Creature, Food
from genetics import create_new_generation
from stats import Statistics
from ui import SpeedController, ScrollablePanel, draw_ui_panel, draw_status_indicators
from save_load import save_simulation_state, load_simulation_state, save_auto

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

    # Create a folder in the saves directory
    saves_dir = "saves"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_folder = os.path.join(saves_dir, f"session_{timestamp}")
    os.makedirs(save_folder, exist_ok=True)

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
    selected_creature = None

    running = True
    paused = False
    show_fov = False
    
    # Save/Load status message
    status_message = None
    status_message_timer = 0
    
    while running:
        real_dt = clock.tick(60) / 1000
        
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
                
                # Save simulation state
                elif event.key == pygame.K_s:
                    # Hide tkinter root window
                    root = tk.Tk()
                    root.withdraw()
                    root.attributes('-topmost', True)
                    
                    # Generate default filename with timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    default_filename = f"simulation_save_{timestamp}.json"
                    
                    filename = filedialog.asksaveasfilename(
                        defaultextension=".json",
                        filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                        initialfile=default_filename,
                        title="Save Simulation State"
                    )
                    
                    root.destroy()
                    
                    if filename:
                        try:
                            # Find selected creature index
                            selected_index = None
                            if selected_creature and selected_creature in creatures:
                                selected_index = creatures.index(selected_creature)
                            
                            save_simulation_state(
                                filename, creatures, foods, stats,
                                generation, gen_timer, selected_index
                            )
                            status_message = f"Saved to {os.path.basename(filename)}"
                            status_message_timer = 3.0  # Show for 3 seconds
                            # Regenerate graph surface after save
                            if len(stats.generations) >= 2:
                                graph_surface = stats.render_graphs(GRAPH_PANEL_WIDTH, 380)
                        except Exception as e:
                            status_message = f"Save failed: {str(e)}"
                            status_message_timer = 3.0
                
                # Load simulation state
                elif event.key == pygame.K_l:
                    # Hide tkinter root window
                    root = tk.Tk()
                    root.withdraw()
                    root.attributes('-topmost', True)
                    
                    filename = filedialog.askopenfilename(
                        defaultextension=".json",
                        filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                        title="Load Simulation State"
                    )
                    
                    root.destroy()
                    
                    if filename:
                        try:
                            result = load_simulation_state(filename)
                            if result is not None:
                                loaded_creatures, loaded_foods, loaded_stats, loaded_gen, loaded_timer, selected_index = result
                                
                                # Replace current state
                                creatures = loaded_creatures
                                foods = loaded_foods
                                stats = loaded_stats
                                generation = loaded_gen
                                gen_timer = loaded_timer
                                
                                # Restore selected creature
                                if selected_index is not None and 0 <= selected_index < len(creatures):
                                    selected_creature = creatures[selected_index]
                                else:
                                    selected_creature = None
                                
                                # Regenerate graph surface
                                if len(stats.generations) >= 2:
                                    graph_surface = stats.render_graphs(GRAPH_PANEL_WIDTH, 380)
                                else:
                                    graph_surface = None
                                
                                status_message = f"Loaded from {os.path.basename(filename)}"
                                status_message_timer = 3.0
                            else:
                                status_message = "Load failed: Invalid file"
                                status_message_timer = 3.0
                        except Exception as e:
                            status_message = f"Load failed: {str(e)}"
                            status_message_timer = 3.0

                elif event.key == pygame.K_n:
                    selected_creature = random.choice(creatures) if creatures else None

        # =========================
        # SIMULATION UPDATE
        # =========================
        if not paused:
            if speed_controller.turbo_mode:
                # Turbo: run many steps, skip rendering
                for _ in range(TURBO_STEPS):
                    # sim_dt = (1/60) * speed_controller.current_speed
                    # gen_timer += 1/60  # Use fixed timestep for gen_timer
                    sim_dt = real_dt * speed_controller.current_speed
                    # Use fixed timestep for gen_timer to prevent FPS-dependent generation length
                    fixed_dt = (1/60) * speed_controller.current_speed
                    gen_timer += fixed_dt
                    simulation_step(creatures, foods, sim_dt, speed_controller.current_speed)
                    
                    # Check generation end
                    if gen_timer >= GENERATION_TIME or all(not c.alive for c in creatures):
                        selected_creature = None
                        stats.record_generation(generation, creatures, gen_timer)
                        
                        save_auto(save_folder, creatures, foods, stats, generation, gen_timer)
                        
                        creatures = create_new_generation(creatures)
                        foods = [Food() for _ in range(FOOD_COUNT)]
                        generation += 1
                        gen_timer = 0
                        graph_surface = stats.render_graphs(GRAPH_PANEL_WIDTH, 380)
            else:
                # Normal speed
                sim_dt = real_dt * speed_controller.current_speed
                # Use fixed timestep for gen_timer to prevent FPS-dependent generation length
                fixed_dt = (1/60) * speed_controller.current_speed
                gen_timer += fixed_dt
                simulation_step(creatures, foods, sim_dt, speed_controller.current_speed)
                
                # Check generation end
                if gen_timer >= GENERATION_TIME or all(not c.alive for c in creatures):
                    selected_creature = None
                    stats.record_generation(generation, creatures, gen_timer)

                    save_auto(save_folder, creatures, foods, stats, generation, gen_timer)

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
        
        # Highlight selected creature
        if selected_creature and selected_creature.alive:
            pygame.draw.circle(screen, YELLOW, (int(selected_creature.x), int(selected_creature.y)), 
                             selected_creature.radius + 3, 3)

        # Right panel with scrolling
        draw_ui_panel(screen, scrollable_panel, font, small_font, clock, generation, creatures, gen_timer, stats, speed_controller, graph_surface, selected_creature, foods)

        # Status indicators
        draw_status_indicators(screen, font, paused, speed_controller, show_fov)
        
        # Update and draw status message
        if status_message_timer > 0:
            status_message_timer -= real_dt
            if status_message_timer <= 0:
                status_message = None
            else:
                # Draw status message
                msg_surface = font.render(status_message, True, GREEN)
                msg_bg = pygame.Surface((msg_surface.get_width() + 20, msg_surface.get_height() + 10))
                msg_bg.fill((240, 240, 240))
                msg_bg.set_alpha(220)
                screen.blit(msg_bg, (SIM_WIDTH//2 - msg_surface.get_width()//2 - 10, 50))
                screen.blit(msg_surface, (SIM_WIDTH//2 - msg_surface.get_width()//2, 55))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()