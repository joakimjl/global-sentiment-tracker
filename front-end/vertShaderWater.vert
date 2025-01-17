varying vec3 vColor;
varying vec3 pos;
vec3 tempPos;
uniform float time;
varying float lerp;
varying vec3 tempNormal;
varying vec2 uvMap;

void main() {
    tempPos = position;

    tempNormal = normal;

    uvMap = uv;

    lerp = sin( (mod(time/100000.,100.)*10.) * (3.141592) );
    
    vColor = tempPos * 1.;

    pos = tempPos;

    //tempPos *= 1.005+0.005*sin(tempPos*50.0+(time*0.01));

    /* vec3 sumOfSines = vec3(0.0,0.0,0.0);

    for(int i=1;i<10;++i)
    {
        sumOfSines += (0.0004 + 0.0001/float(i))*sin( tempPos*10.0*float(i) + ((time*float(i))/100.0) );
    } */

    vec3 sine1 = 0.0008*sin(tempPos*100.0+(time*0.0092));
    vec3 sine2 = 0.0013*sin(tempPos*50.0+(time*0.003));
    vec3 sine3 = 0.0013*sin(tempPos*25.0+(time*0.01));
    vec3 sine4 = 0.0015*sin(tempPos*10.0+(time*0.0022))+0.0001;

    vec3 sumOfSines = sine1 + sine2 + sine3 + sine4;

    tempPos *= 1.005+sumOfSines;

    gl_Position = projectionMatrix * modelViewMatrix * vec4(tempPos, 1.);
}