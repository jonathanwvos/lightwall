#version 330 core

uniform float iTime;
uniform vec2 iResolution;

layout (location=0) in vec2 fragCoord;

out vec4 fragColor;

void main() {
    vec2 uv = (fragCoord.xy * 2.0 - iResolution.xy)/iResolution.y;
    float d = length(uv);
    float sin_mod = 8.0;
    d = sin(d*sin_mod + iTime)/sin_mod;
    d = abs(d);
    d = smoothstep(0.0, 0.1, d);
    d = 0.02/d;

    fragColor = vec4(d,d,d,1.0);
}
