// A drawn 3D object you can film. Model it in world units (x runs right-down, y toward the viewer left-down, z up)
// and draw it as SVG paths through a projection: `P`/`poly` give the fixed isometric view of the hairline drawings;
// `camProj` gives a perspective camera that orbits a target and matches P when far away at the iso angles, so a shot
// can start isometric and swing round into the object without a cut. Draw a face only when `proj.sees` it, and put
// flat content (a screen, a label) on a plane with `planeFit`, clipped to the plane's projected outline.
// From the Nightcrew launch film (dev/nightcrew-launch, src/iso.ts and src/IsoLaptop.tsx).

export type V3 = [number, number, number];
const C30 = Math.cos(Math.PI / 6);
const S30 = 0.5;

export const P = ([x, y, z]: V3): [number, number] => [(x - y) * C30, (x + y) * S30 - z];
export const add = (a: V3, b: V3): V3 => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
export const mul = (a: V3, k: number): V3 => [a[0] * k, a[1] * k, a[2] * k];

/** SVG path through projected points, closed by default. */
export const poly = (pts: V3[], close = true) =>
  pts.map((p, i) => `${i ? "L" : "M"}${P(p)[0].toFixed(2)},${P(p)[1].toFixed(2)}`).join(" ") + (close ? " Z" : "");

/** SVG matrix that draws 2D content (x right, y down) onto the plane at origin with axes u (x) and v (y). */
export const planeMatrix = (origin: V3, u: V3, v: V3) => {
  const [ox, oy] = P(origin);
  const lin = (d: V3) => [(d[0] - d[1]) * C30, (d[0] + d[1]) * S30 - d[2]];
  const [a, b] = lin(u);
  const [c, d] = lin(v);
  return `matrix(${a} ${b} ${c} ${d} ${ox} ${oy})`;
};

/** A face is visible when its outward normal points toward the viewer, who looks along -(1, 1, 1). */
export const facing = (n: V3) => n[0] + n[1] + n[2] > 0;

// ---------- a moving camera ----------

/** A projection: where a world point lands (in the same 2D units as P), and whether a face at a point is seen. */
export type Proj = { p: (v: V3) => [number, number]; sees: (n: V3, at: V3) => boolean };
export const ISO: Proj = { p: P, sees: (n) => facing(n) };

const dot = (a: V3, b: V3) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const cross = (a: V3, b: V3): V3 => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const norm = (a: V3): V3 => mul(a, 1 / Math.hypot(a[0], a[1], a[2]));
export const sub = (a: V3, b: V3): V3 => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];

/** The isometric view's angles: looking down -(1, 1, 1). */
export const ISO_YAW = 45;
export const ISO_PITCH = (Math.asin(1 / Math.sqrt(3)) * 180) / Math.PI;

/**
 * A perspective camera orbiting `target`: yaw from +x toward +y, pitch up from the floor, `dist` away. The target
 * lands on `anchor` (P units) at `zoom` times the isometric scale. Far away at the iso angles it matches P.
 */
export type Cam = { target: V3; yaw: number; pitch: number; dist: number; zoom: number; anchor: [number, number] };

export const camProj = (c: Cam): Proj => {
  const yaw = (c.yaw * Math.PI) / 180;
  const pitch = (c.pitch * Math.PI) / 180;
  const back: V3 = [Math.cos(pitch) * Math.cos(yaw), Math.cos(pitch) * Math.sin(yaw), Math.sin(pitch)];
  const eye = add(c.target, mul(back, c.dist));
  const fw = mul(back, -1);
  const right = norm(cross([0, 0, 1], fw));
  const down = cross(right, fw);
  const k0 = c.zoom * Math.sqrt(1.5) * c.dist;
  return {
    p: (v) => {
      const d = sub(v, eye);
      const k = k0 / Math.max(1e-3, dot(d, fw));
      return [c.anchor[0] + dot(d, right) * k, c.anchor[1] + dot(d, down) * k];
    },
    sees: (n, at) => dot(sub(eye, at), n) > 0,
  };
};

/** SVG path through projected points. */
export const polyP = (proj: Proj, pts: V3[], close = true) =>
  pts.map((p, i) => `${i ? "L" : "M"}${proj.p(p)[0].toFixed(2)},${proj.p(p)[1].toFixed(2)}`).join(" ") + (close ? " Z" : "");

/**
 * The SVG matrix that draws 2D content (x right, y down, w × h) onto a plane: the affine map fitted to the four
 * projected corners. Exact under parallel projection and for a plane facing the camera; close enough in between.
 */
export const planeFit = (proj: Proj, origin: V3, u: V3, v: V3, w: number, h: number) => {
  const c00 = proj.p(origin);
  const c10 = proj.p(add(origin, mul(u, w)));
  const c01 = proj.p(add(origin, mul(v, h)));
  const c11 = proj.p(add(add(origin, mul(u, w)), mul(v, h)));
  const a = (c10[0] - c00[0] + c11[0] - c01[0]) / (2 * w);
  const b = (c10[1] - c00[1] + c11[1] - c01[1]) / (2 * w);
  const cc = (c01[0] - c00[0] + c11[0] - c10[0]) / (2 * h);
  const d = (c01[1] - c00[1] + c11[1] - c10[1]) / (2 * h);
  const mx = (c00[0] + c10[0] + c01[0] + c11[0]) / 4;
  const my = (c00[1] + c10[1] + c01[1] + c11[1]) / 4;
  return `matrix(${a} ${b} ${cc} ${d} ${mx - a * (w / 2) - cc * (h / 2)} ${my - b * (w / 2) - d * (h / 2)})`;
};
