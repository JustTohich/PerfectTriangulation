import geo
import triangle as tr
import numpy as np


SRC_POINT_MARKERS = 'src_points'   # source point markers
VERTICES = 'vertices'              # points
GRAPH = 'graph'                    # graph of triangulation (optional)
HULL = 'hull'                      # hull markers           (optional)
VERTEX_MARKERS = 'vertex_markers'  # field used by Triangle algorithms
TRIANGLES = 'triangles'            # triangles


def refresh_hull(triangulation):
    if GRAPH not in triangulation.keys():
        if TRIANGLES in triangulation.keys():
            refresh_graph(triangulation)
    n = len(triangulation[VERTICES])
    triangulation[HULL] = [geo.is_point_on_hull(v, triangulation[GRAPH], triangulation[VERTICES]) for v in range(n)]


def refresh_graph(triangulation):
    n = len(triangulation[VERTICES])
    graph = [[] for _ in range(n)]
    for triangle in triangulation[TRIANGLES]:
        for i in triangle:
            for j in triangle:
                if i == j or j in graph[i]:
                    continue
                else:
                    graph[i].append(j)
                    graph[j].append(i)
    triangulation[GRAPH] = graph


def refresh_triangles(triangulation):
    graph = triangulation[GRAPH]
    points = triangulation[VERTICES]
    triangles = []
    visited = [False for _ in range(len(graph))]
    for idx, neighbours in enumerate(graph):
        for i in range(1, len(neighbours)):
            for j in range(i):
                if not visited[neighbours[i]] and not visited[neighbours[j]] \
                        and neighbours[i] in graph[neighbours[j]] \
                        and geo.is_empty(idx, neighbours[i], neighbours[j], points):
                    triangles.append([idx, neighbours[i], neighbours[j]])
        visited[idx] = True
    triangulation[TRIANGLES] = triangles


def __add_point__(triangulation, p):
    new_v = len(triangulation[VERTICES])
    triangulation[GRAPH].append([])
    triangulation[VERTICES].append(p)
    triangulation[HULL].append(False)
    triangulation[VERTEX_MARKERS].append(False)
    triangulation[SRC_POINT_MARKERS].append(False)
    return new_v


def __delete_edge__(triangulation, v1, v2):
    triangulation[GRAPH][v1].remove(v2)
    triangulation[GRAPH][v2].remove(v1)


def __add_edge__(triangulation, v1, v2):
    triangulation[GRAPH][v1].append(v2)
    triangulation[GRAPH][v2].append(v1)


def split(triangulation, v, edge_v1, edge_v2):
    points = triangulation[VERTICES]
    new_v = __add_point__(triangulation, geo.get_middle(points[edge_v1], points[edge_v2]))
    __delete_edge__(triangulation, edge_v1, edge_v2)
    __add_edge__(triangulation, edge_v1, new_v)
    __add_edge__(triangulation, edge_v2, new_v)
    __add_edge__(triangulation, v, new_v)
    return new_v


def flip(triangulation, v1, v2, v3, v4):
    graph = triangulation[GRAPH]
    if v1 in graph[v3] and v2 not in graph[v4]:
        __add_edge__(triangulation, v2, v4)
        __delete_edge__(triangulation, v1, v3)
    elif v2 in graph[v4] and v1 not in graph[v3]:
        __add_edge__(triangulation, v1, v3)
        __delete_edge__(triangulation, v2, v4)
    else:
        print(v1, v2, v3, v4)
        raise AttributeError


def init(points, params='a5000'):
    triangulation = tr.triangulate(dict(vertices=np.array(points)), params)
    triangulation[SRC_POINT_MARKERS] = [i < len(points) for i in range(len(triangulation[VERTICES]))]
    triangulation[VERTICES] = [*triangulation[VERTICES]]
    triangulation[VERTEX_MARKERS] = [*triangulation[VERTEX_MARKERS]]
    return triangulation
