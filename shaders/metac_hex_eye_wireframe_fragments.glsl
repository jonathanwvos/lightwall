
#version 460 core

in vec4 interpolatedPosition;

out vec4 fragColor;

uniform vec2 resolution;

void main()
{
    fragColor = vec4(0.141, 0, 0.337, 1.0);
}