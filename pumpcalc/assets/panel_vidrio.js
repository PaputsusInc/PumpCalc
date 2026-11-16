import { THREE } from 'nicegui-scene';

export default class PanelVidrio {
  create_mesh(width, depth, height) {
    const panel = new THREE.Mesh(
      new THREE.BoxGeometry(width, depth, height),
      new THREE.MeshPhysicalMaterial({
        color: '#8bb5ca', transparent: true, opacity: .13,
        metalness: .02, roughness: .12, depthWrite: false,
        side: THREE.DoubleSide,
      }),
    );
    panel.renderOrder = 11;
    return panel;
  }
}
