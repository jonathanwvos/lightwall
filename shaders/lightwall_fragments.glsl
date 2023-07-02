#version 330 core

out vec4 fragColor;

in vec4 interpolatedPosition;

uniform float time;
uniform vec2 resolution;
uniform mat4 projection;
uniform mat4 model;
uniform float bassDampened;
uniform float midDampened;
uniform float umidDampened;
uniform float trebDampened;

float gaussian(in float x, in float p) {
    return exp(-pow(x,p));
}

float manhattanDistance(in vec2 C) {
    return abs(C.x) + abs(C.y);
}

float squareDistance(in vec2 C) {
    return max(abs(C.x), abs(C.y));
}

vec3 palette(float t) {
    vec3 a = vec3(0.5,0.5,0.5);
    vec3 b = vec3(0.5,0.5,0.5);
    vec3 c = vec3(1.0,1.0,1.0);
    vec3 d = vec3(0.263,0.416,0.557);
    
    return a + b*cos(6.28318*(c*t+d));
}

vec3 subwooferPalette(float t) {
    vec3 a = vec3(0.180, -0.222, -1.392);
    vec3 b = vec3(1.748, 1.808, 2.528);
    vec3 c = vec3(3.138, 3.138, 3.138);
    vec3 d = vec3(-0.362, -0.362, -0.422);

    return a + b*cos(c*t+d);
}

vec3 squareSubwoofer(vec2 uv, float gaussCoeff, float sinMod) {
    float subwooferRadius = 1.1;
    float subMask = 0.0;
    float d = 0.0;

    subMask = squareDistance(uv);
    d = squareDistance(uv);
    
    subMask = 0.8/subMask;
    subMask = step(subwooferRadius, subMask);
    
    vec3 col = subwooferPalette(d);

    d = sin(d*sinMod+bassDampened)/sinMod;
    d = abs(d);
    d = 0.01/d;

    col *= d;
    col *= subMask;

    return col;
}

vec3 manhattanSubwoofer(vec2 uv, float radius, float sinMod) {
    // float subwooferRadius = 1.1;
    float subMask = 0.0;
    float d = 0.0;

    subMask = manhattanDistance(uv);
    d = manhattanDistance(uv);
    
    subMask = 0.8/subMask;
    subMask = step(radius, subMask);
    
    vec3 col = subwooferPalette(d);

    d = sin(d*sinMod+bassDampened)/sinMod;
    d = abs(d);
    d = 0.01/d;

    col *= d;
    col *= subMask;

    return col;
}

vec3 manhattanGaussPulse(vec2 uv, float gaussCoeff, float sinMod, float timeCoeff) {
    float d = gaussian(manhattanDistance(uv), gaussCoeff);
    vec3 col = palette(d);
    d = sin(d*sinMod+timeCoeff*time)/sinMod;
    d = abs(d);
    d = 0.02/d;
    
    col *= d;

    return col;
}

void main() {
    vec2 uv = interpolatedPosition.xy;
    uv.x *= resolution.x/resolution.y;

    float gaussCoeff = 1.8;
    float sinMod = 10.0;
    float timeCoeff = 2.0;
    vec3 mgp = manhattanGaussPulse(uv, gaussCoeff, sinMod, timeCoeff);
    vec3 sub = manhattanSubwoofer(uv, 1.0, sinMod);
    vec3 col = sub + mgp;

    fragColor = vec4(col, 1.0);
}

// void main() {
//     vec2 uvOrigin = interpolatedPosition.xy*resolution.x/resolution.y;
//     vec2 uvL1 = interpolatedPosition.xy + vec2(0.5, 0.0);
//     vec2 uvL2 = interpolatedPosition.xy + vec2(1.0, 0.0);
//     vec2 uvR1 = interpolatedPosition.xy - vec2(0.5, 0.0);
//     vec2 uvR2 = interpolatedPosition.xy - vec2(1.0, 0.0);

//     float gaussCoeff = 1.8;
//     float sinMod = 10.0;
//     float timeCoeff = 2.0;
//     vec3 mgp = manhattanGaussPulse(uvOrigin, gaussCoeff, sinMod, timeCoeff);
//     vec3 subOrigin = manhattanSubwoofer(uvOrigin, 1.1, sinMod);
//     vec3 subL1 = manhattanSubwoofer(uvL1, 1.0, sinMod);
//     vec3 subL2 = manhattanSubwoofer(uvL2, 1.0, sinMod);
//     vec3 subR1 = manhattanSubwoofer(uvR1, 1.0, sinMod);
//     vec3 subR2 = manhattanSubwoofer(uvR2, 1.0, sinMod);
    
//     vec3 col = mgp + subOrigin + subL1 + subL2 + subR1 + subR2;
//     fragColor = vec4(col, 1.0);
// }
