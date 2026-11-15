/* Motor de pronóstico de hotspots armonizados (sin dependencias ni DOM).
   Modelo: climatología de la misma fecha en años previos × ajuste de nivel reciente que se disipa con el horizonte.
   Intervalos: cuantiles empíricos de los errores relativos del propio modelo en orígenes pasados. */
(function (root) {
'use strict';
const D0 = Date.UTC(2000, 10, 1), DAY = 864e5;
const MOFF = [[0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334], [0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]];
const isLeap = y => (y % 4 === 0 && y % 100 !== 0) || y % 400 === 0;
const YS = {}; for (let y = 1980; y <= 2060; y++) YS[y] = Math.round((Date.UTC(y, 0, 1) - D0) / DAY);
const dayIdx = (y, m, d) => YS[y] + MOFF[isLeap(y) ? 1 : 0][m] + d - 1;
const OFF = 4000, NCAL = 14000, CY = new Int16Array(NCAL), CM = new Int8Array(NCAL), CD = new Int8Array(NCAL), CDOY = new Int16Array(NCAL);
for (let i = 0; i < NCAL; i++) { const dt = new Date(D0 + (i - OFF) * DAY); CY[i] = dt.getUTCFullYear(); CM[i] = dt.getUTCMonth(); CD[i] = dt.getUTCDate(); CDOY[i] = Math.round((Date.UTC(CY[i], CM[i], CD[i]) - Date.UTC(CY[i], 0, 1)) / DAY); }
const ymd = t => ({ y: CY[t + OFF], m: CM[t + OFF], d: CD[t + OFF] });
const doy = t => CDOY[t + OFF];

/* Parámetros elegidos con orígenes 2010–2019 (ver pipeline/11_pronostico_ajuste.js) */
const DEFAULTS = { K: 12, lam: 1, W: 14, tau: 60, L: 28, c: 5 };
const HMAX = 400;           // días que cubre la trayectoria (12 meses calendario caben)

function makeSeries(vals) { const n = vals.length, cum = new Float64Array(n + 1); for (let i = 0; i < n; i++) cum[i + 1] = cum[i] + vals[i]; return { n, cum }; }
const sumRange = (S, a, b) => S.cum[b + 1] - S.cum[a];

/* Promedio diario de la ventana ±W alrededor de la misma fecha k años antes, solo con datos ≤ T. */
function climAt(S, t, T, K, lam, W) {
  const i = t + OFF, y = CY[i], m = CM[i]; let d = CD[i]; if (m === 1 && d === 29) d = 28;
  let num = 0, den = 0;
  for (let k = 1; k <= K; k++) {
    const yy = y - k, dd = (m === 1 && d === 28 && isLeap(yy)) ? 28 : d, c = dayIdx(yy, m, dd), a = c - W, b = c + W;
    if (a < 0 || b > T) continue;
    const w = Math.pow(lam, k - 1); num += w * (S.cum[b + 1] - S.cum[a]) / (2 * W + 1); den += w;
  }
  return den > 0 ? num / den : NaN;
}
function climPath(S, T, H, K, lam, W) { const out = new Float64Array(H + 1); for (let h = 1; h <= H; h++) out[h] = climAt(S, T + h, T, K, lam, W); return out; }
function levelRatio(S, T, P) {
  const L = P.L, a = T - L + 1; if (a < 0) return 1;
  let cl = 0, ok = 0; for (let t = a; t <= T; t++) { const v = climAt(S, t, T, P.K, P.lam, P.W); if (v === v) { cl += v; ok++; } }
  if (ok < 0.8 * L) return 1; cl *= L / ok;
  return Math.min(4, Math.max(0.25, (sumRange(S, a, T) + P.c) / (cl + P.c)));
}
/* Trayectoria diaria pronosticada (índice h = 1..H). mode: 'model' | 'clim' | 'naive' */
function path(S, T, H, P, mode) {
  const K = mode === 'naive' ? 1 : P.K, lam = mode === 'naive' ? 1 : P.lam;
  const clim = climPath(S, T, H, K, lam, P.W), fb = (sumRange(S, Math.max(0, T - 364), T)) / Math.min(365, T + 1);
  const out = new Float64Array(H + 1), r = mode === 'model' ? levelRatio(S, T, P) : 1, lr = Math.log(r);
  for (let h = 1; h <= H; h++) { let v = clim[h]; if (!(v === v)) v = fb; out[h] = (mode === 'model' && P.tau > 0) ? v * Math.exp(lr * Math.exp(-h / P.tau)) : v; }
  return { path: out, clim, r };
}

/* Periodos pronosticados a partir del origen T (último día observado). */
function periods(T) {
  const days = [], weeks = [], months = [];
  for (let h = 1; h <= 30; h++) days.push({ a: T + h, b: T + h });
  for (let w = 0; w < 12; w++) weeks.push({ a: T + 1 + 7 * w, b: T + 7 + 7 * w });
  const f = ymd(T + 1);
  for (let j = 0; j < 12; j++) {
    const a = Math.round((Date.UTC(f.y, f.m + j, 1) - D0) / DAY), b = Math.round((Date.UTC(f.y, f.m + j + 1, 1) - D0) / DAY) - 1;
    months.push({ a, b, y: new Date(Date.UTC(f.y, f.m + j, 1)).getUTCFullYear(), m: new Date(Date.UTC(f.y, f.m + j, 1)).getUTCMonth() });
  }
  return { day: days, week: weeks, month: months };
}
/* Parte pronosticada de un periodo (los días ≤ T ya son datos) y parte observada hasta T. */
function split(S, T, pa, pb, tr) {
  const obsPart = pa <= T ? sumRange(S, pa, Math.min(pb, T)) : 0; let rem = 0, nrem = 0;
  for (let t = Math.max(pa, T + 1); t <= pb; t++) { rem += tr[t - T]; nrem++; }
  return { obsPart, rem, nrem };
}

/* ---------- validación hacia atrás: errores relativos del modelo ---------- */
const KAPPA = 0.5; // pseudoconteo por día en la razón (obs+κ)/(pred+κ)
function buildPool(S, P, startIdx, step) {
  const pool = { day: { te: [], se: [], lr: [] }, week: { te: [], se: [], lr: [] }, month: { te: [], se: [], lr: [] } };
  for (let T = startIdx; T < S.n - 1; T += step) {
    const H = Math.min(HMAX, S.n - 1 - T), M = path(S, T, H, P, 'model'), per = periods(T), se = doy(T);
    for (const lvl of ['day', 'week', 'month']) for (const p of per[lvl]) {
      if (p.b > S.n - 1 || p.b - T > H) continue;
      const sp = split(S, T, p.a, p.b, M.path); if (sp.nrem === 0) continue;
      const obsRem = sumRange(S, Math.max(p.a, T + 1), p.b), k = KAPPA * sp.nrem;
      pool[lvl].te.push(p.b); pool[lvl].se.push(se); pool[lvl].lr.push(Math.log((obsRem + k) / (sp.rem + k)));
    }
  }
  return pool;
}
function quantile(sorted, q) { const i = (sorted.length - 1) * q, lo = Math.floor(i), hi = Math.ceil(i); return sorted[lo] + (sorted[hi] - sorted[lo]) * (i - lo); }
/* Cuantiles 10 % y 90 % de log((obs+κ)/(pred+κ)) con errores ya observables en T0, en estaciones parecidas. */
function intervalQ(pl, T0, season) {
  for (const win of [45, 90, 183]) {
    const v = []; for (let i = 0; i < pl.te.length; i++) { if (pl.te[i] > T0) continue; let dd = Math.abs(pl.se[i] - season); dd = Math.min(dd, 366 - dd); if (dd <= win) v.push(pl.lr[i]); }
    if (v.length >= 40) { v.sort((a, b) => a - b); return { lo: quantile(v, 0.1), hi: quantile(v, 0.9), n: v.length }; }
  }
  return null;
}

/* Pronóstico completo para la interfaz. */
function forecastAll(S, T, P, pool) {
  P = Object.assign({}, DEFAULTS, P || {});
  const H = HMAX, M = path(S, T, H, P, 'model'), C = path(S, T, H, P, 'clim'), per = periods(T), season = doy(T), out = { T, r: M.r, level: {} };
  for (const lvl of ['day', 'week', 'month']) {
    const q = pool ? intervalQ(pool[lvl], T, season) : null;
    out.level[lvl] = per[lvl].map(p => {
      const sm = split(S, T, p.a, p.b, M.path), sc = split(S, T, p.a, p.b, C.path), k = KAPPA * sm.nrem;
      const pred = sm.obsPart + sm.rem, clim = sc.obsPart + sc.rem;
      let lo = NaN, hi = NaN; if (q && sm.nrem > 0) { lo = sm.obsPart + Math.max(0, (sm.rem + k) * Math.exp(q.lo) - k); hi = sm.obsPart + Math.max(0, (sm.rem + k) * Math.exp(q.hi) - k); } else if (sm.nrem === 0) { lo = hi = pred; }
      const known = p.b <= S.n - 1 && p.b > T ? sumRange(S, p.a, p.b) : NaN;
      return { a: p.a, b: p.b, y: p.y, m: p.m, pred, lo, hi, clim, obsPart: sm.obsPart, obs: known };
    });
  }
  return out;
}

/* Métricas en orígenes dados: WAPE (restante), sesgo y cobertura del intervalo para modelo, climatología y mismo periodo del año anterior. */
function evaluate(S, P, origins, pool) {
  P = Object.assign({}, DEFAULTS, P || {});
  const acc = {}; for (const lvl of ['day', 'week', 'month']) acc[lvl] = { model: { abs: 0, obs: 0, err: 0 }, clim: { abs: 0, obs: 0, err: 0 }, naive: { abs: 0, obs: 0, err: 0 }, cov: 0, ncov: 0, n: 0 };
  for (const T of origins) {
    const M = path(S, T, HMAX, P, 'model'), C = path(S, T, HMAX, P, 'clim'), N = path(S, T, HMAX, P, 'naive'), per = periods(T), season = doy(T);
    for (const lvl of ['day', 'week', 'month']) {
      const q = pool ? intervalQ(pool[lvl], T, season) : null;
      for (const p of per[lvl]) {
        if (p.b > S.n - 1) continue;
        const sm = split(S, T, p.a, p.b, M.path); if (sm.nrem === 0) continue;
        const obsRem = sumRange(S, Math.max(p.a, T + 1), p.b), A = acc[lvl];
        for (const [key, tr] of [['model', M.path], ['clim', C.path], ['naive', N.path]]) { const s = split(S, T, p.a, p.b, tr); A[key].abs += Math.abs(obsRem - s.rem); A[key].obs += obsRem; A[key].err += s.rem - obsRem; }
        A.n++;
        if (q) { const k = KAPPA * sm.nrem, lo = Math.max(0, (sm.rem + k) * Math.exp(q.lo) - k), hi = (sm.rem + k) * Math.exp(q.hi) - k; A.ncov++; if (obsRem >= lo && obsRem <= hi) A.cov++; }
      }
    }
  }
  return acc;
}

const api = { DEFAULTS, HMAX, makeSeries, dayIdx, ymd, doy, path, periods, buildPool, intervalQ, forecastAll, evaluate, levelRatio, climAt, sumRange, quantile };
if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.FC = api;
})(typeof window !== 'undefined' ? window : globalThis);
