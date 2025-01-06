varying vec3 vColor;
varying vec3 pos;
vec3 tempPos;
uniform float time;
varying float lerp;
varying vec3 tempNormal;
varying float landMovement;
uniform float givenRandTime;

void main() {
    tempPos = position;

    tempNormal = normal;

    lerp = sin( (mod(time/100000.,100.)*10.) * (3.141592) );
    
    vColor = tempPos * 1.;

    pos = tempPos;

    gl_Position = projectionMatrix * modelViewMatrix * vec4(tempPos, 1.);
}