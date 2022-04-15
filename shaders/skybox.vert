// skybox vertex shader: removes translation component from modelview matrx
// (or rather just uses the given rotation matrix)

#version 330 core

uniform mat4 rotation, projection;

in vec3 position;

out vec3 frag_tex_coords;

void main() {
    // texture coordinates in this case should be a vec3 specifying where to sample the cubemap
    // i.e. just the position of the cube vertices
    frag_tex_coords = position;

    gl_Position = projection * rotation * vec4(position, 1);
}