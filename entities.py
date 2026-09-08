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

    def _closest_in_sectors(self, entities, include=None):
        """Track closest entity distance per FOV sector.

        include: optional callable(entity) -> bool filter.
        """
        sector_dist = [float('inf')] * NUM_SECTORS
        sector_angle = FOV_ANGLE / NUM_SECTORS
        half_fov = FOV_ANGLE / 2

        for entity in entities:
            if include is not None and not include(entity):
                continue

            dx = entity.x - self.x
            dy = entity.y - self.y
            dist = np.sqrt(dx * dx + dy * dy)

            if dist > SENSOR_RANGE:
                continue

            relative_angle = np.arctan2(dy, dx) - self.angle
            relative_angle = np.arctan2(np.sin(relative_angle), np.cos(relative_angle))

            if abs(relative_angle) <= half_fov:
                sector_idx = int((relative_angle + half_fov) / sector_angle)
                sector_idx = max(0, min(NUM_SECTORS - 1, sector_idx))

                if dist < sector_dist[sector_idx]:
                    sector_dist[sector_idx] = dist

        return sector_dist

    def sense(self, foods, creatures):
        """Gather sensory inputs about the environment using field of view sectors"""
        sector_food_dist = self._closest_in_sectors(foods)
        sector_creature_dist = self._closest_in_sectors(
            creatures,
            include=lambda c: c is not self and c.alive,
        )

        # Normalize distances (closer = lower value, further = higher value, capped at 1.0)
        # If no object in sector, use 1.0 (maximum distance)
        food_inputs = [
            min(dist / SENSOR_RANGE, 1.0) if dist != float('inf') else 1.0
            for dist in sector_food_dist
        ]
        creature_inputs = [
            min(dist / SENSOR_RANGE, 1.0) if dist != float('inf') else 1.0
            for dist in sector_creature_dist
        ]

        wall_dist = np.tanh(
            min(
                self.x,
                self.y,
                SIM_WIDTH - self.x,
                WINDOW_HEIGHT - self.y,
            ) / 100
        )

        energy_input = np.tanh(self.energy / 100)

        # Return: [food_sector_0, ..., food_sector_N-1, creature_sector_0, ..., creature_sector_N-1, wall_dist, energy]
        return food_inputs + creature_inputs + [wall_dist, energy_input]

    def think(self, inputs):
        return self.brain.forward(inputs)

    def update(self, foods, creatures, dt):
        if not self.alive:
            return

        self.time_alive += dt

        inputs = self.sense(foods, creatures)
        outputs = self.think(inputs)

        self.angle += outputs[0] * 0.2
        self.speed = (outputs[1] + 1) * 1.5 + 0.5

        self.x += np.cos(self.angle) * self.speed
        self.y += np.sin(self.angle) * self.speed

        # Keep within simulation bounds
        self.x = max(10, min(SIM_WIDTH - 10, self.x))
        self.y = max(10, min(WINDOW_HEIGHT - 10, self.y))

        self.energy -= (0.1 + self.speed * 0.04)

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


class Food:
    def __init__(self, x=None, y=None):
        self.x = random.uniform(20, SIM_WIDTH - 20) if x is None else x
        self.y = random.uniform(20, WINDOW_HEIGHT - 20) if y is None else y
        self.radius = 5
