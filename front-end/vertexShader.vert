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

    //tempPos.x = (tempPos.x+lerp);
    //tempPos.z = (tempPos.z+lerp);

    vColor = tempPos * 1.;

    pos = tempPos;

    //tempPos *= 0.90+time*0.0000011;

    tempPos *= 0.95+0.05*sin(tempPos*100.0+(time*0.001));

    gl_Position = projectionMatrix * modelViewMatrix * vec4(tempPos, 1.);
}