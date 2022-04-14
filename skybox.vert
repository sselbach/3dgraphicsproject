#version 330 core

uniform mat4 rotation, projection;

in vec3 position;

out vec3 frag_tex_coords;

void main() {
    frag_tex_coords = position;

    gl_Position = projection * rotation * vec4(position, 1);
}