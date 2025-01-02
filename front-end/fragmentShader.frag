varying vec3 vColor;
varying vec3 pos;

void main() {

    vec3 newColor = pos * 0.5 + 0.5;

    gl_FragColor = vec4(newColor, 1.); 
}