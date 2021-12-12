#version 120

// Uniforms
// ------------------------------------
uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;
uniform float u_linewidth;
uniform float u_linewidth_selected;
uniform float u_antialias;
uniform float u_scale;

// Attributes
// ------------------------------------
attribute vec3  a_position;
attribute vec4  a_fg_color;
attribute vec4  a_fg_color_selected;
attribute vec4  a_bg_color;
attribute float a_size;
attribute float a_selected;

// Varyings
// ------------------------------------
varying vec4 v_fg_color;
varying vec4 v_bg_color;
varying float v_size;
varying float v_linewidth;
varying float v_antialias;

void main (void) {
    if (a_selected > 0) {
        v_linewidth = u_linewidth_selected;
        v_fg_color  = a_fg_color_selected;
    } else {
        v_linewidth = u_linewidth;
        v_fg_color  = a_fg_color;
    }
    v_size = a_size * u_scale;
    v_antialias = u_antialias;
    v_bg_color  = a_bg_color;
    gl_Position = u_projection * u_view * u_model * vec4(a_position,1.0);
    gl_PointSize = v_size + 2.*(v_linewidth + 1.5*v_antialias);
}