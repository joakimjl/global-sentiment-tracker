varying vec3 vColor;
varying vec3 pos;
vec3 tempPos;
uniform float time;
varying float lerp;

void main() {
    tempPos = position;
    //float mult_val = mod(abs(cos( (2.*3.14)*time ))*1.,1.);
    //float newX = tempPos.x+abs(cos(tempPos.x*time*314.)*0.1);
    //float newZ = tempPos.z+abs(cos(tempPos.z*time*314.)*0.1);
    //tempPos.y = tempPos.y+abs(cos(tempPos.y*time*314.)*0.1);

    //float newX = fract(abs(50.0*tempPos.x));
    //float newZ = fract(abs(50.0*tempPos.z));

    //tempPos.x = mix(tempPos.x,newX, mod( (time/2.0)+0.5 ,1.));
    //tempPos.z = mix(tempPos.z,newZ, mod( (time/2.0)+0.5 ,1.));

    lerp = sin( (mod(time/100000.,100.)*10.) * (3.141592) );

    tempPos.x = fract(tempPos.x+lerp);
    tempPos.z = fract(tempPos.z+lerp);

    

    vColor = tempPos * 1.;

    pos = tempPos;

    gl_Position = projectionMatrix * modelViewMatrix * vec4(tempPos, 1.);
}