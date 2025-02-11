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
import { FontLoader } from 'three/addons/loaders/FontLoader.js';
import { TextGeometry } from 'three/addons/geometries/TextGeometry.js';
import { TessellateModifier } from 'three/examples/jsm/modifiers/TessellateModifier.js';

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer();
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
        const geometry = new TextGeometry(displayText, {
            font: font,
            size: 0.1,
            depth: 0.02,
        });

        //testing dummy data
        if (data == null){
            data = [-1,-0.7,-0,1,-1,-1,-1,-0.5,0,0.1,0.2,1]
        }
        console.log(displayText[0]+displayText[1])
        console.log(data.get(displayText[0]+displayText[1]))
        var dataCoords = [];
        for (let index = 0; index < data.length-1; index++) {
            const element = data[index];//Should be dates
            dataCoords.push([(index-parseInt(data.length/2))/5, element/3+0.5])
        }

        for (let index = data.length-1; index >= 0; index--) {
            const element = data[index];//Should be dates
            dataCoords.push([(index-parseInt(data.length/2))/5, element/3+0.3])
        }
        dataCoords.push([(0-parseInt(data.length/2))/5, data[0]/3+0.3])

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
    
        const dataMaterial = new THREE.MeshBasicMaterial( { color: 0xff0000 } );
        const dataMesh = new THREE.Mesh( dataGeometry, dataMaterial );

        infographicScene.add(dataMesh)

        //Move origin of mesh
        geometry.translate(-0.03*displayText.length,0,0)

        const textMesh = new THREE.Mesh(geometry, [
            new THREE.MeshBasicMaterial({color: new THREE.Color(0xffffff)}),
            new THREE.MeshBasicMaterial({color: new THREE.Color(0xffffff)})
        ]);

        textMesh.name = "infographic";
        infographicScene.name = "infographic";
        
        textMesh.position.y = 1
        //textMesh.position.x = -0.35
        infographicScene.add(textMesh)
        infographicScene.position.y = 2.2
        
        scene.add(infographicScene);
        const tempLight = new THREE.PointLight({color: new THREE.Color(0xffffff), intensity: 1000, decay: 0});
        tempLight.position.z = 10;
        scene.add(tempLight);
    });
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
                    names.set(ele[0], [ele[1],ele[2],ele[3],ele[4]]);
                }
                
                
                for (let index = 0; index < land_mat_arr.length; index++) {
                    const element = land_mat_arr[index];
                    const countryCode = element.name[0] + element.name[1];
                    if (names.has(countryCode)) {
                        //Data format is country, vader national, roberta national, vader international, roberta international
                        var vader;
                        var rob

                        if (mode == "international") {
                            vader = names.get(countryCode)[2];
                            rob = names.get(countryCode)[3];
                        } else if (mode == "national") {
                            vader = names.get(countryCode)[0];
                            rob = names.get(countryCode)[1];
                        }
                        //const national_vader = names.get(countryCode)[0];
                        //const national_rob = names.get(countryCode)[1];
                        //const inter_vader = names.get(countryCode)[2];
                        //const inter_rob = names.get(countryCode)[3];

                        let res = addSentiment(vader);
                        let temp = addSentiment(rob);

                        for (let index = 0; index < temp.length; index++) {
                            const element = temp[index];
                            res[index] += element;
                        }

                        let neg = res[0];
                        let neu = res[1];
                        let pos = res[2];
                        
                        element.uniforms.sentiment.value = (pos-neg)/neu;
                    }
                    else {
                        element.uniforms.sentiment.value = -500;
                    }
                }
            }
            dataFetching = names
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

function animate() {
    raycaster.setFromCamera( pointer, camera );
    intersects = raycaster.intersectObjects( scene.children );
    if (intersects.length >= 1){
        if (intersects[0] != undefined) {
            if (intersects[0].object != "_Water"){
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
        fetchQuery("World","Any",1);
        const controls = new OrbitControls(camera, renderer.domElement);
    }
    if (clickChange == true && dataFetching != null){
        clickChange = false
        scene.remove(scene.getObjectByName("infographic"))
        generateText(hoveredMesh.name, dataFetching)
    }

    requestAnimationFrame(animate);
    renderer.render(scene, camera);
    var time_val = Math.floor( ((Date.now()/100000)%1)*100000 );
    water_planet_material.uniforms.time.value = time_val;
    land_planet_material.uniforms.time.value = time_val;
    land_planet_material.uniforms.landMovement.value = 0.05;
    for (let index = 0; index < land_mat_arr.length; index++) {
        const element = land_mat_arr[index];
        element.uniforms.time.value = time_val;
        element.uniforms.landMovement.value = 0.05;
    }
    var infographic = scene.getObjectByName("infographic")
    if (infographic != undefined) {
        scene.getObjectByName("infographic").lookAt(camera.position)
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
    if (hoveredMesh.name != undefined && hoveredMesh.name[0] != "_"){
        if (hoveredMesh.name != prevName){
            clickChange = true;
            prevName = hoveredMesh.name
            dataFetching = null;
            fetchQuery("World","Any",1);
        }
    }
    //console.log(hoveredMesh)
});
