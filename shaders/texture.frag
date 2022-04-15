// main fragment shader

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

// function to calculate fog based on distance to camera
float exponentialFog(float dist, float density) {
    return clamp(1 - exp(-pow(density * dist, 2)), 0, 1);
}

void main() {
    // diffuse color is given by diffuse map
    vec3 k_d = texture(diffuse_map, frag_tex_coords).xyz;
    
    // some fraction of that is the ambient color
    vec3 k_a = k_d * 0.25;

    // light direction is rotated in the xy plane based on time
    // (not realistic given the skybox, but looks kinda cool)
    vec3 light_dir = normalize(vec3(cos(timer), sin(timer), 1));

    // read normal from normal map and re-scale to [-1, 1]
    vec3 n = 2 * texture(normal_map, frag_map_coords).xyz - 1;

    // transform into tangent space so that vertex normals are taken into account
    n = normalize(TBN * n);

    // reflected light vector
    vec3 r = reflect(light_dir, n);

    // view direction
    vec3 v = normalize(w_position - w_camera_position);

    // get reflectiveness from specular map
    float actual_reflectiveness = reflectiveness * texture(specular_map, frag_map_coords).r;

    // specular term for phong shading
    vec3 spec = actual_reflectiveness * k_s * max(0, pow(dot(r, -v), s));

    // rest of phong shading
    vec4 phong_color = vec4(k_a + k_d * max(0, dot(n, light_dir)) + spec, 1);

    // fog based on distance to camera
    float distance_to_camera = distance(w_position, w_camera_position);
    float fog_factor = exponentialFog(distance_to_camera, 0.0035);

    // fog color is matched to skybox
    vec4 fog_color = vec4(0.8, 1, 0.8, 1);

    // reflect view direction to sample from environment map
    vec3 reflected = reflect(v, n);
    vec4 reflection_color = vec4(texture(environment_map, reflected.xzy).rgb, 1);

    // first interpolate between phong and reflection
    out_color = mix(phong_color, reflection_color, actual_reflectiveness);

    // then between that and fog color
    out_color = mix(out_color, fog_color, fog_factor);
}
