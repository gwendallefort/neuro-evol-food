import pygame
from settings import *
from genetics import calculate_fitness
from brain_viz import visualize_network

# Recompute panel fitness summary every N frames (cheap enough to stay readable).
_FITNESS_REFRESH_FRAMES = 10
_MAX_TEXT_CACHE = 256

_text_cache = {}
_controls_cache = None
_pause_surface = None
_placeholder_surface = None
_brain_surface = None
_label_font = None

_fitness_state = {
    'frame': -_FITNESS_REFRESH_FRAMES,
    'best': 0.0,
    'avg': 0.0,
}


def _cached_text(font, text, color):
    key = (id(font), text, color)
    surface = _text_cache.get(key)
    if surface is None:
        if len(_text_cache) >= _MAX_TEXT_CACHE:
            _text_cache.clear()
        surface = font.render(text, True, color)
        _text_cache[key] = surface
    return surface


def _get_label_font():
    global _label_font
    if _label_font is None:
        _label_font = pygame.font.Font(None, 18)
    return _label_font


def _fitness_summary(creatures, frame_id):
    if frame_id - _fitness_state['frame'] < _FITNESS_REFRESH_FRAMES:
        return _fitness_state['best'], _fitness_state['avg']

    if not creatures:
        best = avg = 0.0
    else:
        fitnesses = [calculate_fitness(c) for c in creatures]
        best = max(fitnesses)
        avg = sum(fitnesses) / len(fitnesses)

    _fitness_state['frame'] = frame_id
    _fitness_state['best'] = best
    _fitness_state['avg'] = avg
    return best, avg


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
        self._content_surface = None
        self._content_size = (0, 0)

    def set_content_height(self, height):
        self.content_height = height

    def get_max_scroll(self):
        return max(0, self.content_height - self.height)

    def can_scroll(self):
        return self.content_height > self.height

    def scroll(self, amount):
        if self.can_scroll():
            self.scroll_offset = max(0, min(self.get_max_scroll(), self.scroll_offset + amount))

    def _content_width(self):
        return self.width - (self.scrollbar_width if self.can_scroll() else 0)

    def _scrollbar_metrics(self):
        """Return (handle_height, handle_y) for the current scroll state."""
        handle_height = max(30, (self.height / self.content_height) * self.height)
        max_scroll = self.get_max_scroll()
        if max_scroll > 0:
            handle_y = self.y + (self.scroll_offset / max_scroll) * (self.height - handle_height)
        else:
            handle_y = self.y
        return handle_height, handle_y

    def handle_mouse_event(self, event):
        if not self.can_scroll():
            return False

        mouse_x, mouse_y = pygame.mouse.get_pos()
        scrollbar_x = self.x + self.width - self.scrollbar_width

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if scrollbar_x <= mouse_x <= scrollbar_x + self.scrollbar_width:
                    handle_height, handle_y = self._scrollbar_metrics()

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
                handle_height, _ = self._scrollbar_metrics()
                scroll_ratio = (
                    delta_y / (self.height - handle_height)
                    if (self.height - handle_height) > 0 else 0
                )
                self.scroll_offset = max(
                    0,
                    min(
                        self.get_max_scroll(),
                        self.drag_start_offset + scroll_ratio * self.get_max_scroll(),
                    ),
                )
                return True

        return False

    def draw_scrollbar(self, screen):
        if not self.can_scroll():
            return

        scrollbar_x = self.x + self.width - self.scrollbar_width

        pygame.draw.rect(
            screen, (200, 200, 200),
            (scrollbar_x, self.y, self.scrollbar_width, self.height),
        )

        handle_height, handle_y = self._scrollbar_metrics()
        handle_color = (120, 120, 120) if self.scrollbar_dragging else (150, 150, 150)
        pygame.draw.rect(
            screen, handle_color,
            (scrollbar_x + 2, handle_y, self.scrollbar_width - 4, handle_height),
            border_radius=5,
        )

    def begin_draw(self, screen):
        """Return a reused surface to draw content on."""
        width = self._content_width()
        height = max(self.content_height, self.height)
        size = (width, height)
        if self._content_surface is None or self._content_size != size:
            # Opaque fill — no SRCALPHA needed.
            self._content_surface = pygame.Surface(size)
            self._content_size = size
        self._content_surface.fill(GRAY)
        return self._content_surface

    def end_draw(self, screen, content_surface):
        """Blit scrolled content directly onto the screen (no intermediate viewport)."""
        width = self._content_width()
        prev_clip = screen.get_clip()
        screen.set_clip(pygame.Rect(self.x, self.y, width, self.height))
        screen.blit(content_surface, (self.x, self.y - self.scroll_offset))
        screen.set_clip(prev_clip)

        self.draw_scrollbar(screen)
        pygame.draw.line(screen, DARK_GRAY, (self.x, self.y), (self.x, self.y + self.height), 2)


def draw_panel_background(screen):
    """Draw the right panel background"""
    pygame.draw.rect(screen, GRAY, (SIM_WIDTH, 0, WINDOW_WIDTH - SIM_WIDTH, WINDOW_HEIGHT))
    pygame.draw.line(screen, DARK_GRAY, (SIM_WIDTH, 0), (SIM_WIDTH, WINDOW_HEIGHT), 2)


def draw_fps(screen, font, fps, x_offset=0, y_start=0):
    """Draw FPS display at the top (integer FPS for better text-cache hits)."""
    fps_surface = _cached_text(font, f"FPS: {fps:.0f}", BLACK)
    screen.blit(fps_surface, (10 + x_offset, y_start))
    return y_start + 28


def draw_stats_text(screen, font, generation, creatures, gen_timer, stats, foods,
                    x_offset=0, y_start=20, seed=None, frame_id=0):
    alive_count = sum(1 for c in creatures if c.alive)
    current_best, current_avg = _fitness_summary(creatures, frame_id)
    total_food = sum(c.food_eaten for c in creatures)
    best_ever = max(stats.best_fitness) if stats.best_fitness else current_best

    texts = [
        f"Seed: {seed}" if seed is not None else "Seed: —",
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
        surface = _cached_text(font, text, BLACK)
        screen.blit(surface, (10 + x_offset, y_offset))
        y_offset += 28

    return y_offset


def draw_controls_help(screen, font, x_offset=0, y_start=0):
    """Draw control instructions (surfaces cached after first call)."""
    global _controls_cache
    controls = (
        "Controls:",
        "SPACE - Pause/Resume",
        "V - FOV (selected)",
        "Mouse Wheel - Scroll Panel",
    )
    if _controls_cache is None or _controls_cache[0] != id(font):
        _controls_cache = (id(font), [_cached_text(font, text, DARK_GRAY) for text in controls])

    y = y_start
    for surface in _controls_cache[1]:
        screen.blit(surface, (10 + x_offset, y))
        y += 20

    return y


def _get_brain_surface():
    global _brain_surface
    brain_width = GRAPH_PANEL_WIDTH - 20
    brain_height = BRAIN_LAYERS[0] * 30
    size = (brain_width, brain_height)
    if _brain_surface is None or _brain_surface.get_size() != size:
        _brain_surface = pygame.Surface(size)
    return _brain_surface


def draw_brain_visualization(screen, font, selected_creature, foods, creatures, x_offset=0, y_start=0):
    """Draw neural network visualization for selected creature"""
    if selected_creature is None or not selected_creature.alive:
        return y_start

    title = _cached_text(font, "Neural Network", BLACK)
    screen.blit(title, (10 + x_offset, y_start))
    y_pos = y_start + 28

    inputs = selected_creature.sense(foods, creatures)

    brain_surface = _get_brain_surface()
    brain_surface.fill(WHITE)

    visualize_network(
        selected_creature.brain, brain_surface, 10, 10,
        brain_surface.get_width() - 20, brain_surface.get_height() - 20, inputs,
    )

    screen.blit(brain_surface, (10 + x_offset, y_pos))
    y_pos += brain_surface.get_height() + 10

    fitness = calculate_fitness(selected_creature)
    stats_text = [
        f"Fitness: {fitness:.0f}",
        f"Food Eaten: {selected_creature.food_eaten}",
        f"Energy: {selected_creature.energy:.0f}",
        f"Time Alive: {selected_creature.time_alive:.1f}s",
    ]

    small_font = _get_label_font()
    for text in stats_text:
        surface = _cached_text(small_font, text, DARK_GRAY)
        screen.blit(surface, (10 + x_offset, y_pos))
        y_pos += 20

    return y_pos + 10


def draw_ui_panel(screen, scrollable_panel, font, small_font, clock, generation, creatures,
                  gen_timer, stats, graph_surface, selected_creature=None, foods=None,
                  seed=None, frame_id=0):
    """Draw the entire UI panel with scrolling"""
    global _placeholder_surface

    draw_panel_background(screen)

    content_surface = scrollable_panel.begin_draw(screen)

    current_fps = clock.get_fps()
    y_pos = draw_fps(content_surface, font, current_fps, x_offset=0, y_start=10)

    y_pos = draw_stats_text(
        content_surface, font, generation, creatures, gen_timer, stats, foods,
        x_offset=0, y_start=y_pos + 10, seed=seed, frame_id=frame_id,
    )

    y_pos += 20

    if graph_surface:
        content_surface.blit(graph_surface, (5, y_pos))
        y_pos += GRAPH_PANEL_HEIGHT
    else:
        if _placeholder_surface is None:
            _placeholder_surface = small_font.render("Graphs appear after Gen 1", True, DARK_GRAY)
        content_surface.blit(_placeholder_surface, (20, y_pos + 100))
        y_pos += 200

    y_pos += 20

    if selected_creature and foods is not None:
        y_pos = draw_brain_visualization(
            content_surface, font, selected_creature, foods, creatures,
            x_offset=0, y_start=y_pos,
        )

    y_pos += 20

    y_pos = draw_controls_help(content_surface, small_font, x_offset=0, y_start=y_pos)

    scrollable_panel.set_content_height(y_pos + 20)
    scrollable_panel.end_draw(screen, content_surface)


def draw_status_indicators(screen, font, paused):
    """Draw the paused indicator on the simulation area."""
    global _pause_surface
    if paused:
        if _pause_surface is None:
            _pause_surface = font.render("PAUSED", True, RED)
        pygame.draw.rect(screen, WHITE, (SIM_WIDTH // 2 - 45, 15, 90, 30))
        screen.blit(_pause_surface, (SIM_WIDTH // 2 - 35, 20))
