import { THREE } from 'nicegui-scene';

export default class CanalAgua {
  create_mesh(points, radius, sceneKey) {
    this.sceneKey = sceneKey;
    const curve = new THREE.CatmullRomCurve3(points.map(p => new THREE.Vector3(...p)), false, 'centripetal');
    const geometry = new THREE.TubeGeometry(curve, 100, radius, 16, false);
    this.uniforms = {
      time: { value: 0 },
      movement: { value: 0 },
    };
    this.active = false;
    this.paused = false;
    this.speed = 0;
    this.lastTime = performance.now();
    this.time = 0;
    const material = new THREE.ShaderMaterial({
      uniforms: this.uniforms,
      transparent: true,
      depthTest: false,
      depthWrite: false,
      side: THREE.FrontSide,
      vertexShader: `
        varying vec2 positionOnTube;
        void main() {
          positionOnTube = uv;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: `
        uniform float time;
        uniform float movement;
        varying vec2 positionOnTube;
        void main() {
          float along = positionOnTube.x;
          float across = positionOnTube.y;
          float stripe = pow(max(0.0, sin(along * 61.0 - time * 10.0 + across * 4.0)), 9.0);
          float current = sin(along * 109.0 - time * 15.0 + across * 12.0) * 0.07;
          float light = 0.22 + stripe * movement * 0.68 + current * movement;
          vec3 deep = vec3(0.008, 0.25, 0.39);
          vec3 cyan = vec3(0.39, 0.95, 1.0);
          gl_FragColor = vec4(mix(deep, cyan, light), 0.92);
        }
      `,
    });
    this.mesh = new THREE.Mesh(geometry, material);
    this.mesh.renderOrder = 12;
    this.mesh.onBeforeRender = () => {
      const now = performance.now();
      const seconds = Math.min((now - this.lastTime) / 1000, .1);
      this.lastTime = now;
      if (window.__pumpcalcWaterStates?.get(this.sceneKey)?.finished) {
        this.uniforms.movement.value = 0;
        return;
      }
      if (this.active && !this.paused && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
        const speed = window.__pumpcalcWaterStates?.get(this.sceneKey)?.speed ?? this.speed;
        this.time += seconds * speed;
        this.uniforms.time.value = this.time;
      }
    };
    return this.mesh;
  }

  set_flow(speed, active, paused) {
    this.speed = Number.isFinite(speed) ? Math.max(0, speed) : 0;
    this.active = Boolean(active);
    this.paused = Boolean(paused);
    this.uniforms.movement.value = this.active && !window.__pumpcalcWaterStates?.get(this.sceneKey)?.finished ? 1 : 0;
    this.lastTime = performance.now();
  }

  restart() {
    this.time = 0;
    this.uniforms.time.value = 0;
    this.uniforms.movement.value = this.active && !this.paused ? 1 : 0;
    this.lastTime = performance.now();
  }
}
