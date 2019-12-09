
def square(poly):
    nxt = lambda i: poly[(i+1) % len(poly)]
    prv = lambda i: poly[i-1]
    return abs(sum([poly[i][0]*(nxt(i)[1] - prv(i)[1]) for i in range(len(poly))]))/2


def get_middle(v1, v2):
    return [(v1[0] + v2[0])/2, (v1[1] + v2[1])/2]


def intersect(vect1, vect2):
    for i in vect1:
        if i in vect2:
            yield i


def get_graph_from_triangulation(triangulation):
    graph = [[] for _ in range(len(triangulation['vertices']))]
    for triangle in triangulation['triangles']:
        for i in triangle:
            for j in triangle:
                if i == j or j in graph[i]:
                    continue
                else:
                    graph[i].append(j)
                    graph[j].append(i)
    return graph


def delete_edge(v1, v2, graph):
    graph[v1].remove(v2)
    graph[v2].remove(v1)


def add_edge(v1, v2, graph):
    graph[v1].append(v2)
    graph[v2].append(v1)


def get_triangles_from_graph(graph, points):
    triangles = []
    visited = [False for _ in range(len(graph))]
    for idx, neighbours in enumerate(graph):
        for i in range(1, len(neighbours)):
            for j in range(i):
                if not visited[neighbours[i]] and not visited[neighbours[j]] \
                        and neighbours[i] in graph[neighbours[j]]\
                        and is_empty(idx, neighbours[i], neighbours[j], points):
                    triangles.append([idx, neighbours[i], neighbours[j]])
        visited[idx] = True
    return triangles


def is_empty(v1, v2, v3, points):
    def sqr(a, b, c):
        return square([points[a], points[b], points[c]])

    sqr123 = sqr(v1, v2, v3)
    for p in range(len(points)):
        if p not in [v1, v2, v3] and abs(sqr(v1, v2, p) + sqr(v1, v3, p) + sqr(v2, v3, p) - sqr123) < 0.0001*sqr123:
            return False
    return True


def triangle_area_2(v1, v2, v3):
    return (v2[0] - v1[0]) * (v3[1] - v1[1]) - (v2[1] - v1[1]) * (v3[0] - v1[0])


def clockwise(v1, v2, v3):
    return -1 if triangle_area_2(v1, v2, v3) < 0 else 1


def on_hull_edge(v1, v2, graph, points):
    sign = 0
    for v in intersect(graph[v1], graph[v2]):
        cur_sign = clockwise(points[v1], points[v2], points[v])
        if sign != 0 and cur_sign != sign:
            return False
        elif sign == 0:
            sign = cur_sign
    return True


def on_hull_point(v, graph, points):
    return any([on_hull_edge(v, vn, graph, points) for vn in graph[v]])
