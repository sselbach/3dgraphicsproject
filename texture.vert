#version 330 core

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
in vec3 position;
in vec3 normal;
in vec2 tex_coord;

out vec2 frag_tex_coords;
out vec3 w_position, w_normal;

void main() {
    gl_Position = projection * view * model * vec4(position, 1);
    frag_tex_coords = tex_coord;

    w_position = position;
    w_normal = (transpose(inverse(mat3(model)))) * normal;
}