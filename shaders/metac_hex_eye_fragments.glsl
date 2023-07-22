#version 460 core

in vec4 interpolatedPosition;

out vec4 fragColor;

uniform vec2 resolution;
uniform float time;

vec3 purple_gradient(float t)
{
    vec3 start = vec3(0.271, 0, 0.612);
    vec3 end = vec3(0.812, 0.667, 1.0);

    return cos(t)*(start - end) + start;
}

float manhattanDist(in vec2 C) {
    return abs(C.x) + abs(C.y);
}

float squareDist(in vec2 C) {
    return max(abs(C.x), abs(C.y));
}

float discreteDist(in vec2 C) {
    if(C.x == C.y) {
        return 0.0;
    }
    else {
        return 1.0;
    }
}

vec2 astroid(float d) {
    float a = 3.0;
    float x = a*pow(cos(d+time), 3.0);
    float y = a*pow(sin(d+time), 3.0);
    x = 1.0/x;
    y = 1.0/y;

    return vec2(x, y);
}

float cissoid(float d) {
    float a = 1.0;
    return 2.0*a*tan(d+time)*sin(d+time);
}

float cochleoid(float d) {
    float a = 0.5;
    return a*sin(d+time)/(d);
}

vec2 conchoid(float d) {
    float a = 1.0;
    float x = a + cos(d+time);
    float y = a*tan(d+time) + sin(d+time);

    return vec2(x, y);
}

float conchoidDeSluze(float d) {
    float a = 1.0;
    float k = 1.0;

    return (k*pow(cos(d+time), 2.0)+pow(a, 2.0))/(a*cos(d+time));
}

float devilsCurve(float d) {
    return sqrt((25.0-24.0*pow(tan(d+time), 2.0))/(1.0-pow(tan(d+time), 2.0)));
}

float doubleFolium(float d) {
    float a = 1.0;
    return 4.0*a*cos(d+time)*pow(sin(d+time), 2.0);
}

float figureEight(float d) {
    float a = 1.0;
    return abs(a)*sqrt(cos(2.0*(d+time)*pow(1.0/cos(d+time), 4.0)));
}

vec2 epicycloid(float d) {
    float a = 1.0;
    float b = 1.0;
    float x = (a+b)*cos(d+time)-b*cos((a/b+1.0)*(d+time));
    float y = (a+b)*sin(d+time)-b*sin((a/b+1.0)*(d+time));

    return vec2(x, y);
}

vec2 lissajous(float d) {
    float a = 1.0;
    float b = 1.0;
    float c = 1.0;
    float n = 1.0;
    
    float x = a*sin(n*(d+time)+c);
    float y = b*sin(d+time);

    return vec2(x, y);
}


// vec3 palette(float t) {
//     vec3 a = vec3(0.5,0.5,0.5);
//     vec3 b = vec3(0.5,0.5,0.5);
//     vec3 c = vec3(1.0,1.0,1.0);
//     vec3 d = vec3(0.263,0.416,0.557);
    
//     return a + b*cos(6.28318*(c*t+d));
// }

void main()
{
    vec2 uv = interpolatedPosition.xy;
    uv.x *= resolution.x/resolution.y;
    float d = length(uv);
    d = cochleoid(d);
    vec3 col = purple_gradient(d);
    fragColor = vec4(col, 1.0);
}