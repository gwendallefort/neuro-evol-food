import pygame

_label_font = None
_label_surfaces = None


def _get_label_font():
    global _label_font
    if _label_font is None:
        _label_font = pygame.font.Font(None, 18)
    return _label_font


def _layout_neurons(layer_sizes, x, y, width, height):
    """Calculate screen positions for each neuron in each layer."""
    num_layers = len(layer_sizes)
    layer_spacing = width / (num_layers + 1)
    neuron_positions = []

    for layer_idx, num_neurons in enumerate(layer_sizes):
        layer_x = x + layer_spacing * (layer_idx + 1)
        total_height = (num_neurons - 1) * 30 if num_neurons > 1 else 0
        start_y = y + (height - total_height) / 2

        positions = []
        for neuron_idx in range(num_neurons):
            neuron_y = start_y + neuron_idx * 30 if num_neurons > 1 else y + height / 2
            positions.append((layer_x, neuron_y))
        neuron_positions.append(positions)

    return neuron_positions


def _draw_connections(surface, network, neuron_positions, max_weight_thickness):
    for layer_idx in range(len(network.layer_sizes) - 1):
        for i, (from_x, from_y) in enumerate(neuron_positions[layer_idx]):
            for j, (to_x, to_y) in enumerate(neuron_positions[layer_idx + 1]):
                weight = network.weights[layer_idx][i, j]

                if weight > 0:
                    color = (0, min(255, int(weight * 150 + 100)), 0)
                else:
                    color = (min(255, int(-weight * 150 + 100)), 0, 0)

                thickness = max(1, int(abs(weight) * max_weight_thickness))
                pygame.draw.line(
                    surface, color,
                    (int(from_x), int(from_y)), (int(to_x), int(to_y)),
                    thickness,
                )


def _draw_neurons(surface, neuron_positions, activations):
    for layer_idx, positions in enumerate(neuron_positions):
        for neuron_idx, (neuron_x, neuron_y) in enumerate(positions):
            if activations is not None and layer_idx < len(activations):
                activation = activations[layer_idx][neuron_idx]
                intensity = int((activation + 1) * 127.5)
                neuron_color = (intensity, intensity, 255)
            else:
                neuron_color = (200, 200, 200)

            pygame.draw.circle(surface, neuron_color, (int(neuron_x), int(neuron_y)), 10)
            pygame.draw.circle(surface, (0, 0, 0), (int(neuron_x), int(neuron_y)), 10, 2)


def _draw_labels(surface, neuron_positions, y):
    global _label_surfaces
    font = _get_label_font()
    layer_names = ('Input', 'Hidden', 'Output')
    if _label_surfaces is None:
        _label_surfaces = [font.render(name, True, (0, 0, 0)) for name in layer_names]

    for layer_idx, positions in enumerate(neuron_positions):
        if layer_idx < len(_label_surfaces):
            label = _label_surfaces[layer_idx]
            label_x = positions[0][0] - label.get_width() // 2
            label_y = y - 20
            surface.blit(label, (label_x, label_y))


def visualize_network(network, surface, x, y, width, height, inputs=None, max_weight_thickness=2):
    """
    Visualize a neural network on a pygame surface.

    Args:
        network: NeuralNetwork instance
        surface: pygame.Surface to draw on
        x, y: Top-left position of the visualization
        width, height: Size of the visualization area
        inputs: Optional input values to show activations (if None, shows structure only)
        max_weight_thickness: Maximum line thickness for connections
    """
    neuron_positions = _layout_neurons(network.layer_sizes, x, y, width, height)
    activations = network.forward_activations(inputs) if inputs is not None else None

    _draw_connections(surface, network, neuron_positions, max_weight_thickness)
    _draw_neurons(surface, neuron_positions, activations)
    _draw_labels(surface, neuron_positions, y)
