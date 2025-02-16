varying vec3 vColor;
varying vec3 pos;
vec3 tempPos;
uniform float time;
varying float lerp;
varying vec3 tempNormal;
varying float landMovement;
uniform float givenRandTime;
uniform float sentiment;
uniform sampler2D noiseTexture;

uniform vec3 relativeCamera;
varying vec3 vPositionW;
varying vec3 vNormalW;

void main() {
    tempPos = position;

    tempNormal = normal;

    lerp = sin( (mod(time/100000.,100.)*10.) * (3.141592) );
    
    vColor = tempPos * 1.;

    pos = tempPos;

    vPositionW = vec3( vec4( pos, 1.0 ) );
    vNormalW = normalize( vec3( vec4( tempNormal, 0.0 )  ));

    gl_Position = projectionMatrix * modelViewMatrix * vec4(tempPos, 1.);
}