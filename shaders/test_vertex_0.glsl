#version 330 core

uniform float iTime;
uniform vec2 iResolution;

layout (location=0) in vec3 fragCoord;
layout (location=1) in vec3 vertexColor;

out vec3 fragmentColor;

void main() {
    vec2 uv = (fragCoord.xy * 2.0 - iResolution.xy)/iResolution.y;
    float d = length(uv);
    float sin_mod = 8.0;
    d = sin(d*sin_mod + iTime)/sin_mod;
    d = abs(d);
    d = smoothstep(0.0, 0.1, d);
    d = 0.02/d;

    gl_Position = vec4(fragCoord, 1.0);
    fragmentColor = vec3(d,d,d);
}
