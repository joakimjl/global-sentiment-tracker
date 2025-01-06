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

    vec3 landNormal = tempNormal*pos*0.8;

    vec3 diffStrength = landNormal*sunLocation*4.;

    float diffSum = diffStrength.x + diffStrength.y + diffStrength.z;

    diffStrength = vec3(diffSum/3.);

    newColor *= diffStrength;

    vec3 halfWay = normalize(cameraPosition+sunLocation);

    vec3 refVal = reflect(halfWay, landNormal);

    float reflectSum = refVal.x + refVal.y + refVal.z;

    refVal = vec3(-reflectSum/6.)*vec3(0.9882,0.8882,0.539);

    newColor = newColor + refVal-0.2;

    float rand = givenRandTime*100.;

    newColor += 0.2*sin(rand*pos*1.+time*0.001);

    gl_FragColor = vec4(clamp(newColor,0.,1.), 1.); 
}