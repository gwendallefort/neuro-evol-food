import json
import pickle
import numpy as np
from entities import Creature, Food
from brain import NeuralNetwork
from stats import Statistics
from settings import *
import os


def serialize_neural_network(brain):
    """Serialize a NeuralNetwork to a dictionary"""
    weights = [w.tolist() for w in brain.weights]
    biases = [b.tolist() for b in brain.biases]
    return {
        'layer_sizes': brain.layer_sizes,
        'weights': weights,
        'biases': biases
    }


def deserialize_neural_network(data):
    """Deserialize a dictionary back to a NeuralNetwork"""
    brain = NeuralNetwork(data['layer_sizes'])
    weights = [np.array(w) for w in data['weights']]
    biases = [np.array(b) for b in data['biases']]
    brain.set_weights(weights, biases)
    return brain


def serialize_creature(creature):
    """Serialize a Creature to a dictionary"""
    return {
        'x': float(creature.x),
        'y': float(creature.y),
        'angle': float(creature.angle),
        'speed': float(creature.speed),
        'energy': float(creature.energy),
        'food_eaten': int(creature.food_eaten),
        'alive': bool(creature.alive),
        'time_alive': float(creature.time_alive),
        'brain': serialize_neural_network(creature.brain)
    }


def deserialize_creature(data):
    """Deserialize a dictionary back to a Creature"""
    brain = deserialize_neural_network(data['brain'])
    creature = Creature(data['x'], data['y'], brain)
    creature.angle = data['angle']
    creature.speed = data['speed']
    creature.energy = data['energy']
    creature.food_eaten = data['food_eaten']
    creature.alive = data['alive']
    creature.time_alive = data['time_alive']
    return creature


def serialize_food(food):
    """Serialize a Food to a dictionary"""
    return {
        'x': float(food.x),
        'y': float(food.y)
    }


def deserialize_food(data):
    """Deserialize a dictionary back to a Food"""
    food = Food()
    food.x = data['x']
    food.y = data['y']
    return food


def serialize_statistics(stats):
    """Serialize Statistics to a dictionary"""
    return {
        'generations': [int(g) for g in stats.generations],
        'best_fitness': [float(f) for f in stats.best_fitness],
        'avg_fitness': [float(f) for f in stats.avg_fitness],
        'total_food_eaten': [int(f) for f in stats.total_food_eaten],
        'survival_rate': [float(s) for s in stats.survival_rate]
    }


def deserialize_statistics(data):
    """Deserialize a dictionary back to Statistics"""
    stats = Statistics()
    stats.generations = data['generations']
    stats.best_fitness = data['best_fitness']
    stats.avg_fitness = data['avg_fitness']
    stats.total_food_eaten = data['total_food_eaten']
    stats.survival_rate = data['survival_rate']
    return stats

def save_auto(save_folder, creatures, foods, stats, generation, gen_timer):
    """
    Auto-save at end of generation
    """
    try:
        # Generate filename for this generation
        save_filename = os.path.join(save_folder, f"generation_{generation:04d}.json")
        save_simulation_state(save_filename, creatures, foods, stats, generation, gen_timer)
    except Exception as e:
        print(f"Auto-save failed for generation {generation}: {e}")

def save_simulation_state(filename, creatures, foods, stats, generation, gen_timer, selected_creature_index=None):
    """
    Save the entire simulation state to a JSON file.
    
    Args:
        filename: Path to save the file
        creatures: List of Creature objects
        foods: List of Food objects
        stats: Statistics object
        generation: Current generation number
        gen_timer: Current generation timer
        selected_creature_index: Index of selected creature (if any)
    """
    state = {
        'version': '1.0',
        'generation': int(generation),
        'gen_timer': float(gen_timer),
        'selected_creature_index': selected_creature_index,
        'creatures': [serialize_creature(c) for c in creatures],
        'foods': [serialize_food(f) for f in foods],
        'statistics': serialize_statistics(stats),
        'settings': {
            'CREATURE_COUNT': CREATURE_COUNT,
            'FOOD_COUNT': FOOD_COUNT,
            'GENERATION_TIME': GENERATION_TIME,
            'BRAIN_LAYERS': BRAIN_LAYERS
        }
    }
    
    with open(filename, 'w') as f:
        json.dump(state, f, indent=2)
    
    return True


def load_simulation_state(filename):
    """
    Load a simulation state from a JSON file.
    
    Returns:
        tuple: (creatures, foods, stats, generation, gen_timer, selected_creature_index)
        Returns None if loading fails
    """
    try:
        with open(filename, 'r') as f:
            state = json.load(f)
        
        # Deserialize components
        creatures = [deserialize_creature(c) for c in state['creatures']]
        foods = [deserialize_food(f) for f in state['foods']]
        stats = deserialize_statistics(state['statistics'])
        
        generation = state.get('generation', 1)
        gen_timer = state.get('gen_timer', 0.0)
        selected_creature_index = state.get('selected_creature_index', None)
        
        return creatures, foods, stats, generation, gen_timer, selected_creature_index
    
    except Exception as e:
        print(f"Error loading simulation state: {e}")
        return None
