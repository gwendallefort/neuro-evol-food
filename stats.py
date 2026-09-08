import pygame
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from io import BytesIO
from genetics import calculate_fitness
from settings import *


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
        """Render matplotlib graphs to a pygame surface"""
        if len(self.generations) < 1:
            return None

        fig, axes = plt.subplots(3, 2, figsize=(width / 100, height / 100), dpi=100)
        fig.patch.set_facecolor('#f5f5f5')

        plt.style.use('seaborn-v0_8-whitegrid')

        # Graph 1: Fitness over generations (multi-series)
        ax1 = axes[0, 0]
        ax1.plot(self.generations, self.best_fitness,
                 color=self.green_color, linewidth=2, label='Best')
        ax1.plot(self.generations, self.avg_fitness,
                 color=self.blue_color, linewidth=2, label='Average')
        ax1.plot(self.generations, self.worst_fitness,
                 color=self.red_color, linewidth=2, label='Worst', alpha=0.7)
        ax1.fill_between(self.generations, self.worst_fitness, self.best_fitness,
                         alpha=0.3, color=self.blue_color)
        ax1.set_title('Fitness', fontweight='bold', fontsize=10)
        ax1.set_xlabel('Generation', fontsize=8)
        ax1.set_ylabel('Fitness', fontsize=8)
        ax1.legend(loc='upper left', fontsize=7)
        ax1.tick_params(labelsize=7)

        _style_line_chart(
            axes[0, 1], self.generations, self.total_food_eaten,
            self.blue_color, 'Food Eaten', 'Food Count',
        )
        _style_line_chart(
            axes[1, 0], self.generations, self.survival_rate,
            self.purple_color, 'Survival Rate', 'Survival %', ylim=(0, 100),
        )
        _style_line_chart(
            axes[1, 1], self.generations, self.creatures_count,
            self.green_color, 'Creatures Count', 'Creatures Count',
        )
        _style_line_chart(
            axes[2, 0], self.generations, self.average_speed,
            self.orange_color, 'Average Speed', 'Average Speed',
        )

        axes[2, 1].axis('off')

        plt.tight_layout()
        return _fig_to_pygame_surface(fig)

    def normalize_color(self, color):
        return tuple(c / 255.0 for c in color)
