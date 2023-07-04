#version 460 core

out vec4 fragColor;

in vec4 interpolatedPosition;

uniform float time;
uniform vec2 resolution;
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

vec3 squareSubwoofer(vec2 uv, float radius, float sinMod, float ampMod, float dampener) {
    float subMask = 0.0;
    float d = 0.0;

    subMask = ampMod*squareDistance(uv);
    d = ampMod*squareDistance(uv);
    
    subMask = 0.8/subMask;
    subMask = step(radius, subMask);
    
    vec3 col = subwooferPalette(d);

    d = sin(d*sinMod+dampener)/sinMod;
    d = abs(d);
    d = 0.01/d;

    col *= d;
    col *= subMask;

    return col;
}

vec3 circleSubwoofer(vec2 uv, float radius, float sinMod, float ampMod, float dampener) {
    float subMask = 0.0;
    float d = 0.0;

    subMask =ampMod*length(uv);
    d = ampMod*length(uv);
    
    subMask = 0.8/subMask;
    subMask = step(radius, subMask);
    
    vec3 col = subwooferPalette(d);

    d = sin(d*sinMod+dampener)/sinMod;
    d = abs(d);
    d = 0.01/d;

    col *= d;
    col *= subMask;

    return col;
}

vec3 manhattanSubwoofer(vec2 uv, float radius, float sinMod, float ampMod, float dampener) {
    float d = 0.0;
    float subMask = ampMod*manhattanDistance(uv);
    
    d = ampMod*manhattanDistance(uv);
    subMask = 0.8/subMask-0.1;
    subMask = step(radius, subMask);
    
    vec3 col = subwooferPalette(d);

    d = sin(d*sinMod+dampener)/sinMod;
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

vec2 lemniscateOfBernoulliRight(vec2 uv, float radius, float timeCoeff) {
    float x = radius*cos(timeCoeff+1.5*time)/(1+pow(sin(timeCoeff+1.5*time), 2.0));
    float y = radius*sin(timeCoeff+1.5*time)*cos(timeCoeff+1.5*time)/(1+pow(sin(timeCoeff+1.5*time), 2.0));

    return uv + vec2(x, y);
}

vec2 lemniscateOfBernoulliLeft(vec2 uv, float radius, float timeCoeff) {
    float x = radius*cos(timeCoeff-1.5*time)/(1+pow(sin(timeCoeff-1.5*time), 2.0));
    float y = radius*sin(timeCoeff-1.5*time)*cos(timeCoeff-1.5*time)/(1+pow(sin(timeCoeff-1.5*time), 2.0));

    return uv + vec2(x, y);
}

void main() {
    float gaussCoeff = 1.8;
    float sinMod = 10.0;
    float timeCoeff = 2.0;

    vec2 uvOrigin = interpolatedPosition.xy*resolution.x/resolution.y;
    vec2 uvL1 = interpolatedPosition.xy + vec2(bassDampened*0.04, 0.0);
    vec2 uvL2 = interpolatedPosition.xy + vec2(bassDampened*0.067, 0.0);
    vec2 uvR1 = interpolatedPosition.xy - vec2(bassDampened*0.04, 0.0);
    vec2 uvR2 = interpolatedPosition.xy - vec2(bassDampened*0.067, 0.0);

    vec3 mgp = manhattanGaussPulse(uvOrigin, gaussCoeff, sinMod, timeCoeff);
    vec3 subOrigin = manhattanSubwoofer(uvOrigin, 1.1, sinMod, 1.0, bassDampened);
    vec3 subL1 = manhattanSubwoofer(uvL1, 1.1, sinMod, 1.7, bassDampened);
    vec3 subL2 = manhattanSubwoofer(uvL2, 1.1, sinMod, 2.5, bassDampened);
    vec3 subR1 = manhattanSubwoofer(uvR1, 1.1, sinMod, 1.7, bassDampened);
    vec3 subR2 = manhattanSubwoofer(uvR2, 1.1, sinMod, 2.5, bassDampened);

    // CROWN
    vec2 uvC1 = interpolatedPosition.xy + vec2(0.0, -0.8);
    vec3 subC1 = manhattanSubwoofer(uvC1, 1.1, sinMod, 8.0, umidDampened);

    vec2 uvC2 = interpolatedPosition.xy + vec2(0.1, -0.7);
    vec3 subC2 = manhattanSubwoofer(uvC2, 1.1, sinMod, 8.0, umidDampened);

    vec2 uvC3 = interpolatedPosition.xy + vec2(-0.1, -0.7);
    vec3 subC3 = manhattanSubwoofer(uvC3, 1.1, sinMod, 8.0, umidDampened);

    vec2 uvC4 = interpolatedPosition.xy + vec2(0.2, -0.6);
    vec3 subC4 = manhattanSubwoofer(uvC4, 1.1, sinMod, 8.0, umidDampened);

    vec2 uvC5 = interpolatedPosition.xy + vec2(-0.2, -0.6);
    vec3 subC5 = manhattanSubwoofer(uvC5, 1.1, sinMod, 8.0, umidDampened);

    vec2 uvC6 = interpolatedPosition.xy + vec2(0.3, -0.5);
    vec3 subC6 = manhattanSubwoofer(uvC6, 1.1, sinMod, 8.0, umidDampened);

    vec2 uvC7 = interpolatedPosition.xy + vec2(-0.3, -0.5);
    vec3 subC7 = manhattanSubwoofer(uvC7, 1.1, sinMod, 8.0, umidDampened);

    vec2 uvC8 = interpolatedPosition.xy + vec2(0.2, -0.4);
    vec3 subC8 = manhattanSubwoofer(uvC8, 1.1, sinMod, 8.0, umidDampened);

    vec2 uvC9 = interpolatedPosition.xy + vec2(-0.2, -0.4);
    vec3 subC9 = manhattanSubwoofer(uvC9, 1.1, sinMod, 7.0, umidDampened);

    vec2 uvC10 = interpolatedPosition.xy + vec2(0.0, -1.0);
    vec3 subC10 = manhattanSubwoofer(uvC10, 1.1, sinMod, 6.0, trebDampened);

    vec2 uvC11 = interpolatedPosition.xy + vec2(0.15, -0.9);
    vec3 subC11 = manhattanSubwoofer(uvC11, 1.1, sinMod, 6.0, trebDampened);

    vec2 uvC12 = interpolatedPosition.xy + vec2(-0.15, -0.9);
    vec3 subC12 = manhattanSubwoofer(uvC12, 1.1, sinMod, 6.0, trebDampened);

    vec2 uvC13 = interpolatedPosition.xy + vec2(0.15, -1.13);
    vec3 subC13 = manhattanSubwoofer(uvC13, 1.1, sinMod, 6.0, trebDampened);

    vec2 uvC14 = interpolatedPosition.xy + vec2(-0.15, -1.13);
    vec3 subC14 = manhattanSubwoofer(uvC14, 1.1, sinMod, 6.0, trebDampened);

    // BEARD
    vec2 uvB1 = interpolatedPosition.xy - vec2(0.0, -0.8);
    vec3 subB1 = manhattanSubwoofer(uvB1, 1.1, sinMod, 8.0, midDampened);

    vec2 uvB2 = interpolatedPosition.xy - vec2(0.1, -0.7);
    vec3 subB2 = manhattanSubwoofer(uvB2, 1.1, sinMod, 8.0, midDampened);

    vec2 uvB3 = interpolatedPosition.xy - vec2(-0.1, -0.7);
    vec3 subB3 = manhattanSubwoofer(uvB3, 1.1, sinMod, 8.0, midDampened);

    vec2 uvB4 = interpolatedPosition.xy - vec2(0.2, -0.6);
    vec3 subB4 = manhattanSubwoofer(uvB4, 1.1, sinMod, 8.0, midDampened);

    vec2 uvB5 = interpolatedPosition.xy - vec2(-0.2, -0.6);
    vec3 subB5 = manhattanSubwoofer(uvB5, 1.1, sinMod, 8.0, midDampened);

    vec2 uvB6 = interpolatedPosition.xy - vec2(0.3, -0.5);
    vec3 subB6 = manhattanSubwoofer(uvB6, 1.1, sinMod, 8.0, midDampened);

    vec2 uvB7 = interpolatedPosition.xy - vec2(-0.3, -0.5);
    vec3 subB7 = manhattanSubwoofer(uvB7, 1.1, sinMod, 8.0, midDampened);

    vec2 uvB8 = interpolatedPosition.xy - vec2(0.2, -0.4);
    vec3 subB8 = manhattanSubwoofer(uvB8, 1.1, sinMod, 8.0, midDampened);

    vec2 uvB9 = interpolatedPosition.xy - vec2(-0.2, -0.4);
    vec3 subB9 = manhattanSubwoofer(uvB9, 1.1, sinMod, 8.0, midDampened);

    vec2 uvB10 = interpolatedPosition.xy - vec2(0.4, -0.4);
    vec3 subB10 = manhattanSubwoofer(uvB10, 1.1, sinMod, 8.0, midDampened);

    vec2 uvB11 = interpolatedPosition.xy - vec2(-0.4, -0.4);
    vec3 subB11 = manhattanSubwoofer(uvB11, 1.1, sinMod, 8.0, midDampened);

    vec3 col = mgp + subOrigin +
               subL1 + subL2 + subR1 + subR2 +
               subC1 + subC2 + subC3 + subC4 + subC5 + subC6 + subC7 + subC8 + subC9 + subC10 + subC11 + subC12 + subC13 + subC14 +
               subB1 + subB2 + subB3 + subB4 + subB5 + subB6 + subB7 + subB8 + subB9 + subB10 + subB11;

    // float radius = 2.0;
    // float trebAbs = 0.1*abs(trebDampened);
    // const int trailSize = 100;
    // float trailDist = 0.1;

    // for (float i = 0.0; i < trailSize; i++) {
    //     vec2 lemLeft = lemniscateOfBernoulliLeft(interpolatedPosition.xy, radius, -trebAbs-i*0.01);
    //     vec2 lemRight = lemniscateOfBernoulliRight(interpolatedPosition.xy, radius, trebAbs+i*0.01);
    //     col += manhattanSubwoofer(lemLeft, 5.0/(i*0.1), sinMod, 10.0, midDampened);
    //     col += manhattanSubwoofer(lemRight, 5.0/(i*0.1), sinMod, 10.0, midDampened);
    // }
    // vec2 lem = lemniscateOfBernoulliRight(interpolatedPosition.xy, radius, trebAbs);
    // vec2 lem2 = lemniscateOfBernoulliLeft(interpolatedPosition.xy, radius, -trebAbs);

    // vec3 lemSub = circleSubwoofer(lem, 5.0, sinMod, 5.0, midDampened);
    // vec3 lemSub2 = circleSubwoofer(lem2, 5.0, sinMod, 5.0, midDampened);

    // vec3 col = mgp + subOrigin + subL1 + subL2 + subR1 + subR2 + lemSub + lemSub2;
    fragColor = vec4(col, 1.0);
}
