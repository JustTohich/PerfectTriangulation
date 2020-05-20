import triangle as tr
import matplotlib.pyplot as plt
import time
import numpy as np


def compare(ax1, vertexes, ax2, triangulation, usr_vertexes=None):
    if usr_vertexes:
        usr_vert = np.array(usr_vertexes)
        ax1.scatter(*usr_vert.T, color='r', linewidths=5)
        ax2.scatter(*usr_vert.T, color='r', linewidths=5)
    tr.plot(ax1, **vertexes)
    lim = ax1.axis()
    tr.plot(ax2, **triangulation)
    ax2.axis(lim)
    plt.tight_layout()


def draw_debug(ax, triangulation, usr_vertexes=None, sleep_time=0):
    if usr_vertexes is None:
        usr_vertexes = []
    tr.plot(ax, **triangulation)
    for vert in usr_vertexes:
        ax.scatter(*vert, color='r', linewidths=5)
    if sleep_time:
        time.sleep(sleep_time)
