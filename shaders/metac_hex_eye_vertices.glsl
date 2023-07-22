#version 460 core

layout (location=0) in vec3 position;

out vec4 interpolatedPosition;

uniform mat4 projection;
uniform mat4 model;

void main()
{
    gl_Position = projection * model * vec4(position, 1.0);
    interpolatedPosition = gl_Position;
}