import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { clamp, randFloat } from 'three/src/math/MathUtils';
//import { GLTFExporter } from 'three/addons/exporters/GLTFExporter.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
//import { forEachChild } from 'typescript';
import vertWater from './vertShaderWater.vert?raw';
import vertLand from './vertShaderLand.vert?raw';
import fragWater from './fragShaderWater.frag?raw';
import fragLand from './fragShaderLand.frag?raw';
import vertChart from './vertChartShader.vert?raw';
import fragChart from './fragChartShader.frag?raw';
import vertOpacity from './vertOpacityShader.vert?raw';
import fragOpacity from './fragOpacityShader.frag?raw';
import { FontLoader } from 'three/addons/loaders/FontLoader.js';
import { TextGeometry } from 'three/addons/geometries/TextGeometry.js';
import { TessellateModifier } from 'three/examples/jsm/modifiers/TessellateModifier.js';
import { count, reverse } from 'd3';

const scene = new THREE.Scene();
const width = window.innerWidth;
const height = window.innerHeight;
const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
//const camera = new THREE.OrthographicCamera( width / - 2, width / 2, height / 2, height / - 2, 1, 1000 );
const renderer = new THREE.WebGLRenderer({antialias : true});
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();

var initMoveUi = false;
var initMoveReturnUi = false;
var noiseDone = false;

var noiseTexture = new THREE.TextureLoader().load(
    "./PernlinNoise.png",
    (texture) => {
        noiseTexture = texture;
        noiseDone = true;
    }
);

var noiseTexture2 = new THREE.TextureLoader().load(
    "./Pernlin2.png",
    (texture) => {
        noiseTexture2 = texture;
    }
);

function onPointerMove( event ) {
	pointer.x = ( event.clientX / window.innerWidth ) * 2 - 1;
	pointer.y = - ( event.clientY / window.innerHeight ) * 2 + 1;
}


var dataFetching = null;
function generateText(displayText, data=null, name){
    const fontloader = new FontLoader();
    fontloader.load('./Roboto_Regular.json', function(font) {
        const infographicScene = new THREE.Scene();

        //testing dummy data
        if (data == null){
            data = [-1,-0.7,-0,1,-1,-1,-1,-0.5,0,0.1,0.2,1]
            return
        }
        var cur = data.get(name[0]+name[1])

        var processed = processData(mode,cur,false)
        var resArr = []
        
        for (let index = 0; index < processed[0].length; index++) {
            const element1 = processed[0][index];
            const element2 = processed[1][index];

            let neg = element1[0] + element2[0];
            let neu = element1[1] + element2[1];
            let pos = element1[2] + element2[2];
            let res = (pos-neg)/(neu+(Math.abs(pos-neg)))
            //console.log('pos: %f,  neu: %f,  neg: %f   res: %f', pos,neu,neg,res)
            resArr.push(res)
        }

        const hDiv = 2.3; //Height division
        const wDiv = 0.3*resArr.length; 
        
        var dataCoords = [];
        for (let index = 0; index < resArr.length-1; index++) {
            const element = resArr[index];//Should be dates
            dataCoords.push([(index-parseInt(resArr.length/2))/wDiv, element/hDiv+0.5])
        }
        dataCoords.push([(resArr.length-1-parseInt(resArr.length/2))/wDiv, resArr[resArr.length-1]/hDiv+0.5])
        for (let index = resArr.length-1; index >= 0; index--) {
            const element = resArr[index];//Should be dates
            dataCoords.push([(index-parseInt(resArr.length/2))/wDiv, element/hDiv+0.45])
        }resArr
        dataCoords.push([(0-parseInt(resArr.length/2))/wDiv, resArr[0]/hDiv+0.45])

        const dataShape = new THREE.Shape();//Needs to make shape into cubes..
        dataShape.moveTo(dataCoords[0][0], dataCoords[0][1]);
        for (let i = 0; i < dataCoords.length; i++) {
            dataShape.lineTo(dataCoords[i][0], dataCoords[i][1]);
        }

        const extrudeSettings = {
            steps: 1,
            depth: 0.0001,
            bevelEnabled: false
        };

        let dataGeometry = new THREE.ExtrudeGeometry(dataShape, extrudeSettings);

        let dataTesselateAmount = clamp(dataCoords.length/2,5,100);
        const tessellateModifier = new TessellateModifier(3,dataTesselateAmount);
        dataGeometry = tessellateModifier.modify(dataGeometry);

        for (let i = 0; i < dataGeometry.attributes.position.count; i++) {
            const x = dataGeometry.attributes.position.getX(i);
            const y = dataGeometry.attributes.position.getY(i);
            const z = dataGeometry.attributes.position.getZ(i);

            dataGeometry.attributes.position.setXYZ(i, x, y, z);
        }
    
        const dataMaterial = new THREE.ShaderMaterial({
            vertexShader: vertChart,
            fragmentShader: fragChart,
            uniforms: {
                time: {value: (Date.now()/10)%10}
            }
        });
        const dataMesh = new THREE.Mesh( dataGeometry, dataMaterial );
        dataMesh.name = "chart";

        infographicScene.add(dataMesh)

        const textMesh = makeTextMesh(displayText,font)
        textMesh.name = "_infographic";
        infographicScene.name = "_infographic";
        textMesh.position.y = 1
        infographicScene.add(textMesh)

        //Making the date label at bottom
        const dataAtCountrySorted = new Map([...data.get(name[0]+name[1]).entries()].sort());

        const iter = dataAtCountrySorted.keys();
        let key = iter.next().value;
        let stringTemp = "";
        let locXArr = dataCoords;
        let count = 0;
        let year = "";
        let month = "";
        let day = "";
        let count_dash = 0;
        let jumpDays = 0;
        let distAway = 4;
        let lastDayPlace = 999;
        while (key != undefined){
            for (let index = 0; index < key.length; index++) {
                const element = key[index];
                if (element == "-"){
                    if (count_dash == 0){
                        if (stringTemp != year && stringTemp.length == 4){
                            const resText = makeTextMesh(stringTemp,font)
                            resText.position.x += locXArr[parseInt(count)][0]
                            infographicScene.add(resText)
                            year = stringTemp
                            resText.position.y -= 0.25
                        }
                    }
                    if (count_dash == 1){
                        if (stringTemp != month){
                            const resText = makeTextMesh(stringTemp,font)
                            resText.position.x += locXArr[parseInt(count)][0]
                            infographicScene.add(resText)
                            month = stringTemp
                            resText.position.y -= 0.125
                        }
                    }
                    if (count_dash == 2){
                        let dayAwayLogic = (parseInt(day)-jumpDays <= parseInt(stringTemp) && parseInt(day)+jumpDays >= parseInt(stringTemp));
                        let distAwayLogic = (lastDayPlace >= distAway);
                        if (!dayAwayLogic && distAwayLogic){
                            const resText = makeTextMesh(stringTemp,font)
                            resText.position.x += locXArr[parseInt(count)][0]
                            infographicScene.add(resText)
                            lastDayPlace = 0
                        }
                        day = stringTemp;
                        count += 1
                        lastDayPlace += 1
                    }
                    count_dash += 1
                    stringTemp = ""
                    
                } else {
                    stringTemp += element
                }
            }
            count_dash = 0
            key = iter.next().value;
        }


        infographicScene.position.y = 0
        
        scene.add(infographicScene);
        const tempLight = new THREE.PointLight({color: new THREE.Color(0xffffff), intensity: 1000, decay: 0});
        tempLight.position.z = 10;
        scene.add(tempLight);
        initMoveUi = true;
    });
}

function makeTextMesh(text,font,locX){
    const geometry = new TextGeometry(text, {
        font: font,
        size: 0.1,
        depth: 0.02,
    });

    //Move origin of mesh
    geometry.translate(-0.03*text.length,0,0)

    const textMesh = new THREE.Mesh(geometry, [
        new THREE.MeshBasicMaterial({color: new THREE.Color(0xffffff)}),
        new THREE.MeshBasicMaterial({color: new THREE.Color(0xffffff)})
    ]);

    return textMesh;
}

const initCameraDistance = 1000;
camera.position.z = initCameraDistance;
const finishCameraDist = 7 + clamp( Math.abs( (window.innerHeight -1000)/300 ), 0, 10);
//const controls = new OrbitControls(camera, renderer.domElement);

var intersects = raycaster.intersectObjects( scene.children );
var hoveredMesh;

var land_mat_arr = [];

const water_planet_material = new THREE.ShaderMaterial({
    vertexShader: vertWater,
    fragmentShader: fragWater,
    uniforms: {
        time: {value: (Date.now()/10)%10},
        relativeCamera: {value: new THREE.Vector3(0,0,0)},
        noiseTexture: {value: noiseTexture2}
    }
});

water_planet_material.needsUpdate = true;

const land_planet_material = new THREE.ShaderMaterial({
    vertexShader: vertLand,
    fragmentShader: fragLand,
    uniforms: {
        time: {value: (Date.now()/10)%10},
        landMovement: {value: 0.001},
        givenRandTime: {value: randFloat(0,1)},
        relativeCamera: {value: new THREE.Vector3(0, 1, 1)},
        noiseTexture: {value: noiseTexture}
    }
});

land_planet_material.needsUpdate = true;

const loader = new GLTFLoader();
loader.setCrossOrigin('use-credentials');

// Load a glTF resource
loader.load(
    // resource URL
    './planet.gltf',
    
    // called when the resource is loaded
    function ( gltf ) {

        let relativeEuler = new THREE.Vector3(0, 0, 1).applyEuler(new THREE.Euler(eulerPitch,eulerYaw,0));

        gltf.scene.children[gltf.scene.children.length-1].material = water_planet_material;

        for (let index = 0; index < gltf.scene.children.length-1; index++) {
            const element = gltf.scene.children[index];
            let rand = randFloat(0,1);
            const land_planet_temp = new THREE.ShaderMaterial({
                vertexShader: vertLand,
                fragmentShader: fragLand,
                uniforms: {
                    time: {value: (Date.now()/10)%10},
                    landMovement: {value: 0.001},
                    givenRandTime: {value: rand},
                    sentiment: {value: rand},
                    noiseTexture: {value: noiseTexture},
                    relativeCamera: {value: relativeEuler},
                }
            });
            land_planet_temp.name = element.name
            land_mat_arr.push(land_planet_temp); //ADD COUNTRY NAME
            land_planet_temp.needsUpdate = true;
            element.material = land_planet_temp;
        }

        //console.log(land_mat_arr)

        scene.add( gltf.scene );

        gltf.animations; // Array<THREE.AnimationClip>
        gltf.scene; // THREE.Group
        gltf.scenes; // Array<THREE.Group>
        //gltf.cameras; // Array<THREE.Camera>
        gltf.asset; // Object

    },
    // called while loading is progressing
    function ( xhr ) {
        console.log( ( xhr.loaded / xhr.total * 100 ) + '% loaded' );
    },
    // called when loading has errors
    function ( error ) {
        console.log( error );
    }
);

function lerp(a, b, alpha) {
    return a + alpha * (b - a);
}
var frame_count = 0;
var alpha = 0;

var mode = "international";

function processData(mode,data,sumOverTime){
    const iter = data.keys();
    let key = iter.next().value;
    var vader = [];
    var rob = [];
    while (key != undefined) {
        if (mode == "international") {
            vader.push(data.get(key)[2]);
            rob.push(data.get(key)[3]);
        } else if (mode == "national") {
            vader.push(data.get(key)[0]);
            rob.push(data.get(key)[1]);
        }
        key = iter.next().value
    }

    if (sumOverTime == false) {
        let vaderArr = [];
        let robArr = [];
        for (let index = 0; index < vader.length; index++) {
            const elementVader = vader[index];
            const elementRob = rob[index];
            vaderArr.push(addSentiment(elementVader));
            robArr.push(addSentiment(elementRob));
        }
        return ([vaderArr, robArr])
    }

    if (sumOverTime == true) {
        let vaderCalc = [0,0,0];
        let robCalc = [0,0,0];
        for (let index = 0; index < vader.length; index++) {
            const elementVader = vader[index];
            const elementRob = rob[index];
            let vaderTemp = addSentiment(elementVader);
            let robTemp = addSentiment(elementRob);
            for (let j = 0; j < 3; j++) {
                const eleInVad = vaderTemp[j];
                const eleInRob = robTemp[j];
                vaderCalc[j] += eleInVad
                robCalc[j] += eleInRob
            }
        }
        for (let index = 0; index < vaderCalc.length; index++) {
            const element = vaderCalc[index];
            robCalc[index] += element
        }
        return robCalc
    }
}

function addSentiment(checked){
    let tempNum = "";
    let isNum = false;
    let numArr = [];

    for (let index = 1; index < checked.length; index++) {
        const char = checked[index];
        const prevChar = checked[index-1];
        if (prevChar == "(" || prevChar == ","){
            isNum = true;
        }
        if (char == "," || char == ")"){
            isNum = false;
            numArr.push(parseInt(tempNum));
            tempNum = "";
        }
        if (isNum) {
            tempNum += char;
        }
    }
    return numArr;
}



async function fetchQuery(country, query, timeframe) {
    const url = `https://6x8t077c58.execute-api.eu-west-1.amazonaws.com/gst-prod/gst-fetch-info?country=${country}&query=${query}&timeframe=${timeframe}`;
    try {
        const response = await fetch(url, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin" : '*',
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Methods": "GET,HEAD,OPTIONS,POST,PUT",
                "Access-Control-Allow-Headers": "Access-Control-Allow-Headers, Origin,Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers",
            },
        });
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        const json = await response.json();
        //console.log("Fetching: %s", country);
        try{
            const names = new Map();
            if (land_mat_arr[0] != null){
                for (let index = 0; index < json.length; index++) {
                    const ele = json[index];
                    if (names.has(ele[0]) == false){
                        const in_map = new Map()
                        names.set(ele[0], in_map.set(ele[5], [ele[1],ele[2],ele[3],ele[4],ele[6]]) );
                    } else {
                        names.get(ele[0]).set(ele[5], [ele[1],ele[2],ele[3],ele[4],ele[6]]);
                    }
                }
                let prevCountry = []
                for (let index = 0; index < land_mat_arr.length; index++) {
                    const element = land_mat_arr[index];
                    const countryCode = element.name[0] + element.name[1];
                    if (countryCode == prevCountry[0]) {
                        element.uniforms.sentiment.value = prevCountry[1]
                    } else if (names.has(countryCode)) {
                        let cur = names.get(countryCode)
                        const iter = cur.keys();
                        let key = iter.next().value;
                        var vader = [];
                        var rob = [];
                        while (key != undefined) {
                            if (mode == "international") {
                                vader.push(cur.get(key)[2]);
                                rob.push(cur.get(key)[3]);
                            } else if (mode == "national") {
                                vader.push(cur.get(key)[0]);
                                rob.push(cur.get(key)[1]);
                            }
                            key = iter.next().value
                        }

                        let vaderCalc = [0,0,0];
                        let robCalc = [0,0,0];
                        for (let index = 0; index < vader.length; index++) {
                            const elementVader = vader[index];
                            const elementRob = rob[index];
                            let vaderTemp = addSentiment(elementVader);
                            let robTemp = addSentiment(elementRob);
                            for (let j = 0; j < 3; j++) {
                                const eleInVad = vaderTemp[j];
                                const eleInRob = robTemp[j];
                                vaderCalc[j] += eleInVad
                                robCalc[j] += eleInRob
                            }
                        }

                        for (let index = 0; index < robCalc.length; index++) {
                            const element = robCalc[index];
                            vaderCalc[index] += element;
                        }

                        let neg = vaderCalc[0];
                        let neu = vaderCalc[1];
                        let pos = vaderCalc[2];

                        let tempRes = (pos-neg)/(neu+(Math.abs(pos-neg)))
                        element.uniforms.sentiment.value = tempRes;
                        prevCountry = [countryCode, tempRes]
                    }
                    else {
                        if (country == "World") {
                            element.uniforms.sentiment.value = -500;
                        }
                    }
                }
            }
            if (names.size == 0) {
                clickChange = false
                dataFetching = dataFetching
                console.log("Country not in DB")
            } else {
                dataFetching = names  
            }
        }
        catch(error){console.log("Land not done yet", error.message);}
    } catch (error) {
        console.error("Fetch error:", error.message);
    }
}


var controls_done = false;
var last_fps_time = Date.now();
let fetched = false;
var prevName = "";
var clickChange = false;


const outlineSphereMat = new THREE.ShaderMaterial({
    vertexShader: vertOpacity,
    fragmentShader: fragOpacity,
    uniforms: {
        time: {value: (Date.now()/10)%10}
    }
});

outlineSphereMat.needsUpdate = true;
outlineSphereMat.transparent = true;

const outlineSphere = new THREE.Mesh(new THREE.SphereGeometry(3.2,22,22),outlineSphereMat);
outlineSphere.scale.z = 0.001;
outlineSphere.name = "_outlineSphere"
scene.add(outlineSphere);
fetchQuery("World","Any",1);

var moveUILerp = -1;
var accelUI = 0;

function movePlanetAndText(){
    let moveUILerpChange = 0.5+moveUILerp/2;
    scene.getObjectByName("_outlineSphere").position.x = lerp(0,-3,moveUILerpChange)
    scene.getObjectByName("Scene").position.x = lerp(0,-3,moveUILerpChange)
    if (scene.getObjectByName("_infographic") != undefined){
        scene.getObjectByName("_infographic").position.x = lerp(0,3,moveUILerpChange)
    }
}

var heldTime = -1;

function performMeshTrace(){
    raycaster.setFromCamera( pointer, camera );
    intersects = raycaster.intersectObjects( scene.children );
    if (intersects.length >= 1){
        if (intersects[0] != undefined) {
            if (intersects[0].object.name[0] != "_"){
                hoveredMesh = intersects[0].object;
            } else if (intersects[1] != undefined && intersects[1].object.name[0] != "_") {
                hoveredMesh = intersects[1].object;
            } else if (intersects[2] != undefined && intersects[2].object.name[0] != "_") {
                hoveredMesh = intersects[2].object;
            } else if (intersects[3] != undefined && intersects[3].object.name[0] != "_") {
                hoveredMesh = intersects[3].object;
            }
        }
    } else {
        hoveredMesh = "None"
    }
}

function checkForMesh(event){
    if (event.targetTouches == undefined) {
        pointer.x = ( event.clientX / window.innerWidth ) * 2 - 1;
        pointer.y = - ( event.clientY / window.innerHeight ) * 2 + 1;
    } else {
        pointer.x = ( event.targetTouches[0].clientX / window.innerWidth ) * 2 - 1;
        pointer.y = - ( event.targetTouches[0].clientY / window.innerHeight ) * 2 + 1;
    }
    performMeshTrace()
    if (hoveredMesh == "None" || hoveredMesh == undefined) {
        initMoveUi = true;
        initMoveReturnUi = true;
        return
    }
    if (hoveredMesh.name != undefined && hoveredMesh.name[0] != "_" && clickChange == false){
        let tempName = hoveredMesh.name[0] + hoveredMesh.name[1];
        if (hoveredMesh.name != prevName){
            clickChange = true;
            prevName = tempName;
            dataFetching = null;
            fetchQuery(tempName,"Any",1);
        }
    }
}


var holdingPlanet = false;
var initialMousePos = false;

function mouseDown(e){
    heldTime = Date.now()
    holdingPlanet = true;
    initialMousePos = false;
}

var prevMouse = new THREE.Vector2(0,0);
var eulerYaw = 0;
var eulerPitch = 0;

var prevSpinYaw = 0;
var prevSpinPitch = 0;

const pitchSpeedMulti = 0.0007;
const yawSpeedMulti = 0.00032;
let notMobile = false;

var movedLast = false;
var mouseMovement = new THREE.Vector2(0,0);

function mouseMove(e){
    if (e.targetTouches == undefined) {
        if (!holdingPlanet){
            return
        }
        mouseMovement.x = e.clientX;
        mouseMovement.y = - e.clientY;
        notMobile = true;
    } else {
        mouseMovement.x = e.targetTouches[0].clientX;
	    mouseMovement.y = - e.targetTouches[0].clientY;
    }
    if (initialMousePos == true) {
        movedLast = true;
        prevSpinPitch += -(prevMouse.y - mouseMovement.y)*pitchSpeedMulti;
        prevSpinYaw += -(prevMouse.x - mouseMovement.x)*yawSpeedMulti;
    }
    if (initialMousePos == false) {
        prevMouse = new THREE.Vector2(mouseMovement.x,mouseMovement.y);
        initialMousePos = true;
    }
    prevMouse = new THREE.Vector2(mouseMovement.x,mouseMovement.y);
}

function mouseUp(e){
    if (heldTime == -1 || heldTime >= Date.now()-150){
        checkForMesh(e)
    }
    holdingPlanet = false;
    initialMousePos = false;
}

window.addEventListener("mouseup", (e) => mouseUp(e));
window.addEventListener("mousemove", (e) => mouseMove(e));
window.addEventListener("mousedown", (e) => mouseDown(e));
window.addEventListener("touchstart", (e) => mouseDown(e));
window.addEventListener("touchmove", (e) => mouseMove(e));
window.addEventListener("touchend", (e) => mouseUp(e));




//TODO: Skybox reflection, 3D chart box, closure of box("Inside showing amount of green&red? floating emotive faces (procederual mouth)? thumbs?"), improved controls for mobile, 
//allow switching country, clearer graph, more data, vertex offset on land(high noise), small wave effect, remove dupe headlines
function animate() {
    raycaster.setFromCamera( pointer, camera );
    intersects = raycaster.intersectObjects( scene.children );
    //performMeshTrace()
    //console.log(intersects)
    alpha = clamp( Math.pow(alpha + (Date.now()-last_fps_time)/550000, 0.9) ,0,1);
    if (!controls_done) {
        camera.position.z = lerp(initCameraDistance, finishCameraDist, alpha);
    }
    if (alpha >= 0.5 && !controls_done){
        if (!fetched){
            fetched = true;
            fetchQuery("World","Any",1);
        }
    }
    if (alpha >= 1 && !controls_done){
        controls_done = true;
        //const controls = new OrbitControls(camera, renderer.domElement);
    }
    if (alpha >= 1) {
        eulerPitch -= prevSpinPitch;
        eulerYaw += prevSpinYaw;
        if (Math.abs(eulerPitch) % 3 >= 1.05) {
            prevSpinPitch *= -1;
            eulerPitch = clamp(eulerPitch,-1.05,1.05);
        }
        if (!holdingPlanet && movedLast == false){
            prevSpinPitch *= 0.99;
            prevSpinYaw *= 0.99;
        }
        if (holdingPlanet == true) {
            prevSpinPitch *= 0.89;
            prevSpinYaw *= 0.89;
        }
        movedLast = false;
        scene.getObjectByName("Scene").setRotationFromEuler(new THREE.Euler(eulerPitch, eulerYaw, 0,"XYZ"))
    }
    if (clickChange == true && dataFetching != null){
        clickChange = false
        scene.remove(scene.getObjectByName("_infographic"))
        console.log(dataFetching)
        let name = dataFetching.values().next()['value'].values().next()['value'][4]
        generateText(name + " " + mode + " sentiment", dataFetching, hoveredMesh.name)
    }
    if (initMoveUi == true){
        var accel = 0.0001 * -(initMoveReturnUi*2-1);
        if (Math.abs(moveUILerp+accelUI / Math.abs(accel*200)) >= 1) {
            accelUI = accelUI-accel;
        } else {
            accelUI = accelUI+accel;
        }
        moveUILerp += accelUI;
        movePlanetAndText()
        if (Math.abs(moveUILerp) >= 1){
            moveUILerp = clamp(moveUILerp,-0.9999,0.9999);
            accelUI = 0;
            initMoveReturnUi = false;
            initMoveUi = false;
        }
    }
    
    var time_val = Math.floor( ((Date.now()/1000000)%1)*1000000 );
    let orbLoc;
    if ( scene.getObjectByName("Scene") != undefined ) {
        orbLoc = scene.getObjectByName("Scene").position
    } else {
        orbLoc = new THREE.Vector3(0,0,0)
    }
    const eulerVector = new THREE.Vector3(0-orbLoc.x,0-orbLoc.y,5-orbLoc.z).applyEuler(new THREE.Euler(-eulerPitch, -eulerYaw, 0,"ZYX"));
    water_planet_material.uniforms.time.value = time_val;
    water_planet_material.uniforms.relativeCamera.value = eulerVector;
    outlineSphereMat.uniforms.time.value = time_val;
    scene.getObjectByName("_outlineSphere").lookAt(camera.position)
    for (let index = 0; index < land_mat_arr.length; index++) {
        const element = land_mat_arr[index];
        element.uniforms.time.value = time_val;
        element.uniforms.landMovement.value = 0.05;
        element.uniforms.relativeCamera.value = eulerVector;
    }
    var infographic = scene.getObjectByName("_infographic")
    if (infographic != undefined) {
        infographic.getObjectByName("chart").material.uniforms.time.value = time_val;
        //scene.getObjectByName("_infographic").lookAt(camera.position)
    }
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
    if (last_fps_time + 1000 <= Date.now()){
        console.log(frame_count);
        frame_count = 0
        last_fps_time = Date.now()
    }
    frame_count += 1;
}
animate();
window.addEventListener( 'pointermove', onPointerMove );

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

window.addEventListener("resize", onWindowResize);



