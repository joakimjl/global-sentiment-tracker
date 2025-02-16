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

    sumOfSines = vec3(0.0,0.0,0.0);
    for(int i=3;i<10;++i)
    {
        sumOfSines += clamp( (0.00002 * float(i) )*sin( tempPos*20.00*float(i) + ((0.5*time* (float(i))/900.0))),-0.3,0.3 );
    }
    vec3 sine1 = 0.0008*sin(timeMulti*tempPos*2000.0+(0.5*time*0.0052));
    vec3 sine2 = 0.0013*sin(timeMulti*tempPos*900.0+(0.5*time*0.0015));
    vec3 sine3 = 0.0013*sin(timeMulti*tempPos*550.0+(0.5*time*0.005));
    vec3 sine4 = 0.0015*sin(timeMulti*tempPos*200.0+(0.5*time*0.0012));

    sumOfSines += sine1 + sine2 + sine3 + sine4;

    pos = tempPos;

    float timeScroll = time * 0.0001;
    float scrollFactor = sin(timeScroll + pos.z*1.5 + pos.x*0.8) + cos(timeScroll + pos.z*1.2 + pos.y*0.5);
    vec2 size = vec2(textureSize(noiseTexture, 0));
    vec2 uv = vec2(mod(scrollFactor*(0.1+pos.x/30.0),1.0),mod(scrollFactor*(0.1+pos.y/30.0),1.0));
    vec4 testTexture = texture(noiseTexture, uv);

    tempPos *= 0.94+(testTexture.x*0.08);

    pos = tempPos;

    vPositionW = vec3( vec4( pos, 1.0 ) );
    vNormalW = normalize( vec3( vec4( tempNormal, 0.0 )  ));

    gl_Position = projectionMatrix * modelViewMatrix * vec4(tempPos, 1.);
}