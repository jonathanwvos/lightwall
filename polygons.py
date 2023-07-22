from numpy import array, cos, sin
from numpy import float32 as FLOAT32
from numpy import pi as PI


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