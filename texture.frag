#version 330 core

uniform sampler2D diffuse_map;
uniform sampler2D displacement_map;
uniform sampler2D normal_map;
in vec2 frag_tex_coords;

uniform mat4 view;
in vec3 w_position, w_normal;

uniform vec3 w_camera_position;

uniform float timer;

out vec4 out_color;

void main() {
    vec3 texel_diffuse = texture(diffuse_map, frag_tex_coords).xyz;
    
    vec3 k_d = texel_diffuse;
    vec3 k_a = texel_diffuse * 0.25;
    vec3 k_s = vec3(0.1);
    vec3 light_dir = normalize(vec3(cos(timer), sin(timer), 1));

    float s = 100;
    //vec3 light_dir = normalize(vec3(1, 1, 1));

    // TODO: compute Lambert illumination
    vec3 n = normalize(w_normal);

    // reflected light vector
    vec3 r = reflect(light_dir, n);

    // view direction
    // Why do the first two methods result in flickering?
    // Why can we use a constant view direction?

    vec3 v = normalize(w_position - w_camera_position);
    //vec3 v = normalize((view * vec4(w_position, 1)).xyz);
    //vec3 v = normalize((view * vec4(1, 0, 0, 1)).xyz);

    vec3 spec = k_s * max(0, pow(dot(r, v), s));
    
    out_color = vec4(k_a + k_d * max(0, dot(n, light_dir)) + spec, 1);
    //out_color = texture(normal_map, frag_tex_coords);
}
