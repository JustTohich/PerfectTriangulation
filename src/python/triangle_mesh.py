#!/usr/bin/env python

import math
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import seaborn as sns
import time

__author__ = "Anton Barski"
__credits__ = ["Anton Barski"]
__version__ = "1.0.1"
__maintainer__ = "Anton Barski"
__email__ = "nightbars@tut.by"
__status__ = "Development"

from triangulate_defines import *
import viewer
import balance
import triangulate2


class Box:
    def __init__(self, left, right, top, bottom):
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom


def bounding_box(points):
    xx, yy = tuple(zip(*points))
    return Box(min(xx), max(xx), min(yy), max(yy))

# Class below creates grid like this
#   ____________
#  /\  /\  /\  /
# /__\/__\/__\/
# \  /\  /\  /\
#  \/__\/__\/__\
#  /\  /\  /\  /
# /__\/__\/__\/


class TriangleGrid:
    def __init__(self, usr_points, max_area=None):
        box = bounding_box(usr_points)
        self.convex_hull = ConvexHull(np.array(usr_points))
        if not max_area:
            side_length = max(box.right - box.left, box.bottom - box.top) / len(usr_points)
        else:
            side_length = math.sqrt(max_area / (3 ** (1 / 2) / 4))

        self.x_delta = side_length
        self.y_delta = side_length * 3 ** (1 / 2) / 2
        box.left -= self.x_delta / 2
        box.right += self.x_delta / 2
        box.top -= self.y_delta / 2
        box.bottom += self.y_delta / 2
        self.bounding_box = box
        self.nx = math.ceil((box.right - box.left) / self.x_delta) + 1
        self.ny = math.ceil((box.bottom - box.top) / self.y_delta)
        self.usr_points = usr_points
        self.mesh = self.make_mesh()

    def make_mesh(self):
        triangulation = dict()
        triangulation[GRAPH] = self.make_graph()
        triangulation[HULL] = [False] * len(triangulation[GRAPH])
        triangulation[TRIANGLES] = self.make_triangles()
        self.add_vertices(triangulation)
        return triangulation

    def add_vertices(self, triangulation):
        triangulation[VERTICES] = self.get_vertices_grid()
        triangulation[VERTEX_MARKERS] = [False] * (self.nx * self.ny)
        triangulation[SRC_POINT_MARKERS] = [False] * (self.nx * self.ny)

        for gl_idx, p_dest in self.get_points_move().items():
            triangulation[VERTICES][gl_idx] = p_dest
            triangulation[SRC_POINT_MARKERS][gl_idx] = True

        marked = self.mark_outdoor_points(triangulation)
        self.remove_marked_points(triangulation, marked)

    def remove_marked_points(self, triangulation, marked):
        first_src_point_idx = 0
        for i in range(len(triangulation[SRC_POINT_MARKERS])):
            if triangulation[SRC_POINT_MARKERS][i]:
                first_src_point_idx = i
                break

        for i in range(len(triangulation[VERTICES])):
            if not marked[i]:
                continue
            triangulation[GRAPH][i] = []
            # TODO delete vertices
            triangulation[VERTICES][i] = triangulation[VERTICES][first_src_point_idx]
            for j in range(len(triangulation[GRAPH])):
                if i in triangulation[GRAPH][j]:
                    triangulation[GRAPH][j].remove(i)
            triangles_size = len(triangulation[TRIANGLES])
            for j in range(triangles_size - 1, -1, -1):
                if i in triangulation[TRIANGLES][j]:
                    triangulation[TRIANGLES].pop(j)

    def mark_outdoor_points(self, triangulation):
        hull_points = list()
        for p_idx in self.convex_hull.vertices:
            hull_points.append((self.usr_points[p_idx][0], self.usr_points[p_idx][1]))
        poly = Polygon(hull_points)
        outdoor = [False] * len(triangulation[VERTICES])
        for i in range(len(outdoor)):
            outdoor[i] = not (triangulation[SRC_POINT_MARKERS][i] or poly.contains(Point(triangulation[VERTICES][i])))
        return [outdoor[i]
                and all([outdoor[v] or triangulation[SRC_POINT_MARKERS][v] for v in triangulation[GRAPH][i]])
                for i in range(len(outdoor))]

    def get_vertices_grid(self):
        vertices = [list()] * (self.nx * self.ny)
        for x in range(self.nx):
            for y in range(self.ny):
                left = self.bounding_box.left
                top = self.bounding_box.top
                if y % 2 == 0:
                    left += self.x_delta / 2
                vertices[self.get_global_idx(x, y)] = [left + x * self.x_delta, top + y * self.y_delta]
        return vertices

    def get_points_move(self):
        points_move = dict()
        for i, usr_p in enumerate(self.usr_points):
            nearest_gl_idx = None
            nearest_dist = math.inf
            for idx in self.get_point_triangle_indexes(usr_p):
                gl_idx = self.get_global_idx(*idx)
                if gl_idx in points_move.keys():
                    continue
                else:
                    p = self.get_real(*idx)
                    dist = math.sqrt(abs(p[0] - usr_p[0]) ** 2 + abs(p[1] - usr_p[1]) ** 2)
                    if dist < nearest_dist:
                        nearest_dist = dist
                        nearest_gl_idx = gl_idx
            if nearest_gl_idx:
                points_move[nearest_gl_idx] = usr_p
            else:
                print("WARNING!")
        return points_move

    def get_point_triangle_indexes(self, p):
        dy = p[1] - self.bounding_box.top
        y1 = math.floor(dy / self.y_delta)
        y2 = y1 + 1
        dx = p[0] - self.bounding_box.left
        x1 = math.floor(dx / self.x_delta)
        x2 = math.floor((dx - self.x_delta / 2) / self.x_delta)
        if y1 % 2 == 0:
            x1, x2 = x2, x1
        x1b, x2b = x1, x2
        if x1 < x2:
            x1b += 1
        else:
            x2b += 1

        p1 = self.get_real(x1b, y1)
        p2 = self.get_real(x2b, y2)

        if ((p1[1] - p2[1]) * p[0] + (p1[0] * p2[1] - p2[0] * p1[1])) / (p1[0] - p2[0]) > p[1]:
            return [[x1b, y1], [x2, y2], [x2 + 1, y2]]
        else:
            return [[x2b, y2], [x1, y1], [x1 + 1, y1]]

    def make_graph(self):
        graph = [list()] * (self.nx * self.ny)
        for x in range(self.nx):
            for y in range(self.ny):
                graph[self.get_global_idx(x, y)] = self.get_neighbours(x, y)
        return graph

    def make_triangles(self):
        triangles = list()
        for x in range(self.nx):
            for y in range(self.ny):
                dx = -1 if y % 2 else 0
                if x + dx < 0 or x + dx + 1 >= self.nx:
                    continue
                if y != 0:
                    triangles.append([self.get_global_idx(x, y),
                                      self.get_global_idx(x + dx, y - 1),
                                      self.get_global_idx(x + dx + 1, y - 1)])
                if y != self.ny - 1:
                    triangles.append([self.get_global_idx(x, y),
                                      self.get_global_idx(x + dx, y + 1),
                                      self.get_global_idx(x + dx + 1, y + 1)])
        return triangles

    def get_global_idx(self, x, y):
        return x + y * self.nx

    def get_xy(self, idx):
        return idx // self.nx, idx % self.nx

    def get_real(self, x, y):
        p = [0, 0]
        p[1] = self.bounding_box.top + self.y_delta * y
        p[0] = self.bounding_box.left + self.x_delta * x
        if y % 2 == 0:
            p[0] += self.x_delta / 2
        return p

    def get_neighbours(self, x, y):
        neighbours = []
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue
                neighbour = [x + dx, y + dy]
                if neighbour[0] < 0 or neighbour[1] < 0 or neighbour[0] >= self.nx or neighbour[1] >= self.ny:
                    continue
                neighbours.append(self.get_global_idx(*neighbour))

        return neighbours


def triangulate(points):
    if len(points) < 3:
        return

    ax1 = plt.subplot(421)
    ax2 = plt.subplot(422, sharey=ax1)
    ax3 = plt.subplot(423, sharex=ax1)
    ax4 = plt.subplot(424, sharey=ax3)
    ax1.set_title('Proprietary')
    ax2.set_title('Standard')
    ax3.set_title('Balanced proprietary')
    ax4.set_title('Balanced standard improved')

    area = 3000

    time_start = time.time()
    triangulation = TriangleGrid(points, area).mesh
    time1 = time.time() - time_start
    viewer.draw_debug(ax1, triangulation, points)
    stat1 = balance.get_stat(triangulation)

    time_start = time.time()
    standard_triangulation = init(points, "a" + str(area))
    time2 = time.time() - time_start
    viewer.draw_debug(ax2, standard_triangulation, points)
    stat2 = balance.get_stat(standard_triangulation)

    time_start = time.time()
    balance.balance_triangulation(triangulation, 10)
    time3 = time.time() - time_start
    viewer.draw_debug(ax3, triangulation, points)
    stat3 = balance.get_stat(triangulation)

    time_start = time.time()
    triangulate2.improve_triangulation(standard_triangulation)
    balance.balance_triangulation(standard_triangulation)
    time4 = time.time() - time_start
    viewer.draw_debug(ax4, standard_triangulation, points)
    stat4 = balance.get_stat(standard_triangulation)

    ax1 = plt.subplot(425)
    ax2 = plt.subplot(426)
    ax3 = plt.subplot(427)
    ax4 = plt.subplot(428)
    ax1.set_title('tm=' + str(time1))
    ax2.set_title('tm=' + str(time2))
    ax3.set_title('tm=' + str(time3))
    ax4.set_title('tm=' + str(time4))
    sns.distplot(stat1, ax=ax1)
    sns.distplot(stat2, ax=ax2)
    sns.distplot(stat3, ax=ax3)
    sns.distplot(stat4, ax=ax4)
    plt.show()
