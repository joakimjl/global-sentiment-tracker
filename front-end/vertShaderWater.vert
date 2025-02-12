varying vec3 vColor;
varying vec3 pos;
vec3 tempPos;
uniform float time;
varying float lerp;
varying vec3 tempNormal;
varying vec2 uvMap;
varying vec3 sumOfSines;
varying vec3 diffVert;

void main() {
    tempPos = position*0.996;

    tempNormal = normal;

    uvMap = uv;

    lerp = sin( (mod(time/100000.,100.)*10.) * (3.141592) );
    
    vColor = tempPos * 1.;

    sumOfSines = vec3(0.0,0.0,0.0);
    for(int i=3;i<10;++i)
    {
        sumOfSines += clamp( (0.00002 * float(i) )*sin( tempPos*20.00*float(i) + ((time* (float(i))/900.0))),-0.3,0.3 );
    }
    vec3 sine1 = 0.0008*sin(tempPos*2000.0+(time*0.0052));
    vec3 sine2 = 0.0013*sin(tempPos*900.0+(time*0.0015));
    vec3 sine3 = 0.0013*sin(tempPos*550.0+(time*0.005));
    vec3 sine4 = 0.0015*sin(tempPos*200.0+(time*0.0012));

    sumOfSines += sine1 + sine2 + sine3 + sine4;

    tempPos *= 1.005+(sumOfSines*2.15);

    pos = tempPos;

    gl_Position = projectionMatrix * modelViewMatrix * vec4(tempPos, 1.);
}