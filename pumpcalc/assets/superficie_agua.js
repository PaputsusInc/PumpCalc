import { THREE } from 'nicegui-scene';

export default class SuperficieAgua {
  create_mesh(width, depth, bottom, top, drop, sceneKey) {
    this.sceneKey = sceneKey;
    this.bottom = bottom;
    this.top = top;
    this.drop = drop;
    this.active = false;
    this.paused = false;
    this.lastTime = performance.now();
    this.time = 0;
    this.uniforms = {
      time: { value: 0 },
      movement: { value: 0 },
    };
    const group = new THREE.Group();
    const liquid = new THREE.Mesh(
      new THREE.BoxGeometry(width, depth, 1),
      new THREE.MeshBasicMaterial({
        color: '#057fae', transparent: true, opacity: .56,
        depthWrite: false, side: THREE.DoubleSide,
      }),
    );
    liquid.renderOrder = 6;
    group.add(liquid);
    this.liquid = liquid;
    this.updateLevel = () => {
      const progress = window.__pumpcalcWaterStates?.get(this.sceneKey)?.progress ?? 0;
      const level = this.top - this.drop * progress;
      const height = Math.max(.01, level - this.bottom);
      this.liquid.scale.z = height;
      this.liquid.position.z = this.bottom + height / 2;
      this.mesh.position.z = level + .008;
      this.levelLine.position.z = level;
    };
    liquid.onBeforeRender = () => this.updateLevel();
    const geometry = new THREE.PlaneGeometry(width, depth, 40, 22);
    const material = new THREE.ShaderMaterial({
      uniforms: this.uniforms,
      transparent: true,
      side: THREE.DoubleSide,
      depthWrite: false,
      vertexShader: `
        uniform float time;
        uniform float movement;
        varying vec2 uvPosition;
        void main() {
          uvPosition = uv;
          vec3 p = position;
          p.z += movement * (0.015 * sin(p.x * 13.0 + time * 2.4) * cos(p.y * 9.0 - time * 1.5));
          gl_Position = projectionMatrix * modelViewMatrix * vec4(p, 1.0);
        }
      `,
      fragmentShader: `
        uniform float time;
        uniform float movement;
        varying vec2 uvPosition;
        void main() {
          float wave = sin(uvPosition.x * 37.0 + time * 2.0) * sin(uvPosition.y * 20.0 - time * 1.35);
          float fine = sin(uvPosition.x * 79.0 - uvPosition.y * 28.0 + time * 1.6);
          float shimmer = movement * (wave * 0.13 + fine * 0.05);
          vec3 deep = vec3(0.005, 0.32, 0.51);
          vec3 bright = vec3(0.14, 0.84, 0.96);
          vec3 color = mix(deep, bright, clamp(0.56 + shimmer + uvPosition.y * 0.12, 0.0, 1.0));
          gl_FragColor = vec4(color, 0.94);
        }
      `,
    });
    this.mesh = new THREE.Mesh(geometry, material);
    this.mesh.renderOrder = 8;
    group.add(this.mesh);
    const levelLine = new THREE.Mesh(
      new THREE.BoxGeometry(width - .03, .018, .012),
      new THREE.MeshBasicMaterial({
        color: '#62eaff', transparent: true, opacity: .7,
        depthWrite: false,
      }),
    );
    levelLine.position.y = -depth / 2 + .012;
    levelLine.renderOrder = 10;
    group.add(levelLine);
    this.levelLine = levelLine;
    this.mesh.onBeforeRender = () => {
      const now = performance.now();
      const seconds = Math.min((now - this.lastTime) / 1000, .1);
      this.lastTime = now;
      this.updateLevel();
      const state = window.__pumpcalcWaterStates?.get(this.sceneKey);
      const moving = this.active && !this.paused && !state?.finished
        && !matchMedia('(prefers-reduced-motion: reduce)').matches;
      this.uniforms.movement.value = moving ? 1 : 0;
      if (moving) {
        this.time += seconds;
        this.uniforms.time.value = this.time;
      }
    };
    this.mesh.position.z = this.top + .008;
    this.levelLine.position.z = this.top;
    this.liquid.scale.z = this.top - this.bottom;
    this.liquid.position.z = (this.top + this.bottom) / 2;
    return group;
  }

  restart() {
    this.time = 0;
    this.uniforms.time.value = 0;
    this.lastTime = performance.now();
  }

  set_flow(active, paused) {
    this.active = Boolean(active);
    this.paused = Boolean(paused);
    this.uniforms.movement.value = this.active && !this.paused
      && !window.__pumpcalcWaterStates?.get(this.sceneKey)?.finished ? 1 : 0;
    this.lastTime = performance.now();
  }
}
