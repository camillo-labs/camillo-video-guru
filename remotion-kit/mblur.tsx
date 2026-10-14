// Directional motion blur for fast slides: a layer moving v px/frame gets a Gaussian blur along its direction of
// travel (about 0.12 px of blur per px of travel, capped), so 100+ px/frame moves smear instead of strobing.
// Mount <BlurDefs/> once; use mblur(vx, vy) as the moving layer's CSS filter.
import React from "react";

const STEPS = [0, 2, 4, 6, 8, 11, 14, 18, 22];
export const BlurDefs: React.FC = () => (
  <svg width={0} height={0} style={{ position: "absolute" }}>
    <defs>
      {STEPS.slice(1).map((s) => (
        <React.Fragment key={s}>
          <filter id={`mbx${s}`} x="-10%" y="-2%" width="120%" height="104%"><feGaussianBlur stdDeviation={`${s} 0`} /></filter>
          <filter id={`mby${s}`} x="-2%" y="-10%" width="104%" height="120%"><feGaussianBlur stdDeviation={`0 ${s}`} /></filter>
        </React.Fragment>
      ))}
    </defs>
  </svg>
);
const nearest = (v: number) => STEPS.reduce((a, b) => (Math.abs(b - v) < Math.abs(a - v) ? b : a), 0);
export const mblur = (vx: number, vy = 0): string | undefined => {
  const horizontal = Math.abs(vx) >= Math.abs(vy);
  const s = nearest(Math.min(22, Math.abs(horizontal ? vx : vy) * 0.12));
  return s === 0 ? undefined : `url(#${horizontal ? "mbx" : "mby"}${s})`;
};
// velocity of a position function at frame f, in px/frame
export const vel = (fn: (f: number) => number, f: number) => fn(f + 0.5) - fn(f - 0.5);
