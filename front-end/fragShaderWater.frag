varying vec3 vColor;
varying vec3 pos;
varying float lerp;
uniform float time;
varying vec3 tempNormal;
varying vec2 uvMap;
varying vec3 sumOfSines;
varying vec3 diffVert;

void main() {
    //vec3 sunLocation = normalize(vec3(0.,0.,10.));
    vec3 sunLocation = normalize(cameraPosition);
    vec3 waterNormal = tempNormal;
    vec3 cameraDir = normalize(cameraPosition - pos);

    vec3 reflection = reflect(-cameraDir, waterNormal);
    float diffStrength = max(dot(waterNormal,sunLocation),0.0);

    vec3 posDir = normalize(pos);
    float distToCenter = (abs(pos.x) + abs(pos.y) + abs(pos.z)) / (abs(posDir.x) + abs(posDir.y) + abs(posDir.z));

    vec3 baseDiffuse = vec3(0.2,0.2,0.8)+clamp(pow(distToCenter,50.2)*0.00000000000000032*(vec3(0.8,0.8,0.2))-0.3, 0.0,1.0);

    vec3 reflectionColor = vec3(0.8,0.8,0.8) * pow(max(dot(reflection,sunLocation), 0.0), 16.0);
    vec3 diffuseColor = baseDiffuse * diffStrength;

    
    
    vec3 testSine = vec3(0.0,0.0,0.0);
    for(int i=3;i<10;++i)
    {
        testSine += clamp( (0.00002 * float(i) )*sin( pos*20.00*float(i) + ((time* (float(i))/900.0))),-0.3,0.3 );
    }
    vec3 sine1 = 0.0008*sin(pos*2000.0+(time*0.0052));
    vec3 sine2 = 0.0013*sin(pos*900.0+(time*0.0015));
    vec3 sine3 = 0.0013*sin(pos*550.0+(time*0.005));
    vec3 sine4 = 0.0015*sin(pos*200.0+(time*0.0012));

    testSine += sine4;

    float waveMagnitude = 0.0;

    float test = abs(testSine.x)+abs(testSine.y)+abs(testSine.z);
    test *= test*100.0;
    vec3 waveTops = vec3(test,test,test)*4.0;
    
    vec3 finalColor = diffuseColor + reflectionColor + waveTops;
    gl_FragColor = vec4(finalColor,1.0); 
}