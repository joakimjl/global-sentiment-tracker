varying vec3 vColor;
vec3 tempPos;

void main() {
    vColor = position * 0.5 + 0.5;

    if (tempPos == vec3(0.0,0.0,0.0)) {
        tempPos = position;
    }

    tempPos.y *= sin(0.5);

    gl_Position = projectionMatrix * modelViewMatrix * vec4(tempPos, 1.);
}