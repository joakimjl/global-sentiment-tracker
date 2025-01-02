varying vec3 vColor;
varying vec3 pos;
vec3 tempPos;
uniform float time;

void main() {
    tempPos = position;
    //float mult_val = mod(abs(cos( (2.*3.14)*time ))*1.,1.);
    //float newX = tempPos.x+abs(cos(tempPos.x*time*314.)*0.1);
    //float newZ = tempPos.z+abs(cos(tempPos.z*time*314.)*0.1);
    //tempPos.y = tempPos.y+abs(cos(tempPos.y*time*314.)*0.1);

    float newX = 1.1*tempPos.x;
    float newZ = 1.1*tempPos.z;

    tempPos.x = mix(tempPos.x,newX, mod( (time/2.0)+0.5 ,1.));
    tempPos.z = mix(tempPos.z,newZ, mod( (time/2.0)+0.5 ,1.));

    vColor = tempPos * 1.;

    pos = tempPos;

    vColor += vec3(0.,0.,0.);

    gl_Position = projectionMatrix * modelViewMatrix * vec4(tempPos, 1.);
}