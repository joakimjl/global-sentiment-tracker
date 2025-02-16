varying vec3 vColor;
varying vec3 pos;
vec3 tempPos;
uniform float time;
varying float lerp;
varying vec3 tempNormal;
varying vec2 uvMap;
varying vec3 sumOfSines;
varying vec3 diffVert;
uniform sampler2D noiseTexture;

uniform vec3 relativeCamera;
varying vec3 vPositionW;
varying vec3 vNormalW;

void main() {
    tempPos = position*0.996;

    tempNormal = normal;

    uvMap = uv;

    lerp = sin( (mod(time/100000.,100.)*10.) * (3.141592) );
    
    vColor = tempPos * 0.001;

    float timeMulti = 9.0;
    timeMulti = timeMulti*timeMulti;

    pos = tempPos;

    vPositionW = vec3( vec4( pos, 1.0 ) );
    vNormalW = normalize( vec3( vec4( tempNormal, 0.0 )  ));

    gl_Position = projectionMatrix * modelViewMatrix * vec4(tempPos, 1.);
}