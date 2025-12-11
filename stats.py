import pygame
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from io import BytesIO

class Statistics:
    def __init__(self):
        self.generations = []
        self.best_fitness = []
        self.avg_fitness = []
        self.total_food_eaten = []
        self.survival_rate = []
        
    def record_generation(self, gen_number, creatures, gen_time):
        """Record stats at the end of each generation"""
        fitnesses = [self.calculate_fitness(c) for c in creatures]
        alive_count = sum(1 for c in creatures if c.alive)
        food_eaten = sum(c.food_eaten for c in creatures)
        
        self.generations.append(gen_number)
        self.best_fitness.append(max(fitnesses))
        self.avg_fitness.append(np.mean(fitnesses))
        self.total_food_eaten.append(food_eaten)
        self.survival_rate.append((alive_count / len(creatures)) * 100)
        
    def calculate_fitness(self, creature):
        return creature.food_eaten * 10 + creature.energy
    
    def render_graphs(self, width, height):
        """Render matplotlib graphs to a pygame surface"""
        if len(self.generations) < 2:
            return None
            
        fig, axes = plt.subplots(2, 2, figsize=(width/100, height/100), dpi=100)
        fig.patch.set_facecolor('#f5f5f5')
        
        # Style settings
        plt.style.use('seaborn-v0_8-whitegrid')
        colors = ['#2ecc71', '#3498db', '#e74c3c', '#9b59b6']
        
        # Graph 1: Fitness over generations
        axes[0, 0].plot(self.generations, self.best_fitness, 
                        color=colors[0], linewidth=2, label='Best')
        axes[0, 0].plot(self.generations, self.avg_fitness, 
                        color=colors[1], linewidth=2, label='Average')
        axes[0, 0].fill_between(self.generations, self.avg_fitness, alpha=0.3, color=colors[1])
        axes[0, 0].set_title('Fitness Over Time', fontweight='bold', fontsize=10)
        axes[0, 0].set_xlabel('Generation', fontsize=8)
        axes[0, 0].set_ylabel('Fitness', fontsize=8)
        axes[0, 0].legend(loc='upper left', fontsize=7)
        axes[0, 0].tick_params(labelsize=7)
        
        # Graph 2: Food eaten per generation
        axes[0, 1].bar(self.generations, self.total_food_eaten, color=colors[2], alpha=0.7)
        axes[0, 1].plot(self.generations, self.total_food_eaten, color=colors[2], linewidth=2)
        axes[0, 1].set_title('Food Eaten Per Generation', fontweight='bold', fontsize=10)
        axes[0, 1].set_xlabel('Generation', fontsize=8)
        axes[0, 1].set_ylabel('Food Count', fontsize=8)
        axes[0, 1].tick_params(labelsize=7)
        
        # Graph 3: Survival rate
        axes[1, 0].plot(self.generations, self.survival_rate, 
                        color=colors[3], linewidth=2, marker='o', markersize=3)
        axes[1, 0].fill_between(self.generations, self.survival_rate, alpha=0.3, color=colors[3])
        axes[1, 0].set_title('Survival Rate', fontweight='bold', fontsize=10)
        axes[1, 0].set_xlabel('Generation', fontsize=8)
        axes[1, 0].set_ylabel('Survival %', fontsize=8)
        axes[1, 0].set_ylim(0, 100)
        axes[1, 0].tick_params(labelsize=7)
        
        # Graph 4: Improvement metrics
        if len(self.generations) > 1:
            improvement = [0]
            for i in range(1, len(self.best_fitness)):
                imp = self.best_fitness[i] - self.best_fitness[i-1]
                improvement.append(imp)
            
            colors_bars = [colors[0] if x >= 0 else colors[2] for x in improvement]
            axes[1, 1].bar(self.generations, improvement, color=colors_bars, alpha=0.7)
            axes[1, 1].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
            axes[1, 1].set_title('Fitness Change', fontweight='bold', fontsize=10)
            axes[1, 1].set_xlabel('Generation', fontsize=8)
            axes[1, 1].set_ylabel('Δ Fitness', fontsize=8)
            axes[1, 1].tick_params(labelsize=7)
        
        plt.tight_layout()
        
        # Convert to pygame surface
        buf = BytesIO()
        plt.savefig(buf, format='png', facecolor=fig.get_facecolor())
        buf.seek(0)
        plt.close(fig)
        
        return pygame.image.load(buf)