"""Exporta a GLB una base editable de la vista 3D del escenario A.

Ejecutar con: blender --background --python tools/blender/generar_instalacion_base.py
Las coordenadas y proporciones siguen pumpcalc/escena3d.py. No sustituye la
animación del agua ni la geometría variable de la aplicación.
"""

import math
from pathlib import Path

import bpy
from mathutils import Vector


SALIDA = Path(__file__).resolve().parents[2] / 'assets' / 'modelos' / 'referencia' / 'instalacion_base.glb'
NIVEL_ORIGEN = 1.0
NIVEL_DESTINO = 1 + 2.45 * math.log1p(12) / math.log1p(100)
X_DESTINO = 3.9 + 0.42 * math.log1p(40 / 10) / math.log1p(100)
RADIO = 0.082 + 0.052 * math.log(0.025 / 0.01, 20)
BASE_DESTINO = NIVEL_DESTINO - 0.84
ENTRADA_DESTINO = NIVEL_DESTINO - 0.35


bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for collection in list(bpy.data.collections):
    if collection.name != 'Collection':
        bpy.data.collections.remove(collection)


def material(nombre, hex_color, *, alpha=1.0, metalico=0.0, rugosidad=0.42):
    rgb = tuple(int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5))
    mat = bpy.data.materials.new(nombre)
    mat.diffuse_color = (*rgb, alpha)
    mat.use_nodes = True
    principled = mat.node_tree.nodes.get('Principled BSDF')
    principled.inputs['Base Color'].default_value = (*rgb, 1)
    principled.inputs['Alpha'].default_value = alpha
    principled.inputs['Metallic'].default_value = metalico
    principled.inputs['Roughness'].default_value = rugosidad
    if alpha < 1:
        mat.surface_render_method = 'BLENDED'
    return mat


MAT = {
    'suelo': material('Suelo azul noche', '#101833', rugosidad=0.3),
    'base': material('Base violeta oscura', '#25254d'),
    'pedestal': material('Pedestal descarga', '#1f2748'),
    'tanque_base': material('Depósito base', '#414e74', metalico=0.35),
    'tanque_postes': material('Depósito postes', '#7188aa', metalico=0.48),
    'tanque_bordes': material('Depósito bordes', '#9aafd0', metalico=0.55),
    'tanque_travesaños': material('Depósito travesaños', '#8fa6c5', metalico=0.48),
    'agua': material('Agua cian translúcida', '#057fae', alpha=0.64, rugosidad=0.1),
    'agua_superficie': material('Superficie agua', '#16b9df', alpha=0.82, rugosidad=0.08),
    'agua_borde': material('Nivel de agua luminoso', '#62eaff', alpha=0.88, rugosidad=0.1),
    'tubo_externo': material('Tubería exterior', '#155c7d', alpha=0.74, metalico=0.35),
    'tubo_interno': material('Tubería interior cian', '#20c6e5', alpha=0.72, metalico=0.2),
    'tubo_reflejo': material('Reflejo de tubería', '#9cecff', alpha=0.74),
    'motor': material('Motor violeta', '#4b3ac0', metalico=0.5),
    'motor_centro': material('Motor centro', '#322883', metalico=0.45),
    'motor_aletas': material('Aletas motor', '#7869df', metalico=0.55),
    'voluta': material('Voluta bomba', '#5541c5', metalico=0.5),
    'voluta_tapa': material('Tapa voluta', '#382986', metalico=0.55),
    'bridas': material('Bridas bomba', '#6754d4', metalico=0.55),
    'tornillos': material('Tornillos claros', '#b9aaf5', metalico=0.6),
    'soporte': material('Soporte bomba', '#4535a7', metalico=0.4),
    'caja': material('Caja superior bomba', '#4634ac', metalico=0.4),
    'caja_tapa': material('Tapa caja bomba', '#7966ed', metalico=0.5),
    'rotulo_agua': material('Rótulos cian', '#4beaff'),
    'rotulo_bomba': material('Rótulo bomba', '#b999ff'),
}


def grupo(nombre):
    col = bpy.data.collections.new(nombre)
    bpy.context.scene.collection.children.link(col)
    return col


GRUPOS = {
    clave: grupo(nombre)
    for clave, nombre in (
        ('suelo', '01 Suelo y bases'),
        ('origen', '02 Depósito de succión'),
        ('succion', '03 Tubería de succión'),
        ('bomba', '04 Bomba'),
        ('descarga', '05 Tubería de descarga'),
        ('destino', '06 Depósito de descarga'),
        ('rotulos', '07 Rótulos opcionales'),
        ('conexiones', '08 Referencias de conexión'),
    )
}
RAICES = {}
for clave, col in GRUPOS.items():
    raiz = bpy.data.objects.new('GRUPO / ' + col.name, None)
    raiz.empty_display_type = 'PLAIN_AXES'
    raiz.empty_display_size = .16
    col.objects.link(raiz)
    RAICES[clave] = raiz


def mover_a_grupo(obj, clave):
    for col in list(obj.users_collection):
        col.objects.unlink(obj)
    GRUPOS[clave].objects.link(obj)
    obj.parent = RAICES[clave]
    return obj


def acabado(obj, nombre, clave_grupo, clave_material):
    obj.name = nombre
    obj.data.materials.append(MAT[clave_material])
    mover_a_grupo(obj, clave_grupo)
    return obj


def caja(nombre, dimensiones, centro, grupo_clave, material_clave, rotacion=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=centro)
    obj = bpy.context.object
    obj.dimensions = dimensiones
    if rotacion is not None:
        obj.rotation_euler = rotacion
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return acabado(obj, nombre, grupo_clave, material_clave)


def esfera(nombre, centro, radio, grupo_clave, material_clave):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=radio, location=centro)
    return acabado(bpy.context.object, nombre, grupo_clave, material_clave)


def cilindro(nombre, a, b, radio, grupo_clave, material_clave, vertices=32):
    a, b = Vector(a), Vector(b)
    direccion = b - a
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radio, depth=direccion.length,
                                        location=(a + b) / 2)
    obj = bpy.context.object
    obj.rotation_euler = direccion.to_track_quat('Z', 'Y').to_euler()
    return acabado(obj, nombre, grupo_clave, material_clave)


def codo(nombre, a, control, b, radio, grupo_clave, material_clave):
    a, control, b = Vector(a), Vector(control), Vector(b)
    vertices, caras = [], []
    secciones, lados = 30, 16
    transversal = Vector((0, 1, 0))
    for i in range(secciones + 1):
        t = i / secciones
        punto = (1 - t) ** 2 * a + 2 * (1 - t) * t * control + t ** 2 * b
        tangente = (2 * (1 - t) * (control - a) + 2 * t * (b - control)).normalized()
        otra = tangente.cross(transversal).normalized()
        for j in range(lados):
            angulo = 2 * math.pi * j / lados
            vertices.append(punto + radio * (math.cos(angulo) * transversal + math.sin(angulo) * otra))
    for i in range(secciones):
        for j in range(lados):
            siguiente = (j + 1) % lados
            caras.append((i*lados+j, i*lados+siguiente,
                          (i+1)*lados+siguiente, (i+1)*lados+j))
    caras.append(tuple(reversed(tuple(range(lados)))))
    caras.append(tuple(secciones*lados + j for j in range(lados)))
    mesh = bpy.data.meshes.new(nombre)
    mesh.from_pydata(vertices, [], caras)
    mesh.update()
    obj = bpy.data.objects.new(nombre, mesh)
    GRUPOS[grupo_clave].objects.link(obj)
    obj.parent = RAICES[grupo_clave]
    obj.data.materials.append(MAT[material_clave])
    return obj


def tramo_horizontal(nombre, x0, x1, z, clave):
    cilindro(nombre + ' / exterior', (x0, 0, z), (x1, 0, z), RADIO * 1.48,
             clave, 'tubo_externo', 24)
    cilindro(nombre + ' / agua visible', (x0, 0, z), (x1, 0, z), RADIO,
             clave, 'tubo_interno', 24)
    cilindro(nombre + ' / reflejo', (x0, 0, z + RADIO * .88),
             (x1, 0, z + RADIO * .88), RADIO * .12, clave, 'tubo_reflejo', 12)


def tramo_vertical(nombre, z0, z1, x):
    cilindro(nombre + ' / exterior', (x, 0, z0), (x, 0, z1), RADIO * 1.48,
             'descarga', 'tubo_externo', 24)
    cilindro(nombre + ' / agua visible', (x, 0, z0), (x, 0, z1), RADIO,
             'descarga', 'tubo_interno', 24)


def codo_doble(nombre, a, control, b):
    codo(nombre + ' / exterior', a, control, b, RADIO * 1.48, 'descarga', 'tubo_externo')
    codo(nombre + ' / agua visible', a, control, b, RADIO, 'descarga', 'tubo_interno')


def tanque(nombre, x, base, nivel, ancho, clave):
    fondo = 1.5
    alto = nivel - base + .42
    caja(nombre + ' / fondo', (ancho, fondo, .12), (x, 0, base), clave, 'tanque_base')
    for lado in (-1, 1):
        for profundidad in (-.72, .72):
            caja(nombre + f' / poste {lado:+d} {profundidad:+.2f}', (.09, .09, alto),
                 (x + lado * ancho / 2, profundidad, base + alto / 2),
                 clave, 'tanque_postes')
        caja(nombre + f' / borde lateral {lado:+d}', (.12, fondo + .12, .08),
             (x + lado * ancho / 2, 0, base + alto), clave, 'tanque_bordes')
    for profundidad in (-.72, .72):
        caja(nombre + f' / borde frontal {profundidad:+.2f}', (ancho + .1, .09, .07),
             (x, profundidad, base + alto), clave, 'tanque_travesaños')
    caja(nombre + ' / volumen de agua', (ancho - .15, fondo - .17, nivel - base - .05),
         (x, 0, (base + nivel) / 2 + .015), clave, 'agua')
    caja(nombre + ' / superficie de agua', (ancho - .15, fondo - .17, .014),
         (x, 0, nivel), clave, 'agua_superficie')
    caja(nombre + ' / línea de nivel frontal', (ancho - .18, .024, .018),
         (x, -.65, nivel), clave, 'agua_borde')


def rotulo(texto, x, inicio, fin, clave_material):
    cilindro(texto + ' / guía', (x, -.36, inicio), (x, -.36, fin - .2), .012,
             'rotulos', clave_material, 12)
    esfera(texto + ' / punto', (x, -.36, inicio), .031, 'rotulos', clave_material)
    curva = bpy.data.curves.new(texto, type='FONT')
    curva.body = texto
    curva.size = .18
    curva.align_x = 'CENTER'
    obj = bpy.data.objects.new(texto, curva)
    GRUPOS['rotulos'].objects.link(obj)
    obj.parent = RAICES['rotulos']
    obj.location = (x, -.36, fin)
    obj.rotation_euler = (math.pi / 2, 0, 0)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    obj.select_set(False)
    obj.data.materials.append(MAT[clave_material])


def referencia(nombre, punto):
    obj = bpy.data.objects.new(nombre, None)
    obj.empty_display_type = 'SPHERE'
    obj.empty_display_size = .12
    obj.location = punto
    GRUPOS['conexiones'].objects.link(obj)
    obj.parent = RAICES['conexiones']


# Formas y ubicaciones equivalentes a las primitivas de la vista de la aplicación.
caja('Suelo oscuro', (12.8, 5.1, .01), (.08, 0, -.05), 'suelo', 'suelo')
caja('Base de bomba', (3.0, 2.15, .08), (-1, 0, .08), 'suelo', 'base')
caja('Pedestal depósito de descarga', (2.6, 1.9, BASE_DESTINO - .12),
     (X_DESTINO, 0, (BASE_DESTINO + .12) / 2), 'suelo', 'pedestal')
tanque('Depósito de succión', -4.05, .16, NIVEL_ORIGEN, 2.05, 'origen')
tanque('Depósito de descarga', X_DESTINO, BASE_DESTINO, NIVEL_DESTINO, 2.2, 'destino')

tramo_horizontal('Aspiración', -4.16, -1.93, .58, 'succion')
tramo_horizontal('Descarga horizontal inferior', .23, 1.92, .58, 'descarga')
codo_doble('Codo inferior', (1.92, 0, .58), (2.12, 0, .58), (2.12, 0, .78))
tramo_vertical('Ascenso', .78, ENTRADA_DESTINO - .2, 2.12)
codo_doble('Codo superior', (2.12, 0, ENTRADA_DESTINO - .2),
            (2.12, 0, ENTRADA_DESTINO), (2.32, 0, ENTRADA_DESTINO))
tramo_horizontal('Descarga horizontal superior', 2.32, X_DESTINO - .52,
                 ENTRADA_DESTINO, 'descarga')

cilindro('Motor / carcasa', (-1.78, 0, .58), (-.42, 0, .58), .31, 'bomba', 'motor')
cilindro('Motor / centro', (-1.70, 0, .58), (-.44, 0, .58), .25, 'bomba', 'motor_centro')
for indice in range(10):
    angulo = indice * math.tau / 10
    caja(f'Motor / aleta {indice + 1:02d}', (1.20, .045, .055),
         (-1.07, .285 * math.sin(angulo), .58 + .285 * math.cos(angulo)),
         'bomba', 'motor_aletas', (angulo, 0, 0))
cilindro('Voluta / cuerpo', (-.45, 0, .58), (.11, 0, .58), .40, 'bomba', 'voluta')
cilindro('Voluta / tapa', (.08, 0, .58), (.16, 0, .58), .34, 'bomba', 'voluta_tapa')
for indice in range(8):
    angulo = indice * math.tau / 8
    esfera(f'Voluta / tornillo {indice + 1:02d}',
           (.18, .275 * math.sin(angulo), .58 + .275 * math.cos(angulo)),
           .035, 'bomba', 'tornillos')
for indice, x in enumerate((-1.87, .17), 1):
    cilindro(f'Brida {indice}', (x - .05, 0, .58), (x + .05, 0, .58),
             .42, 'bomba', 'bridas')
caja('Bomba / soporte', (1.24, .62, .09), (-.94, 0, .20), 'bomba', 'soporte')
for x in (-1.46, -.44):
    esfera(f'Soporte / tornillo {x:+.2f}', (x, -.31, .26), .055, 'bomba', 'tornillos')
caja('Bomba / caja superior', (.58, .52, .34), (-.9, 0, 1.05), 'bomba', 'caja')
caja('Bomba / tapa de caja', (.69, .61, .07), (-.9, 0, 1.24), 'bomba', 'caja_tapa')
for x in (-1.15, -.65):
    for y in (-.23, .23):
        esfera(f'Caja / tornillo {x:+.2f} {y:+.2f}', (x, y, 1.29),
               .023, 'bomba', 'tornillos')

rotulo('DEPÓSITO DE SUCCIÓN', -4.05, NIVEL_ORIGEN + .45, NIVEL_ORIGEN + 1.0,
       'rotulo_agua')
rotulo('BOMBA', -.9, 1.30, 2.16, 'rotulo_bomba')
rotulo('DEPÓSITO DE DESCARGA', X_DESTINO, NIVEL_DESTINO + .45,
       NIVEL_DESTINO + 1.0, 'rotulo_agua')
referencia('CONEXIÓN / entrada bomba', (-1.93, 0, .58))
referencia('CONEXIÓN / salida bomba', (.23, 0, .58))
referencia('CONEXIÓN / entrada depósito destino', (X_DESTINO - .52, 0, ENTRADA_DESTINO))

bpy.ops.export_scene.gltf(filepath=str(SALIDA), export_format='GLB',
                          export_yup=True, export_extras=True)
print(f'MODELO_EXPORTADO {SALIDA} objetos={len(bpy.data.objects)}')
