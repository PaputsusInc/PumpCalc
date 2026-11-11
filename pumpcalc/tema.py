"""Identidad visual del laboratorio; estilos locales sin recursos externos."""

from nicegui import ui


def aplicar_tema() -> None:
    ui.colors(primary='#087f8c', secondary='#633bd6', accent='#d5fa55', positive='#087f65',
              negative='#c12b46', warning='#a65b09')
    ui.add_css(ESTILOS)


ESTILOS = '''
:root {
    --pc-ink: #102c40; --pc-muted: #526b7c; --pc-aqua: #55e7df;
    --pc-navy: #082b3a; --pc-lime: #d5fa55; --pc-line: #dce7ed;
}
body { background: #eef4f7; color: var(--pc-ink);
    font-family: 'Segoe UI Variable', 'Segoe UI', sans-serif; }
.nicegui-content { padding: 0; gap: 0; }
.pc-header { background: var(--pc-navy); color: white; box-shadow: none;
    padding: 14px max(24px, calc((100vw - 1500px)/2)); border-bottom: 1px solid #244653; }
.pc-brand { font-size: 25px; font-weight: 800; letter-spacing: -1px; }
.pc-logo { color: var(--pc-navy); background: var(--pc-aqua); padding: 8px;
    border-radius: 12px 12px 12px 3px; }
.pc-header-note { color: #bbd2dc; font-size: 12px; letter-spacing: 1.5px; text-transform: uppercase; }
.pc-local { margin-left: auto; border: 1px solid #3c616b; border-radius: 100px;
    padding: 6px 12px; font-size: 12px; color: #d7f4f3; gap: 7px; align-items: center; }
.pc-local .q-icon { color: var(--pc-lime); font-size: 10px; }
.pc-main { width: 100%; max-width: 1500px; margin: auto; padding: 26px 24px 20px; gap: 22px; }
.pc-hero { position: relative; overflow: hidden; width: 100%; border-radius: 26px;
    background: var(--pc-navy); color: white; padding: 36px 40px;
    display: grid; grid-template-columns: 1.45fr 1fr; gap: 24px; align-items: center; }
.pc-eyebrow { font-size: 11px; font-weight: 800; letter-spacing: 2px; text-transform: uppercase; }
.pc-hero .pc-eyebrow { color: var(--pc-aqua); }
.pc-hero h1 { margin: 12px 0 14px; font-size: clamp(36px, 4.4vw, 64px);
    line-height: 1.02; letter-spacing: -2.7px; font-weight: 800; }
.pc-hero h1 span { color: var(--pc-aqua); }
.pc-hero-copy { font-size: 15px; line-height: 1.6; color: #c0d8e0; max-width: 500px; }
.pc-hero-art { position: relative; min-height: 190px; display: flex; align-items: center;
    justify-content: center; gap: 18px; border-left: 1px solid #31505b; }
.pc-orbit { position: absolute; width: 180px; height: 180px; border: 1px solid #355662;
    border-radius: 50%; right: 30px; top: 5px; }
.pc-orbit:after { content: ''; position: absolute; inset: 22px; border: 1px dashed #355662; border-radius: 50%; }
.pc-hero-water { color: var(--pc-aqua); z-index: 1; transform: rotate(-12deg); }
.pc-hero-equation { position: relative; z-index: 1; background: var(--pc-lime); color: var(--pc-navy);
    border-radius: 15px; padding: 18px 22px; transform: rotate(-5deg); box-shadow: 0 12px 0 #051e2b55; }
.pc-hero-equation strong { font-size: 35px; letter-spacing: -1.5px; font-weight: 800; }
.pc-hero-equation small { display: block; font-size: 11px; font-weight: 650; margin-top: 3px; }
.pc-methods { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 22px; }
.pc-methods > div { padding: 5px 10px; border-radius: 6px; background: #193e4c; color: #d3e9ec;
    font-size: 11px; font-weight: 600; }
.pc-panel { border: 1px solid var(--pc-line); border-radius: 20px; box-shadow: 0 5px 20px #17364a05;
    background: white; padding: 24px; gap: 16px; min-width: 0; }
.pc-toolbar { padding: 16px 20px; gap: 14px; }
.pc-toolbar-main { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; width: 100%; }
.pc-toolbar .q-toggle { margin-left: auto; font-size: 13px; font-weight: 650; }
.pc-toolbar .q-btn-toggle { border: 1px solid var(--pc-line); border-radius: 12px; box-shadow: none; }
.pc-toolbar .q-btn-toggle .q-btn { min-width: 45px; }
.pc-action { background: var(--pc-lime) !important; color: var(--pc-navy) !important;
    box-shadow: 0 4px 0 #a3c42c; font-weight: 800; padding-left: 22px; padding-right: 22px; }
.pc-example-row { width: 100%; border-top: 1px solid var(--pc-line); padding-top: 12px;
    display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
.pc-example-row .q-field { width: 220px; }
.pc-example-note { margin-left: auto; color: var(--pc-muted); font-size: 12px; }
.pc-lab { display: grid; grid-template-columns: minmax(340px, 390px) minmax(0, 1fr);
    gap: 22px; width: 100%; align-items: start; }
.pc-config, .pc-stage { display: flex; flex-direction: column; gap: 22px; min-width: 0; width: 100%; }
.pc-section-head { width: 100%; display: flex; align-items: center; gap: 11px; }
.pc-section-icon { background: #e3f6f5; color: #087f8c; padding: 9px; border-radius: 11px; }
.pc-section-title { font-size: 19px; font-weight: 750; letter-spacing: -.4px; }
.pc-section-subtitle { font-size: 12px; color: var(--pc-muted); margin-top: 2px; }
.pc-panel .text-slate-600 { color: var(--pc-muted); }
.pc-panel .q-field--outlined .q-field__control { border-radius: 10px; background: #f8fbfc; }
.pc-panel .q-field--outlined .q-field__control:before { border-color: #c5d8e2; }
.pc-panel .q-field__label { color: #4c6678; }
.pc-panel .q-field__native { color: var(--pc-ink); font-variant-numeric: tabular-nums; }
.pc-panel .q-btn { border-radius: 10px; text-transform: none; font-weight: 650; letter-spacing: 0; }
.pc-input-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; width: 100%; }
.pc-input-grid > :last-child { grid-column: 1 / -1; }
.pc-pump-table { width: 100%; table-layout: fixed; border-collapse: collapse; }
.pc-pump-table th { font-size: 11px; padding: 0 4px 10px; color: var(--pc-muted); font-weight: 650; }
.pc-pump-table th:first-child { width: 30px; }
.pc-pump-table th:last-child { width: 36px; }
.pc-pump-table td { padding: 4px; vertical-align: top; }
.pc-pump-table td:first-child { font-size: 12px; color: #688295; }
.pc-pump-table .q-field__label { font-size: 11px; }
.pc-pump-table .q-field__native { font-size: 13px; }
.pc-pump-table .q-btn { min-width: 28px; min-height: 32px; font-size: 11px; }
.pc-target { border-top: 4px solid #633bd6; }
.pc-meta-grid { width: 100%; display: grid; gap: 10px; }
.pc-meta { border-left: 3px solid #087f8c; background: #f2f9fa; border-radius: 0 10px 10px 0;
    padding: 10px 12px; font-size: 12px; font-weight: 650; }
.pc-meta-b { border-left-color: #633bd6; background: #f5f2fd; }
.pc-meta small { display: block; font-size: 11px; font-weight: 400; margin-top: 3px; color: var(--pc-muted); }
.pc-scene { background: #082b3a; border-color: #244c5a; color: #e2f5f5; padding: 22px; overflow: hidden; }
.pc-scene-b { background: #202544; border-color: #393b65; }
.pc-scene .pc-section-title { font-size: 16px; }
.pc-scene .pc-scene-letter { background: var(--pc-aqua); color: #082b3a; border-radius: 8px;
    width: 30px; height: 30px; display: grid; place-items: center; font-size: 14px; font-weight: 850; }
.pc-scene-b .pc-scene-letter { background: #c8b8ff; color: #202544; }
.pc-scene .q-btn { color: #ddf5f3 !important; border-radius: 8px; text-transform: none; font-size: 11px; }
.pc-scene .text-slate-600 { color: #b1ced6; }
.pc-scene-caption { font-size: 11px; color: #a5c5ce; border-top: 1px solid #315260; padding-top: 12px; width: 100%; }
.pc-scene-status { font-size: 11px; color: #b9d9dc; }
.pc-scenes { width: 100%; display: grid; grid-template-columns: minmax(0, 1fr); gap: 18px; }
.pc-scenes.pc-comparing { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.pc-scenes.pc-comparing .pc-scene { padding: 16px; }
.pc-scenes.pc-comparing .pc-scene-heading { flex-direction: column; align-items: flex-start; }
.pc-scene .nicegui-interactive_image { width: 100%; }
.pc-status { align-self: flex-start; border-radius: 7px; padding: 5px 10px;
    font-size: 12px; font-weight: 700; background: #e1f6ed; color: #146347; }
.pc-status-pendiente { background: #fff2d6; color: #875500; }
.pc-status-datos_invalidos, .pc-status-falta_convergencia { background: #ffe9ed; color: #a52540; }
.pc-status-sin_interseccion { background: #fff0de; color: #95540f; }
.pc-kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 170px), 1fr));
    gap: 12px; width: 100%; }
.pc-kpi { border-radius: 14px; background: #f0f7f9; padding: 17px 15px; min-width: 0; }
.pc-kpi-label { font-size: 11px; color: #456375; font-weight: 600; }
.pc-kpi-value { font-size: clamp(17px, 1.8vw, 27px); letter-spacing: -1px;
    font-weight: 800; font-variant-numeric: tabular-nums; white-space: nowrap; margin-top: 5px; }
.pc-kpi-0 { background: #d5fa55; color: #163711; }
.pc-kpi-0 .pc-kpi-label { color: #375429; }
.pc-kpi-1 { background: #dff8f6; color: #075b62; }
.pc-kpi-2 { background: #eee8ff; color: #52319c; }
.pc-metrics { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); width: 100%; gap: 0 22px; }
.pc-metric { padding: 12px 0; border-bottom: 1px solid #e9eff3; gap: 3px; }
.pc-metric-label { font-size: 11px; color: var(--pc-muted); }
.pc-metric-value { font-size: 16px; font-weight: 700; font-variant-numeric: tabular-nums; }
.pc-detail { border: 1px solid var(--pc-line); background: #f8fbfc; border-radius: 12px; overflow: hidden; }
.pc-detail .q-expansion-item__content { padding: 0 16px 16px; font-size: 13px; }
.pc-panel .q-table th { background: #f0f6f9; font-size: 11px; color: #476578; font-weight: 700; }
.pc-panel .q-table tbody td { font-size: 12px; }
.pc-panel .q-table__container { border-radius: 10px; }
.pc-compare-delta { border-radius: 12px; padding: 14px 18px; background: #eee8ff; color: #4f3197; width: 100%; }
.pc-compare-delta > div:first-child { font-size: 20px; font-weight: 800; }
.pc-footer { width: 100%; display: flex; flex-wrap: wrap; gap: 12px; justify-content: space-between;
    border-top: 1px solid #d4e1e8; padding: 18px 4px; color: #526b7c; font-size: 11px; }
.pc-footer strong { color: var(--pc-ink); font-weight: 800; }
.q-btn { transition: transform .16s ease, box-shadow .16s ease; }
.q-btn:not(.disabled):hover { transform: translateY(-1px); }
:focus-visible { outline: 3px solid #633bd6; outline-offset: 3px; }
@media(min-width: 1500px) { .pc-main { padding-top: 30px; } }
@media(max-width: 1100px) {
    .pc-lab { grid-template-columns: 320px minmax(0, 1fr); gap: 16px; }
    .pc-panel { padding: 18px; }
    .pc-scenes.pc-comparing { grid-template-columns: minmax(0, 1fr); }
    .pc-scenes.pc-comparing .pc-scene-heading { flex-direction: row; align-items: center; }
    .pc-kpi-value { font-size: 18px; }
}
@media(max-width: 850px) {
    .pc-main { padding: 16px; gap: 16px; }
    .pc-hero { padding: 28px; grid-template-columns: 1fr; }
    .pc-hero-art { display: none; }
    .pc-lab { grid-template-columns: minmax(0, 1fr); }
    .pc-stage { grid-row: 1; }
    .pc-header-note { display: none; }
    .pc-example-note { margin-left: 0; }
    .pc-toolbar .q-toggle { margin-left: 0; }
    .pc-kpi-value { font-size: 23px; }
}
@media(max-width: 480px) {
    .pc-main { padding: 10px; }
    .pc-hero { padding: 24px; border-radius: 20px; }
    .pc-hero h1 { font-size: 39px; letter-spacing: -1.8px; }
    .pc-local { padding: 5px 8px; font-size: 10px; }
    .pc-kpis { grid-template-columns: minmax(0, 1fr); }
    .pc-kpi { padding: 12px 16px; }
    .pc-kpi-value { font-size: 27px; }
    .pc-scene-heading { flex-wrap: wrap; gap: 10px; }
    .pc-scenes.pc-comparing .pc-scene-heading { flex-direction: column; align-items: flex-start; }
    .pc-metrics { gap: 0 12px; }
    .pc-input-grid { grid-template-columns: minmax(0, 1fr); }
    .pc-example-row .q-field { width: 100%; }
}
@media(prefers-reduced-motion: reduce) { .q-btn { transition: none; } .q-btn:hover { transform: none; } }
'''
