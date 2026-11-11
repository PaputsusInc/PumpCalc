# Guía breve de sustentación

Duración sugerida: 6–8 minutos. Instala y abre la aplicación según el [manual](README.md). Antes de exponer, repasa el recorrido del [informe](VALIDACION_FINAL.md), cuya aceptación visual comunicó el usuario al cerrar el desarrollo.

## Recorrido

| Momento | Acción | Explicación |
| --- | --- | --- |
| 0–1 min | Cargar **Caso base** en A | Una bomba, una tubería, depósitos abiertos y niveles fijos. Q ≈ 3,765450 m³/h y H ≈ 20,641853 m; no alcanza la meta de 4 m³/h. |
| 1–2 min | **Copiar A en B**, cambiar solo D de 25 a 32 mm y activar **Comparar A y B** | A conserva sus entradas. B da Q ≈ 4,381752 m³/h y supera la meta; incremento ≈ 16,3673 %. |
| 2–3 min | Comparar escenas, curvas y velocidades | v baja de ≈ 2,130809 a ≈ 1,513406 m/s. Aumenta el área y disminuye la resistencia. El mayor Q no implica mayor v: v = Q/área. Grosor y movimiento usan escalas comunes. |
| 3–5 min | Abrir detalle numérico | Interpolación obtiene Hb; punto fijo obtiene f para Hs; bisección equilibra ambas alturas. Mostrar intervalo, semiancho, residuo y las dos condiciones de parada. Colebrook mostrado corresponde a la evaluación final. |
| 5–6 min | Pausar y reanudar; introducir temporalmente D = 0 y restaurar D = 32 | Pausar conserva Q y H. Un dato inválido se señala y retira el resultado vigente; al corregirlo se recalcula. |
| 6–7 min | Cargar **Sin intersección** en B | Con Δz = 40 m, la curva disponible no alcanza la altura exigida. Escena detenida, aviso y ausencia de punto o diferencia de caudal inventados. |
| 7–8 min | Mostrar una verificación conocida y los límites | Interpolación da 28,5 m a 2,5 m³/h. El control aislado de bisección reproduce √21 − 1. La animación no representa llenado ni certifica una instalación. |

## Preguntas que debe poder responder todo el equipo

- **¿Qué representa el punto de operación?** El caudal para el cual la altura de bomba coincide con la altura estática más las pérdidas: F(Q) = Hb(Q) − Hs(Q) = 0.
- **¿Por qué tres métodos?** La curva llega tabulada, la fricción turbulenta es implícita y el caudal de equilibrio requiere buscar una raíz. Cada método resuelve una necesidad distinta.
- **¿Cuándo termina el cálculo?** Bisección exige semiancho ≤ 10⁻⁷ m³/s y residuo absoluto ≤ 10⁻⁴ m, salvo raíz exacta, con máximo 80 iteraciones. Colebrook exige cambio y residuo absolutos ≤ 10⁻¹⁰, con máximo 100.
- **¿Qué pasa en otros regímenes?** Laminar usa 64/Re. Transición usa una unión didáctica con advertencia y un auxiliar de Colebrook en Re = 4000. En Q = 0 no se evalúa f.
- **¿Por qué no extrapolar?** Solo se conocen los puntos ingresados; afirmar el comportamiento exterior requiere más información. El aviso sin cruce se limita a ese dominio.
- **¿Qué significa En el límite numérico?** El margen frente al objetivo no supera la cota numérica de la raíz. No representa tolerancia constructiva ni incertidumbre de una bomba real.
- **¿Qué aporta el proyecto?** Integra experimentación A/B, movimiento vinculado a la velocidad y trazas de los métodos para un público principiante. No se afirma haber inventado la simulación de bombas.

## Evidencia y límites

El [informe](VALIDACION_FINAL.md) registra instalación limpia, versiones, 282 pruebas aprobadas, resultados y aceptación visual comunicada por el usuario. Explica la omisión del módulo de escritorio antiguo. Las pruebas del simulador oficial de NiceGUI verifican eventos y estado sin observar el dibujo en pantalla; la aceptación manual se registra aparte.

El modelo usa agua a aproximadamente 20 °C, una bomba a velocidad fija y una tubería llena. No calcula cavitación, eficiencia, transitorios ni redes. La curva de demostración es ficticia y alcanzar la meta solo describe este modelo. Todos los integrantes deben comprender el recorrido de datos desde validación hasta resultados y poder explicar estas limitaciones.
