#version 120

// Varyings
// ------------------------------------
varying vec4 v_color;

// Main
// ------------------------------------
void main() {
    gl_FragColor = v_color;
}