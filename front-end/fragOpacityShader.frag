uniform float time;
varying vec3 givenPos;
varying vec3 vPositionW;
varying vec3 vNormalW;

void main() {
    vec3 color = vec3(.58, .74, 1.);
    vec3 viewDirectionW = normalize(vec3(0.0,0.0,50.0));
    float fresnelTerm = dot(viewDirectionW, vNormalW) * (1. - 0.01/2.);
    fresnelTerm = clamp(0.999 - fresnelTerm, 0.0, 1.0);

    gl_FragColor = vec4(vec3(0.5,0.5,1.0), 0.75-fresnelTerm);
} 