// water fragment shader

#version 330 core

uniform samplerCube environment_map;

uniform float timer;
uniform vec3 w_camera_position;

in vec3 w_position;

out vec4 out_color;

float exponentialFog(float dist, float density) {
    return clamp(1 - exp(-pow(density * dist, 2)), 0, 1);
}

void main() {
    // calculate normals from derivative of position
    // (i understand how the derivative functions work, but it still feels like black magic)
    vec3 normal = normalize(cross(dFdx(w_position), dFdy(w_position)));

    // light direction is the same as in the "big" shader used for the rest
    // in hindsight we should have used a uniform for that...
    vec3 light_dir = normalize(vec3(cos(timer), sin(timer), 1));

    // reflect view direction and sample from environment map for reflection color
    vec3 view_direction = normalize(w_camera_position - w_position);
    vec4 reflected_color = texture(environment_map, reflect(view_direction, normal));

    // phong shading
    vec3 k_d = vec3(0, 0, 1);
    vec3 k_a = vec3(0, 0, 0.1);
    vec3 k_s = vec3(1, 1, 1);

    vec3 reflected_light = reflect(light_dir, normal);
    vec3 spec = k_s * max(0, pow(dot(reflected_light, view_direction), 100));
    vec4 phong_color = vec4(k_a + k_d * max(0, dot(normal, light_dir)) + spec, 1);

    // output color is a mix between phong and reflection
    out_color = mix(phong_color, reflected_color, 0.8);

    // set transparency to semi-transparent
    out_color.a = 0.6;

    // lastly, apply the same fog effect as in the main fragment shader
    float distance_to_camera = distance(w_position, w_camera_position);
    float fog_factor = exponentialFog(distance_to_camera, 0.0035);

    vec4 fog_color = vec4(0.8, 1, 0.8, 1);

    out_color = mix(out_color, fog_color, fog_factor);
}