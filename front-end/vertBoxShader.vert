varying vec3 vColor;
varying vec3 pos;
vec3 tempPos;
uniform float time;
varying float lerp;
varying vec3 tempNormal;
varying float landMovement;

uniform vec3 relativeCamera;
uniform sampler2D roughness;

void main() {
    tempPos = position;
    tempNormal = normal;

    pos = tempPos;

    float tScale = 0.233;
    float tScaleHorizontal = 1.0;
    vec4 roughText = texture(roughness, vec2(mod(tempPos.x*tScale,1.0),mod(tempPos.y*tScale*tScaleHorizontal,1.0)));

    gl_Position = projectionMatrix * modelViewMatrix * vec4(tempPos, 1.);
}