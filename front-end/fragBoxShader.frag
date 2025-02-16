varying vec3 vColor;
varying vec3 pos;
varying float lerp;
uniform float time;
varying vec3 tempNormal;
varying float landMovement;

uniform vec3 relativeCamera;
uniform sampler2D roughness;

uniform float fadeLine;

void main() {
    //vec3 sunLocation = normalize(vec3(0.,0.,10.));
    
    float tScale = 0.233*0.6667;
    float tScaleHorizontal = 1.03;
    vec4 rough = texture(roughness, vec2(mod(0.5+pos.x*tScale,1.0),mod(0.5+pos.y*tScale*tScaleHorizontal,1.0)));

    vec3 sunLocation = normalize(relativeCamera);
    vec3 cameraDir = normalize(relativeCamera - pos);

    vec3 reflection = reflect(-cameraDir, pos);
    float diffStrength = max(dot(pos,sunLocation),0.0);

    float midDist = 0.00;

    float greenMask = 4.0*(pos.y-midDist);
    float redMask = -4.0*(pos.y-midDist);
    float between = clamp(0.8-(clamp(-8.0*(pos.y-midDist),0.0,1.0) + clamp(8.0*(pos.y-midDist),0.0,1.0)),0.0,1.0);
    //vec3 baseDiffuse = vec3(redMask*0.2+between,greenMask*0.2+between,between);
    vec3 baseDiffuse = vec3(rough.x-0.2,rough.x-0.2,rough.x-0.2);

    vec3 reflectionColor = vec3(0.8,0.8,0.8) * pow(max(dot(reflection,sunLocation), 0.0), 16.0);
    vec3 diffuseColor = baseDiffuse;

    vec3 finalColor = diffuseColor + reflectionColor*0.5;
    
    //gl_FragColor = rough; 

    float opacityMask = pos.x + fadeLine;
    gl_FragColor = vec4(finalColor, rough.x-0.2); 
}