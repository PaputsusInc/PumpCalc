"""Identidad visual del laboratorio; estilos locales sin recursos externos."""

from nicegui import ui


def aplicar_tema() -> None:
    """Define colores de NiceGUI y estilos de los paneles de PumpCalc."""
    ui.colors(primary='#0c4a6e', secondary='#6366f1', accent='#06b6d4', positive='#059669',
              negative='#dc2626', warning='#d97706')
    ui.add_head_html(
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900'
        '&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">'
    )
    ui.add_css(ESTILOS)


def encabezado_seccion(titulo: str, subtitulo: str, icono: str) -> None:
    """Dibuja el encabezado compartido por la configuración y los resultados."""
    with ui.element('div').classes('pc-section-head'):
        ui.icon(icono, size='20px').classes('pc-section-icon').props('aria-hidden=true')
        with ui.column().classes('gap-0'):
            ui.label(titulo).classes('pc-section-title')
            ui.label(subtitulo).classes('pc-section-subtitle')


ESTILOS = '''
/* ═══════════════════════════════════════════════════════════════════════
   PumpCalc — Design System · Minimalism & Swiss Style
   Paleta: Navy profesional + Teal/Cyan (dominio hidráulico)
   Tipografía: Inter (UI) + JetBrains Mono (datos numéricos)
   ═══════════════════════════════════════════════════════════════════════ */

/* ── Tokens ────────────────────────────────────────────────────────── */
:root {
    /* Colores */
    --pc-ink:       #0f172a;
    --pc-muted:     #64748b;
    --pc-subtle:    #94a3b8;
    --pc-surface:   #f8fafc;
    --pc-card:      #ffffff;
    --pc-border:    #e2e8f0;
    --pc-border-s:  #cbd5e1;

    /* Acentos */
    --pc-navy:      #0c1929;
    --pc-navy-mid:  #0f2740;
    --pc-teal:      #0891b2;
    --pc-teal-soft: #06b6d4;
    --pc-cyan:      #22d3ee;
    --pc-indigo:    #6366f1;
    --pc-emerald:   #059669;
    --pc-lime:      #d5fa55;
    --pc-amber:     #f59e0b;

    /* Efectos */
    --pc-shadow-sm: 0 1px 2px 0 rgb(15 23 42 / .04);
    --pc-shadow:    0 1px 3px 0 rgb(15 23 42 / .06), 0 1px 2px -1px rgb(15 23 42 / .06);
    --pc-shadow-md: 0 4px 6px -1px rgb(15 23 42 / .07), 0 2px 4px -2px rgb(15 23 42 / .05);
    --pc-radius:    14px;
    --pc-radius-sm: 10px;

    /* Tipografía */
    --pc-font:      'Inter', 'Segoe UI', system-ui, sans-serif;
    --pc-mono:      'JetBrains Mono', 'Fira Code', ui-monospace, monospace;
}

/* ── Base ──────────────────────────────────────────────────────────── */
body {
    background: var(--pc-surface);
    color: var(--pc-ink);
    font-family: var(--pc-font);
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}
.nicegui-content { padding: 0; gap: 0; }

/* ── Header ────────────────────────────────────────────────────────── */
.pc-header {
    background: linear-gradient(135deg, var(--pc-navy) 0%, var(--pc-navy-mid) 100%);
    color: white;
    box-shadow: 0 1px 0 0 rgba(255,255,255,.04);
    padding: 0 max(28px, calc((100vw - 1440px)/2));
    min-height: 64px;
    border-bottom: 1px solid rgba(255,255,255,.06);
}
.pc-brand {
    font-size: 22px;
    font-weight: 800;
    letter-spacing: -0.5px;
    background: linear-gradient(135deg, #ffffff 40%, var(--pc-cyan) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.pc-logo {
    color: var(--pc-navy);
    background: linear-gradient(135deg, var(--pc-cyan), var(--pc-teal));
    padding: 7px;
    border-radius: 10px 10px 10px 3px;
    box-shadow: 0 0 12px rgba(6,182,212,.25);
}
.pc-header-note {
    color: rgba(148,203,220,.7);
    font-size: 11px;
    letter-spacing: 2px;
    text-transform: uppercase;
    font-weight: 500;
}
.pc-local {
    margin-left: auto;
    border: 1px solid rgba(255,255,255,.12);
    border-radius: 100px;
    padding: 6px 14px;
    font-size: 11px;
    color: rgba(255,255,255,.7);
    gap: 7px;
    align-items: center;
    backdrop-filter: blur(4px);
    background: rgba(255,255,255,.04);
    font-weight: 500;
}
.pc-local .q-icon { color: var(--pc-cyan); font-size: 8px; }

/* ── Main Container ────────────────────────────────────────────────── */
.pc-main {
    width: 100%;
    max-width: 1440px;
    margin: 0 auto;
    padding: 28px 28px 24px;
    gap: 20px;
}

/* ── Card / Panel ──────────────────────────────────────────────────── */
.pc-panel {
    border: 1px solid var(--pc-border);
    border-radius: var(--pc-radius);
    box-shadow: var(--pc-shadow);
    background: var(--pc-card);
    padding: 24px;
    gap: 18px;
    min-width: 0;
    transition: box-shadow .2s ease;
}
.pc-panel:hover { box-shadow: var(--pc-shadow-md); }

/* ── Toolbar ───────────────────────────────────────────────────────── */
.pc-eyebrow {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: var(--pc-teal);
}
.pc-toolbar { padding: 18px 22px; gap: 14px; }
.pc-toolbar-main {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
    width: 100%;
}
.pc-toolbar .q-toggle {
    margin-left: auto;
    font-size: 13px;
    font-weight: 600;
}
.pc-toolbar .q-btn-toggle {
    border: 1px solid var(--pc-border);
    border-radius: var(--pc-radius-sm);
    box-shadow: none;
    background: var(--pc-surface);
}
.pc-toolbar .q-btn-toggle .q-btn { min-width: 44px; }
.pc-action {
    background: linear-gradient(135deg, var(--pc-teal) 0%, #0e7490 100%) !important;
    color: white !important;
    box-shadow: 0 2px 8px rgba(8,145,178,.3);
    font-weight: 700;
    padding-left: 22px;
    padding-right: 22px;
    letter-spacing: .2px;
}
.pc-action:hover { box-shadow: 0 4px 14px rgba(8,145,178,.4); }

/* ── Example Row ───────────────────────────────────────────────────── */
.pc-example-row {
    width: 100%;
    border-top: 1px solid var(--pc-border);
    padding-top: 14px;
    display: flex;
    gap: 12px;
    align-items: center;
    flex-wrap: wrap;
}
.pc-example-row .q-field { width: 220px; }
.pc-example-note {
    margin-left: auto;
    color: var(--pc-subtle);
    font-size: 11px;
    font-style: italic;
}

/* ── Lab Layout (sidebar + main) ───────────────────────────────────── */
.pc-lab {
    display: grid;
    grid-template-columns: minmax(340px, 400px) minmax(0, 1fr);
    gap: 20px;
    width: 100%;
    align-items: start;
}
.pc-config, .pc-stage {
    display: flex;
    flex-direction: column;
    gap: 20px;
    min-width: 0;
    width: 100%;
}

/* ── Section Headers ───────────────────────────────────────────────── */
.pc-section-head {
    width: 100%;
    display: flex;
    align-items: center;
    gap: 12px;
}
.pc-section-icon {
    background: linear-gradient(135deg, #ecfeff, #e0f2fe);
    color: var(--pc-teal);
    padding: 9px;
    border-radius: var(--pc-radius-sm);
}
.pc-section-title {
    font-size: 18px;
    font-weight: 700;
    letter-spacing: -0.3px;
    color: var(--pc-ink);
}
.pc-section-subtitle {
    font-size: 12px;
    color: var(--pc-muted);
    margin-top: 1px;
}

/* ── Form Fields ───────────────────────────────────────────────────── */
.pc-panel .text-slate-600 { color: var(--pc-muted); }
.pc-panel .q-field--outlined .q-field__control {
    border-radius: var(--pc-radius-sm);
    background: var(--pc-surface);
    transition: border-color .15s ease, background .15s ease;
}
.pc-panel .q-field--outlined .q-field__control:before { border-color: var(--pc-border-s); }
.pc-panel .q-field--outlined .q-field__control:hover:before { border-color: var(--pc-teal); }
.pc-panel .q-field--outlined.q-field--focused .q-field__control { background: #f0fdfa; }
.pc-panel .q-field__label { color: var(--pc-muted); font-weight: 500; font-size: 13px; }
.pc-panel .q-field__native {
    color: var(--pc-ink);
    font-variant-numeric: tabular-nums;
    font-family: var(--pc-mono);
    font-size: 14px;
    font-weight: 500;
}
.pc-panel .q-btn {
    border-radius: var(--pc-radius-sm);
    text-transform: none;
    font-weight: 600;
    letter-spacing: 0;
    transition: all .18s ease;
}

/* ── Input Grids ───────────────────────────────────────────────────── */
.pc-input-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
    width: 100%;
}
.pc-input-grid > :last-child { grid-column: 1 / -1; }
.pc-bomba-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px;
    width: 100%;
}
.pc-bomba-grid > :last-child { grid-column: 1 / -1; }

/* ── Tanks ─────────────────────────────────────────────────────────── */
.pc-tanks { border-top: 3px solid var(--pc-teal); }
.pc-tank-card {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px;
    padding: 16px;
    width: 100%;
    border: 1px solid #cce5eb;
    border-radius: 12px;
    background: linear-gradient(145deg, #f0fdfa, #f0f9ff);
}
.pc-tank-card > :first-child { grid-column: 1 / -1; }
.pc-tank-card > :last-child { grid-column: 1 / -1; }
.pc-tank-title { font-size: 13px; font-weight: 700; color: #0c4a6e; }
.pc-tank-icon { color: var(--pc-teal); }

/* ── Pump Table ────────────────────────────────────────────────────── */
.pc-pump-table { width: 100%; table-layout: fixed; border-collapse: collapse; }
.pc-pump-table th {
    font-size: 11px;
    padding: 0 4px 10px;
    color: var(--pc-muted);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .5px;
}
.pc-pump-table th:first-child { width: 30px; }
.pc-pump-table th:last-child { width: 36px; }
.pc-pump-table td { padding: 4px; vertical-align: top; }
.pc-pump-table td:first-child {
    font-size: 12px;
    color: var(--pc-subtle);
    font-family: var(--pc-mono);
    font-weight: 600;
}
.pc-pump-table .q-field__label { font-size: 11px; }
.pc-pump-table .q-field__native { font-size: 13px; }
.pc-pump-table .q-btn { min-width: 28px; min-height: 32px; font-size: 11px; }

/* ── Target / Meta ─────────────────────────────────────────────────── */
.pc-target { border-top: 3px solid var(--pc-indigo); }
.pc-meta-grid { width: 100%; display: grid; gap: 10px; }
.pc-meta {
    border-left: 3px solid var(--pc-teal);
    background: #f0fdfa;
    border-radius: 0 var(--pc-radius-sm) var(--pc-radius-sm) 0;
    padding: 10px 14px;
    font-size: 12px;
    font-weight: 600;
}
.pc-meta-b { border-left-color: var(--pc-indigo); background: #eef2ff; }
.pc-meta small {
    display: block;
    font-size: 11px;
    font-weight: 400;
    margin-top: 3px;
    color: var(--pc-muted);
}

/* ── 3D / 2D Scene ─────────────────────────────────────────────────── */
.pc-scene {
    background: linear-gradient(160deg, #0c1929 0%, #0f2740 100%);
    border-color: rgba(255,255,255,.08);
    color: #e2f5f5;
    padding: 22px;
    overflow: hidden;
}
.pc-scene-b {
    background: linear-gradient(160deg, #1e1b4b 0%, #312e81 100%);
    border-color: rgba(255,255,255,.08);
}
.pc-scene .pc-section-title { font-size: 16px; color: white; }
.pc-scene .pc-scene-letter {
    background: linear-gradient(135deg, var(--pc-cyan), var(--pc-teal));
    color: var(--pc-navy);
    border-radius: 8px;
    width: 30px; height: 30px;
    display: grid; place-items: center;
    font-size: 14px; font-weight: 800;
    font-family: var(--pc-mono);
}
.pc-scene-b .pc-scene-letter {
    background: linear-gradient(135deg, #a5b4fc, #818cf8);
    color: #1e1b4b;
}
.pc-scene .q-btn {
    color: rgba(255,255,255,.85) !important;
    border-radius: 8px;
    text-transform: none;
    font-size: 11px;
}
.pc-scene .text-slate-600 { color: rgba(148,203,220,.7); }
.pc-scene-caption {
    font-size: 11px;
    color: rgba(148,203,220,.6);
    border-top: 1px solid rgba(255,255,255,.08);
    padding-top: 12px;
    width: 100%;
}
.pc-scene-status { font-size: 11px; color: rgba(180,220,230,.8); }

/* ── Scene Grid ────────────────────────────────────────────────────── */
.pc-scenes {
    width: 100%;
    display: grid;
    grid-template-columns: minmax(0, 1fr);
    gap: 18px;
}
.pc-scenes.pc-comparing { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.pc-scenes.pc-comparing .pc-scene { padding: 16px; }
.pc-scenes.pc-comparing .pc-scene-heading { flex-direction: column; align-items: flex-start; }
.pc-scene .nicegui-interactive_image { width: 100%; }

/* ── View Switch ───────────────────────────────────────────────────── */
.pc-view-switch {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    flex-wrap: wrap;
    width: 100%;
}
.pc-view-switch-label {
    color: var(--pc-ink);
    font-size: 16px;
    font-weight: 700;
}
.pc-view-switch .q-btn-toggle {
    background: var(--pc-surface);
    border: 1px solid var(--pc-border);
    padding: 3px;
    border-radius: var(--pc-radius-sm);
}
.pc-view-switch .q-btn {
    min-width: 54px;
    border-radius: 8px;
    font-weight: 700;
}

/* ── 3D Viewport ───────────────────────────────────────────────────── */
.pc-3d-shell, .pc-2d-shell { min-width: 0; }
.pc-3d-viewport {
    position: relative;
    width: 100%;
    height: clamp(330px, 45vw, 470px);
    overflow: hidden;
    border-radius: 12px;
    background: #050d1a;
    box-shadow: inset 0 0 0 1px rgba(255,255,255,.06), 0 2px 12px rgba(0,0,0,.3);
}
.pc-three-canvas { width: 100% !important; height: 100% !important; cursor: grab; }
.pc-three-canvas:active { cursor: grabbing; }
.pc-3d-reset {
    position: absolute !important;
    z-index: 3;
    right: 10px; bottom: 11px;
    background: rgba(12,25,41,.85) !important;
    border: 1px solid rgba(255,255,255,.15) !important;
    backdrop-filter: blur(6px);
}
.pc-scene .pc-scene-heading .q-btn {
    color: rgba(255,255,255,.85) !important;
    background: rgba(255,255,255,.06) !important;
    border: 1px solid rgba(255,255,255,.12) !important;
    backdrop-filter: blur(4px);
}
.pc-3d-overlay-state {
    position: absolute; z-index: 3; top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    color: white;
    font-size: 14px; font-weight: 700;
    background: rgba(12,25,41,.92);
    border: 1px solid rgba(255,255,255,.1);
    border-radius: var(--pc-radius-sm);
    padding: 12px 16px;
    text-align: center;
    max-width: 80%;
    pointer-events: none;
    backdrop-filter: blur(8px);
}
.pc-3d-readout { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }
.pc-3d-readout > div {
    border: 1px solid rgba(255,255,255,.1);
    border-radius: 8px;
    padding: 7px 12px;
    color: var(--pc-cyan);
    background: rgba(12,25,41,.6);
    font-size: 12px; font-weight: 700;
    font-variant-numeric: tabular-nums;
    font-family: var(--pc-mono);
    backdrop-filter: blur(4px);
}

/* ── Timeline ──────────────────────────────────────────────────────── */
.pc-timeline {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
    gap: 4px 14px;
    width: 100%;
    margin-top: 12px;
    padding: 14px 18px;
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 12px;
    background: linear-gradient(110deg, rgba(12,25,41,.8), rgba(15,39,64,.8));
    box-shadow: inset 3px 0 var(--pc-cyan);
}
.pc-timeline-heading {
    grid-column: 1 / -1;
    font-size: 10px;
    letter-spacing: 2px;
    font-weight: 800;
    color: var(--pc-cyan);
    font-family: var(--pc-mono);
}
.pc-timeline-main {
    font-size: 16px; font-weight: 800; color: white;
    font-variant-numeric: tabular-nums;
    font-family: var(--pc-mono);
}
.pc-timeline-volume {
    font-size: 13px; font-weight: 700; color: rgba(200,245,241,.8);
    font-variant-numeric: tabular-nums;
    font-family: var(--pc-mono);
}
.pc-timeline-level {
    grid-column: 1 / -1;
    font-size: 12px; font-weight: 600;
    color: rgba(136,220,231,.8);
    font-variant-numeric: tabular-nums;
    font-family: var(--pc-mono);
}
.pc-timeline-note {
    grid-column: 1 / -1;
    font-size: 11px;
    color: rgba(148,203,220,.5);
}
.pc-3d-shell .pc-scene-caption, .pc-2d-shell .pc-scene-caption {
    display: block;
    margin-top: 12px;
}

/* ── Status Badge ──────────────────────────────────────────────────── */
.pc-status {
    align-self: flex-start;
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 12px; font-weight: 700;
    background: #ecfdf5;
    color: #065f46;
    letter-spacing: .2px;
}
.pc-status-pendiente { background: #fffbeb; color: #92400e; }
.pc-status-datos_invalidos, .pc-status-falta_convergencia { background: #fef2f2; color: #991b1b; }
.pc-status-sin_interseccion { background: #fff7ed; color: #9a3412; }

/* ── KPIs ──────────────────────────────────────────────────────────── */
.pc-kpis {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 180px), 1fr));
    gap: 12px;
    width: 100%;
}
.pc-kpi {
    border-radius: 12px;
    background: var(--pc-surface);
    padding: 18px 16px;
    min-width: 0;
    border: 1px solid var(--pc-border);
    transition: border-color .2s ease;
}
.pc-kpi:hover { border-color: var(--pc-teal); }
.pc-kpi-label {
    font-size: 11px;
    color: var(--pc-muted);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .3px;
}
.pc-kpi-value {
    font-size: clamp(17px, 1.8vw, 26px);
    letter-spacing: -0.5px;
    font-weight: 800;
    font-variant-numeric: tabular-nums;
    font-family: var(--pc-mono);
    white-space: nowrap;
    margin-top: 6px;
}
.pc-kpi-0 {
    background: linear-gradient(135deg, #ecfdf5, #d1fae5);
    border-color: #a7f3d0;
    color: #065f46;
}
.pc-kpi-0 .pc-kpi-label { color: #047857; }
.pc-kpi-1 {
    background: linear-gradient(135deg, #ecfeff, #cffafe);
    border-color: #a5f3fc;
    color: #155e75;
}
.pc-kpi-2 {
    background: linear-gradient(135deg, #eef2ff, #e0e7ff);
    border-color: #c7d2fe;
    color: #3730a3;
}

/* ── Metrics Grid ──────────────────────────────────────────────────── */
.pc-metrics {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    width: 100%;
    gap: 0 24px;
}
.pc-metric {
    padding: 14px 0;
    border-bottom: 1px solid var(--pc-border);
    gap: 4px;
}
.pc-metric-label {
    font-size: 11px;
    color: var(--pc-muted);
    font-weight: 500;
}
.pc-metric-value {
    font-size: 16px;
    font-weight: 700;
    font-variant-numeric: tabular-nums;
    font-family: var(--pc-mono);
}

/* ── Detail Expansion ──────────────────────────────────────────────── */
.pc-detail {
    border: 1px solid var(--pc-border);
    background: var(--pc-surface);
    border-radius: 12px;
    overflow: hidden;
}
.pc-detail .q-expansion-item__content {
    padding: 0 16px 16px;
    font-size: 13px;
    font-family: var(--pc-mono);
}
.pc-panel .q-table th {
    background: var(--pc-surface);
    font-size: 11px;
    color: var(--pc-muted);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .3px;
}
.pc-panel .q-table tbody td {
    font-size: 12px;
    font-family: var(--pc-mono);
}
.pc-panel .q-table__container { border-radius: var(--pc-radius-sm); }

/* ── Comparison ────────────────────────────────────────────────────── */
.pc-compare-delta {
    border-radius: 12px;
    padding: 16px 20px;
    background: linear-gradient(135deg, #eef2ff, #e0e7ff);
    color: #3730a3;
    width: 100%;
    border: 1px solid #c7d2fe;
}
.pc-compare-delta > div:first-child {
    font-size: 20px;
    font-weight: 800;
    font-family: var(--pc-mono);
}

/* ── Footer ────────────────────────────────────────────────────────── */
.pc-footer {
    width: 100%;
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    justify-content: space-between;
    border-top: 1px solid var(--pc-border);
    padding: 20px 4px;
    color: var(--pc-muted);
    font-size: 11px;
}
.pc-footer strong {
    color: var(--pc-ink);
    font-weight: 800;
}

/* ── Global Button Polish ──────────────────────────────────────────── */
.q-btn {
    transition: transform .16s ease, box-shadow .16s ease, background .16s ease;
}
.q-btn:not(.disabled):hover {
    transform: translateY(-1px);
}
:focus-visible {
    outline: 2px solid var(--pc-teal);
    outline-offset: 2px;
}

/* ═══════════════════════════════════════════════════════════════════════
   Responsive — mismos breakpoints originales
   ═══════════════════════════════════════════════════════════════════════ */
@media(min-width: 1500px) { .pc-main { padding-top: 32px; } }
@media(max-width: 1100px) {
    .pc-lab { grid-template-columns: 320px minmax(0, 1fr); gap: 16px; }
    .pc-panel { padding: 18px; }
    .pc-scenes.pc-comparing { grid-template-columns: minmax(0, 1fr); }
    .pc-scenes.pc-comparing .pc-scene-heading { flex-direction: row; align-items: center; }
    .pc-kpi-value { font-size: 18px; }
}
@media(max-width: 850px) {
    .pc-main { padding: 16px; gap: 16px; }
    .pc-lab { grid-template-columns: minmax(0, 1fr); }
    .pc-stage { grid-row: 1; }
    .pc-header-note { display: none; }
    .pc-example-note { margin-left: 0; }
    .pc-toolbar .q-toggle { margin-left: 0; }
    .pc-kpi-value { font-size: 23px; }
}
@media(max-width: 480px) {
    .pc-main { padding: 10px; }
    .pc-local { padding: 5px 8px; font-size: 10px; }
    .pc-kpis { grid-template-columns: minmax(0, 1fr); }
    .pc-kpi { padding: 12px 16px; }
    .pc-kpi-value { font-size: 27px; }
    .pc-scene-heading { flex-wrap: wrap; gap: 10px; }
    .pc-scenes.pc-comparing .pc-scene-heading { flex-direction: column; align-items: flex-start; }
    .pc-metrics { gap: 0 12px; }
    .pc-input-grid { grid-template-columns: minmax(0, 1fr); }
    .pc-example-row .q-field { width: 100%; }
    .pc-3d-viewport { height: 270px; }
    .pc-timeline { grid-template-columns: minmax(0, 1fr); }
    .pc-tank-card { grid-template-columns: minmax(0, 1fr); }
}
@media(prefers-reduced-motion: reduce) { .q-btn { transition: none; } .q-btn:hover { transform: none; } }
'''
