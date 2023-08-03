from argparse import ArgumentParser
from numpy import array, cos, sin, zeros
from numpy import pi as PI
from numpy import float32 as FLOAT32
from numpy import uint8 as UINT8
from random import uniform, choice

import cv2


def _bolt(no_edges, edge_len, origin, branch_angle, z, grid=True):
    bolt = [origin]
    if grid:
        angle = choice([0, PI/3, PI*2/3, PI, PI*4/3, PI*5/3])
    else:
        angle = uniform(0, 2*PI)
    p1 = [edge_len*cos(angle), edge_len*sin(angle), z]
    bolt.append(p1+origin)
    
    for _ in range(no_edges-1):
        ran_angle = choice([-branch_angle, branch_angle])
        angle += ran_angle
        p = [edge_len*cos(angle), edge_len*sin(angle), z]
        bolt.append(p+bolt[-1])
        
    return array(bolt, FLOAT32)

def tri_bolt(no_edges, edge_len, origin, z):
    return _bolt(no_edges, edge_len, origin, PI*2/3, z)

def hex_bolt(no_edges, edge_len, origin, z):
    return _bolt(no_edges, edge_len, origin, PI/3, z)

def square_bolt(no_edges, edge_len, origin, z):
    return _bolt(no_edges, edge_len, origin, PI/2, z)

def display_hex_bolt(width, height, no_edges, edge_len):
    origin = array([height//2, width//2, 0], FLOAT32)
    bolt = hex_bolt(no_edges, edge_len, origin)
    im = zeros((height, width, 3), UINT8)
    
    for i in range(no_edges):
        x0, y0, _ = bolt[i]
        x1, y1, _ = bolt[i+1]

        cv2.line(im, (int(y0), int(x0)), (int(y1), int(x1)), (255,10,255), 1)
    
    cv2.imshow('Hex bolt', im)
    cv2.waitKey(0)

# TODO: Refactor display code
def display_tri_bolt(width, height, no_edges, edge_len):
    origin = array([height//2, width//2, 0], FLOAT32)
    bolt = tri_bolt(no_edges, edge_len, origin)
    im = zeros((height, width, 3), UINT8)
    
    for i in range(no_edges):
        x0, y0, _ = bolt[i]
        x1, y1, _ = bolt[i+1]

        cv2.line(im, (int(y0), int(x0)), (int(y1), int(x1)), (255,10,255), 1)
    
    cv2.imshow('Hex bolt', im)
    cv2.waitKey(0)

    
if __name__ == '__main__':
    width = 1920
    height = 1080
    
    ap = ArgumentParser()
    ap.add_argument(
        '--hex',
        action='store_true',
        help='Display hexagonal bolt.'
    )
    ap.add_argument(
        '-l',
        '--len',
        help='The length of an individual edge in the bolt.',
        default=10
    )
    ap.add_argument(
        '-n',
        '--no-edges',
        help='The total length of the bolt',
        default=200
    )
    
    args = ap.parse_args()
    
    if args.hex:
        display_hex_bolt(width, height, args.no_edges, args.len)
