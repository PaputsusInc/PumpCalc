import { THREE } from 'nicegui-scene';

export default class AguaEnTuberia {
  create_mesh(path, count, radius, sceneKey) {
    this.sceneKey = sceneKey;
    this.path = path.map(point => new THREE.Vector3(...point));
    this.lengths = [0];
    for (let i = 1; i < this.path.length; i++) {
      this.lengths.push(this.lengths.at(-1) + this.path[i].distanceTo(this.path[i - 1]));
    }
    this.total = this.lengths.at(-1);
    this.count = count;
    this.radius = radius;
    this.phase = 0;
    this.speed = 0;
    this.active = false;
    this.paused = false;
    this.lastTime = performance.now();
    const positions = new Float32Array(count * 3);
    this.geometry = new THREE.BufferGeometry();
    this.geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    const canvas = document.createElement('canvas');
    canvas.width = canvas.height = 32;
    const context = canvas.getContext('2d');
    const halo = context.createRadialGradient(16, 16, 0, 16, 16, 16);
    halo.addColorStop(0, '#ffffff');
    halo.addColorStop(.28, '#c2ffff');
    halo.addColorStop(.62, '#36dcff88');
    halo.addColorStop(1, '#36dcff00');
    context.fillStyle = halo;
    context.fillRect(0, 0, 32, 32);
    const material = new THREE.PointsMaterial({
      color: '#a7eff5', size: radius * 1.45, map: new THREE.CanvasTexture(canvas),
      transparent: true, opacity: .62, depthTest: false, depthWrite: false,
      blending: THREE.AdditiveBlending,
      sizeAttenuation: true,
    });
    this.mesh = new THREE.Points(this.geometry, material);
    this.mesh.renderOrder = 15;
    this.mesh.visible = false;
    this.mesh.onBeforeRender = () => this.animate();
    return this.mesh;
  }

  set_flow(speed, active, paused) {
    this.speed = Number.isFinite(speed) ? Math.max(0, speed) : 0;
    this.active = Boolean(active);
    this.paused = Boolean(paused);
    this.mesh.visible = this.active && !window.__pumpcalcWaterStates?.get(this.sceneKey)?.finished;
    this.lastTime = performance.now();
    this.draw();
  }

  restart() {
    this.phase = 0;
    this.lastTime = performance.now();
    this.mesh.visible = this.active;
    this.draw();
  }

  animate() {
    const now = performance.now();
    const seconds = Math.min((now - this.lastTime) / 1000, .1);
    this.lastTime = now;
    if (window.__pumpcalcWaterStates?.get(this.sceneKey)?.finished) {
      this.mesh.visible = false;
      return;
    }
    if (!this.active || this.paused || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const speed = window.__pumpcalcWaterStates?.get(this.sceneKey)?.speed ?? this.speed;
    if (speed <= 0) return;
    this.phase = (this.phase + seconds * speed) % this.total;
    this.draw();
  }

  draw() {
    if (!this.active) return;
    const positions = this.geometry.attributes.position.array;
    for (let i = 0; i < this.count; i++) {
      const distance = (this.phase + i * this.total / this.count) % this.total;
      let segment = 1;
      while (segment < this.lengths.length - 1 && this.lengths[segment] < distance) segment++;
      const span = this.lengths[segment] - this.lengths[segment - 1];
      const point = this.path[segment - 1].clone().lerp(this.path[segment], (distance - this.lengths[segment - 1]) / span);
      if (point.x > -1.93 && point.x < .23) {
        positions[i * 3] = 0;
        positions[i * 3 + 1] = 0;
        positions[i * 3 + 2] = -100;
        continue;
      }
      // Una pequeña dispersión fija deja leer el agua como volumen, no como una línea abstracta.
      const angle = i * 2.39996;
      point.y += Math.sin(angle) * this.radius * .32;
      point.z += Math.cos(angle) * this.radius * .32;
      positions[i * 3] = point.x;
      positions[i * 3 + 1] = point.y;
      positions[i * 3 + 2] = point.z;
    }
    this.geometry.attributes.position.needsUpdate = true;
  }
}
