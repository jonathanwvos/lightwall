#version 330

layout (location=0) in vec3 fragCoord;

out vec4 interpolatedPosition;

uniform mat4 projection;
uniform mat4 model;

void main()
{
    gl_Position = projection *  model * vec4(fragCoord, 1.0);
    // gl_Position = vec4(fragCoord, 1.0);
    interpolatedPosition = gl_Position;
}