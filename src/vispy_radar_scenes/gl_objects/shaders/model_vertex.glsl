#version 120

// Uniforms
// ------------------------------------
uniform mat4 u_view;
uniform mat4 u_model;
uniform mat4 u_projection;
uniform float u_scale;

// Attributes
// ------------------------------------
attribute vec3 a_position;
attribute vec3 a_normals;
attribute vec4 a_color;

// Varyings
// ------------------------------------
varying vec4 v_color;

// Main
// ------------------------------------
void main() {
    vec4 pos = u_view * u_model * vec4(a_position, 1);
    gl_Position = u_projection * pos;

    // Compute the vertex's normal in camera space
    vec3 normal_cameraspace = normalize(( u_view * u_model * vec4(a_normals,0)).xyz);
    // Vector from the vertex (in camera space) to the camera (which is at the origin)
    vec3 cameraVector = normalize(vec3(0, 0, 0) - (pos).xyz);

    // Compute the angle between the two vectors
    float cosTheta = clamp( dot( normal_cameraspace, cameraVector ), 0,1 );

    // The coefficient will create a nice looking shining effect.
    // Also, we shouldn't modify the alpha channel value.
    v_color  = vec4(0.3 * a_color.rgb + cosTheta * a_color.rgb, a_color.a);
}

