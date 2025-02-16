uniform float time;
varying vec3 givenPos;
varying vec3 vPositionW;
varying vec3 vNormalW;

void main() {
    //vec3 sunLocation = normalize(vec3(0.,0.,10.));
    vPositionW = vec3( vec4( position, 1.0 ) );
    vNormalW = normalize( vec3( vec4( normal, 0.0 ) ));

    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}