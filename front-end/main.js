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

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({antialias : true});
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();

function onPointerMove( event ) {
	pointer.x = ( event.clientX / window.innerWidth ) * 2 - 1;
	pointer.y = - ( event.clientY / window.innerHeight ) * 2 + 1;
}


var dataFetching = null;
function generateText(displayText, data=null){
    const fontloader = new FontLoader();
    fontloader.load('./Roboto_Regular.json', function(font) {
        const infographicScene = new THREE.Scene();

        //testing dummy data
        if (data == null){
            data = [-1,-0.7,-0,1,-1,-1,-1,-0.5,0,0.1,0.2,1]
            return
        }
        var cur = data.get(displayText[0]+displayText[1])

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

        const hDiv = 2.3 //Height division
        
        var dataCoords = [];
        for (let index = 0; index < resArr.length-1; index++) {
            const element = resArr[index];//Should be dates
            dataCoords.push([(index-parseInt(resArr.length/2))/5, element/hDiv+0.5])
        }
        dataCoords.push([(resArr.length-1-parseInt(resArr.length/2))/5, resArr[resArr.length-1]/hDiv+0.5])
        for (let index = resArr.length-1; index >= 0; index--) {
            const element = resArr[index];//Should be dates
            dataCoords.push([(index-parseInt(resArr.length/2))/5, element/hDiv+0.45])
        }resArr
        dataCoords.push([(0-parseInt(resArr.length/2))/5, resArr[0]/hDiv+0.45])

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

        //const cube = new THREE.BoxGeometry(1,1,1)
        //infographicScene.add(cube)

        const textMesh = makeTextMesh(displayText,font)
        textMesh.name = "_infographic";
        infographicScene.name = "_infographic";
        textMesh.position.y = 1
        infographicScene.add(textMesh)

        //Making the date label at bottom
        const dataAtCountrySorted = new Map([...data.get(displayText[0]+displayText[1]).entries()].sort());

        const iter = dataAtCountrySorted.keys();
        let key = iter.next().value;
        let stringTemp = "";
        let locXArr = dataCoords;
        let count = 0;
        let year = "";
        let month = "";
        let day = "";
        let count_dash = 0;
        while (key != undefined){
            for (let index = 0; index < key.length; index++) {
                const element = key[index];
                if (element == "-"){
                    if (count >= 1){
                        if (count_dash == 2){
                            if (day == stringTemp){
                                day = stringTemp
                            } else{
                                const resText = makeTextMesh(stringTemp,font)
                                resText.position.x += locXArr[parseInt(count)][0]
                                infographicScene.add(resText)
                            }
                            day = stringTemp;
                            count += 1;
                        }
                    } else {
                        const resText = makeTextMesh(stringTemp,font)
                        resText.position.x += locXArr[parseInt(count)][0]
                        infographicScene.add(resText)
                        if (count_dash == 0) {
                            year = stringTemp
                            resText.position.y -= 0.25
                        }
                        if (count_dash == 1) {
                            month = stringTemp
                            resText.position.y -= 0.125
                        }
                        if (count_dash >= 2) {
                            day = stringTemp
                            count += 1;
                        }
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


        infographicScene.position.y = 2.2
        
        scene.add(infographicScene);
        const tempLight = new THREE.PointLight({color: new THREE.Color(0xffffff), intensity: 1000, decay: 0});
        tempLight.position.z = 10;
        scene.add(tempLight);
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

var displayText = "1 2 3 4 5 6 7 8 9 10";
generateText(displayText)

const initCameraDistance = 1000;
camera.position.z = initCameraDistance;
const finishCameraDist = 5;
//const controls = new OrbitControls(camera, renderer.domElement);

var intersects = raycaster.intersectObjects( scene.children );
var hoveredMesh;

var land_mat_arr = [];

const water_planet_material = new THREE.ShaderMaterial({
    vertexShader: vertWater,
    fragmentShader: fragWater,
    uniforms: {
        time: {value: (Date.now()/10)%10}
    }
});

water_planet_material.needsUpdate = true;

const land_planet_material = new THREE.ShaderMaterial({
    vertexShader: vertLand,
    fragmentShader: fragLand,
    uniforms: {
        time: {value: (Date.now()/10)%10},
        landMovement: {value: 0.001},
        givenRandTime: {value: randFloat(0,1)}
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
                    sentiment: {value: rand}
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
        try{
            const names = new Map();
            if (land_mat_arr[0] != null){
                for (let index = 0; index < json.length; index++) {
                    const ele = json[index];
                    if (names.has(ele[0]) == false){
                        const in_map = new Map()
                        names.set(ele[0], in_map.set(ele[5], [ele[1],ele[2],ele[3],ele[4]]) );
                    } else {
                        names.get(ele[0]).set(ele[5], [ele[1],ele[2],ele[3],ele[4]]);
                    }
                }
                var prevCountry = []
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


//TODO: Move planet down when clicking on vertical screen, move to the left on horizontal, background, skybox
function animate() {
    raycaster.setFromCamera( pointer, camera );
    intersects = raycaster.intersectObjects( scene.children );
    if (intersects.length >= 1){
        if (intersects[0] != undefined) {
            if (intersects[0].object[0] != "_"){
                hoveredMesh = intersects[0].object;
            } else {
                if (intersects[1] != undefined) {
                    hoveredMesh = intersects[1].object;
                }
            }
        }
    } else {
        hoveredMesh = "None"
    }
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
        const controls = new OrbitControls(camera, renderer.domElement);
    }
    if (clickChange == true && dataFetching != null){
        clickChange = false
        scene.remove(scene.getObjectByName("_infographic"))
        generateText(hoveredMesh.name, dataFetching)
    }

    requestAnimationFrame(animate);
    renderer.render(scene, camera);
    var time_val = Math.floor( ((Date.now()/100000)%1)*100000 );
    water_planet_material.uniforms.time.value = time_val;
    land_planet_material.uniforms.time.value = time_val;
    land_planet_material.uniforms.landMovement.value = 0.05;
    outlineSphereMat.uniforms.time.value = time_val;
    scene.getObjectByName("_outlineSphere").lookAt(camera.position)
    for (let index = 0; index < land_mat_arr.length; index++) {
        const element = land_mat_arr[index];
        element.uniforms.time.value = time_val;
        element.uniforms.landMovement.value = 0.05;
    }
    var infographic = scene.getObjectByName("_infographic")
    if (infographic != undefined) {

        infographic.getObjectByName("chart").material.uniforms.time.value = time_val;
        scene.getObjectByName("_infographic").lookAt(camera.position)
    }
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

window.addEventListener('click', (e) => {
    if (hoveredMesh.name != undefined && hoveredMesh.name[0] != "_" && clickChange == false){
        hoveredMesh.name = hoveredMesh.name[0] + hoveredMesh.name[1]
        if (hoveredMesh.name != prevName){
            clickChange = true;
            prevName = hoveredMesh.name
            dataFetching = null;
            fetchQuery(hoveredMesh.name,"Any",1);
        }
    }
    //console.log(hoveredMesh)
});
