// skybox fragment shader: just sample the environment map at given texture coordinates

#version 330 core

uniform samplerCube environment_map;

in vec3 frag_tex_coords;

out vec4 out_color;

void main() {
    out_color = texture(environment_map, frag_tex_coords.xzy);
}
