import pygame
import numpy as np
import random
from settings import *
from brain import NeuralNetwork

class Creature:
    def __init__(self, x, y, brain=None):
        self.x = x
        self.y = y
        self.angle = random.uniform(0, 2 * np.pi)
        self.speed = 2
        self.radius = 10
        self.energy = 100
        self.food_eaten = 0
        self.alive = True
        self.time_alive = 0

        if brain is None:
            self.brain = NeuralNetwork(BRAIN_LAYERS)
        else:
            self.brain = brain

    def sense(self, foods, creatures):
        """Gather sensory inputs about the environment using field of view sectors"""
        # Initialize sector arrays: each sector tracks closest food and creature
        sector_food_dist = [float('inf')] * NUM_SECTORS
        sector_creature_dist = [float('inf')] * NUM_SECTORS
        
        # Calculate sector angle range
        sector_angle = FOV_ANGLE / NUM_SECTORS
        half_fov = FOV_ANGLE / 2
        
        # Process foods
        for food in foods:
            dx = food.x - self.x
            dy = food.y - self.y
            dist = np.sqrt(dx * dx + dy * dy)
            
            # Only consider foods within sensor range
            if dist > SENSOR_RANGE:
                continue
            
            # Calculate relative angle (normalized to [-pi, pi])
            relative_angle = np.arctan2(dy, dx) - self.angle
            # Normalize to [-pi, pi]
            relative_angle = np.arctan2(np.sin(relative_angle), np.cos(relative_angle))
            
            # Check if within field of view
            if abs(relative_angle) <= half_fov:
                # Determine which sector this food belongs to
                # Sector 0 is leftmost, sector N-1 is rightmost
                sector_idx = int((relative_angle + half_fov) / sector_angle)
                sector_idx = max(0, min(NUM_SECTORS - 1, sector_idx))  # Clamp to valid range
                
                # Update if this is the closest food in this sector
                if dist < sector_food_dist[sector_idx]:
                    sector_food_dist[sector_idx] = dist
        
        # Process creatures
        for creature in creatures:
            if creature is not self and creature.alive:
                dx = creature.x - self.x
                dy = creature.y - self.y
                dist = np.sqrt(dx * dx + dy * dy)
                
                # Only consider creatures within sensor range
                if dist > SENSOR_RANGE:
                    continue
                
                # Calculate relative angle (normalized to [-pi, pi])
                relative_angle = np.arctan2(dy, dx) - self.angle
                # Normalize to [-pi, pi]
                relative_angle = np.arctan2(np.sin(relative_angle), np.cos(relative_angle))
                
                # Check if within field of view
                if abs(relative_angle) <= half_fov:
                    # Determine which sector this creature belongs to
                    sector_idx = int((relative_angle + half_fov) / sector_angle)
                    sector_idx = max(0, min(NUM_SECTORS - 1, sector_idx))  # Clamp to valid range
                    
                    # Update if this is the closest creature in this sector
                    if dist < sector_creature_dist[sector_idx]:
                        sector_creature_dist[sector_idx] = dist
        
        # Normalize distances (closer = lower value, further = higher value, capped at 1.0)
        # If no object in sector, use 1.0 (maximum distance)
        food_inputs = [min(dist / SENSOR_RANGE, 1.0) if dist != float('inf') else 1.0 
                      for dist in sector_food_dist]
        creature_inputs = [min(dist / SENSOR_RANGE, 1.0) if dist != float('inf') else 1.0 
                          for dist in sector_creature_dist]
        
        # Wall distance (distance to nearest wall)
        wall_dist = min(self.x, self.y, 
                       SIM_WIDTH - self.x, 
                       WINDOW_HEIGHT - self.y) / 100
        
        # Energy level
        energy_input = self.energy / 100
        
        # Return: [food_sector_0, ..., food_sector_N-1, creature_sector_0, ..., creature_sector_N-1, wall_dist, energy]
        return food_inputs + creature_inputs + [wall_dist, energy_input]

    def think(self, inputs):
        return self.brain.forward(inputs)

    def update(self, foods, creatures, dt, speed_multiplier=1):
        if not self.alive:
            return

        self.time_alive += dt

        inputs = self.sense(foods, creatures)
        outputs = self.think(inputs)

        self.angle += outputs[0] * 0.2
        self.speed = (outputs[1] + 1) * 1.5 + 0.5

        self.x += np.cos(self.angle) * self.speed * speed_multiplier
        self.y += np.sin(self.angle) * self.speed * speed_multiplier

        # Keep within simulation bounds
        self.x = max(10, min(SIM_WIDTH - 10, self.x))
        self.y = max(10, min(WINDOW_HEIGHT - 10, self.y))

        self.energy -= (0.1 + self.speed * 0.05) * speed_multiplier

        if self.energy <= 0:
            self.alive = False

    def eat(self, foods):
        for food in foods[:]:
            dx = food.x - self.x
            dy = food.y - self.y
            if dx * dx + dy * dy < (self.radius + food.radius) ** 2:
                self.energy = min(150, self.energy + 30)
                self.food_eaten += 1
                foods.remove(food)
                return True
        return False

    def draw(self, screen, show_fov=False):
        if not self.alive:
            color = RED
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)
            return
        
        # Draw field of view (if enabled)
        if show_fov:
            half_fov = FOV_ANGLE / 2
            left_angle = self.angle - half_fov
            right_angle = self.angle + half_fov
            
            # Optimized: Use smaller surface and fewer arc points
            # Create a surface just big enough for the FOV area (with padding)
            surface_size = int(SENSOR_RANGE * 2.2)  # Slightly larger than needed
            surface_half = surface_size // 2
            
            # Calculate bounding box for the FOV
            # Find the extreme points to determine surface position
            cos_left = np.cos(left_angle)
            sin_left = np.sin(left_angle)
            cos_right = np.cos(right_angle)
            sin_right = np.sin(right_angle)
            
            # Create FOV polygon points relative to creature center
            num_arc_points = 12  # Reduced from 20 for better performance
            fov_points = [(surface_half, surface_half)]  # Center point
            
            # Pre-calculate angle step
            angle_step = (right_angle - left_angle) / num_arc_points
            
            # Add points along the arc at sensor range
            for i in range(num_arc_points + 1):
                angle = left_angle + angle_step * i
                cos_a = np.cos(angle)
                sin_a = np.sin(angle)
                # Points relative to surface center
                arc_x = surface_half + cos_a * SENSOR_RANGE
                arc_y = surface_half + sin_a * SENSOR_RANGE
                fov_points.append((int(arc_x), int(arc_y)))
            
            # Create small surface instead of full screen
            fov_surface = pygame.Surface((surface_size, surface_size), pygame.SRCALPHA)
            pygame.draw.polygon(fov_surface, (255, 255, 0, 30), fov_points)
            
            # Blit at correct position (offset by creature position minus surface center)
            blit_x = int(self.x - surface_half)
            blit_y = int(self.y - surface_half)
            screen.blit(fov_surface, (blit_x, blit_y))
            
            # Draw sector divider lines (reuse pre-calculated cos/sin where possible)
            sector_angle = FOV_ANGLE / NUM_SECTORS
            cx, cy = int(self.x), int(self.y)
            
            for i in range(NUM_SECTORS + 1):
                sector_line_angle = self.angle - half_fov + (sector_angle * i)
                cos_sector = np.cos(sector_line_angle)
                sin_sector = np.sin(sector_line_angle)
                line_end_x = cx + cos_sector * SENSOR_RANGE
                line_end_y = cy + sin_sector * SENSOR_RANGE
                pygame.draw.line(screen, (200, 200, 0), 
                               (cx, cy), 
                               (int(line_end_x), int(line_end_y)), 1)
            
            # Draw FOV boundary lines (reuse pre-calculated values)
            left_end_x = cx + cos_left * SENSOR_RANGE
            left_end_y = cy + sin_left * SENSOR_RANGE
            right_end_x = cx + cos_right * SENSOR_RANGE
            right_end_y = cy + sin_right * SENSOR_RANGE
            pygame.draw.line(screen, YELLOW, 
                            (cx, cy), 
                            (int(left_end_x), int(left_end_y)), 2)
            pygame.draw.line(screen, YELLOW, 
                            (cx, cy), 
                            (int(right_end_x), int(right_end_y)), 2)
        
        # Draw creature
        energy_ratio = min(1, self.energy / 100)
        green = int(100 + 155 * energy_ratio)
        color = (50, green, 50)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)
        
        # Direction indicator
        end_x = self.x + np.cos(self.angle) * self.radius * 1.5
        end_y = self.y + np.sin(self.angle) * self.radius * 1.5
        pygame.draw.line(screen, BLACK, (self.x, self.y), (end_x, end_y), 2)
        
        # Energy bar
        bar_width = 20
        bar_height = 4
        energy_width = (self.energy / 150) * bar_width
        pygame.draw.rect(screen, RED, 
                        (self.x - bar_width//2, self.y - self.radius - 8, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, 
                        (self.x - bar_width//2, self.y - self.radius - 8, energy_width, bar_height))


class Food:
    def __init__(self):
        self.x = random.uniform(20, SIM_WIDTH - 20)
        self.y = random.uniform(20, WINDOW_HEIGHT - 20)
        self.radius = 5

    def draw(self, screen):
        pygame.draw.circle(screen, BLUE, (int(self.x), int(self.y)), self.radius)