varying vec3 vColor;
varying vec3 pos;
vec3 tempPos;
uniform float time;
varying float lerp;
varying vec3 tempNormal;

void main() {
    tempPos = position;

    tempNormal = normal;

    lerp = sin( (mod(time/100000.,100.)*10.) * (3.141592) );
    
    vColor = tempPos * 1.;

    pos = tempPos;

    //tempPos *= 1.005+0.005*sin(tempPos*100.0+(time*0.001));

    tempPos *= 1.005+0.005*sin(tempPos*100.0+(time*0.01));

    gl_Position = projectionMatrix * modelViewMatrix * vec4(tempPos, 1.);
}