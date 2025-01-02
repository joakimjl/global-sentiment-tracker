import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { clamp, randInt } from 'three/src/math/MathUtils';
import { TessellateModifier } from 'three/examples/jsm/modifiers/TessellateModifier.js';
import { GLTFExporter } from 'three/addons/exporters/GLTFExporter.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import vertexShader from './vertexShader.vert?raw';
import fragmentShader from './fragmentShader.frag?raw';

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const radius = 2;

function fetchGeo(){
fetch('/UN_Geodata_stylized.geojson')
    .then(response => response.json())
    .then(geojsonData => {
        geojsonData.features.forEach(feature => {
            const coordType = feature.geometry.type;

            if ( (coordType == "MultiPolygon" || coordType == "Polygon") && feature.properties.nam_en != null){
                
                const coordinateSet = feature.geometry.coordinates;
                const randColor = randInt(0,999999);
                for (let index = 0; index < coordinateSet.length; index++) {
                    
                    var coordinates = coordinateSet[index][0];
                    if (coordType == "Polygon") {
                        coordinates = coordinateSet[0];
                    }
                    var tempCoords = [];
                    
                    for (let index = 0; index < coordinates.length; index++) {
                        const coordsArr = coordinates[index];
                        tempCoords.push(coordsArr);
                    }
                    coordinates = tempCoords;
                    
                    const shape = new THREE.Shape();
                    shape.moveTo(coordinates[0][0], coordinates[0][1]);
                    for (let i = 1; i < coordinates.length; i++) {
                        shape.lineTo(coordinates[i][0], coordinates[i][1]);
                    }

                    const extrudeSettings = {
                        steps: 1,
                        depth: 0.001,
                        bevelEnabled: true,
                        bevelThickness: 0.02,
                        bevelSize: 0.05,
                        bevelOffset: 0,
                        bevelSegments: 1,
                        curveSegments: 8
                    };

                    let geometry = new THREE.ExtrudeGeometry(shape, extrudeSettings);

                    let tesselateAmount = clamp(coordinates.length/2,5,100);
                    const tessellateModifier = new TessellateModifier(3,tesselateAmount);
                    geometry = tessellateModifier.modify(geometry);

                    for (let i = 0; i < geometry.attributes.position.count; i++) {
                        const x = geometry.attributes.position.getX(i);
                        const y = geometry.attributes.position.getY(i);
                        const z = geometry.attributes.position.getZ(i);

                        const newXYZ = latLonToVector3(y, x, radius + z);
                        geometry.attributes.position.setXYZ(i, newXYZ[0], newXYZ[1], newXYZ[2]);
                    }
                    geometry.computeBoundingSphere();

                    const material = new THREE.MeshPhysicalMaterial({ color: randColor, side: THREE.DoubleSide});

                    const country = new THREE.Mesh(geometry, material);
                    country.name = feature.properties.iso2cd
                    if (typeof(country.name) != "undefined") {
                        scene.add(country);
                    }
                }
            }
        });
    });
}

//fetchGeo();

function latLonToVector3(lat, lon, radius) {
    const phi = (90 - lat) * (Math.PI / 180);
    const theta = (-lon + 180) * (Math.PI / 180);

    return [
        radius * Math.sin(phi) * Math.cos(theta),
        radius * Math.cos(phi),
        radius * Math.sin(phi) * Math.sin(theta)];
}

const geometrySphere = new THREE.SphereGeometry( 2, 64, 64 ); 
const materialSphere = new THREE.MeshPhysicalMaterial( { color: 0x3030ff } ); 
//const sphere = new THREE.Mesh( geometrySphere, materialSphere );

for (let index = 0; index < 3; index++) {
    const newLight = new THREE.PointLight({color: 0xFFFFFF}, 50, 30);
    let val = 5;
    if (index == 0){
        val = -5;
    } else if (index == 1){
        val = 0;
    }
    newLight.position.x = 10;
    newLight.position.y = val;
    newLight.position.z = 10;
    newLight.name = "Light"
    scene.add(newLight);
}

const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();

function onPointerMove( event ) {
	pointer.x = ( event.clientX / window.innerWidth ) * 2 - 1;
	pointer.y = - ( event.clientY / window.innerHeight ) * 2 + 1;
}

camera.position.z = 5;
const controls = new OrbitControls(camera, renderer.domElement);
//scene.add(sphere);

var intersects = raycaster.intersectObjects( scene.children );
var hoveredMesh;

// Instantiate a loader
const loader = new GLTFLoader();

const water_planet_material = new THREE.ShaderMaterial({
    vertexShader: vertexShader,
    fragmentShader: fragmentShader,
    uniforms: {
        time: {value: (Date.now()/10)%10}
    }
});

water_planet_material.needsUpdate = true;

// Load a glTF resource
loader.load(
	// resource URL
	'planet_test.gltf',
    
	// called when the resource is loaded
	function ( gltf ) {

        console.log(gltf.scene.children[0])
        gltf.scene.children[0].material = water_planet_material

		scene.add( gltf.scene );

		gltf.animations; // Array<THREE.AnimationClip>
		gltf.scene; // THREE.Group
		gltf.scenes; // Array<THREE.Group>
		gltf.cameras; // Array<THREE.Camera>
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

function animate() {
    raycaster.setFromCamera( pointer, camera );
    intersects = raycaster.intersectObjects( scene.children );
    if (intersects.length >= 1){
        hoveredMesh = intersects[0].object;
    } else {
        hoveredMesh = "None"
    }
    requestAnimationFrame(animate);
    scene.rotateY(0.0001);
    renderer.render(scene, camera);
    var time_val = Math.floor( ((Date.now()/100000)%1)*100000 );
    water_planet_material.uniforms.time.value = time_val;
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
    console.log(hoveredMesh)
    /* 
    const exporter = new GLTFExporter();

    console.log(scene.toJSON)
    exporter.parse(
        scene,
        // called when the gltf has been generated
        function ( gltf ) {

            console.log( gltf );
            //downloadJSON( gltf );
            console.log( gltf.json );

        },
        // called when there is an error in the generation
        function ( error ) {

            console.log( 'An error happened' );

        }
    ); */
});
