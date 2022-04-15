#version 330 core

in vec3 axes_color;

out vec4 out_color;

void main() {
    out_color = vec4(axes_color, 1);
}