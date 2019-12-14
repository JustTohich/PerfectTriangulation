import triangle as tr
import matplotlib.pyplot as plt
import time


def compare(ax1, vertexes, ax2, triangulation):
    tr.plot(ax1, **vertexes)
    lim = ax1.axis()
    tr.plot(ax2, **triangulation)
    ax2.axis(lim)
    plt.tight_layout()


def draw_debug(ax, triangulation):
    tr.plot(ax, **triangulation)
    time.sleep(10)
