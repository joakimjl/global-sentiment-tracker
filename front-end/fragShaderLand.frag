varying vec3 vColor;
varying vec3 pos;
varying float lerp;
uniform float time;
varying vec3 tempNormal;
varying float landMovement;
uniform float givenRandTime;
uniform float sentiment;
uniform sampler2D noiseTexture;

uniform vec3 relativeCamera;
varying vec3 vPositionW;
varying vec3 vNormalW;

void main() {
    vec3 sunLocation = normalize(relativeCamera);
    //vec3 sunLocation = normalize(cameraPosition);
    vec3 landNormal = normalize(pos);
    vec3 cameraDir = normalize(relativeCamera - pos);

    vec3 cameraFrontLightV3 = (landNormal - cameraDir);

    float cameraFrontLight = 0.9 - pow((abs(cameraFrontLightV3.x)+abs(cameraFrontLightV3.y)+abs(cameraFrontLightV3.z)), 7.0)/5.0;

    float timeScroll = time * 0.0001;

    float scrollFactor = sin(timeScroll + pos.z + pos.x) + cos(timeScroll + pos.z + pos.x);
    vec2 uv = 1.005*fract(vec2(scrollFactor, pos.y));
    vec4 test = texture(noiseTexture, uv);

    vec3 reflection = reflect(-cameraDir, landNormal);
    float diffStrength = max(dot(landNormal,sunLocation),cameraFrontLight);

    float missing = sentiment/500.0;

    vec3 baseColor = vec3(0.4,0.4,0.4) * diffStrength;

    //DO LIGHT WITH REFLECTION
    vec3 reflectionColor = vec3(0.8,0.8,0.8) * pow(max(dot(reflection,sunLocation), 0.0), 32.0);
    float redPortion = abs(clamp(sentiment,-1.0,-0.01))/abs(clamp(sentiment,-500.0,-1.0));
    float greenPortion = abs(clamp(sentiment,0.01,1.0))/abs(clamp(sentiment,-500.0,-1.0));
    
    float texPart = (0.1*test.x+0.2) * diffStrength;
    vec3 colorPortion = vec3(redPortion, greenPortion, 0.0) * (clamp(2.5*test.x-1.15, 0.0,1.0));

    vec3 diffuseColor = clamp(colorPortion, -0.8,0.8) * diffStrength;

    float posAdding = abs(pos.x) + abs(pos.y) + abs(pos.z);

    vec3 finalColor = texPart * baseColor + diffuseColor*0.7 + reflectionColor*0.5 - (posAdding*texPart*missing*vec3(0.1,0.1,0.1)) - 0.25*(posAdding*texPart*missing*vec3(0.1,0.1,0.1)*pos);

    vec3 color = vec3(.58, .74, 1.);
    vec3 viewDirectionW = normalize(relativeCamera - vPositionW);
    float fresnelTerm = dot(viewDirectionW, landNormal) * (1. - 0.0001/2.);
    fresnelTerm = clamp(0.5 - fresnelTerm, 0.0, 1.0);

    //finalColor += fresnelTerm;
    
    gl_FragColor = vec4(reflectionColor,1.0); 
}