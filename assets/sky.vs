#version 330 core
layout(location = 0) in vec3 position;
layout(location = 1) in vec2 vertexUV;
out vec2 uv;
uniform mat4 modelTransformation;
uniform mat4 viewTransformation;
uniform mat4 projectionMatrix;
void main() {
    uv = vertexUV;
    gl_Position = projectionMatrix * viewTransformation * modelTransformation * vec4(position, 1.0);
}
