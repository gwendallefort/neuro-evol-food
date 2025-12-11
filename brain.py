import numpy as np

class NeuralNetwork:
    def __init__(self, layer_sizes):
        self.weights = []
        self.biases = []
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