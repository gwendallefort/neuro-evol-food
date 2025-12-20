import pygame
import numpy as np
from settings import *
from genetics import calculate_fitness

class SpeedController:
    def __init__(self):
        self.speed_index = 0  # Default to 1x speed
        self.turbo_mode = False
        
    @property
    def current_speed(self):
        return SPEED_OPTIONS[self.speed_index]
    
    def increase_speed(self):
        if self.speed_index < len(SPEED_OPTIONS) - 1:
            self.speed_index += 1
            
    def decrease_speed(self):
        if self.speed_index > 0:
            self.speed_index -= 1
            
    def set_speed(self, index):
        if 0 <= index < len(SPEED_OPTIONS):
            self.speed_index = index
            
    def toggle_turbo(self):
        self.turbo_mode = not self.turbo_mode
        
    def get_display_text(self):
        if self.turbo_mode:
            return "TURBO"
        return f"{self.current_speed}x"
    
    def get_color(self):
        if self.turbo_mode:
            return ORANGE
        elif self.current_speed > 5:
            return YELLOW
        elif self.current_speed > 1:
            return GREEN
        else:
            return BLACK


class ScrollablePanel:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.scroll_offset = 0
        self.content_height = 0
        self.scrollbar_width = 15
        self.scrollbar_dragging = False
        self.drag_start_y = 0
        self.drag_start_offset = 0
        
    def set_content_height(self, height):
        self.content_height = height
        
    def get_max_scroll(self):
        return max(0, self.content_height - self.height)
        
    def can_scroll(self):
        return self.content_height > self.height
        
    def scroll(self, amount):
        if self.can_scroll():
            self.scroll_offset = max(0, min(self.get_max_scroll(), self.scroll_offset + amount))
            
    def handle_mouse_event(self, event):
        if not self.can_scroll():
            return False
            
        mouse_x, mouse_y = pygame.mouse.get_pos()
        scrollbar_x = self.x + self.width - self.scrollbar_width
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if scrollbar_x <= mouse_x <= scrollbar_x + self.scrollbar_width:
                    # Check if clicking on scrollbar handle
                    handle_height = max(30, (self.height / self.content_height) * self.height)
                    handle_y = self.y + (self.scroll_offset / self.get_max_scroll()) * (self.height - handle_height) if self.get_max_scroll() > 0 else self.y
                    
                    if handle_y <= mouse_y <= handle_y + handle_height:
                        self.scrollbar_dragging = True
                        self.drag_start_y = mouse_y
                        self.drag_start_offset = self.scroll_offset
                        return True
            elif event.button == 4:  # Scroll up
                if self.x <= mouse_x <= self.x + self.width and self.y <= mouse_y <= self.y + self.height:
                    self.scroll(-30)
                    return True
            elif event.button == 5:  # Scroll down
                if self.x <= mouse_x <= self.x + self.width and self.y <= mouse_y <= self.y + self.height:
                    self.scroll(30)
                    return True
                    
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.scrollbar_dragging = False
                
        elif event.type == pygame.MOUSEMOTION:
            if self.scrollbar_dragging:
                mouse_x, mouse_y = event.pos
                delta_y = mouse_y - self.drag_start_y
                handle_height = max(30, (self.height / self.content_height) * self.height)
                scroll_ratio = delta_y / (self.height - handle_height) if (self.height - handle_height) > 0 else 0
                self.scroll_offset = max(0, min(self.get_max_scroll(), 
                                               self.drag_start_offset + scroll_ratio * self.get_max_scroll()))
                return True
                
        return False
        
    def draw_scrollbar(self, screen):
        if not self.can_scroll():
            return
            
        scrollbar_x = self.x + self.width - self.scrollbar_width
        
        # Draw scrollbar background
        pygame.draw.rect(screen, (200, 200, 200), 
                        (scrollbar_x, self.y, self.scrollbar_width, self.height))
        
        # Draw scrollbar handle
        handle_height = max(30, (self.height / self.content_height) * self.height)
        handle_y = self.y + (self.scroll_offset / self.get_max_scroll()) * (self.height - handle_height) if self.get_max_scroll() > 0 else self.y
        
        handle_color = (120, 120, 120) if self.scrollbar_dragging else (150, 150, 150)
        pygame.draw.rect(screen, handle_color, 
                        (scrollbar_x + 2, handle_y, self.scrollbar_width - 4, handle_height), 
                        border_radius=5)
        
    def begin_draw(self, screen):
        """Returns a surface to draw content on"""
        # Create a surface for the content
        content_surface = pygame.Surface((self.width - (self.scrollbar_width if self.can_scroll() else 0), 
                                         self.content_height), pygame.SRCALPHA)
        content_surface.fill(GRAY)
        return content_surface
        
    def end_draw(self, screen, content_surface):
        """Blits the content surface with scrolling applied"""
        # Create viewport
        viewport = pygame.Surface((self.width - (self.scrollbar_width if self.can_scroll() else 0), 
                                  self.height))
        viewport.fill(GRAY)
        
        # Blit portion of content based on scroll offset
        viewport.blit(content_surface, (0, -self.scroll_offset))
        
        # Blit viewport to screen
        screen.blit(viewport, (self.x, self.y))
        
        # Draw scrollbar
        self.draw_scrollbar(screen)
        
        # Draw border
        pygame.draw.line(screen, DARK_GRAY, (self.x, self.y), (self.x, self.y + self.height), 2)


def draw_panel_background(screen):
    """Draw the right panel background"""
    pygame.draw.rect(screen, GRAY, (SIM_WIDTH, 0, WINDOW_WIDTH - SIM_WIDTH, WINDOW_HEIGHT))
    pygame.draw.line(screen, DARK_GRAY, (SIM_WIDTH, 0), (SIM_WIDTH, WINDOW_HEIGHT), 2)


def draw_speed_indicator(screen, font, speed_controller, x_offset=0, y_offset=0):
    """Draw speed control panel"""
    x = 10 + x_offset
    y = 180 + y_offset
    
    # Title
    title = font.render("Speed Control", True, BLACK)
    screen.blit(title, (x, y))
    y += 28
    
    # Speed buttons visual
    button_width = 55
    button_height = 25
    spacing = 5
    
    for i, speed in enumerate(SPEED_OPTIONS):
        bx = x + i * (button_width + spacing)
        by = y
        
        # Highlight current speed
        if i == speed_controller.speed_index and not speed_controller.turbo_mode:
            color = GREEN
            text_color = WHITE
        else:
            color = WHITE
            text_color = BLACK
            
        pygame.draw.rect(screen, color, (bx, by, button_width, button_height))
        pygame.draw.rect(screen, BLACK, (bx, by, button_width, button_height), 1)
        
        speed_text = font.render(f"{speed}x", True, text_color)
        text_rect = speed_text.get_rect(center=(bx + button_width//2, by + button_height//2))
        screen.blit(speed_text, text_rect)
    
    # Turbo button
    y += button_height + 10
    turbo_color = ORANGE if speed_controller.turbo_mode else WHITE
    turbo_text_color = WHITE if speed_controller.turbo_mode else BLACK
    pygame.draw.rect(screen, turbo_color, (x, y, 120, button_height))
    pygame.draw.rect(screen, BLACK, (x, y, 120, button_height), 1)
    turbo_text = font.render("TURBO [T]", True, turbo_text_color)
    text_rect = turbo_text.get_rect(center=(x + 60, y + button_height//2))
    screen.blit(turbo_text, text_rect)
    
    return y + button_height + 10
    

def draw_fps(screen, font, fps, x_offset=0, y_start=0):
    """Draw FPS display at the top"""
    fps_text = f"FPS: {fps:.1f}"
    fps_surface = font.render(fps_text, True, BLACK)
    screen.blit(fps_surface, (10 + x_offset, y_start))
    return y_start + 28


def draw_stats_text(screen, font, generation, creatures, gen_timer, stats, speed_controller, foods, x_offset=0, y_start=20):
    alive_count = sum(1 for c in creatures if c.alive)

    fitnesses = [calculate_fitness(c) for c in creatures]
    current_best = max(fitnesses)
    current_avg = np.mean(fitnesses)

    total_food = sum(c.food_eaten for c in creatures)
    
    best_ever = max(stats.best_fitness) if stats.best_fitness else current_best
    
    texts = [
        f"Generation: {generation}",
        f"Time Left: {max(0, GENERATION_TIME - gen_timer):.1f}s",
        "",
        f"Alive: {alive_count}/{len(creatures)}",
        f"Current Food : {len(foods)}/{MAX_FOOD}",
        f"Total Food Eaten: {total_food}",
        "",
        f"Current Best: {current_best:.0f}",
        f"Current Avg: {current_avg:.0f}",
        f"All-Time Best: {best_ever:.0f}",
    ]
    
    y_offset = y_start
    for text in texts:
        if text == "":
            y_offset += 10
            continue
        surface = font.render(text, True, BLACK)
        screen.blit(surface, (10 + x_offset, y_offset))
        y_offset += 28
    
    return y_offset


def draw_controls_help(screen, font, x_offset=0, y_start=0):
    """Draw control instructions"""
    controls = [
        "Controls:",
        "SPACE - Pause/Resume",
        "V - Show/Hide FOV",
        "UP/DOWN or +/- - Speed",
        "1-6 - Preset Speeds",
        "T - Toggle Turbo",
        "S - Save Simulation",
        "L - Load Simulation",
        "Mouse Wheel - Scroll Panel"
    ]
    
    y = y_start
    for text in controls:
        surface = font.render(text, True, DARK_GRAY)
        screen.blit(surface, (10 + x_offset, y))
        y += 20
    
    return y


def draw_brain_visualization(screen, font, selected_creature, foods, creatures, x_offset=0, y_start=0):
    """Draw neural network visualization for selected creature"""
    if selected_creature is None or not selected_creature.alive:
        return y_start
    
    # Title
    title = font.render("Neural Network", True, BLACK)
    screen.blit(title, (10 + x_offset, y_start))
    y_pos = y_start + 28
    
    # Get current inputs
    inputs = selected_creature.sense(foods, creatures)
    
    # Create surface for brain visualization
    brain_width = GRAPH_PANEL_WIDTH - 20
    brain_height = BRAIN_LAYERS[0] * 30
    brain_surface = pygame.Surface((brain_width, brain_height))
    brain_surface.fill(WHITE)
    
    # Visualize the network
    selected_creature.brain.visualize(brain_surface, 10, 10, brain_width - 20, brain_height - 20, inputs)
    
    # Blit to screen
    screen.blit(brain_surface, (10 + x_offset, y_pos))
    y_pos += brain_height + 10
    
    # Show creature stats
    from genetics import calculate_fitness
    fitness = calculate_fitness(selected_creature)
    stats_text = [
        f"Fitness: {fitness:.0f}",
        f"Food Eaten: {selected_creature.food_eaten}",
        f"Energy: {selected_creature.energy:.0f}",
        f"Time Alive: {selected_creature.time_alive:.1f}s"
    ]
    
    small_font = pygame.font.Font(None, 18)
    for text in stats_text:
        surface = small_font.render(text, True, DARK_GRAY)
        screen.blit(surface, (10 + x_offset, y_pos))
        y_pos += 20
    
    return y_pos + 10


def draw_ui_panel(screen, scrollable_panel, font, small_font, clock, generation, creatures, gen_timer, stats, speed_controller, graph_surface, selected_creature=None, foods=None):
    """Draw the entire UI panel with scrolling"""
    # Draw panel background
    draw_panel_background(screen)
    
    # Begin drawing on scrollable content
    content_surface = scrollable_panel.begin_draw(screen)
    
    # Draw FPS at top
    current_fps = clock.get_fps()
    y_pos = draw_fps(content_surface, font, current_fps, x_offset=0, y_start=10)
    
    # Draw stats below FPS
    y_pos = draw_stats_text(content_surface, font, generation, creatures, gen_timer, stats, speed_controller, foods, x_offset=0, y_start=y_pos + 10)
    
    # Add some spacing
    y_pos += 10
    
    # Draw speed control
    # y_pos = draw_speed_indicator(content_surface, font, speed_controller, x_offset=0, y_offset=y_pos - 180)
    
    # Add spacing before graphs
    y_pos += 20
    
    # Graphs
    if graph_surface:
        content_surface.blit(graph_surface, (5, y_pos))
        y_pos += GRAPH_PANEL_HEIGHT
    else:
        placeholder = small_font.render("Graphs appear after Gen 1", True, DARK_GRAY)
        content_surface.blit(placeholder, (20, y_pos + 100))
        y_pos += 200

    # Add spacing
    y_pos += 20
    
    # Draw brain visualization if creature selected
    if selected_creature and foods is not None:
        y_pos = draw_brain_visualization(content_surface, font, selected_creature, foods, creatures, x_offset=0, y_start=y_pos)
    
    # Add spacing before controls
    y_pos += 20
    
    # Controls help at the end
    y_pos = draw_controls_help(content_surface, small_font, x_offset=0, y_start=y_pos)

    # Set content height    
    scrollable_panel.set_content_height(y_pos + 20)

    # End drawing and apply scroll
    scrollable_panel.end_draw(screen, content_surface)


def draw_status_indicators(screen, font, paused, speed_controller, show_fov=True):
    """Draw status indicators on the simulation area (paused, speed, FOV)"""
    # Paused indicator
    if paused:
        pause_surface = font.render("PAUSED", True, RED)
        pygame.draw.rect(screen, WHITE, (SIM_WIDTH//2 - 45, 15, 90, 30))
        screen.blit(pause_surface, (SIM_WIDTH//2 - 35, 20))
