import { THREE } from 'nicegui-scene';

const estados = window.__pumpcalcWaterStates ||= new Map();

export default class TanqueLlenado {
  create_mesh(width, depth, bottom, initial, target, outlet, sceneKey) {
    this.width = width;
    this.depth = depth;
    this.bottom = bottom;
    this.initial = initial;
    this.target = target;
    this.outlet = outlet;
    this.sceneKey = sceneKey;
    this.revision = null;
    this.frames = [];
    this.cursor = 0;
    this.elapsed = 0;
    this.rate = 60;
    this.stopReason = '';
    this.frame = [0, initial, initial, 0, 0, 0, 0, 0, 0, 0];
    this.active = false;
    this.paused = false;
    this.time = 0;
    this.lastTime = performance.now();
    estados.set(sceneKey, { finished: false, sourceLevel: initial,
      destLevel: initial, speed: 0 });

    const group = new THREE.Group();
    const liquid = new THREE.Mesh(
      new THREE.BoxGeometry(width, depth, 1),
      new THREE.MeshBasicMaterial({
        color: '#079fca', transparent: true, opacity: .72,
        depthWrite: false, side: THREE.DoubleSide,
      }),
    );
    liquid.renderOrder = 6;
    group.add(liquid);
    this.liquid = liquid;

    this.uniforms = { time: { value: 0 }, agitation: { value: 0 }, impactX: { value: .25 } };
    const surface = new THREE.Mesh(
      new THREE.PlaneGeometry(width, depth, 42, 28),
      new THREE.ShaderMaterial({
        uniforms: this.uniforms, transparent: true, depthWrite: false,
        side: THREE.DoubleSide,
        vertexShader: `
          uniform float time;
          uniform float agitation;
          varying vec2 uvWater;
          varying vec3 localPosition;
          void main() {
            uvWater = uv;
            vec3 p = position;
            vec2 impact = vec2(.25, .5);
            float distanceToImpact = length((uv - impact) * vec2(2.0, 1.2));
            float ring = sin(distanceToImpact * 38.0 - time * 5.0);
            p.z += agitation * (.010 * sin(p.x * 13.0 + time * 2.1) * cos(p.y * 11.0 - time)
              + .014 * ring * exp(-distanceToImpact * 3.5));
            localPosition = p;
            gl_Position = projectionMatrix * modelViewMatrix * vec4(p, 1.0);
          }
        `,
        fragmentShader: `
          uniform float time;
          uniform float agitation;
          varying vec2 uvWater;
          varying vec3 localPosition;
          void main() {
            vec2 impact = vec2(.25, .5);
            float d = length((uvWater - impact) * vec2(2.0, 1.2));
            float ring = pow(max(0.0, cos(d * 39.0 - time * 5.0)), 9.0)
              * exp(-d * 3.5) * agitation;
            float wave = sin(uvWater.x * 52.0 + time * 2.1)
              * sin(uvWater.y * 27.0 - time * 1.6);
            float light = clamp(.48 + .12 * wave + .38 * ring + .14 * uvWater.y, 0.0, 1.0);
            vec3 deep = vec3(.014, .30, .45);
            vec3 crest = vec3(.25, .88, .94);
            gl_FragColor = vec4(mix(deep, crest, light), .94);
          }
        `,
      }),
    );
    surface.renderOrder = 8;
    surface.onBeforeRender = () => this.animate();
    group.add(surface);
    this.surface = surface;

    const levelLine = new THREE.Mesh(
      new THREE.BoxGeometry(1, .016, .012),
      new THREE.MeshBasicMaterial({ color: '#79e8ef', transparent: true, opacity: .82,
        depthWrite: false }),
    );
    levelLine.scale.x = width - .04;
    levelLine.position.y = -depth / 2 + .014;
    levelLine.renderOrder = 10;
    group.add(levelLine);
    this.levelLine = levelLine;

    const stream = new THREE.Mesh(
      new THREE.CylinderGeometry(.025, .035, 1, 16, 1, true),
      new THREE.MeshPhysicalMaterial({
        color: '#53d8e9', emissive: '#0e849e', emissiveIntensity: .4,
        metalness: .04, roughness: .18, transparent: true, opacity: .74,
        depthWrite: false, side: THREE.DoubleSide,
      }),
    );
    stream.rotation.x = Math.PI / 2;
    stream.position.x = -width / 4;
    stream.renderOrder = 9;
    group.add(stream);
    this.stream = stream;

    const rippleMaterial = new THREE.MeshBasicMaterial({
      color: '#9af7f1', transparent: true, opacity: .35,
      depthWrite: false, side: THREE.DoubleSide,
    });
    this.ripples = [0, 1].map(index => {
      const ring = new THREE.Mesh(new THREE.RingGeometry(.15, .17, 48), rippleMaterial.clone());
      ring.position.x = -width / 4;
      ring.renderOrder = 10;
      group.add(ring);
      return ring;
    });
    this.updateVisual();
    return group;
  }

  set_trajectory(frames, revision, active, paused, rate, stopReason) {
    this.revision = revision;
    this.frames = frames;
    this.cursor = 0;
    this.elapsed = 0;
    this.rate = rate;
    this.stopReason = stopReason;
    this.active = Boolean(active);
    this.paused = Boolean(paused);
    this.frame = frames[0] ?? [0, this.initial, this.initial, 0, 0, 0, 0, 0, 0, 0];
    this.lastTime = performance.now();
    this.publish();
    this.updateVisual();
  }

  set_playback(active, paused) {
    this.active = Boolean(active);
    this.paused = Boolean(paused);
    this.lastTime = performance.now();
    this.publish();
    this.updateVisual();
  }

  restart() {
    this.elapsed = 0;
    this.cursor = 0;
    this.frame = this.frames[0] ?? this.frame;
    this.time = 0;
    this.lastTime = performance.now();
    this.publish();
    this.updateVisual();
  }

  animate() {
    const now = performance.now();
    const dt = Math.min((now - this.lastTime) / 1000, .08);
    this.lastTime = now;
    const end = this.frames.at(-1)?.[0] ?? 0;
    const moving = this.active && !this.paused && this.elapsed < end
      && !matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (moving) {
      // Solo se interpola una trayectoria previamente resuelta por RK4 en Python.
      this.elapsed = Math.min(end, this.elapsed + dt * this.rate);
      while (this.cursor + 1 < this.frames.length - 1
          && this.frames[this.cursor + 1][0] < this.elapsed) this.cursor++;
      const a = this.frames[this.cursor];
      const b = this.frames[Math.min(this.cursor + 1, this.frames.length - 1)];
      const fraction = b[0] === a[0] ? 0 : (this.elapsed - a[0]) / (b[0] - a[0]);
      this.frame = a.map((value, index) => index === 0 ? this.elapsed
        : value + (b[index] - value) * fraction);
      this.time += dt;
      this.publish();
      this.updateVisual();
    }
  }

  publish() {
    const finished = this.frames.length > 0 && this.elapsed >= this.frames.at(-1)[0];
    const flowing = this.active && !this.paused && !finished;
    estados.set(this.sceneKey, { finished, sourceLevel: this.frame[1],
      destLevel: this.frame[2], speed: flowing ? this.frame[3] : 0 });
    const readout = document.getElementById(`pc-3d-time-${this.sceneKey}`);
    if (readout) readout.textContent = `Tiempo simulado ${(this.elapsed / 60).toFixed(1)} min · `
      + `Q ${(flowing ? this.frame[4] : 0).toFixed(3)} m³/h`;
    const volumes = document.getElementById(`pc-3d-volume-${this.sceneKey}`);
    if (volumes) volumes.textContent = `Origen ${this.frame[5].toFixed(3)} m³  →  `
      + `Destino ${this.frame[6].toFixed(3)} m³`;
    const levels = document.getElementById(`pc-3d-level-${this.sceneKey}`);
    if (levels) levels.textContent = `Alturas de agua ${this.frame[7].toFixed(2)} / `
      + `${this.frame[8].toFixed(2)} m · Δz actual ${this.frame[9].toFixed(2)} m`;
    const status = document.getElementById(`pc-3d-stop-${this.sceneKey}`);
    if (status) status.textContent = finished ? this.stopReason :
      this.paused ? 'Reproducción pausada' : 'Runge–Kutta 4 · 1 s visual = 60 s simulados';
  }

  updateVisual() {
    const level = this.frame[2];
    const height = Math.max(.01, level - this.bottom);
    this.liquid.scale.z = height;
    this.liquid.position.z = this.bottom + height / 2;
    this.surface.position.z = level + .008;
    this.levelLine.position.z = level;
    const flowing = this.active && !this.paused &&
      this.elapsed < (this.frames.at(-1)?.[0] ?? 0)
      && !matchMedia('(prefers-reduced-motion: reduce)').matches;
    this.uniforms.time.value = this.time;
    this.uniforms.agitation.value = flowing ? 1 : 0;
    const length = Math.max(.01, this.outlet - level);
    this.stream.visible = flowing;
    this.stream.scale.y = length;
    this.stream.position.z = level + length / 2;
    this.ripples.forEach((ring, index) => {
      const phase = (this.time * 1.8 + index * .5) % 1;
      ring.visible = flowing;
      ring.position.z = level + .015;
      ring.scale.setScalar(.45 + 2.15 * phase);
      ring.material.opacity = .38 * (1 - phase);
    });
  }
}
