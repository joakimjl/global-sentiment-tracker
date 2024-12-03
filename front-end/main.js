import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const radius = 2;

fetch('/UN_Geodata_stylized.geojson')
    .then(response => response.json())
    .then(geojsonData => {
        geojsonData.features.forEach(feature => {
/*             if (feature.properties.iso2cd == "US") {
                console.log(feature);
            }
            console.log(feature); */
            const coordType = feature.geometry.type;

            /* if (coordinates.length < 3) return; */

            if (coordType == "Polygon") {
                const coordinates = feature.geometry.coordinates[0];
                const shapePoints = coordinates
                    .map(([lon, lat]) => latLonToVector3(lat, lon, radius))
                    .filter(point => !isNaN(point.x) && !isNaN(point.y) && !isNaN(point.z));
                const geometry = new THREE.BufferGeometry().setFromPoints(shapePoints);

                geometry.computeBoundingSphere();

                const material = new THREE.LineBasicMaterial({ color: 0x9d00ff });
                const line = new THREE.Line(geometry, material);
                scene.add(line);
            } else {
                const coordinateSet = feature.geometry.coordinates;
                for (let index = 0; index < coordinateSet.length; index++) {
                    var coordinates = coordinateSet[index][0];
                    var tempCoords = [];
                    if (coordType == "MultiPolygon") {
                        for (let index = 0; index < coordinates.length; index++) {
                            const coordsArr = coordinates[index];
                            tempCoords.push(coordsArr);
                        }
                        coordinates = tempCoords;
                    }
                    const shapePoints = coordinates
                        .map(([lon, lat]) => latLonToVector3(lat, lon, radius))
                        .filter(point => !isNaN(point.x) && !isNaN(point.y) && !isNaN(point.z));
                    const geometry = new THREE.BufferGeometry().setFromPoints(shapePoints);

                    geometry.computeBoundingSphere();

                    const material = new THREE.LineBasicMaterial({ color: 0x9d00ff });
                    const line = new THREE.Line(geometry, material);
                    scene.add(line);
                }
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

const geometry = new THREE.SphereGeometry( 1.96, 64, 64 ); 
const material = new THREE.MeshPhysicalMaterial( { color: 0x1010ff } ); 
const sphere = new THREE.Mesh( geometry, material );

const pointLight = new THREE.PointLight({ color: 0xffffff }, 30,100);
pointLight.position.x = -9;
pointLight.position.z = 0;

scene.add(sphere);
scene.add(pointLight);

camera.position.z = 5;
const controls = new OrbitControls(camera, renderer.domElement);

function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}
animate();
