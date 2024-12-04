import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { randInt } from 'three/src/math/MathUtils';

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

var doneBefore = 0;
const radius = 2;

fetch('/UN_Geodata_simplified.geojson')
    .then(response => response.json())
    .then(geojsonData => {
        geojsonData.features.forEach(feature => {
            const coordType = feature.geometry.type;

            console.log(feature)
            if ( (coordType == "MultiPolygon" || coordType == "Polygon") && feature.properties.nam_en != null){
                
                const coordinateSet = feature.geometry.coordinates;
                const randColor = randInt(0,999999);
                console.log(coordinateSet[0])
                for (let index = 0; index < coordinateSet.length; index++) {
                    if (doneBefore >= 999) {
                        continue;
                    }
                    
                    
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

                    const shapePoints = coordinates
                        .map(([lon, lat]) => latLonToVector3(lat, lon, radius))
                        .filter(point => !isNaN(point.x) && !isNaN(point.y) && !isNaN(point.z));

                    
                    const shape = new THREE.Shape();
                    /* const geometry = new THREE.BufferGeometry();
                    geometry.setAttribute( 'position', new THREE.Float32BufferAttribute( triangleCoords, 3 ) ); */

                    shape.moveTo( coordinates[0][0], coordinates[0][1])
                    for( var i = 2; i < coordinates.length; i++ ){
                        shape.lineTo( coordinates[i][0], coordinates[i][1], coordinates[i-1][0], coordinates[i-1][1], coordinates[i-2][0], coordinates[i-2][1]);
                    }

                    const extrudeSettings = {
                        steps: 1,
                        depth: 0.1,
                        bevelEnabled: true,
                        bevelThickness: 0.05,
                        bevelSize: 0.05,
                        bevelOffset: 0,
                        bevelSegments: 1
                    };

                    const geometry = new THREE.ExtrudeGeometry( shape, extrudeSettings );
                    
                    geometry.computeBoundingSphere();
                    
                    const material = new THREE.MeshBasicMaterial({color: randColor});
                    const country = new THREE.Mesh( geometry, material );

                    /* const material = new THREE.LineBasicMaterial({ color: 0x9d00ff });
                    const country = new THREE.Line(geometry, material); */
                    scene.add(country);
                    
                }
                doneBefore += 1;
            }
        });
    });

function latLonToVector3(lat, lon, radius) {
    const phi = (90 - lat) * (Math.PI / 180);
    const theta = (-lon + 180) * (Math.PI / 180);

    return new THREE.Vector3(
        radius * Math.sin(phi) * Math.cos(theta),
        radius * Math.cos(phi),
        radius * Math.sin(phi) * Math.sin(theta)
    );
}

const geometrySphere = new THREE.SphereGeometry( 1.96, 64, 64 ); 
const materialSphere = new THREE.MeshPhysicalMaterial( { color: 0x3030ff } ); 
const sphere = new THREE.Mesh( geometrySphere, materialSphere );

const pointLight = new THREE.PointLight({ color: 0xffffff }, 30,100);
pointLight.position.x = 9;
pointLight.position.z = 9;

scene.add(pointLight);

const pointLight1 = new THREE.PointLight({ color: 0xffffff }, 30,100);
pointLight1.position.x = -9;
pointLight1.position.z = -9;

scene.add(pointLight1);

const pointLight2 = new THREE.PointLight({ color: 0xffffff }, 30,100);
pointLight2.position.x = -9;
pointLight2.position.z = 9;

scene.add(pointLight2);

const pointLight3 = new THREE.PointLight({ color: 0xffffff }, 30,100);
pointLight3.position.x = 9;
pointLight3.position.z = -9;

scene.add(pointLight3);

const geometry = new THREE.BufferGeometry();

const positions = [
0, 0, 0,    // v1
0, 1, 0,   // v2
0, 1, 1  // v3
];

geometry.setAttribute( 'position', new THREE.Float32BufferAttribute( positions, 3 ) );
geometry.computeVertexNormals();

const object = new THREE.Mesh( geometry, new THREE.MeshNormalMaterial() );
scene.add(object);

camera.position.z = 5;
const controls = new OrbitControls(camera, renderer.domElement);

function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}
animate();
