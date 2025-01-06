varying vec3 vColor;
varying vec3 pos;
varying float lerp;
uniform float time;
varying vec3 tempNormal;
varying vec2 uvMap;

void main() {
    vec3 newColor = vec3(0.2,0.2,0.8);

    vec3 sunLocation = vec3(0.,0.,1.);

    vec3 landNormal = tempNormal;

    vec3 diffStrength = landNormal*sunLocation*5.;

    float diffSum = diffStrength.x + diffStrength.y + diffStrength.z;

    diffStrength = vec3(diffSum/3.);

    vec3 tempPos = pos;

    float sum = tempPos.x + tempPos.y +tempPos.z;

    //vec3 newColor = mix(0.2 + tempPos * vec3(0,0,0.5), vec3(0.2,0.2,0.5),lerp);

    newColor *= diffStrength;

    vec3 halfWay = normalize(cameraPosition+sunLocation);

    vec3 refVal = reflect(halfWay, tempNormal);

    float reflectSum = pow(refVal.x + refVal.y + refVal.z, 3.0);

    refVal = vec3(-reflectSum/4.)*vec3(0.9882,0.8882,0.539);

    newColor = newColor + clamp(refVal-0.5,-0.5,1.0);

    vec3 waves = clamp(0.02*sin(tempPos*10.0+time*0.005)-0.01,0.,0.02);

    float waveSumX = -clamp(tempPos.x/5. -0.1 - waves.x*10., 0.0, 1.0);
    float waveSumY = -clamp(tempPos.y/5. -0.1 - waves.y*10., 0.0, 1.0);
    float waveSumZ = -clamp(tempPos.z/5. -0.1 - waves.z*10., 0.0, 1.0);

    float waveSum = (waveSumX + waveSumZ + waveSumY)/3.;

    //newColor += exp( exp(waveSum/0.2) -10.) ;

    //newColor += waveSum;

    vec2 resUv = sin(uvMap*100.+time*0.001);

    //gl_FragColor = vec4(clamp(newColor,0.,1.), 1.);
    gl_FragColor = vec4(newColor,1.); 
}