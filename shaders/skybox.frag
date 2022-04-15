#version 330 core

uniform samplerCube environment_map;
uniform float timer;

in vec3 frag_tex_coords;

out vec4 out_color;

mat4 rotationMatrix(vec3 axis, float angle)
{
    axis = normalize(axis);
    float s = sin(angle);
    float c = cos(angle);
    float oc = 1.0 - c;
    
    return mat4(oc * axis.x * axis.x + c,           oc * axis.x * axis.y - axis.z * s,  oc * axis.z * axis.x + axis.y * s,  0.0,
                oc * axis.x * axis.y + axis.z * s,  oc * axis.y * axis.y + c,           oc * axis.y * axis.z - axis.x * s,  0.0,
                oc * axis.z * axis.x - axis.y * s,  oc * axis.y * axis.z + axis.x * s,  oc * axis.z * axis.z + c,           0.0,
                0.0,                                0.0,                                0.0,                                1.0);
}

void main() {
    vec3 rotated = mat3(rotationMatrix(vec3(0, 0, 1), timer)) * frag_tex_coords;


    out_color = texture(environment_map, rotated.xzy);
    out_color = texture(environment_map, frag_tex_coords.xzy);
}
