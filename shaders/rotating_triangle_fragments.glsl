#version 330 core

out vec4 fragColor;

in vec4 interpolatedPosition;

uniform float time;
uniform vec2 resolution;
uniform mat4 projection;
uniform mat4 model;

float gaussianAct(in float x) {
    return exp(-pow(x,2.0));
}

float manhattanMetric(in vec2 C) {
    return abs(C.x) + abs(C.y);
}

vec3 palette(float t)
{
    vec3 a = vec3(0.5,0.5,0.5);
    vec3 b = vec3(0.5,0.5,0.5);
    vec3 c = vec3(1.0,1.0,1.0);
    vec3 d = vec3(0.263,0.416,0.557);
    
    return a + b*cos(6.28318*(c*t+d));
}

void main()
{
    float sinMod = 4.0;
    vec3 finalColor = vec3(0.0);

    vec2 uv = interpolatedPosition.xy;
    uv.x *= resolution.x/resolution.y;
    vec2 uv0 = uv;
    
    for(float i = 0.0; i < 3.0; i++) {
        uv = fract(uv*2.0)-0.5;
        
        float d = manhattanMetric(uv) + exp(-length(uv0));
        
        vec3 col = palette(length(uv0)+time*0.6 + i*0.8);

        d = gaussianAct(d);
        d = sin(d*sinMod+time)/sinMod;
        //float d = squareMetric(uv);
        //d = step(0.01, d);
        //d = smoothstep(0.0, 1.0, d);
        d = 0.015/d;

        finalColor += col * d;
    }

    fragColor = vec4(finalColor, 1.0);
}
