#version 330 core

layout (location=0) in vec3 fragCoord;

void main()
{
    gl_Position = vec4(fragCoord, 1.0);
}
