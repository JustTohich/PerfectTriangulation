from scipy.sparse.linalg import lsqr
import numpy as np
import math
from triangulate_defines import *


def length(p1, p2):
    return math.sqrt((p1[0]-p2[0])*(p1[0]-p2[0]) + (p1[1]-p2[1])*(p1[1]-p2[1]))


def balance_triangulation(triangulation):
    if GRAPH not in triangulation.keys():
        refresh_graph(triangulation)
    if HULL not in triangulation.keys():
        refresh_hull(triangulation)
    points = triangulation[VERTICES]
    graph = triangulation[GRAPH]
    cannot_move = [triangulation[SRC_POINT_MARKERS][i] or triangulation[HULL][i] for i in range(len(points))]
    A = np.zeros((2 * len(points), 2 * len(points)))
    b = np.zeros(2 * len(points))
    for p_idx, p in enumerate(points):
        row = 2 * p_idx
        n_neighbours = len(graph[p_idx])
        A[row][row] = 1
        A[row + 1][row + 1] = 1
        p_mean = [0, 0]
        for neighbour in graph[p_idx]:
            A[row][2 * neighbour] = -1. / n_neighbours if not cannot_move[neighbour] else 0
            A[row + 1][2 * neighbour + 1] = -1. / n_neighbours if not cannot_move[neighbour] else 0
            p_mean[0] += points[neighbour][0]/n_neighbours
            p_mean[1] += points[neighbour][1]/n_neighbours
        b[row] = p_mean[0] - p[0]
        b[row + 1] = p_mean[1] - p[1]
    answer = lsqr(A, b)[0]
    points[:] = [[points[i][0] + answer[2 * i], points[i][1] + answer[2 * i + 1]]
                 if not cannot_move[i] else points[i] for i in range(len(points))]
