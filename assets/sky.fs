#version 330 core
in vec2 uv;
out vec4 FragColor;
uniform sampler2D skyTexture;
void main() {
    FragColor = vec4(texture(skyTexture, uv).rgb, 1.0);
}
