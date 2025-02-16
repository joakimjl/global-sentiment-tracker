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

    vec3 reflection = reflect(-cameraDir, pos);
    float diffStrength = max(dot(pos,sunLocation),0.2);

    vec3 posDir = normalize(pos);
    float distToCenter = (abs(pos.x) + abs(pos.y) + abs(pos.z)) / (abs(posDir.x) + abs(posDir.y) + abs(posDir.z));

    vec3 baseDiffuse = vec3(0.2,0.2,0.8)+clamp(pow(distToCenter,50.2)*0.00000000000000032*(vec3(0.8,0.8,0.2))-0.3, 0.0,1.0);

    vec3 reflectionColor = vec3(0.8,0.8,0.8) * pow(max(dot(reflection,sunLocation), 0.0), 16.0);
    vec3 diffuseColor = baseDiffuse * diffStrength;

    float timeMulti = 9.0;
    timeMulti = timeMulti*timeMulti;

    float timeScroll = time * 0.0001;
    float tScale = 0.233*0.6667;
    float tScaleHorizontal = 1.03;
    float scrollFactor = sin(timeScroll + pos.x*0.8) + cos(timeScroll + pos.y*0.5);
    vec2 uv = timeScroll*vec2(mod(0.5+pos.x*tScale,1.0),mod(0.5+pos.y*tScale*tScaleHorizontal,1.0));
    vec4 testTexture = texture(noiseTexture, uv);
    
    vec3 finalColor = diffuseColor + reflectionColor -0.2+ (testTexture.x/2.0);


    vec3 color = vec3(.58, .74, 1.);
    vec3 viewDirectionW = normalize(relativeCamera - vPositionW);
    float fresnelTerm = dot(viewDirectionW, waterNormal) * (1. - 0.0001/2.);
    fresnelTerm = clamp(0.5 - fresnelTerm, 0.0, 1.0);

    //finalColor += fresnelTerm;

    gl_FragColor = vec4(testTexture.x-0.5,0.0,0.0,testTexture.x); 
}

