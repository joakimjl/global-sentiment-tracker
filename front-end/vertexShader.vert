varying vec3 vColor;
varying vec3 pos;
vec3 tempPos;
uniform float time;
varying float lerp;

void main() {
    tempPos = position;

    lerp = sin( (mod(time/100000.,100.)*10.) * (3.141592) );

    //tempPos.x = (tempPos.x+lerp);
    //tempPos.z = (tempPos.z+lerp);

    vColor = tempPos * 1.;

    pos = tempPos;

    gl_Position = projectionMatrix * modelViewMatrix * vec4(tempPos, 1.);
}