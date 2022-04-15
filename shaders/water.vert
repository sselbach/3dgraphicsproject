// water vertex shader: applies z displacement according to wave function
// normals are calculated in the fragment shader

#version 330 core

uniform float amplitude;
uniform float timer;
uniform mat4 projection, view, model;

in vec3 position;

out vec3 w_position;

void main() {
    vec4 w_position4 = model * vec4(position, 1);

    w_position = vec3(w_position4) / w_position4.w;

    w_position.z += (sin(1 * w_position.x + timer) * cos(0.8 * w_position.y + timer) * amplitude);

    gl_Position = projection * view * vec4(w_position, 1);
}