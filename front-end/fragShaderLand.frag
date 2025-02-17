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
    vec3 landNormal = normalize(pos);
    vec3 cameraDir = normalize(relativeCamera - pos);

    float timeScroll = time * 0.0001;
    float scrollFactor = sin(timeScroll  -pos.z + pos.x) + cos(timeScroll -pos.z + pos.x);
    vec2 uv = vec2(mod(scrollFactor*(0.2+pos.x/20.0),1.0),mod(scrollFactor*(0.2+pos.y/20.0),1.0));
    vec4 test = texture(noiseTexture, uv);

    vec3 reflection = reflect(-cameraDir, landNormal);
    float diffStrength = max(dot(landNormal,sunLocation),0.2);

    float missing = sentiment/500.0;

    vec3 baseColor = vec3(0.4,0.4,0.4) * diffStrength;

    vec3 reflectionColor = vec3(0.3,0.3,0.3) * pow(max(dot(reflection,sunLocation), 0.0), 32.0);
    float redPortion = abs(clamp(sentiment,-1.0,-0.01))/abs(clamp(sentiment,-500.0,-1.0));
    float greenPortion = abs(clamp(sentiment,0.01,1.0))/abs(clamp(sentiment,-500.0,-1.0));
    
    float texPart = (0.3*test.x+0.1) * diffStrength;
    vec3 colorPortion = vec3( 3.5*(redPortion-greenPortion), 3.5*(greenPortion-redPortion), 0.0) * (clamp(2.6*test.x-1.15, 0.0,1.0));

    vec3 diffuseColor = clamp(colorPortion, -0.8,0.8) * diffStrength;

    float posAdding = abs(pos.x) + abs(pos.y) + abs(pos.z);

    vec3 finalColor = texPart * baseColor + diffuseColor*0.7 + reflectionColor*0.5 - (posAdding*texPart*missing*vec3(0.1,0.1,0.1)) - 0.25*(posAdding*texPart*missing*vec3(0.1,0.1,0.1)*pos);

    vec3 color = vec3(.58, .74, 1.);
    vec3 viewDirectionW = normalize(relativeCamera - vPositionW);
    float fresnelTerm = dot(viewDirectionW, landNormal) * (1. - 0.0001/2.);
    fresnelTerm = clamp(0.5 - fresnelTerm, 0.0, 1.0);

    finalColor += fresnelTerm;
    
    gl_FragColor = vec4(finalColor, 1.0); 
}