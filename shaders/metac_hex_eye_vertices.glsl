#version 460 core

layout (location=0) in vec3 position;

out vec4 interpolatedPosition;

uniform float angleX;
uniform float angleY;
uniform float angleZ;
uniform mat4 projection;
uniform mat4 model;

mat4 rotationMatrixZ(float angle) {
    float c = cos(angle);
    float s = sin(angle);
    return mat4(
        c, -s, 0, 0,
        s, c, 0, 0,
        0, 0, 1, 0,
        0, 0, 0, 1
    );
}

mat4 rotationMatrixY(float angle) {
    float c = cos(angle);
    float s = sin(angle);
    return mat4(
        c, 0, s, 0,
        0, 1, 0, 0,
        -s, 0, c, 0,
        0, 0, 0, 1
    );
}

mat4 rotationMatrixX(float angle) {
    float c = cos(angle);
    float s = sin(angle);
    return mat4(
        1, 0, 0, 0,
        0, c, -s, 0,
        0, s, c, 0,
        0, 0, 0, 1
    );
}

void main()
{
    mat4 rotationX = rotationMatrixX(angleX);
    mat4 rotationY = rotationMatrixY(angleY);
    mat4 rotationZ = rotationMatrixZ(angleZ);
    vec4 position4D = rotationZ * rotationY * rotationX * vec4(position, 1.0);
    gl_Position = projection * model * position4D;
    interpolatedPosition = gl_Position;
}