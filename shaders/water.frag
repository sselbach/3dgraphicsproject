#version 330 core

uniform samplerCube environment_map;

uniform float timer;
uniform vec3 w_camera_position;

in vec3 w_position;

out vec4 out_color;

void main() {
    vec3 normal = normalize(cross(dFdx(w_position), dFdy(w_position)));
    vec3 light_dir = normalize(vec3(cos(timer), sin(timer), 1));

    vec3 view_direction = normalize(w_camera_position - w_position);

    vec4 reflected_color = texture(environment_map, reflect(view_direction, normal));

    // phong shading
    vec3 k_d = vec3(0, 0, 1);
    vec3 k_a = vec3(0, 0, 0.1);
    vec3 k_s = vec3(1, 1, 1);

    vec3 reflected_light = reflect(light_dir, normal);
    vec3 spec = k_s * max(0, pow(dot(reflected_light, view_direction), 100));
    vec4 phong_color = vec4(k_a + k_d * max(0, dot(normal, light_dir)) + spec, 1);

    out_color = mix(phong_color, reflected_color, 0.8);
    out_color.a = 0.6;
}