#version 330 core

uniform float iTime;

in vec3 fragmentColor;

out vec4 color;

void main()
{   
    vec3 temp = vec3(iTime, iTime, iTime);
    color = vec4(fragmentColor+temp, 1.0);
}