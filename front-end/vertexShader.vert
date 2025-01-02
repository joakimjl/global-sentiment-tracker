varying vec3 vColor;

void main() {
    vColor = position * 0.5 + 0.5;

    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}