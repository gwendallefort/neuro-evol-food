import numpy as np
import pygame

class NeuralNetwork:
    def __init__(self, layer_sizes):
        self.weights = []
        self.biases = []
        self.layer_sizes = layer_sizes
        for i in range(len(layer_sizes) - 1):
            w = np.random.randn(layer_sizes[i], layer_sizes[i + 1]) * 0.5
            b = np.random.randn(layer_sizes[i + 1]) * 0.5
            self.weights.append(w)
            self.biases.append(b)

    def forward(self, inputs):
        x = np.array(inputs)
        for w, b in zip(self.weights, self.biases):
            x = np.tanh(np.dot(x, w) + b)
        return x

    def get_weights(self):
        return [w.copy() for w in self.weights], [b.copy() for b in self.biases]

    def set_weights(self, weights, biases):
        self.weights = [w.copy() for w in weights]
        self.biases = [b.copy() for b in biases]

    def visualize(self, surface, x, y, width, height, inputs=None, max_weight_thickness=2):
            """
            Visualize the neural network on a pygame surface.
            
            Args:
                surface: pygame.Surface to draw on
                x, y: Top-left position of the visualization
                width, height: Size of the visualization area
                inputs: Optional input values to show activations (if None, shows structure only)
                max_weight_thickness: Maximum line thickness for connections
            """
            num_layers = len(self.layer_sizes)
            layer_spacing = width / (num_layers + 1)
            
            # Calculate neuron positions for each layer
            neuron_positions = []
            max_neurons = max(self.layer_sizes)
            
            for layer_idx, num_neurons in enumerate(self.layer_sizes):
                layer_x = x + layer_spacing * (layer_idx + 1)
                neuron_y_positions = []
                
                # Center neurons vertically
                total_height = (num_neurons - 1) * 30 if num_neurons > 1 else 0
                start_y = y + (height - total_height) / 2
                
                for neuron_idx in range(num_neurons):
                    neuron_y = start_y + neuron_idx * 30 if num_neurons > 1 else y + height / 2
                    neuron_y_positions.append((layer_x, neuron_y))
                
                neuron_positions.append(neuron_y_positions)
            
            # Calculate activations if inputs provided
            activations = []
            if inputs is not None:
                x_vals = np.array(inputs)
                activations.append(x_vals.copy())
                for w, b in zip(self.weights, self.biases):
                    x_vals = np.tanh(np.dot(x_vals, w) + b)
                    activations.append(x_vals.copy())
            
            # Draw connections
            for layer_idx in range(num_layers - 1):
                for i, (from_x, from_y) in enumerate(neuron_positions[layer_idx]):
                    for j, (to_x, to_y) in enumerate(neuron_positions[layer_idx + 1]):
                        weight = self.weights[layer_idx][i, j]
                        
                        # Color based on weight sign
                        if weight > 0:
                            color = (0, min(255, int(weight * 150 + 100)), 0)  # Green for positive
                        else:
                            color = (min(255, int(-weight * 150 + 100)), 0, 0)  # Red for negative
                        
                        # Thickness based on weight magnitude
                        thickness = max(1, int(abs(weight) * max_weight_thickness))
                        
                        pygame.draw.line(surface, color, (int(from_x), int(from_y)), (int(to_x), int(to_y)), thickness)
            
            # Draw neurons
            for layer_idx, positions in enumerate(neuron_positions):
                for neuron_idx, (neuron_x, neuron_y) in enumerate(positions):
                    # Determine neuron color based on activation
                    if inputs is not None and layer_idx < len(activations):
                        activation = activations[layer_idx][neuron_idx]
                        # Map tanh output [-1, 1] to color intensity
                        intensity = int((activation + 1) * 127.5)  # 0-255
                        neuron_color = (intensity, intensity, 255)
                    else:
                        neuron_color = (200, 200, 200)  # Gray default
                    
                    # Draw neuron circle
                    pygame.draw.circle(surface, neuron_color, (int(neuron_x), int(neuron_y)), 10)
                    pygame.draw.circle(surface, (0, 0, 0), (int(neuron_x), int(neuron_y)), 10, 2)
            
            # Draw layer labels
            font = pygame.font.Font(None, 18)
            layer_names = ['Input', 'Hidden', 'Output']
            for layer_idx, positions in enumerate(neuron_positions):
                if layer_idx < len(layer_names):
                    label = font.render(layer_names[layer_idx], True, (0, 0, 0))
                    label_x = positions[0][0] - label.get_width() // 2
                    label_y = y - 20
                    surface.blit(label, (label_x, label_y))