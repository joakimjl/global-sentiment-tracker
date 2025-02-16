varying vec3 vColor;
varying vec3 pos;
varying float lerp;
uniform float time;
varying vec3 tempNormal;
varying vec2 uvMap;
varying vec3 sumOfSines;
varying vec3 diffVert;
uniform sampler2D noiseTexture;

uniform vec3 relativeCamera;
varying vec3 vPositionW;
varying vec3 vNormalW;

void main() {
    vec3 sunLocation = normalize(relativeCamera);
    //vec3 sunLocation = normalize(cameraPosition);
    vec3 waterNormal = tempNormal;
    vec3 cameraDir = normalize(relativeCamera - pos);

    vec3 cameraFrontLightV3 = (waterNormal - cameraDir);
    float cameraFrontLight = 0.9 - pow((abs(cameraFrontLightV3.x)+abs(cameraFrontLightV3.y)+abs(cameraFrontLightV3.z)), 7.0)/5.0;

    vec3 reflection = reflect(-cameraDir, waterNormal);
    float diffStrength = max(dot(waterNormal,sunLocation),cameraFrontLight);

    vec3 posDir = normalize(pos);
    float distToCenter = (abs(pos.x) + abs(pos.y) + abs(pos.z)) / (abs(posDir.x) + abs(posDir.y) + abs(posDir.z));

    vec3 baseDiffuse = vec3(0.2,0.2,0.8)+clamp(pow(distToCenter,50.2)*0.00000000000000032*(vec3(0.8,0.8,0.2))-0.3, 0.0,1.0);

    vec3 reflectionColor = vec3(0.4,0.4,0.4) * pow(max(dot(reflection,sunLocation), 0.0), 16.0);
    vec3 diffuseColor = baseDiffuse * diffStrength;

    float timeScroll = time * 0.0001;
    float scrollFactor = sin(timeScroll + pos.z*1.5 + pos.x*0.8) + cos(timeScroll + pos.z*1.2 + pos.y*0.5);
    vec2 size = vec2(textureSize(noiseTexture, 0));
    vec2 uv = vec2(mod(scrollFactor*(0.1+pos.x/30.0),1.0),mod(scrollFactor*(0.1+pos.y/30.0),1.0));
    vec4 testTexture = texture(noiseTexture, uv);
    
    vec3 finalColor = diffuseColor + reflectionColor -0.2;//+ (testTexture.x/2.0);

    vec3 color = vec3(.58, .74, 1.);
    vec3 viewDirectionW = normalize(relativeCamera - vPositionW);
    float fresnelTerm = dot(viewDirectionW, waterNormal) * (1. - 0.0001/2.);
    fresnelTerm = clamp(0.5 - fresnelTerm, 0.0, 1.0);

    finalColor += fresnelTerm;

    gl_FragColor = vec4((finalColor*0.8)+0.1,1.0); 
}

