from testing.inputfnc2 import InputFile
from testing.fnc_objects import Node, Function, prepare_function
from testing.optimize import Optimize
import logging

from pprint import pprint as pp

import matplotlib.pyplot as plt

def plot_points(points, title="Point Plot", color='blue', marker='o'):
    # Unzip the list of (x, y) points
    x_vals, y_vals = zip(*points)

    # Create the plot
    plt.figure(figsize=(6, 6))
    plt.scatter(x_vals, y_vals, color=color, marker=marker)
    
    # Optional aesthetics
    plt.title(title)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.grid(True)
    # plt.axis('equal')  # optional, for keeping aspect ratio 1:1

    # Show the plot
    plt.show()


if __name__ == "__main__":
    level = logging.DEBUG
    fmt = '[%(levelname)s] %(asctime)s %(message)s'
    logging.basicConfig(level=level, format=fmt)
    
    # f = InputFile("testing/381-HW#4.fnc")
    # f = InputFile("testing/Test.fnc")
    # f = InputFile("testing/ZDT1.fnc")
    # f = InputFile("testing/Kursawe.fnc")
    f = InputFile("testing/Binh&Korn.fnc")
    # print(f)

    # d = Optimize.single(f, grid_size=10)
    d = Optimize.multi(f, min_weight=0.01, increment=0.01)
    points = d.data['data']['points']
    plot_points(points)
