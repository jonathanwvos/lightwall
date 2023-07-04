#version 330

out vec4 fragColor;

in vec4 interpolatedPosition;

uniform float time;
uniform vec2 resolution;

void main()
{
    // vec2 uv = interpolatedPosition.xy*resolution.x/resolution.y; // works
    // vec2 uv = (interpolatedPosition.xy * 2.0 - resolution.xy)/resolution.y;


    float d = length(interpolatedPosition.xy);
    d = step(0.1,d);
    d = 0.1/d;

    fragColor = vec4(d, d, d, 1.0);
}