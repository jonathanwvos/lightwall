from numpy import array, cos, sin, mean, vstack
from numpy import float32 as FLOAT32
from numpy import pi as PI
from utils import euclidean_distance


def hexagon(origin, radius, z):
    c1 = origin + [radius, 0.0, z]
    c2 = origin + [radius*cos(-PI/3), radius*sin(-PI/3), z]
    c3 = origin + [radius*cos(-2/3*PI), radius*sin(-2/3*PI), z]
    c4 = origin + [-radius, 0.0, z]
    c5 = origin + [radius*cos(2/3*PI), radius*sin(2/3*PI), z]
    c6 = origin + [radius*cos(PI/3), radius*sin(PI/3), z]
    
    hex = [
        origin, c1, c2,
        origin, c2, c3,
        origin, c3, c4,
        origin, c4, c5,
        origin, c5, c6,
        origin, c6, c1
    ]
    
    return array(hex, FLOAT32)


def truncated_octahedron(origin, edge_len):
    square_faces = array([
        [1, 0, 2],
        [0, 1, 2],
        [-1, 0, 2],
        [-1, 0, 2],        
        [0, -1, 2],
        [1, 0, 2],
        [1, 0, -2],
        [0, 1, -2],
        [-1, 0, -2],
        [-1, 0, -2],
        [0, -1, -2],
        [1, 0, -2],
        [2, 1, 0],
        [2, 0, 1],
        [2, -1, 0],
        [2, -1, 0],
        [2, 0, -1],
        [2, 1, 0],
        [-2, 1, 0],
        [-2, 0, 1],
        [-2, -1, 0],
        [-2, -1, 0],
        [-2, 0, -1],
        [-2, 1, 0],
        [1, 2, 0],
        [0, 2, 1],
        [-1, 2, 0],
        [-1, 2, 0],
        [0, 2, -1],
        [1, 2, 0],
        [1, -2, 0],
        [0, -2, 1],
        [-1, -2, 0],
        [-1, -2, 0],
        [0, -2, -1],
        [1, -2, 0],
    ], FLOAT32)
    
    hex_origins = [
       mean([[-2, 0, 1], [-2, 1, 0], [-1, 2, 0], [0, 2, 1], [0, 1, 2], [-1, 0, 2]], axis=0),
       mean([[0, -2, 1], [-1, -2, 0], [-2, -1, 0], [-2, 0, 1], [-1, 0, 2], [0, -1, 2]], axis=0),
       mean([[2, 0, 1], [2, -1, 0], [1, -2, 0], [0, -2, 1], [0, -1, 2], [1, 0, 2]], axis=0),
       mean([[0, 2, 1], [1, 2, 0], [2, 1, 0], [2, 0, 1], [1, 0, 2], [0, 1, 2]], axis=0),
       mean([[2, 0, -1], [1, 0, -2], [0, -1, -2], [0, -2, -1], [1, -2, 0], [2, -1, 0]], axis=0),
       mean([[0, 2, -1], [0, 1, -2], [1, 0, -2], [2, 0, -1], [2, 1, 0], [1, 2, 0]], axis=0),
       mean([[-2, 0, -1], [-1, 0, -2], [0, 1, -2], [0, 2, -1], [-1, 2, 0], [-2, 1, 0]], axis=0),
       mean([[0, -2, -1], [0, -1, -2], [-1, 0, -2], [-2, 0, -1], [-2, -1, 0], [-1, -2, 0]], axis=0)
    ]
    
    hex_faces = array([
        hex_origins[0], [-2, 0, 1], [-2, 1, 0],
        hex_origins[0], [-2, 1, 0], [-1, 2, 0],
        hex_origins[0], [-1, 2, 0], [0, 2, 1],
        hex_origins[0], [0, 2, 1], [0, 1, 2],
        hex_origins[0], [0, 1, 2], [-1, 0, 2],
        hex_origins[0], [-1, 0, 2], [-2, 0, 1],
        hex_origins[1], [0, -2, 1], [-1, -2, 0],
        hex_origins[1], [-1, -2, 0], [-2, -1, 0],
        hex_origins[1], [-2, -1, 0], [-2, 0, 1],
        hex_origins[1], [-2, 0, 1], [-1, 0, 2],
        hex_origins[1], [-1, 0, 2], [0, -1, 2],
        hex_origins[1], [0, -1, 2], [0, -2, 1],
        hex_origins[2], [2, 0, 1], [2, -1, 0],
        hex_origins[2], [2, -1, 0], [1, -2, 0],
        hex_origins[2], [1, -2, 0], [0, -2, 1],
        hex_origins[2], [0, -2, 1], [0, -1, 2],
        hex_origins[2], [0, -1, 2], [1, 0, 2],
        hex_origins[2], [1, 0, 2], [2, 0, 1],
        hex_origins[3], [0, 2, 1], [1, 2, 0],
        hex_origins[3], [1, 2, 0], [2, 1, 0],
        hex_origins[3], [2, 1, 0], [2, 0, 1],
        hex_origins[3], [2, 0, 1], [1, 0, 2],
        hex_origins[3], [1, 0, 2], [0, 1, 2],
        hex_origins[3], [0, 1, 2], [0, 2, 1],
        hex_origins[4], [2, 0, -1], [1, 0, -2],
        hex_origins[4], [1, 0, -2], [0, -1, -2],
        hex_origins[4], [0, -1, -2], [0, -2, -1],
        hex_origins[4], [0, -2, -1], [1, -2, 0],
        hex_origins[4], [1, -2, 0], [2, -1, 0],
        hex_origins[4], [2, -1, 0], [2, 0, -1],
        hex_origins[5], [0, 2, -1], [0, 1, -2],
        hex_origins[5], [0, 1, -2], [1, 0, -2],
        hex_origins[5], [1, 0, -2], [2, 0, -1],
        hex_origins[5], [2, 0, -1], [2, 1, 0],
        hex_origins[5], [2, 1, 0], [1, 2, 0],
        hex_origins[5], [1, 2, 0], [0, 2, -1],
        hex_origins[6], [-2, 0, -1], [-1, 0, -2],
        hex_origins[6], [-1, 0, -2], [0, 1, -2],
        hex_origins[6], [0, 1, -2], [0, 2, -1],
        hex_origins[6], [0, 2, -1], [-1, 2, 0],
        hex_origins[6], [-1, 2, 0], [-2, 1, 0],
        hex_origins[6], [-2, 1, 0], [-2, 0, -1],
        hex_origins[7], [0, -2, -1], [0, -1, -2],
        hex_origins[7], [0, -1, -2], [-1, 0, -2],
        hex_origins[7], [-1, 0, -2], [-2, 0, -1],
        hex_origins[7], [-2, 0, -1], [-2, -1, 0],
        hex_origins[7], [-2, -1, 0], [-1, -2, 0],
        hex_origins[7], [-1, -2, 0], [0, -2, -1]
    ], FLOAT32)
    
    trunc_oct = vstack([square_faces, hex_faces])
    
    return edge_len*trunc_oct + origin


def truncated_octahedron_edges(origin, edge_len):
    edges = []
    vertices = [
        [2, 1, 0],
        [2, -1, 0],
        [-2, 1, 0],
        [-2, -1, 0],
        [0, 2, 1],
        [0, 2, -1],
        [0, -2, 1],
        [0, -2, -1],
        [1, 0, 2],
        [1, 0, -2],
        [-1, 0, 2],
        [-1, 0, -2],
        [1, 2, 0],
        [1, -2, 0],
        [-1, 2, 0],
        [-1, -2, 0],
        [0, 1, 2],
        [0, 1, -2],
        [0, -1, 2],
        [0, -1, -2],
        [2, 0, 1],
        [2, 0, -1],
        [-2, 0, 1],
        [-2, 0, -1]
    ]
    
    for v1 in vertices:
        dist = []
        for v2 in vertices:
            if v1 == v2:
                continue
            
            dist.append({
                'vertex': v2,
                'dist': euclidean_distance(v1, v2)
            })
            
        sorted_dist = sorted(dist, key=lambda item: item['dist'], reverse=False)
        
        for i in sorted_dist[0:3]:
            if [v1, i['vertex']] not in edges:
                edges.append([i['vertex'], v1])
        
    edges = array(edges, FLOAT32)
    
    return edge_len*edges + origin
