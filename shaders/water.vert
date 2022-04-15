#version 330 core

uniform float amplitude;
uniform float timer;
uniform mat4 projection, view, model;

in vec3 position;
in vec3 normal;

out vec3 w_position;
out vec3 w_normal;

void main() {
    vec4 w_position4 = model * vec4(position, 1);

    w_position4.z += (sin(1 * w_position4.x + timer/1.0) * cos(0.8 * w_position4.y + timer/1.0) * amplitude);

    w_position = vec3(w_position4) / w_position4.w;
    w_normal = transpose(inverse(mat3(model))) * normal;

    gl_Position = projection * view * w_position4;
}