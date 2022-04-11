#version 330 core

uniform sampler2D displacement_map;
uniform sampler2D normal_map;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

uniform int use_normal_map;

in vec3 position;
in vec3 normal;
in vec3 tangent;
in vec2 tex_coord;
in vec2 map_coord;

out vec2 frag_tex_coords;
out vec2 frag_map_coords;
out vec3 w_position, w_normal, w_tangent, w_bitangent;
out mat3 TBN;

void main() {
    float displacement = texture(displacement_map, map_coord).r;
    vec3 displacement_vector = vec3(0, 0, displacement);

    gl_Position = projection * view * model * (vec4(position + displacement_vector, 1));
    frag_tex_coords = tex_coord;
    frag_map_coords = map_coord;

    w_position = position;

    // if (use_normal_map == 1) {
    //     // re-scale normals from [0, 1] to [-1, 1]
    //     w_normal = normalize((2 * texture(normal_map, map_coord).xyz - 1));
    // } else {
    //     w_normal = normal;
    // }

    w_normal = (transpose(inverse(mat3(model)))) * normal;
    w_tangent = mat3(model) * tangent;
    w_bitangent = cross(w_normal, w_tangent);
    
    TBN = mat3(w_tangent, w_bitangent, w_normal);
}
