/* Calendario de quemas — lógica de la aplicación (sin dependencias externas). */
(() => {
'use strict';
const I = window.I18N;
const $ = (s, r = document) => r.querySelector(s);
const SVGNS = 'http://www.w3.org/2000/svg';
const FONT = '"Atkinson Hyperlegible Next","Atkinson Hyperlegible",system-ui,-apple-system,"Segoe UI",sans-serif';
const D0 = Date.UTC(2000, 10, 1);
const DAY = 864e5;
const NCX = 140, NCY = 90;         // malla de celdas de 0.25° (índices de celda)
const MAX_ROWS = 600000;

/* ---------- idioma ---------- */
let LANG = 'es';
try { const sv = localStorage.getItem('qm_lang'); if (sv === 'en' || sv === 'es') LANG = sv; } catch (e) {}
const tr = (k, ...a) => { let s = I[LANG][k]; if (s === undefined) s = I.es[k]; if (s === undefined) return k; a.forEach((v, i) => { s = s.split('{' + i + '}').join(v); }); return s; };
let nf = null;
const setLocale = () => { nf = new Intl.NumberFormat(LANG === 'es' ? 'es-MX' : 'en-US', { maximumFractionDigits: 0 }); };
const fmt = v => (isFinite(v) ? nf.format(Math.round(v)) : '—');
const fmtK = v => (v >= 10000 ? (Math.round(v / 100) / 10).toString().replace(/\.0$/, '') + 'K' : nf.format(Math.round(v * 100) / 100));
const pct = (v, d = 1) => (v * 100).toFixed(d) + (LANG === 'es' ? ' %' : '%');
const mon = () => I[LANG].mon, monthsL = () => I[LANG].months;

/* ---------- estado ---------- */
const S = { region: { type: 'all', state: -1, rect: null }, from: 0, to: 0, metric: 'harm', anom: false, refYear: 2025, mapMode: 'state', layer: 'dens', mapLog: false, tableView: false, showRaw: false, tab: 'explore' };
let M = null, VAL = null, F = null;
let nd = 0, nU = 0, aqua0 = 0, viirs0 = 0;
let ust, ucx, ucy, ucell, kV, kT, dYear, dMon, dYm, dStr, ymStart, ymLen, fragStart;
let mask = null, DL = null, cum = null, A = null;
let mapCache = null, ptsCache = new Map();

/* ---------- utilidades DOM ---------- */
function el(tag, attrs, parent) { const e = document.createElementNS(SVGNS, tag); if (attrs) for (const k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; }
function txt(parent, s, attrs) { const t = el('text', attrs, parent); t.textContent = s; return t; }
function h(tag, cls, text, parent) { const e = document.createElement(tag); if (cls) e.className = cls; if (text !== undefined && text !== null) e.textContent = text; if (parent) parent.appendChild(e); return e; }
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
function niceScale(v) { if (!(v > 0)) return { max: 1, step: 0.25 }; const raw = v / 4, p = Math.pow(10, Math.floor(Math.log10(raw))), f = raw / p, s = (f <= 1 ? 1 : f <= 2 ? 2 : f <= 2.5 ? 2.5 : f <= 5 ? 5 : 10) * p; return { max: Math.ceil(v / s - 1e-9) * s, step: s }; }
function quant(a, p) { const i = (a.length - 1) * p, lo = Math.floor(i), hi = Math.ceil(i); return a[lo] + (a[hi] - a[lo]) * (i - lo); }
function stats(vals) { const a = vals.slice().sort((x, y) => x - y); if (!a.length) return { n: 0 }; return { n: a.length, min: a[0], q1: quant(a, .25), med: quant(a, .5), q3: quant(a, .75), max: a[a.length - 1] }; }
const dispDate = d => { const dt = new Date(D0 + d * DAY); return dt.getUTCDate() + ' ' + mon()[dt.getUTCMonth()] + ' ' + dt.getUTCFullYear(); };
const dayOfISO = s => Math.round((Date.parse(s) - D0) / DAY);
const isoOf = d => new Date(D0 + d * DAY).toISOString().slice(0, 10);
const ymOfDay = d => dYm[d];

/* ---------- tema y color ---------- */
function oklch(L, C, hue) {
  const a = C * Math.cos(hue * Math.PI / 180), b = C * Math.sin(hue * Math.PI / 180);
  const l_ = L + 0.3963377774 * a + 0.2158037573 * b, m_ = L - 0.1055613458 * a - 0.0638541728 * b, s_ = L - 0.0894841775 * a - 1.2914855480 * b;
  const l = l_ ** 3, m = m_ ** 3, s = s_ ** 3;
  const r = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s, g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s, bl = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s;
  const f = x => { x = clamp(x, 0, 1); return Math.round(255 * (x <= 0.0031308 ? 12.92 * x : 1.055 * Math.pow(x, 1 / 2.4) - 0.055)); };
  return 'rgb(' + f(r) + ',' + f(g) + ',' + f(bl) + ')';
}
let themeKey = '', themeObj = null;
function theme() {
  const root = document.documentElement, dt = root.getAttribute('data-theme');
  const dark = dt === 'dark' || (dt !== 'light' && window.matchMedia('(prefers-color-scheme: dark)').matches);
  const cs = getComputedStyle(root); const g = n => cs.getPropertyValue(n).trim();
  const key = (dark ? 'd' : 'l') + g('--surface');
  if (themeObj && key === themeKey) return themeObj;
  const ramp = [], N = 256;
  for (let i = 0; i < N; i++) {
    const t = i / (N - 1); let L, C, hu;
    if (!dark) { L = 0.97 - 0.66 * t; C = t < 0.45 ? 0.02 + 0.17 * (t / 0.45) : 0.19 - 0.09 * ((t - 0.45) / 0.55); hu = 85 - 57 * t; }
    else { L = 0.27 + 0.61 * t; C = t < 0.5 ? 0.03 + 0.15 * (t / 0.5) : 0.18 - 0.06 * ((t - 0.5) / 0.5); hu = 28 + 62 * t; }
    ramp.push(oklch(L, C, hu));
  }
  const div = s => { const a = Math.abs(s); if (s >= 0) return oklch(dark ? 0.31 + 0.41 * a : 0.95 - 0.40 * a, (dark ? 0.15 : 0.20) * a, 28); return oklch(dark ? 0.31 + 0.41 * a : 0.95 - 0.43 * a, (dark ? 0.14 : 0.17) * a, 255); };
  themeObj = { dark, surface: g('--surface'), surface2: g('--surface2'), ink: g('--ink'), ink2: g('--ink2'), muted: g('--muted'), line: g('--line'), grid: g('--grid'), axis: dark ? '#383d41' : '#c3cbd0', accent: g('--accent'), ref: g('--ref'), s1: g('--series1'), s2: g('--series2'), neutral: g('--neutral-series'), ramp, div, neutralCell: dark ? '#383d41' : '#e3e6e8' };
  themeKey = key; return themeObj;
}
const rampAt = (T, v, vmax) => T.ramp[Math.round(clamp(vmax > 0 ? Math.sqrt(Math.max(0, v) / vmax) : 0, 0, 1) * 255)];

/* ---------- carga ---------- */
async function fetchBin(url) {
  const r = await fetch(url); if (!r.ok) throw new Error(url + ' ' + r.status);
  let buf = await r.arrayBuffer(); let u8 = new Uint8Array(buf);
  if (!(u8[0] === 0x1f && u8[1] === 0x8b)) { // los datos se publican como texto base64 de un gzip
    const bin = atob(new TextDecoder().decode(u8).trim()); u8 = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) u8[i] = bin.charCodeAt(i); buf = u8.buffer;
  }
  if (u8[0] === 0x1f && u8[1] === 0x8b) buf = await new Response(new Blob([buf]).stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer();
  return buf;
}
async function fetchJSON(url) { const r = await fetch(url); if (!r.ok) throw new Error(url + ' ' + r.status); return r.json(); }
function parseFrag(buf) {
  const n = new DataView(buf).getUint32(0, true); let o = 4; const mk = () => { const a = new Uint16Array(buf, o, n); o += 2 * n; return a; };
  return { n, d: mk(), u: mk(), T: mk(), A: mk(), S: mk() };
}
function parsePts(buf) {
  const n = new DataView(buf).getUint32(0, true); let o = 4;
  const d = new Uint16Array(buf, o, n); o += 2 * n; const u = new Uint16Array(buf, o, n); o += 2 * n;
  const dy = new Uint8Array(buf, o, n); o += n; const dx = new Uint8Array(buf, o, n); o += n;
  const frp = new Uint16Array(buf, o, n); o += 2 * n; const tm = new Uint16Array(buf, o, n); o += 2 * n; const fl = new Uint8Array(buf, o, n);
  return { n, d, u, dy, dx, frp, tm, fl };
}
function prepare() {
  nd = M.ndays; aqua0 = M.aqua0; viirs0 = M.viirs0; nU = M.units.st.length;
  ust = Uint8Array.from(M.units.st); ucx = Int16Array.from(M.units.cx); ucy = Int16Array.from(M.units.cy);
  ucell = new Int32Array(nU); for (let u = 0; u < nU; u++) ucell[u] = (ucx[u] >= 0 && ucx[u] < NCX && ucy[u] >= 0 && ucy[u] < NCY) ? ucy[u] * NCX + ucx[u] : -1; // algunas celdas (Isla Guadalupe) caen al oeste de la malla del mapa
  kV = new Float32Array(384); kT = new Float32Array(384);
  for (let m = 0; m < 12; m++) for (let s = 0; s < 32; s++) { kV[m * 32 + s] = M.kV[m][s]; kT[m * 32 + s] = M.kT[m][s]; }
  dYear = new Uint16Array(nd); dMon = new Uint8Array(nd); dYm = new Uint16Array(nd); dStr = new Array(nd);
  for (let d = 0; d < nd; d++) { const dt = new Date(D0 + d * DAY); dYear[d] = dt.getUTCFullYear(); dMon[d] = dt.getUTCMonth(); dYm[d] = (dYear[d] - 2000) * 12 + dMon[d]; dStr[d] = dt.toISOString().slice(0, 10); }
  ymStart = new Int32Array(312); ymLen = new Uint8Array(312);
  for (let ym = 0; ym < 312; ym++) { const y = 2000 + Math.floor(ym / 12), m = ym % 12; ymStart[ym] = Math.round((Date.UTC(y, m, 1) - D0) / DAY); ymLen[ym] = new Date(Date.UTC(y, m + 1, 0)).getUTCDate(); }
  fragStart = new Int32Array(nd + 2); let p = 0;
  for (let d = 0; d <= nd; d++) { while (p < F.n && F.d[p] < d) p++; fragStart[d] = p; }
  fragStart[nd + 1] = F.n;
}

/* ---------- región y cálculo diario ---------- */
function buildMask() {
  const m = new Uint8Array(nU), r = S.region;
  if (r.type === 'all') m.fill(1);
  else if (r.type === 'state') { for (let u = 0; u < nU; u++) m[u] = ust[u] === r.state ? 1 : 0; }
  else { const q = r.rect; for (let u = 0; u < nU; u++) m[u] = (ucx[u] >= q.x0 && ucx[u] <= q.x1 && ucy[u] >= q.y0 && ucy[u] <= q.y1) ? 1 : 0; }
  return m;
}
function computeRegion() {
  mask = buildMask();
  const Hd = new Float64Array(nd), Td = new Float64Array(nd), Ad = new Float64Array(nd), Sd = new Float64Array(nd);
  const fd = F.d, fu = F.u, fT = F.T, fA = F.A, fS = F.S;
  for (let i = 0; i < F.n; i++) {
    const u = fu[i]; if (!mask[u]) continue;
    const d = fd[i], a = fT[i], b = fA[i], c = fS[i]; Td[d] += a; Ad[d] += b; Sd[d] += c;
    const k = dMon[d] * 32 + ust[u];
    Hd[d] += d < aqua0 ? a * kT[k] : (d < viirs0 ? a + b : c * kV[k]);
  }
  DL = { H: Hd, T: Td, A: Ad, S: Sd };
  const mk = f => { const c = new Float64Array(nd + 1); for (let d = 0; d < nd; d++) c[d + 1] = c[d] + f(d); return c; };
  cum = { H: mk(d => Hd[d]), M: mk(d => d >= aqua0 ? Td[d] + Ad[d] : 0), V: mk(d => d >= viirs0 ? Sd[d] : 0), T: mk(d => Td[d]), A: mk(d => Ad[d]), S: mk(d => Sd[d]) };
}
const metricStart = () => (S.metric === 'harm' ? 0 : S.metric === 'modis' ? aqua0 : viirs0);
const cumSel = () => (S.metric === 'harm' ? cum.H : S.metric === 'modis' ? cum.M : cum.V);
function dayVal(d) { if (S.metric === 'harm') return DL.H[d]; if (S.metric === 'modis') return d >= aqua0 ? DL.T[d] + DL.A[d] : NaN; return d >= viirs0 ? DL.S[d] : NaN; }
function monthInfo(ym) {
  const st = ymStart[ym], len = ymLen[ym], a = Math.max(S.from, st, 0), b = Math.min(S.to, st + len - 1);
  const covered = Math.max(0, b - a + 1), valid = ym >= 10 && st >= metricStart();
  const c = cumSel();
  return { ym, st, len, covered, valid, inRange: covered > 0, full: covered === len, val: covered > 0 && valid ? c[b + 1] - c[a] : NaN, a, b };
}
function monthFull(ym) { // total del mes completo sin importar el rango; NaN si no hay datos
  if (ym < 10 || ymStart[ym] < metricStart()) return NaN;
  const st = ymStart[ym], e = Math.min(st + ymLen[ym], nd); if (st + ymLen[ym] > nd) return NaN;
  const c = cumSel(); return c[e] - c[st];
}
function rawSum(c, a, b) { return c[b + 1] - c[a]; }

function analyze() {
  const y0 = dYear[S.from], y1 = dYear[S.to], rows = [];
  for (let y = y0; y <= y1; y++) { const cells = []; for (let m = 0; m < 12; m++) cells.push(monthInfo((y - 2000) * 12 + m)); rows.push({ year: y, cells }); }
  rows.forEach(r => {
    let tot = 0, any = false, complete = true;
    r.cells.forEach(c => { if (c.inRange && c.valid) { tot += c.val; any = true; if (!c.full) complete = false; } else complete = false; });
    r.total = any ? tot : NaN; r.complete = complete && any;
  });
  const climo = [], climoEx = [];
  for (let m = 0; m < 12; m++) {
    const vals = [];
    rows.forEach(r => { const c = r.cells[m]; if (c.valid && c.full) vals.push({ y: r.year, v: c.val }); });
    climo.push(Object.assign(stats(vals.map(x => x.v)), { vals }));
    climoEx.push(stats(vals.filter(x => x.y !== S.refYear).map(x => x.v)));
  }
  A = { y0, y1, rows, climo, climoEx };
}

/* ---------- gráficos genéricos ---------- */
const tip = $('#tip');
function showTip(e, title, rows) {
  tip.replaceChildren(); h('div', 'tt', title, tip);
  rows.forEach(r => { const row = h('div', 'tr', null, tip); if (r.c) { const i = h('i', null, null, row); i.style.background = r.c; } h('b', null, r.v, row); if (r.l) h('span', null, r.l, row); });
  tip.style.display = 'block'; moveTip(e);
}
function moveTip(e) {
  const pad = 14, r = tip.getBoundingClientRect(); let x = e.clientX + pad, y = e.clientY + pad;
  if (x + r.width > innerWidth - 8) x = e.clientX - r.width - pad; if (y + r.height > innerHeight - 8) y = e.clientY - r.height - pad;
  tip.style.left = Math.max(8, x) + 'px'; tip.style.top = Math.max(8, y) + 'px';
}
const hideTip = () => { tip.style.display = 'none'; };
function legend(host, items) {
  host.replaceChildren();
  items.forEach(it => { const s = h('span', 'lgd-sw', null, host); const i = h('i', it.box ? 'box' : null, null, s); i.style.background = it.color; if (it.opacity) i.style.opacity = it.opacity; s.appendChild(document.createTextNode(it.label)); });
}
function rampLegend(host, vmax, unit, anom, labels) {
  host.replaceChildren(); const T = theme();
  const wrap = h('div', null, null, host); wrap.style.cssText = 'display:flex;flex-direction:column;gap:2px';
  const c = h('canvas', null, null, wrap); c.width = 200; c.height = 10; c.style.width = '200px'; c.style.height = '10px';
  const ctx = c.getContext('2d');
  for (let x = 0; x < 200; x++) { ctx.fillStyle = anom ? T.div(-1 + 2 * x / 199) : T.ramp[Math.round(255 * x / 199)]; ctx.fillRect(x, 0, 1, 10); }
  const lab = h('div', null, null, wrap); lab.style.cssText = 'display:flex;justify-content:space-between;width:200px;font-size:12px;color:var(--muted)';
  (labels || (anom ? ['¼×', '½×', '1×', '2×', '4×'] : [0, vmax * 0.25, vmax].map(fmtK))).forEach(s => h('span', null, s, lab));
  h('span', null, unit, host);
}

function lineChart(host, o) {
  host.replaceChildren(); const T = theme();
  const W = Math.max(280, host.clientWidth), H = o.height || 270, n = o.n;
  const mL = 50, mR = 14, mT = o.bands && o.bands.length ? 26 : 12, mB = 28, iw = W - mL - mR, ih = H - mT - mB;
  let ymax = 0; o.series.forEach(s => s.vals.forEach(v => { if (isFinite(v) && v > ymax) ymax = v; })); (o.areas || []).forEach(a => a.hi.forEach(v => { if (isFinite(v) && v > ymax) ymax = v; }));
  const sc = niceScale(ymax || 1); ymax = sc.max;
  const step = n > 1 ? iw / (n - 1) : iw, x = i => mL + (n > 1 ? step * i : iw / 2), y = v => mT + ih * (1 - v / ymax);
  const nf2 = new Intl.NumberFormat(LANG === 'es' ? 'es-MX' : 'en-US', { maximumFractionDigits: 2 }); const yf = o.yfmt || (v => (v >= 10000 ? nf2.format(Math.round(v / 100) / 10) + 'K' : nf2.format(v)));
  const svg = el('svg', { width: W, height: H, viewBox: '0 0 ' + W + ' ' + H, role: 'img', 'aria-label': o.aria, 'font-family': FONT }, host);
  (o.bands || []).forEach(b => {
    const x0 = clamp(x(b.a) - step / 2, mL, W - mR), x1 = clamp(x(b.b) + step / 2, mL, W - mR);
    if (x1 > x0) { const r = el('rect', { x: x0, y: mT, width: x1 - x0, height: ih, fill: b.fill }, svg); r.setAttribute('opacity', b.opacity || 1); if (b.label && x1 - x0 > 60) txt(svg, b.label, { x: (x0 + x1) / 2, y: mT - 8, 'text-anchor': 'middle', 'font-size': 11.5, fill: T.muted }); }
  });
  for (let v = 0; v <= ymax + sc.step * 1e-6; v += sc.step) { const k = v === 0 ? 0 : 1, yy = y(v); el('line', { x1: mL, x2: W - mR, y1: yy, y2: yy, stroke: k === 0 ? T.axis : T.grid, 'stroke-width': 1 }, svg); txt(svg, yf(v), { x: mL - 8, y: yy + 4, 'text-anchor': 'end', 'font-size': 12, fill: T.muted }); }
  const seg = (vals, f) => { const out = []; let cur = []; for (let i = 0; i < n; i++) { if (isFinite(vals[i])) cur.push(i); else if (cur.length) { out.push(cur); cur = []; } } if (cur.length) out.push(cur); return out; };
  (o.areas || []).forEach(a => {
    const both = a.hi.map((v, i) => (isFinite(v) && isFinite(a.lo[i]) ? 1 : NaN));
    seg(both).forEach(ix => { if (ix.length < 2) return; let d = 'M' + x(ix[0]) + ',' + y(a.hi[ix[0]]); ix.slice(1).forEach(i => { d += 'L' + x(i) + ',' + y(a.hi[i]); }); for (let q = ix.length - 1; q >= 0; q--) d += 'L' + x(ix[q]) + ',' + y(a.lo[ix[q]]); el('path', { d: d + 'Z', fill: a.color, 'fill-opacity': a.opacity }, svg); });
  });
  o.series.forEach(s => {
    seg(s.vals).forEach(ix => {
      if (ix.length > 1) { let d = 'M' + x(ix[0]) + ',' + y(s.vals[ix[0]]); ix.slice(1).forEach(i => { d += 'L' + x(i) + ',' + y(s.vals[i]); }); el('path', { d, fill: 'none', stroke: s.color, 'stroke-width': s.width || 2, 'stroke-linejoin': 'round', 'stroke-linecap': 'round', opacity: s.opacity || 1 }, svg); }
    });
    if (s.markers) for (let i = 0; i < n; i++) if (isFinite(s.vals[i])) el('circle', { cx: x(i), cy: y(s.vals[i]), r: 4, fill: s.color, stroke: T.surface, 'stroke-width': 2 }, svg);
  });
  let tks = o.xticks || []; if (tks.length > 1) { const sp = Math.abs(x(tks[1].i) - x(tks[0].i)), wd = Math.max(...tks.map(t => t.label.length)) * 6.8 + 10, nth = Math.max(1, Math.ceil(wd / Math.max(1, sp))); if (nth > 1) tks = tks.filter((t, q) => q % nth === 0); }
  tks.forEach(tk => { el('line', { x1: x(tk.i), x2: x(tk.i), y1: mT + ih, y2: mT + ih + 4, stroke: T.axis }, svg); txt(svg, tk.label, { x: x(tk.i), y: H - 8, 'text-anchor': 'middle', 'font-size': 12, fill: T.muted }); });
  const cross = el('line', { y1: mT, y2: mT + ih, stroke: T.muted, 'stroke-width': 1, visibility: 'hidden' }, svg);
  const dots = o.series.map(s => el('circle', { r: 4, fill: s.color, stroke: T.surface, 'stroke-width': 2, visibility: 'hidden' }, svg));
  const ov = el('rect', { x: mL, y: mT, width: iw, height: ih, fill: 'transparent' }, svg);
  const move = e => {
    const r = svg.getBoundingClientRect(); let i = n > 1 ? Math.round((e.clientX - r.left - mL) / step) : 0; i = clamp(i, 0, n - 1);
    cross.setAttribute('x1', x(i)); cross.setAttribute('x2', x(i)); cross.setAttribute('visibility', 'visible');
    o.series.forEach((s, k) => { if (isFinite(s.vals[i])) { dots[k].setAttribute('cx', x(i)); dots[k].setAttribute('cy', y(s.vals[i])); dots[k].setAttribute('visibility', 'visible'); } else dots[k].setAttribute('visibility', 'hidden'); });
    const t = o.tip(i); showTip(e, t.title, t.rows);
  };
  ov.addEventListener('pointermove', move);
  ov.addEventListener('pointerleave', () => { cross.setAttribute('visibility', 'hidden'); dots.forEach(d => d.setAttribute('visibility', 'hidden')); hideTip(); });
  return svg;
}
function yearTicks(ymList, pxPerMonth) { // ymList: índices de mes consecutivos
  const stepY = Math.max(1, Math.ceil(48 / (pxPerMonth * 12))), out = [], first = Math.floor(ymList[0] / 12);
  ymList.forEach((ym, i) => { if (ym % 12 === 0 && (Math.floor(ym / 12) - first) % stepY === 0) out.push({ i, label: String(2000 + Math.floor(ym / 12)) }); });
  return out;
}

/* ---------- calendario año × mes ---------- */
function drawCalendar(host, W, png) {
  host.replaceChildren(); const T = theme(), rows = A.rows;
  const small = W < 560 && !png, mL = small ? 38 : 48, mR = small ? 0 : Math.min(180, Math.round(W * 0.2)), top = png ? 62 : 0, mT = 24 + top;
  const gridW = W - mL - mR, cw = gridW / 12, ch = rows.length > 14 ? 18 : 22, gh = rows.length * ch;
  const mB = (small ? 56 : 66) + (png ? 62 : 0), H = mT + gh + mB;
  const svg = el('svg', { width: W, height: H, viewBox: '0 0 ' + W + ' ' + H, role: 'img', 'aria-label': tr('cal_aria'), 'font-family': FONT }, host);
  const defs = el('defs', null, svg);
  const pat = el('pattern', { id: 'hatch' + (png ? 'p' : ''), patternUnits: 'userSpaceOnUse', width: 6, height: 6, patternTransform: 'rotate(45)' }, defs);
  el('line', { x1: 0, y1: 0, x2: 0, y2: 6, stroke: T.muted, 'stroke-width': 1.4, opacity: .55 }, pat);
  if (png) { el('rect', { x: 0, y: 0, width: W, height: H, fill: T.surface }, svg); txt(svg, tr('cal_t') + ' · ' + regionName(), { x: 12, y: 24, 'font-size': 16, 'font-weight': 700, fill: T.ink }); txt(svg, dispDate(S.from) + ' – ' + dispDate(S.to) + ' · ' + metricLabel(), { x: 12, y: 44, 'font-size': 12.5, fill: T.ink2 }); }
  // escala
  let vmax = 0; rows.forEach(r => r.cells.forEach(c => { if (c.valid && c.inRange && c.val > vmax) vmax = c.val; }));
  A.vmax = vmax;
  for (let m = 0; m < 12; m++) txt(svg, mon()[m], { x: mL + m * cw + cw / 2, y: mT - 8, 'text-anchor': 'middle', 'font-size': 12, fill: T.muted });
  rows.forEach((r, ri) => {
    const y = mT + ri * ch, isRef = r.year === S.refYear;
    const yl = txt(svg, String(r.year), { x: mL - 8, y: y + ch / 2 + 4, 'text-anchor': 'end', 'font-size': 12, fill: T.ink2, 'font-weight': isRef ? 700 : 400, cursor: 'pointer', 'data-k': 'year', 'data-y': r.year, tabindex: png ? null : 0, role: 'button', 'aria-label': String(r.year) });
    if (png) yl.removeAttribute('tabindex');
    for (let m = 0; m < 12; m++) {
      const c = r.cells[m], x = mL + m * cw;
      const a = { x: x + 1, y: y + 1, width: cw - 2, height: ch - 2, rx: 2, 'data-k': 'cell', 'data-ym': c.ym };
      let rect;
      if (!c.inRange) { rect = el('rect', Object.assign(a, { fill: 'none', stroke: T.grid, 'stroke-width': 1 }), svg); }
      else if (!c.valid) { rect = el('rect', Object.assign(a, { fill: 'url(#hatch' + (png ? 'p' : '') + ')', stroke: T.grid }), svg); }
      else if (S.anom) {
        const med = A.climo[m]; let fill = T.neutralCell;
        if (c.full && med.n >= 3) fill = T.div(clamp(Math.log2((c.val + 1) / (med.med + 1)) / 2, -1, 1));
        rect = el('rect', Object.assign(a, { fill }), svg);
      } else rect = el('rect', Object.assign(a, { fill: rampAt(T, c.val, vmax) }), svg);
      if (c.inRange && c.valid && !c.full) el('path', { d: 'M' + (x + cw - 8) + ',' + (y + 1) + 'L' + (x + cw - 1) + ',' + (y + 1) + 'L' + (x + cw - 1) + ',' + (y + 8) + 'Z', fill: T.ink, opacity: .75, 'pointer-events': 'none' }, svg);
    }
    if (mR > 0) {
      const barMax = mR - 74, x0 = mL + gridW + 10;
      if (isFinite(r.total)) {
        A.tmax = A.tmax || Math.max(...rows.map(q => (isFinite(q.total) ? q.total : 0)), 1);
        const w = Math.max(2, barMax * r.total / A.tmax);
        el('rect', { x: x0, y: y + 3, width: w, height: ch - 6, rx: 3, fill: T.ink2, opacity: r.complete ? .6 : .28, 'data-k': 'tot', 'data-y': r.year }, svg);
        if (isRef || r.total === A.tmax) txt(svg, fmt(r.total), { x: x0 + w + 6, y: y + ch / 2 + 4, 'font-size': 12, fill: T.ink2 });
      }
    }
  });
  A.tmax = null;
  const ry = rows.findIndex(r => r.year === S.refYear);
  if (ry >= 0) el('rect', { x: mL - 1, y: mT + ry * ch, width: gridW + 2, height: ch, rx: 3, fill: 'none', stroke: T.ref, 'stroke-width': 2, 'pointer-events': 'none' }, svg);
  // mediana por mes (marginal inferior)
  const by = mT + gh + 12, bh = small ? 22 : 30; const meds = A.climo.map(c => (c.n ? c.med : NaN)); const mm = Math.max(1, ...meds.filter(isFinite));
  meds.forEach((v, m) => { if (isFinite(v)) { const bhh = Math.max(1.5, bh * v / mm); el('rect', { x: mL + m * cw + cw * 0.2, y: by + bh - bhh, width: cw * 0.6, height: bhh, rx: 3, fill: T.ink2, opacity: .6, 'data-k': 'med', 'data-m': m }, svg); } });
  txt(svg, tr('cal_col_med'), { x: mL, y: by + bh + 16, 'font-size': 11.5, fill: T.muted });
  if (!small && mR > 0) txt(svg, tr('cal_row_total'), { x: mL + gridW + 10, y: mT - 8, 'font-size': 11.5, fill: T.muted });
  if (png) { // leyenda dentro de la imagen
    const gy = H - 44, gx = mL, gw = 200, id = 'lg' + Date.now(); const lg = el('linearGradient', { id, x1: 0, x2: 1, y1: 0, y2: 0 }, defs);
    for (let i = 0; i <= 8; i++) el('stop', { offset: i / 8, 'stop-color': S.anom ? T.div(-1 + i / 4) : T.ramp[Math.round(255 * i / 8)] }, lg);
    el('rect', { x: gx, y: gy, width: gw, height: 10, fill: 'url(#' + id + ')' }, svg);
    (S.anom ? ['¼×', '½×', '1×', '2×', '4×'] : [0, vmax * .25, vmax].map(fmtK)).forEach((s, i, arr) => txt(svg, s, { x: gx + gw * i / (arr.length - 1), y: gy + 24, 'text-anchor': i === 0 ? 'start' : i === arr.length - 1 ? 'end' : 'middle', 'font-size': 11, fill: T.muted }));
    txt(svg, S.anom ? tr('cal_lgd_anom') : tr('cal_lgd_count'), { x: gx + gw + 12, y: gy + 9, 'font-size': 12, fill: T.ink2 });
  }
  return svg;
}
function renderCalendar() {
  const host = $('#cal'); if (S.tableView) { host.hidden = true; renderCalTable(); return; }
  host.hidden = false; $('#cal-tbl').hidden = true;
  const svg = drawCalendar(host, Math.max(320, host.clientWidth), false);
  const T = theme();
  const cellTip = (e, t) => {
    const ym = +t.dataset.ym, m = ym % 12, y = 2000 + Math.floor(ym / 12), c = monthInfo(ym), rows = [];
    const title = tr('tip_month', monthsL()[m][0].toUpperCase() + monthsL()[m].slice(1), y);
    if (!c.valid) { rows.push({ v: tr('tip_nodata') }); }
    else {
      rows.push({ v: fmt(c.val), l: tr('tip_value') });
      { const med = A.climo[m]; if (c.full && med.n >= 3) { const d = (c.val + 1) / (med.med + 1) - 1; rows.push({ v: (d >= 0 ? '+' : '−') + Math.abs(Math.round(d * 100)) + ' %', l: tr('tip_vs') + ' (' + fmt(med.med) + ')' }); } }
      if (!c.full) rows.push({ v: tr('tip_partial', c.covered, c.len) });
      if (S.metric === 'harm') { const a = c.a, b = c.b; rows.push({ v: fmt(rawSum(cum.T, a, b)), l: tr('tip_sensor_terra'), c: T.neutral }); rows.push({ v: fmt(rawSum(cum.A, a, b)), l: tr('tip_sensor_aqua'), c: T.neutral }); rows.push({ v: fmt(rawSum(cum.S, a, b)), l: tr('tip_sensor_snpp'), c: T.neutral }); }
    }
    showTip(e, title, rows);
  };
  svg.addEventListener('pointermove', e => {
    const t = e.target; if (!t.dataset) return; const k = t.dataset.k;
    if (k === 'cell') cellTip(e, t);
    else if (k === 'tot') { const r = A.rows.find(q => q.year === +t.dataset.y); showTip(e, String(r.year), [{ v: fmt(r.total), l: r.complete ? tr('tip_year_total') : tr('tip_year_partial') }]); }
    else if (k === 'med') { const m = +t.dataset.m; showTip(e, monthsL()[m][0].toUpperCase() + monthsL()[m].slice(1), [{ v: fmt(A.climo[m].med), l: tr('cal_col_med') + ' (' + A.climo[m].n + ')' }]); }
    else hideTip();
  });
  svg.addEventListener('pointerleave', hideTip);
  svg.addEventListener('click', e => { const t = e.target; if (t.dataset && (t.dataset.k === 'year' || t.dataset.k === 'tot')) setRef(+t.dataset.y); else if (t.dataset && t.dataset.k === 'cell') setRef(2000 + Math.floor(+t.dataset.ym / 12)); });
  svg.addEventListener('keydown', e => { if ((e.key === 'Enter' || e.key === ' ') && e.target.dataset && e.target.dataset.k === 'year') { e.preventDefault(); setRef(+e.target.dataset.y); } });
  const lg = $('#cal-lgd'); lg.replaceChildren();
  const a = h('div', null, null, lg); rampLegend(a, A.vmax, S.anom ? tr('cal_lgd_anom') : tr('cal_lgd_count'), S.anom);
  const p = h('span', 'lgd-sw', null, lg); const tri = h('i', null, null, p); tri.style.cssText = 'width:0;height:0;border-style:solid;border-width:0 9px 9px 0;border-color:transparent var(--ink) transparent transparent;background:none;border-radius:0;opacity:.75'; p.appendChild(document.createTextNode(tr('cal_partial')));
  const q = h('span', 'lgd-sw', null, lg); const hz = h('i', 'box', null, q); hz.style.cssText = 'background:repeating-linear-gradient(45deg,var(--muted) 0 1.4px,transparent 1.4px 4px);opacity:.7;border:1px solid var(--line)'; q.appendChild(document.createTextNode(tr('cal_nodata')));
  lg.style.cssText = 'display:flex;flex-wrap:wrap;gap:8px 24px;align-items:center';
}
function renderCalTable() {
  const box = $('#cal-tbl'); box.hidden = false; box.replaceChildren();
  const tb = h('table', null, null, box), thd = h('thead', null, null, tb), hr = h('tr', null, null, thd);
  h('th', null, tr('tbl_year'), hr); mon().forEach(s => h('th', null, s, hr)); h('th', null, tr('tbl_total'), hr);
  const body = h('tbody', null, null, tb);
  A.rows.forEach(r => { const tr_ = h('tr', null, null, body); h('td', null, String(r.year), tr_); r.cells.forEach(c => h('td', 'n', c.inRange && c.valid ? fmt(c.val) : '—', tr_)); h('td', 'n', fmt(r.total), tr_); });
}
function setRef(y) { S.refYear = y; $('#f-ref').value = String(y); analyze(); renderCalendar(); renderSeasonal(); renderDaily(); }

/* ---------- temporada ---------- */
function renderSeasonal() {
  const host = $('#seas'), T = theme(), cl = A.climoEx, y = S.refYear;
  const ok = cl.map(c => c.n >= 3);
  const ref = []; for (let m = 0; m < 12; m++) { const v = monthFull((y - 2000) * 12 + m); ref.push(isFinite(v) ? v : NaN); }
  const med = cl.map((c, i) => (ok[i] ? c.med : NaN));
  const areas = [{ lo: cl.map((c, i) => (ok[i] ? c.min : NaN)), hi: cl.map((c, i) => (ok[i] ? c.max : NaN)), color: T.s1, opacity: 0.08 }, { lo: cl.map((c, i) => (ok[i] ? c.q1 : NaN)), hi: cl.map((c, i) => (ok[i] ? c.q3 : NaN)), color: T.s1, opacity: 0.2 }];
  const xt = mon().map((s, i) => ({ i, label: s }));
  lineChart(host, {
    n: 12, height: 270, aria: tr('seas_aria'), xticks: xt, areas,
    series: [{ name: 'med', vals: med, color: T.s1, width: 2 }, { name: 'ref', vals: ref, color: T.ref, width: 2, markers: true }],
    tip: i => {
      const rows = [{ c: T.ref, v: fmt(ref[i]), l: tr('seas_year', y) }];
      if (ok[i]) { rows.push({ c: T.s1, v: fmt(cl[i].med), l: tr('seas_tip_med') }); rows.push({ v: fmt(cl[i].q1) + ' – ' + fmt(cl[i].q3), l: tr('seas_tip_iqr') }); rows.push({ v: fmt(cl[i].min) + ' – ' + fmt(cl[i].max), l: tr('seas_tip_range') }); }
      return { title: monthsL()[i][0].toUpperCase() + monthsL()[i].slice(1), rows };
    }
  });
  legend($('#seas-lgd'), [{ color: T.ref, label: tr('seas_year', y) }, { color: T.s1, label: tr('seas_med') }, { color: T.s1, label: tr('seas_iqr'), box: true, opacity: .35 }, { color: T.s1, label: tr('seas_range'), box: true, opacity: .15 }]);
  if (!ok.some(Boolean)) { const p = h('p', 'note', tr('seas_few')); host.appendChild(p); }
}

/* ---------- serie mensual ---------- */
function renderSeries() {
  const host = $('#series'), T = theme(); const yms = [];
  for (let ym = Math.max(10, dYm[S.from]); ym <= dYm[S.to]; ym++) yms.push(ym);
  const infos = yms.map(monthInfo), vals = infos.map(c => (c.valid && c.full ? c.val : NaN));
  const W = Math.max(280, host.clientWidth), px = (W - 64) / Math.max(1, yms.length - 1);
  const bands = [];
  if (S.metric === 'harm') {
    const e1 = dYm[aqua0], e2 = dYm[viirs0], idx = ym => ym - yms[0];
    const b = (a, z, fill, label, opacity) => { if (z >= 0 && a <= yms.length - 1) bands.push({ a: Math.max(0, a), b: Math.min(yms.length - 1, z), fill, label, opacity }); };
    b(idx(10), idx(e1) - 1, T.ref, tr('era_terra'), 0.12); b(idx(e1), idx(e2) - 1, T.neutral, tr('era_ta'), 0.10); b(idx(e2), idx(311), T.s1, tr('era_viirs'), 0.10);
  }
  lineChart(host, {
    n: yms.length, height: 270, aria: tr('series_aria'), xticks: yearTicks(yms, px), bands,
    series: [{ name: 's', vals, color: T.s1, width: 2 }],
    tip: i => { const c = infos[i], m = yms[i] % 12; return { title: monthsL()[m][0].toUpperCase() + monthsL()[m].slice(1) + ' ' + (2000 + Math.floor(yms[i] / 12)), rows: [{ c: T.s1, v: fmt(vals[i]), l: tr('tip_value') }] }; }
  });
}

/* ---------- calendario diario ---------- */
function renderDaily() {
  const host = $('#daily'); host.replaceChildren(); const T = theme(), y = S.refYear;
  $('#daily-t').textContent = tr('daily_t', y);
  const jan1 = Date.UTC(y, 0, 1), first = Math.round((jan1 - D0) / DAY), len = (Date.UTC(y + 1, 0, 1) - jan1) / DAY, off = (new Date(jan1).getUTCDay() + 6) % 7, cols = Math.ceil((off + len) / 7);
  const W = Math.max(300, host.clientWidth), mL = 26, pitch = Math.max(9, Math.min(22, (W - mL - 4) / cols)), mT = 20, H = mT + 7 * pitch + 4;
  const svg = el('svg', { width: mL + cols * pitch + 4, height: H, role: 'img', 'aria-label': tr('daily_aria'), 'font-family': FONT }, host);
  let vmax = 0; for (let k = 0; k < len; k++) { const d = first + k; if (d >= S.from && d <= S.to && d >= 0 && d < nd) { const v = dayVal(d); if (isFinite(v) && v > vmax) vmax = v; } }
  I[LANG].dow.forEach((s, r) => { if (r % 2 === 0) txt(svg, s, { x: mL - 8, y: mT + r * pitch + pitch / 2 + 4, 'text-anchor': 'end', 'font-size': 11.5, fill: T.muted }); });
  for (let m = 0; m < 12; m++) { const k = Math.round((Date.UTC(y, m, 1) - jan1) / DAY), col = Math.floor((off + k) / 7); txt(svg, mon()[m], { x: mL + col * pitch, y: 13, 'font-size': 11.5, fill: T.muted }); }
  for (let k = 0; k < len; k++) {
    const d = first + k, col = Math.floor((off + k) / 7), row = (off + k) % 7, ok = d >= S.from && d <= S.to && d >= 0 && d < nd && isFinite(dayVal(d));
    const r = el('rect', { x: mL + col * pitch, y: mT + row * pitch, width: pitch - 2, height: pitch - 2, rx: 2, fill: ok ? rampAt(T, dayVal(d), vmax) : 'none', stroke: ok ? 'none' : T.grid, 'data-d': d }, svg);
  }
  svg.addEventListener('pointermove', e => {
    const t = e.target; if (!t.dataset || t.dataset.d === undefined) return hideTip(); const d = +t.dataset.d;
    if (d < 0 || d >= nd) return hideTip();
    const v = dayVal(d); const rows = [];
    if (d >= S.from && d <= S.to && isFinite(v)) { rows.push({ v: fmt(v), l: tr('tip_value') }); if (S.metric === 'harm') { rows.push({ v: fmt(DL.T[d]), l: tr('tip_sensor_terra'), c: T.neutral }); rows.push({ v: fmt(DL.A[d]), l: tr('tip_sensor_aqua'), c: T.neutral }); rows.push({ v: fmt(DL.S[d]), l: tr('tip_sensor_snpp'), c: T.neutral }); } } else rows.push({ v: tr('daily_out') });
    showTip(e, dispDate(d), rows);
  });
  svg.addEventListener('pointerleave', hideTip);
  const lg = $('#daily-lgd'); rampLegend(lg, vmax, tr('daily_lgd'), false);
}

/* ---------- mapa ---------- */
const MAP = { lon0: -118.6, lon1: -86.4, lat0: 14.3, lat1: 32.9 };
let G = null, statePaths = null, drag = null;
function mapGeom(W) { const c = Math.cos(23.5 * Math.PI / 180), H = Math.round(W * (MAP.lat1 - MAP.lat0) / ((MAP.lon1 - MAP.lon0) * c)); return { W, H, sx: W / (MAP.lon1 - MAP.lon0), sy: H / (MAP.lat1 - MAP.lat0) }; }
const px = lon => (lon - MAP.lon0) * G.sx, py = lat => (MAP.lat1 - lat) * G.sy;
function buildPaths() {
  statePaths = M.poly.map(rings => { const p = new Path2D(); rings.forEach(r => { for (let i = 0; i < r.length; i += 2) { const lon = r[i] / 100 - 118, lat = r[i + 1] / 100 + 14; if (i === 0) p.moveTo(px(lon), py(lat)); else p.lineTo(px(lon), py(lat)); } p.closePath(); }); return p; });
}
function unitTotals() {
  const key = S.from + '_' + S.to + '_' + S.metric; if (mapCache && mapCache.key === key) return mapCache.tot;
  const tot = new Float64Array(nU), a = S.from, b = S.to, mt = S.metric;
  for (let i = fragStart[a]; i < fragStart[b + 1]; i++) {
    const d = F.d[i], u = F.u[i]; let v;
    if (mt === 'harm') { const k = dMon[d] * 32 + ust[u]; v = d < aqua0 ? F.T[i] * kT[k] : d < viirs0 ? F.T[i] + F.A[i] : F.S[i] * kV[k]; }
    else if (mt === 'modis') v = d >= aqua0 ? F.T[i] + F.A[i] : 0; else v = d >= viirs0 ? F.S[i] : 0;
    tot[u] += v;
  }
  mapCache = { key, tot }; return tot;
}
const MIN_N = 20;
let cellCache = null, LAY = null;
function cellAgg() {
  const key = S.from + '_' + S.to; if (cellCache && cellCache.key === key) return cellCache;
  const n = NCX * NCY, aS = new Float64Array(n), aH = new Float64Array(n), aM = new Float64Array(n), a = Math.max(S.from, viirs0), b = S.to;
  if (b >= a) for (let i = fragStart[a]; i < fragStart[b + 1]; i++) { const d = F.d[i], u = F.u[i], c = ucell[u]; if (c < 0) continue; aS[c] += F.S[i]; aH[c] += F.S[i] * kV[dMon[d] * 32 + ust[u]]; aM[c] += F.T[i] + F.A[i]; }
  cellCache = { key, aS, aH, aM, any: b >= a }; return cellCache;
}
function mapLayer() {
  const n = NCX * NCY, cellIn = new Uint8Array(n); for (let u = 0; u < nU; u++) if (mask[u] && ucell[u] >= 0) cellIn[ucell[u]] = 1;
  const nf1 = new Intl.NumberFormat(LANG === 'es' ? 'es-MX' : 'en-US', { minimumFractionDigits: 1, maximumFractionDigits: 1 });
  if (S.layer === 'dens') {
    const tot = unitTotals(), v = new Float64Array(n); for (let u = 0; u < nU; u++) if (ucell[u] >= 0) v[ucell[u]] += tot[u];
    let vmax = 0; for (let i = 0; i < n; i++) if (v[i] > vmax) vmax = v[i];
    const labels = S.mapLog ? [0, Math.sqrt(1 + vmax) - 1, vmax].map(fmtK) : [0, vmax * 0.25, vmax].map(fmtK);
    return { kind: 'dens', v, cellIn, vmax, labels, unit: tr('map_lgd'), anom: false, tip: i => (v[i] > 0 ? [{ v: fmt(v[i]), l: tr('map_tip_total') }] : []) };
  }
  const C = cellAgg(), v = new Float64Array(n).fill(NaN), vals = [];
  for (let i = 0; i < n; i++) {
    if (S.layer === 'fact') { if (C.aS[i] >= MIN_N && C.aH[i] > 0) { v[i] = C.aS[i] / C.aH[i]; vals.push(v[i]); } }
    else if (C.aM[i] >= MIN_N) v[i] = C.aH[i] / C.aM[i];
  }
  if (S.layer === 'fact') {
    vals.sort((x, y) => x - y); const lo = vals.length ? quant(vals, 0.02) : 0; let hi = vals.length ? quant(vals, 0.98) : 1; if (!(hi > lo)) hi = lo + 1;
    return { kind: 'fact', v, cellIn, lo, hi, empty: !vals.length, labels: [lo, (lo + hi) / 2, hi].map(x => nf1.format(x)), unit: tr('map_lgd_fact'), anom: false,
      tip: i => (isFinite(v[i]) ? [{ v: nf1.format(v[i]), l: tr('map_tip_fact') }, { v: fmt(C.aS[i]), l: tr('map_tip_viirs') }, { v: fmt(C.aH[i]), l: tr('map_tip_harm') }] : []) };
  }
  let any = false; for (let i = 0; i < n; i++) if (isFinite(v[i])) { any = true; break; }
  return { kind: 'resid', v, cellIn, empty: !any, labels: ['½×', '0.7×', '1×', '1.4×', '2×'], unit: tr('map_lgd_resid'), anom: true,
    tip: i => (isFinite(v[i]) ? [{ v: v[i].toFixed(2) + '×', l: tr('map_tip_ratio') }, { v: fmt(C.aH[i]), l: tr('map_tip_harm') }, { v: fmt(C.aM[i]), l: tr('map_tip_modis') }] : []) };
}
function layerColor(T, L, v) {
  if (L.kind === 'dens') { const pos = S.mapLog ? Math.log1p(v) / Math.log1p(L.vmax) : Math.sqrt(v / L.vmax); return T.ramp[Math.round(clamp(pos, 0, 1) * 255)]; }
  if (L.kind === 'fact') return T.ramp[Math.round(clamp((v - L.lo) / (L.hi - L.lo), 0, 1) * 255)];
  return T.div(clamp(Math.log2(Math.max(v, 1e-6)), -1, 1));
}
function paintMap(ctx, T) {
  const W = G.W, Hh = G.H, L = LAY, r = S.region;
  ctx.fillStyle = T.surface2; ctx.fillRect(0, 0, W, Hh);
  ctx.fillStyle = T.surface; statePaths.forEach(p => ctx.fill(p, 'evenodd'));
  const cs = 0.25 * G.sx, csy = 0.25 * G.sy;
  for (let cy = 0; cy < NCY; cy++) for (let cx = 0; cx < NCX; cx++) {
    const i = cy * NCX + cx, v = L.v[i]; if (!isFinite(v) || (L.kind === 'dens' && !(v > 0))) continue;
    ctx.globalAlpha = L.cellIn[i] ? 1 : 0.28; ctx.fillStyle = layerColor(T, L, v);
    ctx.fillRect(px(-118 + cx * 0.25), py(14 + (cy + 1) * 0.25), cs + 0.6, csy + 0.6);
  }
  ctx.globalAlpha = 1; ctx.lineWidth = 0.7; ctx.strokeStyle = T.dark ? 'rgba(255,255,255,.28)' : 'rgba(20,25,29,.35)'; statePaths.forEach(p => ctx.stroke(p));
  if (r.type === 'state') { ctx.lineWidth = 2.2; ctx.strokeStyle = T.accent; ctx.stroke(statePaths[r.state]); }
  const q = r.type === 'rect' ? r.rect : (drag && drag.rect ? drag.rect : null);
  if (q) { const x0 = px(-118 + q.x0 * 0.25), x1 = px(-118 + (q.x1 + 1) * 0.25), y0 = py(14 + (q.y1 + 1) * 0.25), y1 = py(14 + q.y0 * 0.25); ctx.lineWidth = 2.2; ctx.strokeStyle = T.accent; ctx.fillStyle = T.accent; ctx.globalAlpha = .1; ctx.fillRect(x0, y0, x1 - x0, y1 - y0); ctx.globalAlpha = 1; ctx.strokeRect(x0, y0, x1 - x0, y1 - y0); }
  if (L.empty) { ctx.fillStyle = T.ink2; ctx.font = '13px ' + FONT; ctx.textAlign = 'center'; const words = tr('map_nodata_layer').split(' '); let line = '', y = Hh * 0.5; words.forEach(w => { if (ctx.measureText(line + w).width > W * 0.7) { ctx.fillText(line.trim(), W / 2, y); y += 18; line = ''; } line += w + ' '; }); ctx.fillText(line.trim(), W / 2, y); ctx.textAlign = 'start'; }
}
function renderMap() {
  const cv = $('#map'), T = theme(), W = Math.max(280, $('#map-wrap').clientWidth); G = mapGeom(W);
  const dpr = window.devicePixelRatio || 1; cv.width = Math.round(W * dpr); cv.height = Math.round(G.H * dpr); cv.style.height = G.H + 'px';
  cv.setAttribute('aria-label', tr('map_aria'));
  const ctx = cv.getContext('2d'); ctx.setTransform(dpr, 0, 0, dpr, 0, 0); buildPaths();
  LAY = mapLayer(); paintMap(ctx, T);
  rampLegend($('#map-lgd'), LAY.vmax, LAY.unit, LAY.anom, LAY.labels);
  $('#map-sub').textContent = S.layer === 'fact' ? tr('map_s_fact', MIN_N) : S.layer === 'resid' ? tr('map_s_resid', MIN_N) : tr('map_s');
  $('#map-log-w').hidden = S.layer !== 'dens';
  const r = S.region; $('#map-info').textContent = r.type === 'rect' ? rectLabel(r.rect) : '';
}
function exportMapPng() {
  if (!LAY) return; const T = theme(), W = G.W, Hh = G.H, hd = 62, ft = 72, sc = 2, out = document.createElement('canvas');
  out.width = W * sc; out.height = (Hh + hd + ft) * sc; const ctx = out.getContext('2d'); ctx.scale(sc, sc);
  ctx.fillStyle = T.surface; ctx.fillRect(0, 0, W, Hh + hd + ft);
  ctx.fillStyle = T.ink; ctx.font = '700 16px ' + FONT; ctx.fillText(tr('layer_' + S.layer) + ' · ' + regionName(), 12, 26);
  ctx.fillStyle = T.ink2; ctx.font = '12.5px ' + FONT; ctx.fillText(dispDate(S.from) + ' – ' + dispDate(S.to) + (S.layer === 'dens' ? ' · ' + metricLabel() : ''), 12, 46);
  ctx.save(); ctx.translate(0, hd); ctx.beginPath(); ctx.rect(0, 0, W, Hh); ctx.clip(); paintMap(ctx, T); ctx.restore();
  const gx = 12, gy = hd + Hh + 14, gw = 220; for (let x = 0; x < gw; x++) { ctx.fillStyle = LAY.anom ? T.div(-1 + 2 * x / (gw - 1)) : T.ramp[Math.round(255 * x / (gw - 1))]; ctx.fillRect(gx + x, gy, 1, 11); }
  ctx.fillStyle = T.muted; ctx.font = '11.5px ' + FONT; LAY.labels.forEach((s, i, arr) => { ctx.textAlign = i === 0 ? 'left' : i === arr.length - 1 ? 'right' : 'center'; ctx.fillText(s, gx + gw * i / (arr.length - 1), gy + 27); }); ctx.textAlign = 'left';
  ctx.fillStyle = T.ink2; ctx.font = '12px ' + FONT; ctx.fillText(LAY.unit + (S.layer === 'dens' && S.mapLog ? ' (' + tr('map_log').toLowerCase() + ')' : ''), gx + gw + 12, gy + 10);
  out.toBlob(b => { if (b) saveFile('mapa_' + S.layer + '_' + regionSlug() + '_' + isoOf(S.from) + '_' + isoOf(S.to) + '.png', b); else toast(tr('savefail')); }, 'image/png');
}
const rectLabel = q => tr('map_rect_info', (14 + (q.y1 + 1) * 0.25).toFixed(2), (14 + q.y0 * 0.25).toFixed(2), Math.abs(-118 + q.x0 * 0.25).toFixed(2), Math.abs(-118 + (q.x1 + 1) * 0.25).toFixed(2));
function canvasPos(e) { const r = $('#map').getBoundingClientRect(); return { x: e.clientX - r.left, y: e.clientY - r.top }; }
function posToCell(p) { const lon = p.x / G.sx + MAP.lon0, lat = MAP.lat1 - p.y / G.sy; return { lon, lat, cx: Math.floor((lon + 118) / 0.25), cy: Math.floor((lat - 14) / 0.25) }; }
function stateAt(p) { const ctx = $('#map').getContext('2d'); const dpr = window.devicePixelRatio || 1; for (let s = 0; s < statePaths.length; s++) if (ctx.isPointInPath(statePaths[s], p.x * dpr, p.y * dpr, 'evenodd')) return s; return -1; }
function initMap() {
  const cv = $('#map');
  cv.addEventListener('pointerdown', e => { cv.setPointerCapture(e.pointerId); const p = canvasPos(e); drag = { p0: p, moved: false, rect: null }; });
  cv.addEventListener('pointermove', e => {
    const p = canvasPos(e);
    if (drag) {
      if (Math.hypot(p.x - drag.p0.x, p.y - drag.p0.y) > 5) drag.moved = true;
      if (drag.moved && S.mapMode === 'rect') { const a = posToCell(drag.p0), b = posToCell(p); drag.rect = { x0: Math.min(a.cx, b.cx), x1: Math.max(a.cx, b.cx), y0: Math.min(a.cy, b.cy), y1: Math.max(a.cy, b.cy) }; renderMap(); }
      return;
    }
    const c = posToCell(p); const s = stateAt(p); const i = c.cy * NCX + c.cx;
    const rows = LAY && c.cx >= 0 && c.cx < NCX && c.cy >= 0 && c.cy < NCY ? LAY.tip(i) : [];
    showTip(e, (s >= 0 ? M.state_names[s] + ' · ' : '') + tr('map_tip_cell', (14 + c.cy * 0.25).toFixed(2) + '°N', Math.abs(-118 + c.cx * 0.25).toFixed(2) + '°O'), rows);
  });
  cv.addEventListener('pointerleave', hideTip);
  cv.addEventListener('pointerup', e => {
    const d = drag; drag = null; if (!d) return; const p = canvasPos(e);
    if (d.moved && S.mapMode === 'rect' && d.rect) { S.region = { type: 'rect', state: -1, rect: d.rect }; setRegionSelect(); regionChanged(); }
    else if (!d.moved) { const s = stateAt(p); if (s >= 0) { S.region = { type: 'state', state: s, rect: null }; setRegionSelect(); regionChanged(); } }
    else renderMap();
  });
}
function setRegionSelect() { const sel = $('#f-region'), r = S.region; const ro = sel.querySelector('option[value="rect"]'); ro.hidden = r.type !== 'rect'; ro.disabled = r.type !== 'rect'; sel.value = r.type === 'all' ? 'all' : r.type === 'state' ? 's' + r.state : 'rect'; }
function regionName() { const r = S.region; return r.type === 'all' ? tr('r_all') : r.type === 'state' ? M.state_names[r.state] : tr('r_rect'); }
function regionSlug() {
  const r = S.region; if (r.type === 'all') return 'mexico';
  if (r.type === 'state') return M.state_names[r.state].normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '_');
  const q = r.rect; return 'rect_N' + (14 + (q.y1 + 1) * .25) + '_S' + (14 + q.y0 * .25) + '_W' + Math.abs(-118 + q.x0 * .25) + '_E' + Math.abs(-118 + (q.x1 + 1) * .25);
}
const metricLabel = () => tr(S.metric === 'harm' ? 'm_harm' : S.metric === 'modis' ? 'm_modis' : 'm_viirs');

/* ---------- cifras ---------- */
function renderKpis() {
  const box = $('#kpis'); box.replaceChildren();
  const rl = $('#region-line'); rl.replaceChildren(); const sg = h('strong', null, regionName(), rl); rl.appendChild(document.createTextNode(' · ' + dispDate(S.from) + ' – ' + dispDate(S.to) + ' · ' + metricLabel()));
  const tile = (l, v, d) => { const k = h('div', 'kpi', null, box); h('div', 'l', l, k); h('div', 'v', v, k); h('div', 'd', d, k); };
  // total
  const c = cumSel(), a = Math.max(S.from, metricStart()), b = S.to; const tot = b >= a ? c[b + 1] - c[a] : NaN;
  tile(tr('kpi_total'), isFinite(tot) ? fmt(tot) : '—', tr(S.metric === 'harm' ? 'kpi_total_h' : S.metric === 'modis' ? 'kpi_total_m' : 'kpi_total_v'));
  // mes pico
  let bm = -1, bv = -1; A.climo.forEach((q, m) => { if (q.n && q.med > bv) { bv = q.med; bm = m; } });
  tile(tr('kpi_month'), bm >= 0 ? monthsL()[bm][0].toUpperCase() + monthsL()[bm].slice(1) : '—', bm >= 0 ? tr('kpi_month_d', fmt(bv)) : tr('kpi_none'));
  // año pico (completos; si no hay, parciales)
  let cand = A.rows.filter(r => r.complete), partial = false; if (!cand.length) { cand = A.rows.filter(r => isFinite(r.total)); partial = true; }
  let by = null; cand.forEach(r => { if (!by || r.total > by.total) by = r; });
  tile(tr('kpi_year'), by ? String(by.year) : '—', by ? tr(partial || !by.complete ? 'kpi_year_p' : 'kpi_year_d', fmt(by.total)) : tr('kpi_none'));
  // día pico
  let bd = -1, bdv = -1; for (let d = Math.max(S.from, metricStart()); d <= S.to; d++) { const v = dayVal(d); if (isFinite(v) && v > bdv) { bdv = v; bd = d; } }
  tile(tr('kpi_day'), bd >= 0 && bdv > 0 ? dispDate(bd) : '—', bd >= 0 && bdv > 0 ? tr('kpi_day_d', fmt(bdv)) : tr('kpi_none'));
  renderExportButtons();
}

/* ---------- armonización (pestaña) ---------- */
function renderHarm() {
  const T = theme(), host = $('#harm'); const y0 = 145, y1 = 311, yms = []; for (let ym = y0; ym <= y1; ym++) yms.push(ym);
  const sum = (c, ym) => { const st = ymStart[ym]; return c[Math.min(st + ymLen[ym], nd)] - c[st]; };
  const obs = yms.map(ym => sum(cum.M, ym)), cal = yms.map(ym => sum(cum.H, ym)), raw = yms.map(ym => sum(cum.V, ym));
  const metrics = (i0, i1) => {
    let so = 0, sc = 0, sad = 0; const xs = [], ys = [];
    for (let i = i0; i <= i1; i++) { so += obs[i]; sc += cal[i]; sad += Math.abs(cal[i] - obs[i]); xs.push(cal[i]); ys.push(obs[i]); }
    const mx = xs.reduce((p, q) => p + q, 0) / xs.length, my = ys.reduce((p, q) => p + q, 0) / ys.length; let sxy = 0, sxx = 0, syy = 0;
    xs.forEach((v, i) => { sxy += (v - mx) * (ys[i] - my); sxx += (v - mx) ** 2; syy += (ys[i] - my) ** 2; });
    let an = 0; const ya = {}; for (let i = i0; i <= i1; i++) { const yr = 2000 + Math.floor(yms[i] / 12); ya[yr] = ya[yr] || [0, 0]; ya[yr][0] += cal[i]; ya[yr][1] += obs[i]; }
    let sa = 0; Object.values(ya).forEach(v => { an += Math.abs(v[0] - v[1]); sa += v[1]; });
    return { wm: so ? sad / so : NaN, wa: sa ? an / sa : NaN, r: sxx && syy ? sxy / Math.sqrt(sxx * syy) : NaN };
  };
  const iSplit = yms.findIndex(ym => ym === 240); // enero 2020
  const m1 = metrics(0, iSplit - 1), m2 = metrics(iSplit, yms.length - 1), mAll = metrics(0, yms.length - 1);
  const so = obs.reduce((p, q) => p + q, 0), sr = raw.reduce((p, q) => p + q, 0);
  const box = $('#harm-metrics'); box.replaceChildren();
  const tile = (l, v, d) => { const k = h('div', 'kpi', null, box); h('div', 'l', l, k); h('div', 'v', v, k); h('div', 'd', d, k); };
  tile(tr('hm_m_raw'), (so ? sr / so : NaN).toFixed(1).replace(/^NaN$/, '—') + '×', tr('hm_m_raw_d'));
  tile(tr('hm_m_annual'), pct(mAll.wa), tr('hm_m_annual_d', pct(m1.wa), pct(m2.wa)));
  tile(tr('hm_m_month'), pct(mAll.wm), tr('hm_m_month_d', pct(m1.wm), pct(m2.wm)));
  tile(tr('hm_m_r'), isFinite(mAll.r) ? mAll.r.toFixed(3) : '—', tr('hm_m_r_d'));
  const px_ = (host.clientWidth - 64) / yms.length, series = [{ name: 'obs', vals: obs, color: T.s2, width: 2 }, { name: 'cal', vals: cal, color: T.s1, width: 2 }];
  if (S.showRaw) series.push({ name: 'raw', vals: raw, color: T.neutral, width: 2 });
  lineChart(host, {
    n: yms.length, height: 300, aria: tr('hm_aria'), xticks: yearTicks(yms, px_), series,
    bands: [{ a: 0, b: iSplit - 1, fill: T.s1, opacity: .06, label: tr('hm_calib') }, { a: iSplit, b: yms.length - 1, fill: T.neutral, opacity: .12, label: tr('hm_oos') }],
    tip: i => { const m = yms[i] % 12, rows = [{ c: T.s2, v: fmt(obs[i]), l: tr('hm_obs') }, { c: T.s1, v: fmt(cal[i]), l: tr('hm_cal') }]; if (S.showRaw) rows.push({ c: T.neutral, v: fmt(raw[i]), l: tr('hm_raw') }); return { title: monthsL()[m][0].toUpperCase() + monthsL()[m].slice(1) + ' ' + (2000 + Math.floor(yms[i] / 12)), rows }; }
  });
  const items = [{ color: T.s2, label: tr('hm_obs') }, { color: T.s1, label: tr('hm_cal') }]; if (S.showRaw) items.push({ color: T.neutral, label: tr('hm_raw') }); legend($('#harm-lgd'), items);
  // factores
  const r = S.region, kst = r.type === 'state' ? r.state : -1, nat = M.kV_nat, ser = [];
  if (kst >= 0) ser.push({ name: 'st', vals: M.kV.map(row => row[kst]), color: T.s1, width: 2, markers: true });
  ser.push({ name: 'nat', vals: nat, color: kst >= 0 ? T.neutral : T.s1, width: 2, markers: kst < 0 });
  lineChart($('#kchart'), {
    n: 12, height: 240, aria: tr('k_aria'), yfmt: v => (Math.round(v * 100) / 100).toString(), xticks: mon().map((s, i) => ({ i, label: s })), series: ser,
    tip: i => { const rows = []; if (kst >= 0) rows.push({ c: T.s1, v: M.kV[i][kst].toFixed(3), l: M.state_names[kst] }); rows.push({ c: kst >= 0 ? T.neutral : T.s1, v: nat[i].toFixed(3), l: tr('k_nat') }); return { title: monthsL()[i][0].toUpperCase() + monthsL()[i].slice(1) + ' · ' + tr('k_tip'), rows }; }
  });
  const items2 = []; if (kst >= 0) items2.push({ color: T.s1, label: M.state_names[kst] }); items2.push({ color: kst >= 0 ? T.neutral : T.s1, label: tr('k_nat') }); legend($('#k-lgd'), items2);
}
function renderValidation() {
  const box = $('#val-tables'); box.replaceChildren();
  const pc = v => (v * 100).toFixed(1) + (LANG === 'es' ? ' %' : '%');
  const mk = (title, rows, chosenIdx) => {
    h('h3', null, title, box).style.cssText = 'font-size:15px;margin:14px 0 6px';
    const wrap = h('div', 'tbl-wrap', null, box), tb = h('table', null, null, wrap), th = h('thead', null, null, tb);
    const r1 = h('tr', null, null, th); h('th', null, tr('val_col_name'), r1).rowSpan = 2; let c = h('th', null, tr('val_loyo'), r1); c.colSpan = 3; c.style.textAlign = 'center'; c = h('th', null, tr('val_oos'), r1); c.colSpan = 3; c.style.textAlign = 'center';
    const r2 = h('tr', null, null, th); for (let i = 0; i < 2; i++) [tr('val_col_sm'), tr('val_col_nm'), tr('val_col_an')].forEach(s => h('th', null, s, r2));
    const body = h('tbody', null, null, tb);
    rows.forEach((r, i) => { const tr_ = h('tr', null, null, body); const nm = h('td', null, r.nombre + (i === chosenIdx ? ' (' + tr('val_chosen') + ')' : ''), tr_); if (i === chosenIdx) nm.style.fontWeight = '700'; [r.loyo, r.holdout].forEach(q => { [q.wape_estado_mes, q.wape_nacional_mes, q.wape_anual].forEach(v => h('td', 'n', pc(v), tr_)); }); });
  };
  const lv = VAL.niveles, vr = VAL.variantes;
  mk(tr('val_levels'), lv.map(q => ({ nombre: LANG === 'es' ? q.nombre : ({ global: 'Single factor (all of Mexico, all year)', mes: 'Factor by month (national)', 'estado-mes': 'Factor by state and month (shrinkage τ=100)' })[q.clave], loyo: q.loyo, holdout: q.holdout })), 2);
  const vn = ['', 'Footprint 1 km (merge VIIRS pixels)', 'Footprint + VIIRS FRP ≥ 2 MW', 'Footprint + VIIRS FRP ≥ 4 MW', 'Footprint + VIIRS FRP ≥ 6 MW'];
  mk(tr('val_variants'), vr.map((q, i) => ({ nombre: i === 0 ? (LANG === 'es' ? q.nombre.replace(/ \(elegida\)$/, '') : 'No footprint, no FRP threshold') : (LANG === 'es' ? q.nombre : vn[i]), loyo: q.loyo, holdout: q.holdout })), 0);
  const t = VAL.terra; h('p', 'note', tr('val_terra', pc(t.wape_estado_mes), pc(t.wape_nacional_mes), pc(t.wape_anual), pc(t.sesgo)), box);
}
function renderAbout() {
  const loyo = VAL.niveles[2].loyo, oos = VAL.niveles[2].holdout, pc = v => (v * 100).toFixed(1) + (LANG === 'es' ? ' %' : '%');
  $('#about').innerHTML = I[LANG].about_html.split('{tau}').join(String(M.tau)).split('{v_loyo_an}').join(pc(loyo.wape_anual)).split('{v_oos_an}').join(pc(oos.wape_anual)).split('{v_loyo_sm}').join(pc(loyo.wape_estado_mes)).split('{v_oos_sm}').join(pc(oos.wape_estado_mes));
}

/* ---------- exportación ---------- */
let dlCache = null;
async function getDl() { if (dlCache) return dlCache; try { if (window.claude && window.claude.use) dlCache = await window.claude.use('downloads'); } catch (e) { dlCache = null; } return dlCache; }
async function saveFile(name, blob) {
  const dl = await getDl();
  if (dl) { try { await dl.save({ filename: name, data: blob }); toast(tr('saved')); } catch (e) { if (!e || e.code !== 'declined') toast(tr('savefail')); } return; }
  const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = name; document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(a.href), 5000); toast(tr('saved'));
}
let toastT = 0; function toast(s) { const t = $('#toast'); t.textContent = s; t.style.display = 'block'; clearTimeout(toastT); toastT = setTimeout(() => { t.style.display = 'none'; }, 3500); }
const csvBlob = parts => new Blob(['﻿'].concat(parts), { type: 'text/csv;charset=utf-8' });
const fname = kind => 'hotspots_' + kind + '_' + regionSlug() + '_' + isoOf(S.from) + '_' + isoOf(S.to) + '.csv';
function exportDaily() {
  const rows = ['fecha,hotspots_armonizados,modis_terra,modis_aqua,viirs_snpp,fuente'];
  for (let d = S.from; d <= S.to; d++) { const f = d < aqua0 ? 'Terra (escalado)' : d < viirs0 ? 'Terra+Aqua' : 'VIIRS SNPP (calibrado)'; rows.push(dStr[d] + ',' + DL.H[d].toFixed(3) + ',' + DL.T[d] + ',' + DL.A[d] + ',' + DL.S[d] + ',' + f); }
  saveFile(fname('diario'), csvBlob([rows.join('\n') + '\n']));
}
function exportMonthly() {
  const rows = ['anio,mes,dias_en_rango,dias_del_mes,hotspots_armonizados,modis_terra,modis_aqua,viirs_snpp'];
  for (let ym = Math.max(10, dYm[S.from]); ym <= dYm[S.to]; ym++) { const st = ymStart[ym], a = Math.max(S.from, st), b = Math.min(S.to, st + ymLen[ym] - 1); rows.push((2000 + Math.floor(ym / 12)) + ',' + (ym % 12 + 1) + ',' + (b - a + 1) + ',' + ymLen[ym] + ',' + rawSum(cum.H, a, b).toFixed(3) + ',' + rawSum(cum.T, a, b) + ',' + rawSum(cum.A, a, b) + ',' + rawSum(cum.S, a, b)); }
  saveFile(fname('mensual'), csvBlob([rows.join('\n') + '\n']));
}
function pointCount() { let n = 0; for (let d = S.from; d <= S.to; d++) n += d < viirs0 ? DL.T[d] + DL.A[d] : DL.S[d]; return n; }
function renderExportButtons() {
  const n = pointCount(), b = $('#ex-points'); $('#ex-points-l').textContent = tr('ex_points');
  const s = $('#ex-points-s');
  if (n === 0) { s.textContent = tr('ex_points_none'); b.disabled = true; }
  else if (n > MAX_ROWS) { s.textContent = tr('ex_points_big', fmt(n), fmt(MAX_ROWS)); b.disabled = true; }
  else { s.textContent = tr('ex_points_s', fmt(n)); b.disabled = false; }
}
async function loadPts(y) {
  if (ptsCache.has(y)) return ptsCache.get(y);
  const c = parsePts(await fetchBin('data/pts/pts_' + y + '.txt')); ptsCache.set(y, c); if (ptsCache.size > 4) ptsCache.delete(ptsCache.keys().next().value); return c;
}
async function exportPoints() {
  const btn = $('#ex-points'); btn.disabled = true;
  try {
    const y0 = dYear[S.from], y1 = dYear[S.to], parts = ['fecha_utc,hora_utc,latitud,longitud,estado,sensor,frp_mw,confianza,dia_noche,peso_armonizado\n'], sat = ['MODIS Terra', 'MODIS Aqua', 'VIIRS SNPP'];
    let n = 0, buf = [];
    for (let y = y0; y <= y1; y++) {
      if (!M.pts_years[String(y)]) continue; toast(tr('loading_pts', y, y - y0 + 1, y1 - y0 + 1));
      const c = await loadPts(y);
      for (let i = 0; i < c.n; i++) {
        const d = c.d[i]; if (d < S.from || d > S.to) continue; const u = c.u[i]; if (!mask[u]) continue;
        const s = ust[u], k = dMon[d] * 32 + s, fl = c.fl[i], sc = fl & 3;
        const w = d < aqua0 ? kT[k] : d < viirs0 ? 1 : kV[k];
        const lat = 14 + ucy[u] * 0.25 + c.dy[i] * 0.001, lon = -118 + ucx[u] * 0.25 + c.dx[i] * 0.001, tm = c.tm[i], hh = String(Math.floor(tm / 100)).padStart(2, '0'), mm = String(tm % 100).padStart(2, '0');
        buf.push(dStr[d] + ',' + hh + ':' + mm + ',' + lat.toFixed(3) + ',' + lon.toFixed(3) + ',' + M.state_names[s] + ',' + sat[sc] + ',' + (c.frp[i] / 10).toFixed(1) + ',' + (((fl >> 2) & 1) ? 'alta' : 'nominal') + ',' + (((fl >> 3) & 1) ? 'N' : 'D') + ',' + w.toFixed(4) + '\n'); n++;
        if (buf.length >= 5000) { parts.push(buf.join('')); buf = []; }
      }
      await new Promise(r => setTimeout(r, 0));
    }
    if (buf.length) parts.push(buf.join(''));
    await saveFile(fname('puntos'), csvBlob(parts));
  } catch (e) { toast(tr('savefail')); console.error(e); }
  renderExportButtons();
}
function exportPng() {
  const host = document.createElement('div'), W = 1100, svg = drawCalendar(host, W, true), H = +svg.getAttribute('height');
  const xml = new XMLSerializer().serializeToString(svg), url = URL.createObjectURL(new Blob([xml], { type: 'image/svg+xml;charset=utf-8' })), img = new Image(), T = theme();
  img.onload = () => { const c = document.createElement('canvas'); c.width = W * 2; c.height = H * 2; const ctx = c.getContext('2d'); ctx.fillStyle = T.surface; ctx.fillRect(0, 0, c.width, c.height); ctx.scale(2, 2); ctx.drawImage(img, 0, 0, W, H); URL.revokeObjectURL(url); c.toBlob(b => { if (b) saveFile('calendario_' + regionSlug() + '_' + isoOf(S.from) + '_' + isoOf(S.to) + '.png', b); else toast(tr('savefail')); }, 'image/png'); };
  img.onerror = () => { URL.revokeObjectURL(url); toast(tr('savefail')); };
  img.src = url;
}

/* ---------- controles ---------- */
function fillSelects() {
  const sr = $('#f-region'); sr.replaceChildren();
  const add = (sel, v, l) => { const o = h('option', null, l, sel); o.value = v; return o; };
  add(sr, 'all', tr('r_all')); M.state_names.forEach((n, i) => add(sr, 's' + i, n)); const ro = add(sr, 'rect', tr('r_rect')); ro.hidden = true; ro.disabled = true;
  const sm = $('#f-metric'); sm.replaceChildren(); add(sm, 'harm', tr('m_harm')); add(sm, 'modis', tr('m_modis')); add(sm, 'viirs', tr('m_viirs')); sm.value = S.metric;
  const ml = $('#map-layer'); ml.replaceChildren(); add(ml, 'dens', tr('layer_dens')); add(ml, 'fact', tr('layer_fact')); add(ml, 'resid', tr('layer_resid')); ml.value = S.layer; $('#map-log').checked = S.mapLog;
  const rf = $('#f-ref'); rf.replaceChildren(); for (let y = 2025; y >= 2001; y--) add(rf, String(y), String(y)); rf.value = String(S.refYear);
  setRegionSelect();
}
function applyLang() {
  document.documentElement.lang = LANG; setLocale();
  document.querySelectorAll('[data-i18n]').forEach(e => { e.textContent = tr(e.getAttribute('data-i18n')); });
  $('#btn-lang').textContent = LANG === 'es' ? 'EN' : 'ES'; document.title = tr('title');
  $('#cal-toggle').textContent = tr(S.tableView ? 'cal_chart' : 'cal_table');
}
function presetRange(p) { const ymd = (y, m, d) => Math.round((Date.UTC(y, m, d) - D0) / DAY); if (p === 'all') return [0, nd - 1]; if (p === 'viirs') return [ymd(2012, 1, 1), nd - 1]; if (p === '10') return [ymd(2016, 0, 1), nd - 1]; return [ymd(2021, 0, 1), nd - 1]; }
function syncDates() {
  $('#f-from').value = isoOf(S.from); $('#f-to').value = isoOf(S.to);
  document.querySelectorAll('#presets .chip').forEach(b => { const r = presetRange(b.dataset.preset); b.setAttribute('aria-pressed', String(r[0] === S.from && r[1] === S.to)); });
}
function regionChanged() { computeRegion(); renderAll(); }
function rangeChanged() { syncDates(); mapCache = null; renderAll(); }
function renderAll() {
  analyze(); renderKpis(); renderMap(); renderCalendar(); renderSeasonal(); renderSeries(); renderDaily();
  if (S.tab === 'harm') renderHarm();
}
function showTab(name) {
  S.tab = name; ['explore', 'harm', 'about'].forEach(t => { $('#view-' + t).hidden = t !== name; $('#tab-' + t).setAttribute('aria-selected', String(t === name)); });
  $('.filters').hidden = name === 'about'; $('.filters').classList.toggle('on-harm', name === 'harm'); renderAll();
}
function bind() {
  $('#f-region').addEventListener('change', e => { const v = e.target.value; S.region = v === 'all' ? { type: 'all', state: -1, rect: null } : v === 'rect' ? S.region : { type: 'state', state: +v.slice(1), rect: null }; setRegionSelect(); regionChanged(); });
  const dateCh = () => { let a = dayOfISO($('#f-from').value), b = dayOfISO($('#f-to').value); if (!isFinite(a)) a = S.from; if (!isFinite(b)) b = S.to; a = clamp(a, 0, nd - 1); b = clamp(b, 0, nd - 1); if (a > b) b = a; S.from = a; S.to = b; rangeChanged(); };
  $('#f-from').addEventListener('change', dateCh); $('#f-to').addEventListener('change', dateCh);
  document.querySelectorAll('#presets .chip').forEach(b => b.addEventListener('click', () => { const r = presetRange(b.dataset.preset); S.from = r[0]; S.to = r[1]; rangeChanged(); }));
  $('#map-layer').addEventListener('change', e => { S.layer = e.target.value; renderMap(); });
  $('#map-log').addEventListener('change', e => { S.mapLog = e.target.checked; renderMap(); });
  $('#ex-mappng').addEventListener('click', exportMapPng);
  $('#f-metric').addEventListener('change', e => { S.metric = e.target.value; mapCache = null; renderAll(); });
  $('#f-ref').addEventListener('change', e => setRef(+e.target.value));
  $('#cm-count').addEventListener('click', () => { S.anom = false; $('#cm-count').setAttribute('aria-pressed', 'true'); $('#cm-anom').setAttribute('aria-pressed', 'false'); renderCalendar(); });
  $('#cm-anom').addEventListener('click', () => { S.anom = true; $('#cm-count').setAttribute('aria-pressed', 'false'); $('#cm-anom').setAttribute('aria-pressed', 'true'); renderCalendar(); });
  $('#cal-toggle').addEventListener('click', () => { S.tableView = !S.tableView; $('#cal-toggle').textContent = tr(S.tableView ? 'cal_chart' : 'cal_table'); renderCalendar(); });
  $('#mm-state').addEventListener('click', () => { S.mapMode = 'state'; $('#mm-state').setAttribute('aria-pressed', 'true'); $('#mm-rect').setAttribute('aria-pressed', 'false'); });
  $('#mm-rect').addEventListener('click', () => { S.mapMode = 'rect'; $('#mm-state').setAttribute('aria-pressed', 'false'); $('#mm-rect').setAttribute('aria-pressed', 'true'); });
  $('#btn-all').addEventListener('click', () => { S.region = { type: 'all', state: -1, rect: null }; setRegionSelect(); regionChanged(); });
  $('#ex-daily').addEventListener('click', exportDaily); $('#ex-monthly').addEventListener('click', exportMonthly); $('#ex-points').addEventListener('click', exportPoints); $('#ex-png').addEventListener('click', exportPng);
  $('#hm-raw').addEventListener('change', e => { S.showRaw = e.target.checked; renderHarm(); });
  ['explore', 'harm', 'about'].forEach(t => $('#tab-' + t).addEventListener('click', () => showTab(t)));
  $('#btn-lang').addEventListener('click', () => { LANG = LANG === 'es' ? 'en' : 'es'; try { localStorage.setItem('qm_lang', LANG); } catch (e) {} applyLang(); fillSelects(); renderValidation(); renderAbout(); renderAll(); });
  let rt = 0; const onResize = () => { clearTimeout(rt); rt = setTimeout(() => { if (M && DL) renderAll(); }, 150); };
  new ResizeObserver(onResize).observe($('main'));
  const mq = window.matchMedia('(prefers-color-scheme: dark)'); const th = () => { themeObj = null; if (M && DL) renderAll(); };
  if (mq.addEventListener) mq.addEventListener('change', th);
  new MutationObserver(th).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
}

async function boot() {
  setLocale(); applyLang();
  const msg = $('#load-msg'), bar = $('#load-bar'); msg.textContent = tr('loading');
  getDl();
  try {
    bar.style.width = '10%';
    const [meta, val, fr] = await Promise.all([fetchJSON('data/meta.json'), fetchJSON('data/validacion.json'), fetchBin('data/frag.txt')]);
    bar.style.width = '70%'; M = meta; VAL = val; F = parseFrag(fr); prepare(); bar.style.width = '90%';
    S.from = presetRange('all')[0]; S.to = nd - 1; S.refYear = 2025;
    fillSelects(); syncDates(); bind(); initMap(); renderValidation(); renderAbout(); computeRegion(); renderAll();
    $('#loading').hidden = true; window.__qm = { S, M, getDL: () => DL, getA: () => A, getLAY: () => LAY, monthInfo, computeRegion, analyze };
  } catch (e) { console.error(e); msg.textContent = tr('loaderr'); $('.bar').hidden = true; }
}
boot();
})();
