import pygame
import numpy as np
from genetics import calculate_fitness
from settings import *
from web_platform import IS_WEB

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from io import BytesIO
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


def _style_line_chart(ax, xs, ys, color, title, ylabel, ylim=None):
    ax.plot(xs, ys, color=color, linewidth=2, marker='o', markersize=3)
    ax.fill_between(xs, ys, alpha=0.3, color=color)
    ax.set_title(title, fontweight='bold', fontsize=10)
    ax.set_xlabel('Generation', fontsize=8)
    ax.set_ylabel(ylabel, fontsize=8)
    ax.tick_params(labelsize=7)
    if ylim is not None:
        ax.set_ylim(*ylim)


def _fig_to_pygame_surface(fig):
    buf = BytesIO()
    plt.savefig(buf, format='png', facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)
    return pygame.image.load(buf)


def _format_tick(value):
    """Compact tick label for mini charts."""
    if abs(value) >= 100 or float(value).is_integer():
        return str(int(round(value)))
    return f"{value:.1f}"


def _draw_mini_chart(surface, rect, xs, series, colors, title, font, ylim=None):
    """Draw a simple multi-series line chart with pygame (web-safe)."""
    x, y, w, h = rect
    pygame.draw.rect(surface, (245, 245, 245), rect)
    pygame.draw.rect(surface, DARK_GRAY, rect, 1)

    title_surf = font.render(title, True, BLACK)
    surface.blit(title_surf, (x + 6, y + 4))

    tick_font = font
    pad_l, pad_r, pad_t, pad_b = 36, 8, 24, 22
    plot = pygame.Rect(x + pad_l, y + pad_t, w - pad_l - pad_r, h - pad_t - pad_b)
    pygame.draw.rect(surface, WHITE, plot)
    pygame.draw.rect(surface, (200, 200, 200), plot, 1)

    if not xs or not series or not series[0]:
        return

    all_vals = [v for ys in series for v in ys]
    if ylim is not None:
        ymin, ymax = ylim
    else:
        ymin, ymax = min(all_vals), max(all_vals)
        if ymin == ymax:
            ymin -= 1
            ymax += 1

    n = len(xs)
    y_span = ymax - ymin

    # Y-axis ticks (ordinate): min / mid / max
    for frac in (0.0, 0.5, 1.0):
        val = ymin + frac * y_span
        py = plot.bottom - 1 - frac * (plot.height - 1)
        pygame.draw.line(surface, (200, 200, 200), (plot.left, int(py)), (plot.right, int(py)), 1)
        label = tick_font.render(_format_tick(val), True, DARK_GRAY)
        surface.blit(label, (plot.left - label.get_width() - 4, int(py) - label.get_height() // 2))

    # X-axis ticks (abscissa): evenly spaced generation labels
    tick_count = min(4, n)
    if tick_count == 1:
        x_indices = [0]
    else:
        x_indices = [int(round(i * (n - 1) / (tick_count - 1))) for i in range(tick_count)]
        # Deduplicate if n is small
        x_indices = list(dict.fromkeys(x_indices))

    for i in x_indices:
        px = plot.left + (i / max(1, n - 1)) * (plot.width - 1)
        pygame.draw.line(surface, (200, 200, 200), (int(px), plot.bottom), (int(px), plot.bottom + 3), 1)
        label = tick_font.render(_format_tick(xs[i]), True, DARK_GRAY)
        lx = int(px) - label.get_width() // 2
        lx = max(plot.left, min(lx, plot.right - label.get_width()))
        surface.blit(label, (lx, plot.bottom + 4))

    for ys, color in zip(series, colors):
        points = []
        for i, val in enumerate(ys):
            px = plot.left + (i / max(1, n - 1)) * (plot.width - 1)
            t = (val - ymin) / y_span
            py = plot.bottom - 1 - t * (plot.height - 1)
            points.append((int(px), int(py)))
        if len(points) >= 2:
            pygame.draw.lines(surface, color, False, points, 2)
        elif points:
            pygame.draw.circle(surface, color, points[0], 2)


def _render_graphs_pygame(stats, width, height):
    surface = pygame.Surface((width, height))
    surface.fill((245, 245, 245))
    font = pygame.font.Font(None, 18)

    charts = [
        ("Fitness", [stats.best_fitness, stats.avg_fitness, stats.worst_fitness],
         [stats.green_color_rgb, stats.blue_color_rgb, stats.red_color_rgb], None),
        ("Food Eaten", [stats.total_food_eaten], [stats.blue_color_rgb], None),
        ("Survival %", [stats.survival_rate], [stats.purple_color_rgb], (0, 100)),
        ("Creatures", [stats.creatures_count], [stats.green_color_rgb], None),
        ("Avg Speed", [stats.average_speed], [stats.orange_color_rgb], None),
    ]

    cols, rows = 2, 3
    gap = 8
    cell_w = (width - gap * (cols + 1)) // cols
    cell_h = (height - gap * (rows + 1)) // rows

    for idx, (title, series, colors, ylim) in enumerate(charts):
        row, col = divmod(idx, cols)
        rect = (
            gap + col * (cell_w + gap),
            gap + row * (cell_h + gap),
            cell_w,
            cell_h,
        )
        _draw_mini_chart(surface, rect, stats.generations, series, colors, title, font, ylim)

    return surface


def _render_graphs_matplotlib(stats, width, height):
    fig, axes = plt.subplots(3, 2, figsize=(width / 100, height / 100), dpi=100)
    fig.patch.set_facecolor('#f5f5f5')

    plt.style.use('seaborn-v0_8-whitegrid')

    ax1 = axes[0, 0]
    ax1.plot(stats.generations, stats.best_fitness,
             color=stats.green_color, linewidth=2, label='Best')
    ax1.plot(stats.generations, stats.avg_fitness,
             color=stats.blue_color, linewidth=2, label='Average')
    ax1.plot(stats.generations, stats.worst_fitness,
             color=stats.red_color, linewidth=2, label='Worst', alpha=0.7)
    ax1.fill_between(stats.generations, stats.worst_fitness, stats.best_fitness,
                     alpha=0.3, color=stats.blue_color)
    ax1.set_title('Fitness', fontweight='bold', fontsize=10)
    ax1.set_xlabel('Generation', fontsize=8)
    ax1.set_ylabel('Fitness', fontsize=8)
    ax1.legend(loc='upper left', fontsize=7)
    ax1.tick_params(labelsize=7)

    _style_line_chart(
        axes[0, 1], stats.generations, stats.total_food_eaten,
        stats.blue_color, 'Food Eaten', 'Food Count',
    )
    _style_line_chart(
        axes[1, 0], stats.generations, stats.survival_rate,
        stats.purple_color, 'Survival Rate', 'Survival %', ylim=(0, 100),
    )
    _style_line_chart(
        axes[1, 1], stats.generations, stats.creatures_count,
        stats.green_color, 'Creatures Count', 'Creatures Count',
    )
    _style_line_chart(
        axes[2, 0], stats.generations, stats.average_speed,
        stats.orange_color, 'Average Speed', 'Average Speed',
    )

    axes[2, 1].axis('off')

    plt.tight_layout()
    return _fig_to_pygame_surface(fig)


class Statistics:
    def __init__(self):
        self.generations = []
        self.best_fitness = []
        self.avg_fitness = []
        self.worst_fitness = []
        self.total_food_eaten = []
        self.survival_rate = []
        self.creatures_count = []
        self.average_speed = []

        self.green_color = self.normalize_color(GREEN)
        self.blue_color = self.normalize_color(BLUE)
        self.red_color = self.normalize_color(RED)
        self.purple_color = self.normalize_color(PURPLE)
        self.orange_color = self.normalize_color(ORANGE)
        # Integer RGB for pygame fallback charts
        self.green_color_rgb = GREEN
        self.blue_color_rgb = BLUE
        self.red_color_rgb = RED
        self.purple_color_rgb = PURPLE
        self.orange_color_rgb = ORANGE

    def record_generation(self, gen_number, creatures, gen_time):
        """Record stats at the end of each generation"""
        if not creatures:
            return

        fitnesses = [calculate_fitness(c) for c in creatures]
        alive_count = sum(1 for c in creatures if c.alive)
        food_eaten = sum(c.food_eaten for c in creatures)
        alive_speeds = [c.speed for c in creatures if c.alive]

        self.generations.append(gen_number)
        self.best_fitness.append(max(fitnesses))
        self.avg_fitness.append(float(np.mean(fitnesses)))
        self.worst_fitness.append(min(fitnesses))
        self.total_food_eaten.append(food_eaten)
        self.survival_rate.append((alive_count / len(creatures)) * 100)
        self.creatures_count.append(len(creatures))
        self.average_speed.append(float(np.mean(alive_speeds)) if alive_speeds else 0.0)

    def render_graphs(self, width, height):
        """Render graphs to a pygame surface (matplotlib on desktop, pygame on web)."""
        if len(self.generations) < 1:
            return None

        if IS_WEB or not HAS_MATPLOTLIB:
            return _render_graphs_pygame(self, width, height)
        return _render_graphs_matplotlib(self, width, height)

    def normalize_color(self, color):
        return tuple(c / 255.0 for c in color)
