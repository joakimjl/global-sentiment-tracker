varying vec3 vColor;
varying vec3 pos;
varying float lerp;
uniform float time;
varying vec3 tempNormal;
varying float landMovement;
uniform float givenRandTime;
uniform float sentiment;
uniform sampler2D noiseTexture;

varying vec3 vPositionW;
varying vec3 vNormalW;

void main() {
    vec3 sunLocation = normalize(vec3(0.,0.,10.));
    //vec3 sunLocation = normalize(cameraPosition);
    vec3 landNormal = normalize(pos);
    vec3 cameraDir = normalize(cameraPosition - pos);

    float timeScroll = time * 0.0001;

    float scrollFactor = sin(timeScroll + pos.z + pos.x) + cos(timeScroll + pos.z + pos.x);
    vec2 uv = 1.005*fract(vec2(scrollFactor, pos.y));
    vec4 test = texture(noiseTexture, uv);

    vec3 reflection = reflect(-cameraDir, landNormal);
    float diffStrength = max(dot(landNormal,sunLocation),0.6);

    float missing = sentiment/500.0;

    vec3 reflectionColor = vec3(0.8,0.8,0.8) * pow(max(dot(reflection,sunLocation), 0.0), 32.0);
    float redPortion = 0.8*abs(clamp(sentiment,-1.0,-0.2))/abs(clamp(sentiment,-500.0,0.0));
    vec3 diffuseColor = vec3(redPortion,0.8*clamp(sentiment,0.2,1.0),0.2) * diffStrength;

    float posAdding = abs(pos.x) + abs(pos.y) + abs(pos.z);

    float texPart = (0.3*test.x+0.7);

    vec3 finalColor = texPart*diffuseColor + reflectionColor*0.5 - (posAdding*texPart*missing*vec3(0.1,0.1,0.1)) - 0.25*(posAdding*texPart*missing*vec3(0.1,0.1,0.1)*pos);

    vec3 color = vec3(.58, .74, 1.);
    vec3 viewDirectionW = normalize(cameraPosition - vPositionW);
    float fresnelTerm = dot(viewDirectionW, landNormal) * (1. - 0.0001/2.);
    fresnelTerm = clamp(0.5 - fresnelTerm, 0.0, 1.0);

    
    gl_FragColor = vec4(finalColor+fresnelTerm,1.0); 
}