import pygame
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from io import BytesIO
from genetics import calculate_fitness

class Statistics:
    def __init__(self):
        self.generations = []
        self.best_fitness = []
        self.avg_fitness = []
        self.worst_fitness = []
        self.total_food_eaten = []
        self.survival_rate = []
        self.creatures_count = []
        
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
    
    def render_graphs(self, width, height):
        """Render matplotlib graphs to a pygame surface"""
        if len(self.generations) < 1:
            return None
            
        fig, axes = plt.subplots(2, 2, figsize=(width/100, height/100), dpi=100)
        fig.patch.set_facecolor('#f5f5f5')
        
        # Style settings
        plt.style.use('seaborn-v0_8-whitegrid')
        colors = ['#2ecc71', '#3498db', '#e74c3c', '#9b59b6']
        
        # Graph 1: Fitness over generations
        ax1 = axes[0, 0]
        ax1.plot(self.generations, self.best_fitness, 
                        color=colors[0], linewidth=2, label='Best')
        ax1.plot(self.generations, self.avg_fitness, 
                        color=colors[1], linewidth=2, label='Average')
        ax1.plot(self.generations, self.worst_fitness, 
                        color=colors[2], linewidth=2, label='Worst', alpha=0.7)

        ax1.fill_between(self.generations, self.worst_fitness, self.best_fitness, alpha=0.3, color=colors[1])
        ax1.set_title('Fitness Over Time', fontweight='bold', fontsize=10)
        ax1.set_xlabel('Generation', fontsize=8)
        ax1.set_ylabel('Fitness', fontsize=8)
        ax1.legend(loc='upper left', fontsize=7)
        ax1.tick_params(labelsize=7)
        
        # Graph 2: Food eaten per generation
        ax2 = axes[0, 1]
        ax2.plot(self.generations, self.total_food_eaten, color=colors[2], linewidth=2, marker='o', markersize=3)
        ax2.fill_between(self.generations, self.total_food_eaten, alpha=0.3, color=colors[2])
        ax2.set_title('Food Eaten Per Generation', fontweight='bold', fontsize=10)
        ax2.set_xlabel('Generation', fontsize=8)
        ax2.set_ylabel('Food Count', fontsize=8)
        ax2.tick_params(labelsize=7)
        
        # Graph 3: Survival rate
        ax3 = axes[1, 0]
        ax3.plot(self.generations, self.survival_rate, color=colors[3], linewidth=2, marker='o', markersize=3)
        ax3.fill_between(self.generations, self.survival_rate, alpha=0.3, color=colors[3])
        ax3.set_title('Survival Rate', fontweight='bold', fontsize=10)
        ax3.set_xlabel('Generation', fontsize=8)
        ax3.set_ylabel('Survival %', fontsize=8)
        ax3.set_ylim(0, 100)
        ax3.tick_params(labelsize=7)
        
        # Graph 4: Population size
        ax4 = axes[1, 1]
        ax4.plot(self.generations, self.creatures_count, color=colors[0], linewidth=2, marker='o', markersize=3)
        ax4.fill_between(self.generations, self.creatures_count, alpha=0.3, color=colors[0])
        ax4.set_title('Creatures Count', fontweight='bold', fontsize=10)
        ax4.set_xlabel('Generation', fontsize=8)
        ax4.set_ylabel('Creatures Count', fontsize=8)
        ax4.tick_params(labelsize=7)

        plt.tight_layout()
        
        # Convert to pygame surface
        buf = BytesIO()
        plt.savefig(buf, format='png', facecolor=fig.get_facecolor())
        buf.seek(0)
        plt.close(fig)
        
        return pygame.image.load(buf)