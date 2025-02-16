varying vec3 vColor;
varying vec3 pos;
varying float lerp;
uniform float time;
varying vec3 tempNormal;
varying float landMovement;

void main() {
    //vec3 sunLocation = normalize(vec3(0.,0.,10.));
    vec3 sunLocation = normalize(cameraPosition);
    vec3 waterNormal = tempNormal;
    vec3 cameraDir = normalize(cameraPosition - pos);

    vec3 reflection = reflect(-cameraDir, waterNormal);
    float diffStrength = max(dot(waterNormal,sunLocation),0.0);

    float midDist = 0.48;

    float greenMask = 4.0*(pos.y-midDist);
    float redMask = -4.0*(pos.y-midDist);
    float between = clamp(0.8-(clamp(-8.0*(pos.y-midDist),0.0,1.0) + clamp(8.0*(pos.y-midDist),0.0,1.0)),0.0,1.0);
    vec3 baseDiffuse = vec3(redMask+between,greenMask+between,between);

    vec3 reflectionColor = vec3(0.8,0.8,0.8) * pow(max(dot(reflection,sunLocation), 0.0), 16.0);
    vec3 diffuseColor = baseDiffuse;

    vec3 finalColor = diffuseColor + reflectionColor*0.5;
    
    gl_FragColor = vec4(baseDiffuse,1.0); 
}