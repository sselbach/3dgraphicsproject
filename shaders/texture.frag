#version 330 core

uniform sampler2D diffuse_map;
uniform sampler2D normal_map;
uniform sampler2D specular_map;

uniform samplerCube environment_map;

uniform mat4 view;
uniform vec3 w_camera_position;
uniform float timer;
uniform float reflectiveness;
uniform vec3 k_s;
uniform float s;

in vec3 w_position, w_normal, w_tangent, w_bitangent;
in vec2 frag_tex_coords;
in vec2 frag_map_coords;

in mat3 TBN;

out vec4 out_color;

float exponentialFog(float dist, float density) {
    return clamp(1 - exp(-pow(density * dist, 2)), 0, 1);
}

void main() {
    vec3 texel_diffuse = texture(diffuse_map, frag_tex_coords).xyz;
    
    vec3 k_d = texel_diffuse;
    vec3 k_a = texel_diffuse * 0.25;

    vec3 light_dir = normalize(vec3(cos(timer), sin(timer), 1));
    //vec3 light_dir = normalize(vec3(0, -1, 0.6));


    //vec3 n = normalize(w_normal);
    vec3 n = 2 * texture(normal_map, frag_map_coords).xyz - 1;
    n = normalize(TBN * n);

    // reflected light vector
    vec3 r = reflect(light_dir, n);

    vec3 v = normalize(w_position - w_camera_position);

    vec3 spec = k_s * max(0, pow(dot(r, -v), s));

    vec4 phong_color = vec4(k_a + k_d * max(0, dot(n, light_dir)) + spec, 1);

    float distance_to_camera = distance(w_position, w_camera_position);
    float fog_factor = exponentialFog(distance_to_camera, 0.0035);

    vec4 fog_color = vec4(0.8, 1, 0.8, 1);

    vec3 reflected = reflect(v, n);
    vec4 reflection_color = vec4(texture(environment_map, reflected.xzy).rgb, 1);

    float actual_reflectiveness = reflectiveness * texture(specular_map, frag_map_coords).r;

    //out_color = 2 * texture(normal_map, frag_map_coords) - 1;
    //out_color = vec4(n, 1);
    out_color = mix(phong_color, reflection_color, actual_reflectiveness);

    out_color = mix(out_color, fog_color, fog_factor);
}