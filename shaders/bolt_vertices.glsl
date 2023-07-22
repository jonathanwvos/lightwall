#version 460 core

layout (location=0) in vec3 position;
layout (location=1) in vec4 color;

out vec4 interpolatedPosition;
out vec4 interpolatedColor;

uniform mat4 projection;
uniform mat4 model;

void main()
{
    gl_Position = projection * model * vec4(position, 1.0);
    interpolatedPosition = gl_Position;
    interpolatedColor = color;
}
