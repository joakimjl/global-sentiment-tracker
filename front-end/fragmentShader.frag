varying vec3 vColor;
varying vec3 pos;
varying float lerp;
uniform float time;

void main() {
    float newPosX = fract(pos.x*5.);
    float newPosZ = fract(pos.z*5.);

    vec3 tempPos = pos;

    tempPos.x = newPosX;
    tempPos.z = newPosZ;

    float sum = tempPos.x + tempPos.y +tempPos.z;

    tempPos.x = sum/3.;
    tempPos.z = sum/3.;
    tempPos.y = sum/3.;

    vec3 newColor = mix(0.2 + tempPos * vec3(0,0,0.5), vec3(0.2,0.2,0.5),lerp);

    gl_FragColor = vec4(newColor, 1.); 
}