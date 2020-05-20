import matplotlib.pyplot as plt
import numpy as np
import geo
import triangle as tr
import balance
import weak_balance
import copy
import viewer
from triangulate_defines import *


def triangulate(points):
    if len(points) < 3:
        return
    plt.figure(figsize=(6, 3))
    ax1 = plt.subplot(221)
    ax2 = plt.subplot(222, sharey=ax1)
    ax3 = plt.subplot(223, sharex=ax1)
    ax4 = plt.subplot(224, sharey=ax3)
    triangulation = init(points, "a2000")
    improved_triangulation = copy.deepcopy(triangulation)
    improve_triangulation(improved_triangulation)
    ax2.set_title('Standard')
    ax1.set_title('Improved')
    viewer.compare(ax1, improved_triangulation, ax2, triangulation, points)
    weak_balance.balance_triangulation(triangulation)
    weak_balance.balance_triangulation(improved_triangulation)
    balance.balance_triangulation(triangulation)
    balance.balance_triangulation(improved_triangulation)

    ax4.set_title('Balanced standard')
    ax3.set_title('Balanced improved')
    viewer.compare(ax3, improved_triangulation, ax4, triangulation, points)
    plt.show()


def improve_triangulation(triangulation):
    refresh_graph(triangulation)
    refresh_hull(triangulation)
    bad_vertexes = [len(triangulation[GRAPH][i]) != 6 and not triangulation[HULL][i]
                    for i in range(len(triangulation[VERTICES]))]
    for i in range(len(bad_vertexes)):
        if bad_vertexes[i]:
            wave(i, bad_vertexes, triangulation)

    refresh_triangles(triangulation)


def wave(idx_from, bad_vertexes, triangulation):
    graph = triangulation[GRAPH]
    bfs_queue = [idx_from]
    visited = [False for _ in range(len(graph))]
    while bfs_queue:
        v = bfs_queue.pop(0)
        if visited[v]:
            continue
        visited[v] = True
        if len(graph[v]) < 6:
            counts = 6 - len(graph[v])
            for _ in range(counts):
                increase(v, bfs_queue, visited, triangulation)
                # weak_balance.balance_triangulation(triangulation)
            bad_vertexes[v] = False
        elif len(graph[v]) > 6:
            counts = len(graph[v]) - 6
            for _ in range(counts):
                decrease(v, bfs_queue, visited, triangulation)
                # weak_balance.balance_triangulation(triangulation)
            bad_vertexes[v] = False
        else:
            bad_vertexes[v] = False
            continue


def neighbours_for_increase(v, graph):
    for i in range(1, len(graph[v])):
        for j in range(i):
            if graph[v][i] in graph[graph[v][j]]:
                yield graph[v][i], graph[v][j]


def increase(v, bfs_queue, visited, triangulation):
    points = triangulation[VERTICES]
    graph = triangulation[GRAPH]
    hull_markers = triangulation[HULL]
    vertex_for_solve_increase = -1
    vertex_neighbour_for_solve1 = -1
    vertex_neighbour_for_solve2 = -1
    for neib1, neib2 in neighbours_for_increase(v, graph):
        if visited[neib1] or visited[neib2] or not geo.is_empty(v, neib1, neib2, points):
            continue
        if geo.is_edge_on_hull(neib1, neib2, graph, points):
            visited.append(False)
            new_v = split(triangulation, v, neib1, neib2)
            triangulation[HULL][new_v] = True
            return
        for double_neib in geo.intersect(graph[neib1], graph[neib2]):
            if not visited[double_neib] \
                    and geo.is_empty(double_neib, neib1, neib2, points)\
                    and geo.is_empty(double_neib, v, neib1, points) \
                    and geo.is_empty(double_neib, v, neib2, points):
                vertex_for_solve_increase = double_neib
                vertex_neighbour_for_solve1 = neib1
                vertex_neighbour_for_solve2 = neib2
    if vertex_for_solve_increase == -1:
        print("WARNING!!! increase on vertex", v)
        return
    flip(triangulation, v, vertex_neighbour_for_solve1, vertex_for_solve_increase, vertex_neighbour_for_solve2)
    for changed_v in [vertex_for_solve_increase, vertex_neighbour_for_solve1, vertex_neighbour_for_solve2]:
        if not hull_markers[changed_v]:
            bfs_queue.append(changed_v)


def vertices_for_decrease(v, graph, points):
    for i in range(1, len(graph[v])):
        for j in range(i):
            n1 = graph[v][i]
            n2 = graph[v][j]
            for v_int in geo.intersect(graph[n1], graph[n2]):
                if v_int != v and v_int in graph[v] \
                        and geo.is_empty(v_int, v, n1, points) and geo.is_empty(v_int, v, n2, points)\
                        and geo.is_empty(n1, n2, v, points) and geo.is_empty(n1, n2, v_int, points):
                    yield n1, n2, v_int


def decrease(v, bfs_queue, visited, triangulation):
    points = triangulation[VERTICES]
    graph = triangulation[GRAPH]
    hull_markers = triangulation[HULL]
    vertex_for_solve_decrease = -1
    vertex_neighbour_for_solve1 = -1
    vertex_neighbour_for_solve2 = -1
    for neib1, neib2, v_solve in vertices_for_decrease(v, graph, points):
        if visited[neib1] or visited[neib2] or visited[v_solve]:
            continue
        vertex_for_solve_decrease = v_solve
        vertex_neighbour_for_solve1 = neib1
        vertex_neighbour_for_solve2 = neib2
    if vertex_for_solve_decrease == -1:
        print("WARNING!!! decrease on vertex", v)
        return
    flip(triangulation, v, vertex_neighbour_for_solve1, vertex_for_solve_decrease, vertex_neighbour_for_solve2)
    for changed_v in [vertex_for_solve_decrease, vertex_neighbour_for_solve1, vertex_neighbour_for_solve2]:
        if not hull_markers[changed_v]:
            bfs_queue.append(changed_v)
