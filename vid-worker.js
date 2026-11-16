/* Musaed voice ID worker: turns 16 kHz speech into a voiceprint vector, on the phone. */
import * as ort from "./lib/vid/ort.wasm.bundle.min.mjs";
ort.env.wasm.numThreads = 1;
ort.env.wasm.wasmPaths = new URL("./lib/vid/", self.location).href;
let sess = null, MEL = null, WIN = null;
const N = 512, FL = 400, SH = 160, NB = 80;
function melBank() {
  const m = f => 1127 * Math.log(1 + f / 700), lo = m(20), hi = m(8000), d = (hi - lo) / (NB + 1), W = [];
  for (let b = 0; b < NB; b++) {
    const l = lo + b * d, c = l + d, r = c + d, row = new Float64Array(N / 2 + 1);
    for (let i = 0; i < N / 2; i++) { const mf = m(i * 16000 / N); if (mf > l && mf < r) row[i] = mf <= c ? (mf - l) / (c - l) : (r - mf) / (r - c); }
    W.push(row);
  }
  return W;
}
function fft(re, im) {
  for (let i = 1, j = 0; i < N; i++) { let bit = N >> 1; for (; j & bit; bit >>= 1) j ^= bit; j ^= bit; if (i < j) { [re[i], re[j]] = [re[j], re[i]]; [im[i], im[j]] = [im[j], im[i]]; } }
  for (let len = 2; len <= N; len <<= 1) {
    const a = -2 * Math.PI / len, wr = Math.cos(a), wi = Math.sin(a);
    for (let i = 0; i < N; i += len) {
      let cr = 1, ci = 0;
      for (let k = 0; k < len / 2; k++) {
        const ur = re[i + k], ui = im[i + k], xr = re[i + k + len / 2], xi = im[i + k + len / 2];
        const vr = xr * cr - xi * ci, vi = xr * ci + xi * cr;
        re[i + k] = ur + vr; im[i + k] = ui + vi; re[i + k + len / 2] = ur - vr; im[i + k + len / 2] = ui - vi;
        const t = cr * wr - ci * wi; ci = cr * wi + ci * wr; cr = t;
      }
    }
  }
}
function fbank(x) {
  if (!MEL) { MEL = melBank(); WIN = new Float64Array(FL); for (let i = 0; i < FL; i++) WIN[i] = Math.pow(0.5 - 0.5 * Math.cos(2 * Math.PI * i / (FL - 1)), 0.85); }
  const T = 1 + Math.floor((x.length - FL) / SH), out = new Float32Array(T * NB), mean = new Float64Array(NB);
  const re = new Float64Array(N), im = new Float64Array(N), f = new Float64Array(FL), eps = 1.1920928955078125e-7;
  for (let t = 0; t < T; t++) {
    let s = 0; for (let i = 0; i < FL; i++) { f[i] = x[t * SH + i] * 32768; s += f[i]; }
    s /= FL; for (let i = 0; i < FL; i++) f[i] -= s;
    for (let i = FL - 1; i > 0; i--) f[i] -= 0.97 * f[i - 1]; f[0] -= 0.97 * f[0];
    re.fill(0); im.fill(0); for (let i = 0; i < FL; i++) re[i] = f[i] * WIN[i];
    fft(re, im);
    for (let b = 0; b < NB; b++) {
      const w = MEL[b]; let e = 0;
      for (let i = 0; i <= N / 2; i++) if (w[i]) e += w[i] * (re[i] * re[i] + im[i] * im[i]);
      const v = Math.log(Math.max(e, eps)); out[t * NB + b] = v; mean[b] += v;
    }
  }
  for (let b = 0; b < NB; b++) mean[b] /= T;
  for (let t = 0; t < T; t++) for (let b = 0; b < NB; b++) out[t * NB + b] -= mean[b];
  return { feats: out, T };
}
self.onmessage = async (e) => {
  const { id, pcm } = e.data || {};
  try {
    if (!pcm || pcm.length < 16000) throw new Error("too short");
    if (!sess) sess = await ort.InferenceSession.create(new URL("./lib/vid/voice.onnx", self.location).href, { executionProviders: ["wasm"] });
    const { feats, T } = fbank(pcm);
    const r = await sess.run({ feats: new ort.Tensor("float32", feats, [1, T, NB]) });
    const v = r[sess.outputNames[0]].data; let n = 0; for (let i = 0; i < v.length; i++) n += v[i] * v[i]; n = Math.sqrt(n) || 1;
    const emb = new Array(v.length); for (let i = 0; i < v.length; i++) emb[i] = v[i] / n;
    self.postMessage({ id, emb });
  } catch (err) { self.postMessage({ id, error: String(err && err.message || err) }); }
};
self.postMessage({ ready: true });
