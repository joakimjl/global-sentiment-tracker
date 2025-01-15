varying vec3 vColor;
varying vec3 pos;
varying float lerp;
uniform float time;
varying vec3 tempNormal;
varying float landMovement;
uniform float givenRandTime;

void main() {
    vec3 newColor = vec3(0.2,0.8,0.2);

    vec3 sunLocation = vec3(0.,0.,10.);

    vec3 landNormal = normalize(pos);

    vec3 diffStrength = landNormal*sunLocation*1.0;

    float diffSum = diffStrength.x + diffStrength.y + diffStrength.z;

    diffStrength = vec3(diffSum/3.);

    newColor *= diffStrength;

    float relativeMagnitude = abs(cameraPosition.x + cameraPosition.z + cameraPosition.y)/abs(sunLocation.x + sunLocation.z + sunLocation.y);

    float reflection = dot( clamp((sunLocation*relativeMagnitude) + cameraPosition,0.0,1.0), landNormal);

    //vec3 halfWay = normalize(cameraPosition+sunLocation);

    //vec3 refVal = reflect(halfWay, landNormal);

    //float reflectSum = refVal.x + refVal.y + refVal.z;

    //refVal = vec3(-reflectSum/4.)*vec3(0.9882,0.8882,0.539);

    //newColor = newColor + clamp(refVal,-1.0,1.0);
    
    gl_FragColor = vec4(reflection,0.0,0.0,1.); 
}

/* void main() {
    vec3 newColor = vec3(0.2,0.8,0.2);

    vec3 sunLocation = vec3(0.,0.,10.);

    vec3 landNormal = tempNormal;

    vec3 diffStrength = landNormal*sunLocation;

    float diffSum = diffStrength.x + diffStrength.y + diffStrength.z;

    diffStrength = vec3(diffSum/3.0);

    newColor *= diffStrength;

    vec3 halfWay = normalize(cameraPosition+sunLocation);

    vec3 refVal = reflect(halfWay, landNormal);

    float reflectSum = refVal.x + refVal.y + refVal.z;

    refVal = vec3(-reflectSum/4.)*vec3(0.9882,0.8882,0.539);

    newColor = newColor + clamp(refVal,-1.0,1.0);

    float rand = givenRandTime*100.0;

    newColor += 0.2*sin(rand*pos*1.+time*0.001);

    //gl_FragColor = vec4(clamp(newColor,0.,1.), 1.); 
    gl_FragColor = vec4(landNormal,1.); 
} */