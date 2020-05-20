import matplotlib.pyplot as plt
import numpy as np
import geo
import triangle as tr
import math
import viewer
import balance
import weak_balance
import copy
from triangulate_defines import *
from heapq import *


def triangulate(points):
    if len(points) < 3:
        return
    plt.figure(figsize=(6, 3))
    ax1 = plt.subplot(221)
    ax2 = plt.subplot(222, sharey=ax1)
    ax3 = plt.subplot(223, sharex=ax1)
    ax4 = plt.subplot(224, sharey=ax3)
    triangulation = init(points, "a3000")
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


def update_ring_marker(triangulation, ring_markers, v):
    ring_markers[v] = min([ring_markers[i] for i in triangulation[GRAPH][v]]) + 1


def get_ring_markers(triangulation):
    ring_markers = [1 if triangulation[HULL][i] else 0 for i in range(len(triangulation[VERTICES]))]
    cur_vertexes = [i for i in range(len(triangulation[VERTICES])) if triangulation[HULL][i]]
    marked = len(cur_vertexes)
    while marked < len(triangulation[VERTICES]):
        next_cur_vertexes = []
        for i in cur_vertexes:
            for neib in triangulation[GRAPH][i]:
                if ring_markers[neib] == 0:
                    ring_markers[neib] = ring_markers[i] + 1
                    next_cur_vertexes.append(neib)
        cur_vertexes = next_cur_vertexes
        marked += len(cur_vertexes)
    return ring_markers


def improve_triangulation(triangulation):
    refresh_graph(triangulation)
    refresh_hull(triangulation)
    weak_balance.balance_triangulation(triangulation)
    ring_markers = get_ring_markers(triangulation)
    heap = [(mark, idx) for idx, mark in enumerate(ring_markers)]
    heapify(heap)
    visited = [False for _ in range(len(triangulation[VERTICES]))]
    while len(heap) > 0:
        ring, v = heappop(heap)
        if ring_markers[v] != ring:
            continue
        if ring == 1:
            continue
        while len(triangulation[GRAPH][v]) < 6:
            if not increase(v, ring_markers, heap, visited, triangulation, True):
                break
        while len(triangulation[GRAPH][v]) > 6:
            if not decrease(v, ring_markers, heap, visited, triangulation):
                break
        visited[v] = True
        weak_balance.balance_triangulation(triangulation)
    refresh_triangles(triangulation)


def increase(v, ring_markers, heap, visited, triangulation, add_on_hull=False):
    points = triangulation[VERTICES]
    graph = triangulation[GRAPH]
    hull_markers = triangulation[HULL]
    vertex_for_solve_increase = -1
    vertex_neighbour_for_solve1 = -1
    vertex_neighbour_for_solve2 = -1
    ring_m_sum = -1

    neighbours = geo.get_sorted_neighbours(graph, points, v)
    for i in range(len(neighbours)):
        neib1 = neighbours[i-1]
        neib2 = neighbours[i]
        if visited[neib1] or visited[neib2]:
            continue
        if geo.is_edge_on_hull(neib1, neib2, graph, points):
            if add_on_hull:
                new_v = split(triangulation, v, neib1, neib2)
                triangulation[HULL][new_v] = True
                ring_markers.append(1)
                visited.append(False)
                if triangulation[GRAPH][v] != 6:
                    heappush(heap, (ring_markers[v], v))
                return True
            else:
                continue
        for double_neib in geo.get_empty_triangles_vertices(graph, points, neib1, neib2):
            if visited[double_neib]:
                continue
            if double_neib == v or double_neib in graph[v]:
                continue
            rings_sum = ring_markers[double_neib] + ring_markers[neib1] + ring_markers[neib2]
            if ring_m_sum == -1 or rings_sum < ring_m_sum:
                vertex_for_solve_increase = double_neib
                vertex_neighbour_for_solve1 = neib1
                vertex_neighbour_for_solve2 = neib2
                ring_m_sum = rings_sum
    if vertex_for_solve_increase == -1:
        print("WARNING!!! increase on vertex", v)
        return False
    flip(triangulation, v, vertex_neighbour_for_solve1, vertex_for_solve_increase, vertex_neighbour_for_solve2)
    if ring_markers[v] < ring_markers[vertex_for_solve_increase]:
        ring_markers[vertex_for_solve_increase] = ring_markers[v] + 1
    elif ring_markers[vertex_for_solve_increase] < ring_markers[v]:
        ring_markers[v] = ring_markers[vertex_for_solve_increase] + 1
    update_ring_marker(triangulation, ring_markers, vertex_neighbour_for_solve1)
    update_ring_marker(triangulation, ring_markers, vertex_neighbour_for_solve2)
    for changed_v in [v, vertex_for_solve_increase, vertex_neighbour_for_solve1, vertex_neighbour_for_solve2]:
        if not hull_markers[changed_v]:
            heappush(heap, (ring_markers[changed_v], changed_v))
    return True


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


def decrease(v, ring_markers, heap, visited, triangulation):
    visited[v] = True
    points = triangulation[VERTICES]
    graph = triangulation[GRAPH]
    hull_markers = triangulation[HULL]
    vertex_for_solve_decrease = -1
    vertex_neighbour_for_solve1 = -1
    vertex_neighbour_for_solve2 = -1
    ring_sum = -1
    neighbours = geo.get_sorted_neighbours(graph, points, v)
    for idx in range(len(neighbours)):
        neib1 = neighbours[idx-2]
        neib2 = neighbours[idx]
        v_solve = neighbours[idx-1]
        if neib1 in graph[neib2] or neib1 not in graph[v_solve] or neib2 not in graph[v_solve]:
            continue
        if visited[neib1] or visited[neib2] or visited[v_solve]:
            continue
        rings_sum = ring_markers[neib1] + ring_markers[neib2] + ring_markers[v_solve]
        if ring_sum == -1 or rings_sum < ring_sum:
            vertex_for_solve_decrease = v_solve
            vertex_neighbour_for_solve1 = neib1
            vertex_neighbour_for_solve2 = neib2
            ring_sum = rings_sum
    if vertex_for_solve_decrease == -1:
        print("WARNING!!! decrease on vertex", v)
        return False
    flip(triangulation, v, vertex_neighbour_for_solve1, vertex_for_solve_decrease, vertex_neighbour_for_solve2)
    if ring_markers[vertex_neighbour_for_solve1] < ring_markers[vertex_neighbour_for_solve2]:
        ring_markers[vertex_neighbour_for_solve2] = ring_markers[vertex_neighbour_for_solve1] + 1
    elif ring_markers[vertex_neighbour_for_solve2] < ring_markers[vertex_neighbour_for_solve1]:
        ring_markers[vertex_neighbour_for_solve1] = ring_markers[vertex_neighbour_for_solve2] + 1
    update_ring_marker(triangulation, ring_markers, v)
    update_ring_marker(triangulation, ring_markers, vertex_for_solve_decrease)
    for changed_v in [v, vertex_for_solve_decrease, vertex_neighbour_for_solve1, vertex_neighbour_for_solve2]:
        if not hull_markers[changed_v]:
            heappush(heap, (ring_markers[changed_v], changed_v))
    return True
