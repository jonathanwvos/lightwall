#version 460 core

out vec4 fragColor;

in vec4 interpolatedPosition;
in vec4 interpolatedColor;

void main()
{
    fragColor = interpolatedColor;
}