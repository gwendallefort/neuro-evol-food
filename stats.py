import pygame
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from io import BytesIO
from genetics import calculate_fitness
from settings import *

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
        fitnesses = [calculate_fitness(c) for c in creatures]
        alive_count = sum(1 for c in creatures if c.alive)
        food_eaten = sum(c.food_eaten for c in creatures)
        
        self.generations.append(gen_number)
        self.best_fitness.append(max(fitnesses))
        self.avg_fitness.append(np.mean(fitnesses))
        self.worst_fitness.append(min(fitnesses))
        self.total_food_eaten.append(food_eaten)
        self.survival_rate.append((alive_count / len(creatures)) * 100)
        self.creatures_count.append(len(creatures))
        self.average_speed.append(np.mean([c.speed for c in creatures if c.alive]))
    
    def render_graphs(self, width, height):
        """Render matplotlib graphs to a pygame surface"""
        if len(self.generations) < 1:
            return None
            
        fig, axes = plt.subplots(3, 2, figsize=(width/100, height/100), dpi=100)
        fig.patch.set_facecolor('#f5f5f5')
        
        # Style settings
        plt.style.use('seaborn-v0_8-whitegrid')
        
        # Graph 1: Fitness over generations
        ax1 = axes[0, 0]
        ax1.plot(self.generations, self.best_fitness, 
                        color=self.green_color, linewidth=2, label='Best')
        ax1.plot(self.generations, self.avg_fitness, 
                        color=self.blue_color, linewidth=2, label='Average')
        ax1.plot(self.generations, self.worst_fitness, 
                        color=self.red_color, linewidth=2, label='Worst', alpha=0.7)

        ax1.fill_between(self.generations, self.worst_fitness, self.best_fitness, alpha=0.3, color=self.blue_color)
        ax1.set_title('Fitness', fontweight='bold', fontsize=10)
        ax1.set_xlabel('Generation', fontsize=8)
        ax1.set_ylabel('Fitness', fontsize=8)
        ax1.legend(loc='upper left', fontsize=7)
        ax1.tick_params(labelsize=7)
        
        # Graph 2: Food eaten per generation
        ax2 = axes[0, 1]
        ax2.plot(self.generations, self.total_food_eaten, color=self.blue_color, linewidth=2, marker='o', markersize=3)
        ax2.fill_between(self.generations, self.total_food_eaten, alpha=0.3, color=self.blue_color)
        ax2.set_title('Food Eaten', fontweight='bold', fontsize=10)
        ax2.set_xlabel('Generation', fontsize=8)
        ax2.set_ylabel('Food Count', fontsize=8)
        ax2.tick_params(labelsize=7)
        
        # Graph 3: Survival rate
        ax3 = axes[1, 0]
        ax3.plot(self.generations, self.survival_rate, color=self.purple_color, linewidth=2, marker='o', markersize=3)
        ax3.fill_between(self.generations, self.survival_rate, alpha=0.3, color=self.purple_color)
        ax3.set_title('Survival Rate', fontweight='bold', fontsize=10)
        ax3.set_xlabel('Generation', fontsize=8)
        ax3.set_ylabel('Survival %', fontsize=8)
        ax3.set_ylim(0, 100)
        ax3.tick_params(labelsize=7)
        
        # Graph 4: Population size
        ax4 = axes[1, 1]
        ax4.plot(self.generations, self.creatures_count, color=self.green_color, linewidth=2, marker='o', markersize=3)
        ax4.fill_between(self.generations, self.creatures_count, alpha=0.3, color=self.green_color)
        ax4.set_title('Creatures Count', fontweight='bold', fontsize=10)
        ax4.set_xlabel('Generation', fontsize=8)
        ax4.set_ylabel('Creatures Count', fontsize=8)
        ax4.tick_params(labelsize=7)

        # Graph 5: Average speed
        ax5 = axes[2, 0]
        ax5.plot(self.generations, self.average_speed, color=self.orange_color, linewidth=2, marker='o', markersize=3)
        ax5.fill_between(self.generations, self.average_speed, alpha=0.3, color=self.orange_color)
        ax5.set_title('Average Speed', fontweight='bold', fontsize=10)
        ax5.set_xlabel('Generation', fontsize=8)
        ax5.set_ylabel('Average Speed', fontsize=8)
        ax5.tick_params(labelsize=7)

        # Graph 6: nothing yet
        ax6 = axes[2, 1]
        ax6.axis('off')  # Hide empty graph

        plt.tight_layout()
        
        # Convert to pygame surface
        buf = BytesIO()
        plt.savefig(buf, format='png', facecolor=fig.get_facecolor())
        buf.seek(0)
        plt.close(fig)
        
        return pygame.image.load(buf)

    def normalize_color(self, color):
        return tuple(c/255.0 for c in color)