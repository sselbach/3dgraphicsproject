// the main vertex shader used for most everything except water and skybox

#version 330 core

const int MAX_BONES=128;
const int MAX_VERTEX_BONES=4;

uniform sampler2D displacement_map;
uniform sampler2D normal_map;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

uniform mat4 bone_matrix[MAX_BONES];

// these would normally be boolean flags, but we couldn't figure out how to pass booleans
// flags are necessary because not all models support all shader features
uniform int apply_displacement;
uniform int apply_skinning;
uniform int use_separate_map_coords;

in vec3 position;
in vec3 normal;
in vec3 tangent;
in vec2 tex_coord;
in vec2 map_coord;
in vec4 bone_ids;
in vec4 bone_weights;

out vec2 frag_tex_coords;
out vec2 frag_map_coords;
out vec3 w_position, w_normal, w_tangent, w_bitangent;
out mat3 TBN;

void main() {
    // if skinning is not enabled, just use model matrix
    mat4 skin_matrix = model;

    if (apply_skinning > 0) {
        // linear blending for skinning, taken from our solution to TP6
        skin_matrix = mat4(0);

        for (int i = 0; i < MAX_VERTEX_BONES; i++) {
            skin_matrix += bone_weights[i] * bone_matrix[int(bone_ids[i])];
        }
    }

    // displacement mapping, only applied when corresponding flag is true
    float displacement = texture(displacement_map, map_coord).r;
    vec3 displacement_vector = (apply_displacement > 0) ? vec3(0, 0, displacement) : vec3(0);

    // map to camera space
    gl_Position = projection * view * skin_matrix * (vec4(position + displacement_vector, 1));

    // if model uses separate sets of texture coordinates, pass the correct ones here
    frag_tex_coords = tex_coord;
    frag_map_coords = (use_separate_map_coords == 1) ? map_coord : tex_coord;

    // world position, normal, tangent and bitangent are passed to the fragment shader
    vec4 w_position4 = view * skin_matrix * vec4(position, 1);
    w_position = vec3(w_position4) / w_position4.w;

    w_normal = (transpose(inverse(mat3(skin_matrix)))) * normal;
    w_tangent = mat3(skin_matrix) * tangent;
    w_bitangent = cross(w_normal, w_tangent);
    
    // for convenience also pass TBN matrix
    TBN = mat3(w_tangent, w_bitangent, w_normal);
}
