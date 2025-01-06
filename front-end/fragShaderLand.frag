varying vec3 vColor;
varying vec3 pos;
varying float lerp;
uniform float time;
varying vec3 tempNormal;
varying float landMovement;
uniform float givenRandTime;

void main() {
    vec3 newColor = vec3(0.2,0.8,0.2);

    vec3 sunLocation = vec3(0.,0.,1.);

    vec3 landNormal = normal;

    vec3 diffStrength = landNormal*sunLocation;

    float diffSum = diffStrength.x + diffStrength.y + diffStrength.z;

    diffStrength = vec3(diffSum/3.);

    newColor *= diffStrength;

    vec3 halfWay = normalize(cameraPosition+sunLocation);

    vec3 refVal = reflect(halfWay, landNormal);

    float reflectSum = pow(refVal.x + refVal.y + refVal.z, 3.0);

    refVal = vec3(-reflectSum/4.)*vec3(0.9882,0.8882,0.539);

    newColor = newColor + clamp(refVal,-0.5,1.0);

    float rand = givenRandTime*100.0;

    newColor += 0.2*sin(rand*pos*1.+time*0.001);

    gl_FragColor = vec4(clamp(landNormal,0.,1.), 1.); 
}