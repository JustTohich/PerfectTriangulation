from scipy.sparse.linalg import lsqr
import numpy as np
import math
import geo
from triangulate_defines import *


def length(p1, p2):
    return math.sqrt((p1[0]-p2[0])*(p1[0]-p2[0]) + (p1[1]-p2[1])*(p1[1]-p2[1]))


def balance_triangulation(triangulation):
    pretty_vertex_angles = [2 * math.pi / 6 for _ in range(len(triangulation[VERTICES]))]
    for _ in range(4):
        balance_triangulation_once(triangulation, pretty_vertex_angles)


def balance_triangulation_once(triangulation, pretty_vertex_angles):
    if HULL not in triangulation.keys():
        refresh_hull(triangulation)
    points = triangulation[VERTICES]
    cannot_move = [triangulation[SRC_POINT_MARKERS][i] or triangulation[HULL][i] for i in range(len(points))]
    triangles = triangulation[TRIANGLES]
    A = np.zeros((3*len(triangles), 2*len(points)))
    b = np.zeros(3*len(triangles))
    for row1_3, triangle in enumerate(triangles):
        tr_sqr = math.sqrt(geo.square([points[triangle[0]], points[triangle[1]], points[triangle[2]]]))
        row = 3 * row1_3
        for i, j, k in [triangle, triangle[::-1], [triangle[1], triangle[0], triangle[2]]]:
            A[row][2 * i] = 2 * points[i][0] - points[j][0] - points[k][0] \
                if not cannot_move[i] else 0
            A[row][2 * i + 1] = 2*points[i][1] - points[j][1] - points[k][1] \
                if not cannot_move[i] else 0
            A[row][2 * j] = points[k][0] - points[i][0] \
                if not cannot_move[j] else 0
            A[row][2 * j + 1] = points[k][1] - points[i][1] \
                if not cannot_move[j] else 0
            A[row][2 * k] = points[j][0] - points[i][0] \
                if not cannot_move[k] else 0
            A[row][2 * k + 1] = points[j][1] - points[i][1] \
                if not cannot_move[k] else 0
            b[row] = math.cos(pretty_vertex_angles[i])*length(points[i], points[j])*length(points[i], points[k]) \
                - (points[j][0] - points[i][0]) * (points[k][0] - points[i][0]) \
                - (points[j][1] - points[i][1]) * (points[k][1] - points[i][1])
            A[row][2 * i] /= tr_sqr
            A[row][2 * i + 1] /= tr_sqr
            A[row][2 * j] /= tr_sqr
            A[row][2 * j + 1] /= tr_sqr
            A[row][2 * k] /= tr_sqr
            A[row][2 * k + 1] /= tr_sqr
            b[row] /= tr_sqr
            row += 1
    answer = lsqr(A, b)[0]
    points[:] = [[points[i][0] + answer[2*i], points[i][1] + answer[2*i+1]]
                 if not cannot_move[i] else points[i] for i in range(len(points))]
