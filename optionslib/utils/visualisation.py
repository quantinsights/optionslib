from typing import Any

from matplotlib import pyplot as plt


def draw(x: Any, y: Any, xlabel: str, ylabel: str, title: str):
    """Contains boilerplate code to draw a matplotlib plot"""
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.grid(True)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.plot(x, y, alpha=0.75, linewidth=0.80)
    plt.show()
