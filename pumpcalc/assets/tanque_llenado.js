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
    this.progress = 0;
    this.speed = 0;
    this.active = false;
    this.paused = false;
    this.time = 0;
    this.lastTime = performance.now();
    estados.set(sceneKey, { finished: false, progress: 0 });

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

  set_flow(speed, active, paused, revision) {
    if (this.revision !== revision) {
      this.revision = revision;
      this.progress = 0;
      estados.set(this.sceneKey, { finished: false, progress: 0 });
    }
    this.speed = Number.isFinite(speed) ? Math.max(0, speed) : 0;
    this.active = Boolean(active) && this.speed > 0;
    this.paused = Boolean(paused);
    if (!this.active) {
      this.progress = 0;
      estados.set(this.sceneKey, { finished: false, progress: 0 });
    }
    if (this.active && matchMedia('(prefers-reduced-motion: reduce)').matches) {
      this.progress = 1;
      estados.set(this.sceneKey, { finished: true, progress: 1 });
    }
    this.lastTime = performance.now();
    this.updateVisual();
  }

  restart() {
    this.progress = 0;
    this.time = 0;
    this.lastTime = performance.now();
    estados.set(this.sceneKey, { finished: false, progress: 0 });
    this.updateVisual();
  }

  animate() {
    const now = performance.now();
    const dt = Math.min((now - this.lastTime) / 1000, .08);
    this.lastTime = now;
    const moving = this.active && !this.paused && this.progress < 1
      && !matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (moving) {
      // Escala de demostración: Q determina la rapidez relativa, no el tiempo real.
      this.progress = Math.min(1, this.progress + dt * this.speed * .045);
      this.time += dt;
      estados.set(this.sceneKey, { finished: this.progress === 1, progress: this.progress });
      this.updateVisual();
    }
  }

  updateVisual() {
    const level = this.initial + (this.target - this.initial) * this.progress;
    const height = Math.max(.01, level - this.bottom);
    this.liquid.scale.z = height;
    this.liquid.position.z = this.bottom + height / 2;
    this.surface.position.z = level + .008;
    this.levelLine.position.z = level;
    const flowing = this.active && !this.paused && this.progress < 1
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
