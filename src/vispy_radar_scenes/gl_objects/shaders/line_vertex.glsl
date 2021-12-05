#version 120

// Uniforms
// ------------------------------------
uniform float u_linewidth;
uniform mat4 u_view;
uniform mat4 u_model;
uniform mat4 u_projection;
uniform float u_scale;

// Attributes
// ------------------------------------
attribute vec3 a_position;
attribute vec4 a_color;

// Varyings
// ------------------------------------
varying vec4 v_color;

// Main
// ------------------------------------
void main() {
    v_color  = a_color;
    vec4 pos = u_view * u_model * vec4(a_position, 1);
    gl_Position = u_projection * pos;
}