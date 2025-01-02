varying vec3 vColor;
vec3 tempPos;
uniform float time;

void main() {
    vColor = position * 0.5 + 0.5;

    if (tempPos == vec3(0.0,0.0,0.0)) {
        tempPos = position;
    }

    tempPos.y *= cos( (2.*3.14/1.0)*time );

    gl_Position = projectionMatrix * modelViewMatrix * vec4(tempPos, 1.);
}