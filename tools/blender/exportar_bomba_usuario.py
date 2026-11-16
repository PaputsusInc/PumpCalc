"""Extrae la bomba del archivo Blender aportado y la prepara para la escena.

Uso: blender -b ../Untitled.blend --python tools/blender/exportar_bomba_usuario.py
El archivo fuente no se modifica. La instalación variable y el agua se dibujan
en la aplicación; este GLB contiene solo la bomba y sus detalles.
"""

from pathlib import Path

import bpy


SALIDA = Path(__file__).resolve().parents[2] / 'assets' / 'modelos' / 'bomba_usuario.glb'
RAIZ = 'GRUPO / 04 Bomba'


def pertenece_a_bomba(obj):
    actual = obj
    while actual is not None:
        if actual.name == RAIZ:
            return True
        actual = actual.parent
    return obj.name == 'Cylinder'  # detalle adicional en el archivo aportado


partes = [obj for obj in bpy.data.objects if obj.type == 'MESH' and pertenece_a_bomba(obj)]
if not partes:
    raise RuntimeError('El archivo Blender no contiene las piezas de la bomba esperadas.')

# Las superficies planas tienen cantos suaves y normales estables bajo luz rasante.
for obj in partes:
    if obj.name != 'Cylinder' and len(obj.data.polygons) <= 24:
        bisel = obj.modifiers.new('Cantos mecanizados', 'BEVEL')
        bisel.width = .008 if 'tornillo' in obj.name.lower() else .014
        bisel.segments = 2
        bisel.affect = 'EDGES'
    for mat in obj.data.materials:
        if mat is None or not mat.use_nodes:
            continue
        bsdf = mat.node_tree.nodes.get('Principled BSDF')
        if bsdf is None:
            continue
        nombre = mat.name.lower()
        if 'tornillo' in nombre or nombre.startswith('material.002'):
            bsdf.inputs['Metallic'].default_value = .75
            bsdf.inputs['Roughness'].default_value = .26
        elif 'motor' in nombre or 'voluta' in nombre or 'bridas' in nombre:
            bsdf.inputs['Metallic'].default_value = .56
            bsdf.inputs['Roughness'].default_value = .32
        elif 'caja' in nombre or 'tapa' in nombre:
            bsdf.inputs['Metallic'].default_value = .4
            bsdf.inputs['Roughness'].default_value = .36

bpy.ops.object.select_all(action='DESELECT')
for obj in partes:
    obj.select_set(True)
bpy.context.view_layer.objects.active = partes[0]
bpy.ops.export_scene.gltf(
    filepath=str(SALIDA), export_format='GLB', use_selection=True,
    export_yup=False, export_apply=True, export_materials='EXPORT',
)
print(f'BOMBA_EXPORTADA {SALIDA} piezas={len(partes)}')
