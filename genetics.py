import random
import numpy as np
from brain import NeuralNetwork
from entities import Creature
from settings import *
from spawn import random_spawn_position


def calculate_fitness(creature):
    return creature.food_eaten * 10 + creature.energy + creature.time_alive


def select_parents(creatures, num_parents):
    sorted_creatures = sorted(creatures, key=calculate_fitness, reverse=True)
    return sorted_creatures[:num_parents]


def crossover(parent1, parent2):
    child_brain = NeuralNetwork(BRAIN_LAYERS)
    weights1, biases1 = parent1.brain.get_weights()
    weights2, biases2 = parent2.brain.get_weights()

    new_weights = []
    new_biases = []

    for w1, w2 in zip(weights1, weights2):
        mask = np.random.rand(*w1.shape) > 0.5
        new_w = np.where(mask, w1, w2)
        new_weights.append(new_w)

    for b1, b2 in zip(biases1, biases2):
        mask = np.random.rand(*b1.shape) > 0.5
        new_b = np.where(mask, b1, b2)
        new_biases.append(new_b)

    child_brain.set_weights(new_weights, new_biases)
    return child_brain


def mutate(brain, mutation_rate=0.1, mutation_strength=0.3):
    for w in brain.weights:
        mask = np.random.rand(*w.shape) < mutation_rate
        w += mask * np.random.randn(*w.shape) * mutation_strength

    for b in brain.biases:
        mask = np.random.rand(*b.shape) < mutation_rate
        b += mask * np.random.randn(*b.shape) * mutation_strength


def create_new_generation(creatures):
    if len(creatures) < 2:
        return None

    parents = select_parents(creatures, len(creatures) // 4)
    if len(parents) < 2:
        return None

    new_creatures = []

    # Elitism: Keep top 2 unchanged
    for parent in parents[:2]:
        new_brain = NeuralNetwork(BRAIN_LAYERS)
        weights, biases = parent.brain.get_weights()
        new_brain.set_weights(weights, biases)
        x, y = random_spawn_position()
        new_creatures.append(Creature(x, y, new_brain))

    alive_count = sum(1 for c in creatures if c.alive)
    while len(new_creatures) < alive_count * REPRODUCTION_RATE:
        p1, p2 = random.sample(parents, 2)
        child_brain = crossover(p1, p2)
        mutate(child_brain)
        x, y = random_spawn_position()
        new_creatures.append(Creature(x, y, child_brain))

    return new_creatures
