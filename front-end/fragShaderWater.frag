varying vec3 vColor;
varying vec3 pos;
varying float lerp;
uniform float time;
varying vec3 tempNormal;

void main() {
    vec3 newColor = vec3(0.2,0.2,0.8);

    vec3 sunLocation = vec3(0.,0.,1.);

    vec3 landNormal = tempNormal;

    vec3 diffStrength = landNormal*sunLocation*4.;

    float diffSum = diffStrength.x + diffStrength.y + diffStrength.z;

    diffStrength = vec3(diffSum/3.);

    vec3 tempPos = pos;

    float sum = tempPos.x + tempPos.y +tempPos.z;

    //vec3 newColor = mix(0.2 + tempPos * vec3(0,0,0.5), vec3(0.2,0.2,0.5),lerp);

    newColor *= diffStrength;

    vec3 halfWay = normalize(cameraPosition+sunLocation);

    vec3 refVal = reflect(halfWay, tempNormal);

    float reflectSum = refVal.x + refVal.y + refVal.z;

    refVal = vec3(-reflectSum/6.)*vec3(0.9882,0.8882,0.539);

    newColor = newColor + refVal-0.2;

    vec3 waves = 0.02*sin(tempPos*100.0+(time*0.01));

    float waveSum = abs(waves.x-waves.y-waves.z) + abs(waves.y-waves.x-waves.z) + abs(waves.z-waves.x-waves.y);

    newColor += exp( exp(waveSum/0.2) -10.) ;

    newColor += waveSum;

    gl_FragColor = vec4(clamp(newColor,0.,1.), 1.); 
}