from scipy.sparse.linalg import lsqr
import numpy as np
import math
import geo


VERTEX_MARKERS = 'vertex_markers'
VERTICES = 'vertices'


def length(p1, p2):
    return math.sqrt((p1[0]-p2[0])*(p1[0]-p2[0]) + (p1[1]-p2[1])*(p1[1]-p2[1]))


def balance_tr_with_real_points_first(triangulation, real_points_number, graph=None, hull_markers=None):
    triangulation[VERTEX_MARKERS] = [i < real_points_number for i in range(len(triangulation[VERTICES]))]
    balance_triangulation(triangulation, graph, hull_markers)


def balance_triangulation(triangulation, graph=None, hull_markers=None):
    if graph is None or hull_markers is None:
        pretty_vertex_angles = [2 * math.pi / 6 for _ in range(len(triangulation[VERTICES]))]
    else:
        hull_n = sum(hull_markers)
        hull_angle = math.pi*(hull_n - 2)/hull_n
        pretty_vertex_angles = [2 * math.pi / len(graph[v])
                                if not hull_markers[v]
                                else hull_angle / len(graph[v])
                                for v in range(len(graph))]
    for _ in range(4):
        balance_triangulation_once(triangulation, pretty_vertex_angles)


def balance_triangulation_once(triangulation, pretty_vertex_angles):
    cannot_move = triangulation[VERTEX_MARKERS]
    points = triangulation[VERTICES]
    triangles = triangulation['triangles']
    A = np.zeros((3*len(triangles), 2*len(points)))
    b = np.zeros(3*len(triangles))
    for row1_3, triangle in enumerate(triangles):
        tr_sqr = geo.square([points[triangle[0]], points[triangle[1]], points[triangle[2]]])
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
