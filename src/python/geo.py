import math


def square(poly):
    nxt = lambda i: poly[(i+1) % len(poly)]
    prv = lambda i: poly[i-1]
    return abs(sum([poly[i][0]*(nxt(i)[1] - prv(i)[1]) for i in range(len(poly))]))/2


def get_middle(v1, v2):
    return [(v1[0] + v2[0])/2, (v1[1] + v2[1])/2]


def intersect(vect1, vect2):
    return [i for i in vect1 if i in vect2]


def is_empty(v1, v2, v3, points):
    def sqr(a, b, c):
        return square([points[a], points[b], points[c]])
    eps = 0.000001
    sqr123 = sqr(v1, v2, v3)
    for p in range(len(points)):
        if p not in [v1, v2, v3] and abs(sqr(v1, v2, p) + sqr(v1, v3, p) + sqr(v2, v3, p) - sqr123) < eps*sqr123:
            return False
    return True


def get_angle(points, v1, v2):
    return math.atan2(points[v2][1] - points[v1][1], points[v2][0] - points[v1][0])


def get_sorted_neighbours(graph, points, v):
    return [i[1] for i in sorted([(get_angle(points, v, i), i) for i in graph[v]])]


def get_empty_triangles_vertices(graph, points, edge_v1, edge_v2):
    neibrs1 = get_sorted_neighbours(graph, points, edge_v1)
    neibrs2 = get_sorted_neighbours(graph, points, edge_v2)
    nearest_neibrs1 = []
    nearest_neibrs2 = []
    for idx, i in enumerate(neibrs1):
        if i == edge_v2:
            nearest_neibrs1 = [neibrs1[idx-1], neibrs1[(idx+1) % len(neibrs1)]]
    for idx, i in enumerate(neibrs2):
        if i == edge_v1:
            nearest_neibrs2 = [neibrs2[idx-1], neibrs2[(idx+1) % len(neibrs2)]]
    return intersect(nearest_neibrs1, nearest_neibrs2)


def triangle_area_2(v1, v2, v3):
    return (v2[0] - v1[0]) * (v3[1] - v1[1]) - (v2[1] - v1[1]) * (v3[0] - v1[0])


def clockwise(v1, v2, v3):
    return -1 if triangle_area_2(v1, v2, v3) < 0 else 1


def is_edge_on_hull(v1, v2, graph, points):
    sign = 0
    for v in intersect(graph[v1], graph[v2]):
        cur_sign = clockwise(points[v1], points[v2], points[v])
        if sign != 0 and cur_sign != sign:
            return False
        elif sign == 0:
            sign = cur_sign
    return True


def is_point_on_hull(v, graph, points):
    return any([is_edge_on_hull(v, vn, graph, points) for vn in graph[v]])
