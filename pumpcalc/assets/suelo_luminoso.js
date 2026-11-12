import { THREE } from 'nicegui-scene';

export default class SueloLuminoso {
  create_mesh(width, depth) {
    const material = new THREE.ShaderMaterial({
      side: THREE.DoubleSide,
      vertexShader: `
        varying vec2 floorPosition;
        void main() {
          floorPosition = uv;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: `
        varying vec2 floorPosition;
        void main() {
          vec2 p = floorPosition;
          float cyanLeft = exp(-pow((p.x - .19) * 9.0, 2.0) - pow((p.y - .25) * 3.8, 2.0));
          float violet = exp(-pow((p.x - .46) * 8.0, 2.0) - pow((p.y - .29) * 3.5, 2.0));
          float cyanRight = exp(-pow((p.x - .78) * 9.0, 2.0) - pow((p.y - .25) * 3.8, 2.0));
          float sheen = .025 * sin(p.x * 180.0) * sin(p.y * 140.0);
          vec3 base = vec3(.025, .035, .095);
          vec3 color = base + cyanLeft * vec3(.015, .21, .30)
            + violet * vec3(.095, .045, .27) + cyanRight * vec3(.015, .16, .25)
            + sheen * vec3(.12, .14, .24);
          gl_FragColor = vec4(color, 1.0);
        }
      `,
    });
    return new THREE.Mesh(new THREE.PlaneGeometry(width, depth), material);
  }
}
