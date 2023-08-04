#version 330 core

out vec4 fragColor;

in vec4 interpolatedPosition;

uniform vec2 resolution;

void main()
{
    vec2 uv = interpolatedPosition.xy;
    uv.x *= resolution.x/resolution.y;
    float d = length(uv);

    fragColor = vec4(d, d, d, 1.0);
}
