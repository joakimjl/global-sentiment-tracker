varying vec3 vColor;
varying vec3 pos;
varying float lerp;
uniform float time;
varying vec3 tempNormal;
varying vec2 uvMap;

void main() {
    vec3 sunLocation = normalize(vec3(0.,0.,10.));
    vec3 waterNormal = tempNormal;
    vec3 cameraDir = normalize(cameraPosition - pos);

    vec3 reflection = reflect(-cameraDir, waterNormal);
    float diffStrength = max(dot(waterNormal,sunLocation),0.0);

    vec3 reflectionColor = vec3(0.8,0.8,0.8) * pow(max(dot(reflection,sunLocation), 0.0), 16.0);
    vec3 diffuseColor = vec3(0.2,0.2,0.8) * diffStrength;

    vec3 finalColor = diffuseColor + reflectionColor;
    
    gl_FragColor = vec4(finalColor,1.0); 
}