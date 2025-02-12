varying vec3 vColor;
varying vec3 pos;
vec3 tempPos;
uniform float time;
varying float lerp;
varying vec3 tempNormal;
varying float landMovement;

void main() {
    tempPos = position;

    pos = tempPos;

    gl_Position = projectionMatrix * modelViewMatrix * vec4(tempPos, 1.);
}