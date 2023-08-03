
#version 460 core

in vec4 interpolatedPosition;

out vec4 fragColor;

uniform vec2 resolution;

void main()
{
    fragColor = vec4(0.812, 0.667, 1.0, 1.0);
}