#version 330 core

// ---- camera geometry
uniform mat4 projection, view;

// ---- skinning globals and attributes
const int MAX_VERTEX_BONES=4, MAX_BONES=128;
uniform mat4 bone_matrix[MAX_BONES];

// ---- vertex attributes
in vec3 position;
in vec3 normal;
in vec4 bone_ids;
in vec4 bone_weights;

// ----- interpolated attribute variables to be passed to fragment shader
out vec3 fragment_color;

void main() {

    int bone_index;
    float weight;
    int bone_position;
    mat4 skin_matrix = mat4(1.0);

    // ------ creation of the skinning deformation matrix
    for (int i=1; i<=MAX_VERTEX_BONES; i++) {
        
        bone_index = int(bone_ids[i]);
        weight = bone_weights[i];
        skin_matrix +=  weight * bone_matrix[bone_index];
    }

    // ------ compute world and normalized eye coordinates of our vertex
    vec4 w_position4 = skin_matrix * vec4(position, 1.0);
    gl_Position = projection * view * w_position4;

    fragment_color = normal;
}
