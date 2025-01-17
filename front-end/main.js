import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { clamp, randFloat, randInt } from 'three/src/math/MathUtils';
import { TessellateModifier } from 'three/examples/jsm/modifiers/TessellateModifier.js';
//import { GLTFExporter } from 'three/addons/exporters/GLTFExporter.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
//import { forEachChild } from 'typescript';

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

camera.position.z = 5;
const controls = new OrbitControls(camera, renderer.domElement);

var intersects = raycaster.intersectObjects( scene.children );
var hoveredMesh;

var land_mat_arr = [];

const fragWater = await (await fetch('fragShaderWater.frag')).text();
const fragLand = await (await fetch('fragShaderLand.frag')).text();
const vertWater = await (await fetch('vertShaderWater.vert')).text();
const vertLand = await (await fetch('vertShaderLand.vert')).text();

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
                    givenRandTime: {value: rand}
                }
            });
            
            land_mat_arr.push(land_planet_temp);
            land_planet_temp.needsUpdate = true;
            element.material = land_planet_temp;
        }

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

var last_fps_time = Date.now();

var frame_count = 0;

function animate() {
    raycaster.setFromCamera( pointer, camera );
    intersects = raycaster.intersectObjects( scene.children );
    if (intersects.length >= 1){
        hoveredMesh = intersects[0].object;
    } else {
        hoveredMesh = "None"
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
    console.log(hoveredMesh)
});
