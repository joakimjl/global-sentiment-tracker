varying vec3 vColor;
varying vec3 pos;
varying float lerp;
uniform float time;
varying vec3 tempNormal;

void main() {
    float newPosX = fract(pos.x*5.);
    float newPosZ = fract(pos.z*5.);

    vec3 sunLocation = vec3(0.,0.,1.);

    vec3 tempPos = pos;

    tempPos.x = newPosX;
    tempPos.z = newPosZ;

    float sum = tempPos.x + tempPos.y +tempPos.z;

    tempPos.x = sum/3.;
    tempPos.z = sum/3.;
    tempPos.y = sum/3.;

    //vec3 newColor = mix(0.2 + tempPos * vec3(0,0,0.5), vec3(0.2,0.2,0.5),lerp);

    vec3 newColor = vec3(0.2,0.2,0.8);

    vec3 diffuseStrength = tempNormal*sunLocation;

    newColor *= diffuseStrength;

    vec3 halfWay = normalize(cameraPosition+sunLocation);

    vec3 refVal = reflect(halfWay,tempNormal);

    float reflectSum = refVal.x + refVal.y + refVal.z;

    refVal = vec3(-reflectSum/3.)*vec3(0.9882,0.5882,0.0039);

    newColor = clamp(newColor,0.,1.) + refVal;

    gl_FragColor = vec4(newColor, 1.); 
}