#version 330 core

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
in vec3 position;
in vec3 color;

out vec3 axes_color;

void main() {
    axes_color = color;
    gl_Position = projection * view * model * vec4(position, 1);
}
