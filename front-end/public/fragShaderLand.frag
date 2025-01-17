varying vec3 vColor;
varying vec3 pos;
varying float lerp;
uniform float time;
varying vec3 tempNormal;
varying float landMovement;
uniform float givenRandTime;

void main() {
    vec3 sunLocation = normalize(vec3(0.,0.,10.));
    vec3 landNormal = normalize(pos);
    vec3 cameraDir = normalize(cameraPosition - pos);

    vec3 reflection = reflect(-cameraDir, landNormal);
    float diffStrength = max(dot(landNormal,sunLocation),0.0);

    vec3 reflectionColor = vec3(0.8,0.8,0.8) * pow(max(dot(reflection,sunLocation), 0.0), 32.0);
    vec3 diffuseColor = vec3(0.2,0.8,0.2) * diffStrength;

    vec3 finalColor = diffuseColor + reflectionColor*0.5;
    
    gl_FragColor = vec4(finalColor,0.0); 
}