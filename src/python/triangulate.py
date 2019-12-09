import matplotlib.pyplot as plt
import numpy as np
import geo
import triangle as tr
import balance

VERTICES = 'vertices'
TRIANGLES = 'triangles'
VERTEX_MARKERS = 'vertex_markers'


def triangulate(points):
    if len(points) < 3:
        return
    plt.figure(figsize=(6, 3))
    ax1 = plt.subplot(221)
    ax2 = plt.subplot(222, sharey=ax1)
    ax3 = plt.subplot(223, sharex=ax1)
    ax4 = plt.subplot(224, sharey=ax3)
    triangulation = tr.triangulate(dict(vertices=np.array(points)), "qa0.05")
    graph = geo.get_graph_from_triangulation(triangulation)
    improved_graph, improved_triangulation = improve_triangulation(triangulation, len(points))
    ax1.set_title('Standard')
    ax2.set_title('Improved')
    compare(ax1, triangulation, ax2, improved_triangulation)
    balance.balance_tr_with_real_points_first(triangulation, len(points), graph, triangulation[VERTEX_MARKERS])
    balance.balance_tr_with_real_points_first(improved_triangulation, len(points), improved_graph,
                                              improved_triangulation[VERTEX_MARKERS])
    ax3.set_title('Balanced standard')
    ax4.set_title('Balanced improved')
    compare(ax3, triangulation, ax4, improved_triangulation)
    plt.show()


def compare(ax1, vertexes, ax2, triangulation):
    tr.plot(ax1, **vertexes)
    lim = ax1.axis()
    tr.plot(ax2, **triangulation)
    ax2.axis(lim)
    plt.tight_layout()


def improve_triangulation(triangulation, src_points_number):
    graph = geo.get_graph_from_triangulation(triangulation)
    points = [*triangulation[VERTICES]]

    if VERTEX_MARKERS in triangulation.keys():
        hull_markers = [*triangulation[VERTEX_MARKERS]]
    else:
        hull_markers = [geo.on_hull_point(v, graph, points) for v in range(len(graph))]

    bad_vertexes = [len(neighbours) != 6 and not hull_markers[i] for i, neighbours in enumerate(graph)]
    for i in range(len(bad_vertexes)):
        if bad_vertexes[i]:
            wave(i, bad_vertexes, graph, points, hull_markers, src_points_number)

    return graph, dict(triangles=geo.get_triangles_from_graph(graph, points),
                       vertices=points, vertex_markers=hull_markers)


def wave(idx_from, bad_vertexes, graph, points, hull_markers, src_points_number):
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
                increase(v, bfs_queue, visited, graph, points, hull_markers)
                # triangles = geo.get_triangles_from_graph(graph, points)
                # balance.balance_tr_with_real_points_first(dict(triangles=triangles, vertices=points), src_points_number)
            bad_vertexes[v] = False
        elif len(graph[v]) > 6:
            counts = len(graph[v]) - 6
            for _ in range(counts):
                decrease(v, bfs_queue, visited, graph, points, hull_markers)
                # triangles = geo.get_triangles_from_graph(graph, points)
                # balance.balance_tr_with_real_points_first(dict(triangles=triangles, vertices=points), src_points_number)
            bad_vertexes[v] = False
        else:
            bad_vertexes[v] = False
            continue


def neighbours_for_increase(v, graph):
    for i in range(1, len(graph[v])):
        for j in range(i):
            if graph[v][i] in graph[graph[v][j]]:
                yield graph[v][i], graph[v][j]


def increase(v, bfs_queue, visited, graph, points, hull_markers):
    vertex_for_solve_increase = -1
    vertex_neighbour_for_solve1 = -1
    vertex_neighbour_for_solve2 = -1
    for neib1, neib2 in neighbours_for_increase(v, graph):
        if visited[neib1] or visited[neib2] or not geo.is_empty(v, neib1, neib2, points):
            continue
        if geo.on_hull_edge(neib1, neib2, graph, points):
            new_v = len(points)
            visited.append(False)
            graph.append([])
            points.append(geo.get_middle(points[neib1], points[neib2]))
            hull_markers.append(True)
            geo.delete_edge(neib1, neib2, graph)
            geo.add_edge(neib1, new_v, graph)
            geo.add_edge(neib2, new_v, graph)
            geo.add_edge(v, new_v, graph)
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
    geo.delete_edge(vertex_neighbour_for_solve1, vertex_neighbour_for_solve2, graph)
    geo.add_edge(vertex_for_solve_increase, v, graph)
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


def decrease(v, bfs_queue, visited, graph, points, hull_markers):
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
    geo.delete_edge(vertex_for_solve_decrease, v, graph)
    geo.add_edge(vertex_neighbour_for_solve1, vertex_neighbour_for_solve2, graph)
    for changed_v in [vertex_for_solve_decrease, vertex_neighbour_for_solve1, vertex_neighbour_for_solve2]:
        if not hull_markers[changed_v]:
            bfs_queue.append(changed_v)
