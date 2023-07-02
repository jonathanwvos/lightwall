#version 330 core

layout (location=0) in vec3 fragCoord;

out vec4 interpolatedPosition;

uniform float angle;
uniform mat4 projection;
uniform mat4 model;
uniform mat4 fft;

void main()
{
    float c = cos(angle);
    float s = sin(angle);
    mat2 rotationMatrix = mat2(c, -s, s, c);
    vec2 rotatedFragCoord = rotationMatrix * fragCoord.xy;

    gl_Position = projection *  model * vec4(rotatedFragCoord, 0.0, 1.0);
    interpolatedPosition = gl_Position;
}