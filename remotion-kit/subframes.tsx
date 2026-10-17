import React from "react";
import { AbsoluteFill } from "remotion";

/**
 * Real motion blur: the whole frame drawn at n moments across half a frame and averaged, so each part smears along its
 * own path and nothing that stands still goes soft. Each copy must be opaque (it carries its own background): copy i
 * sits on the ones below at opacity 1/(i+1), which is an exact average with normal blending. (Additive blending of
 * transparent copies shifted the colours in Chrome's software compositor.) `speed` is the fastest on-screen movement
 * in px per frame. The shutter is open for half a frame, and the copies sit at most about 1.2 px apart (up to 16), so
 * hairlines smear instead of showing as separate lines; below 1.5 px of travel the frame is drawn once.
 *
 * Use it at the root of the composition, around a function that renders one complete frame (background, shot,
 * captions) at a fractional frame number; fix the shot from the whole frame so samples never mix two shots across a
 * cut. Measure `speed` at the fastest-moving points: in perspective, the near corners. Lower `max` for heavy frames.
 * From the Nightcrew launch film (dev/nightcrew-launch, src/subframes.tsx and the root of src/Sting4.tsx).
 */
export const SubFrames: React.FC<{ f: number; speed: number; max?: number; render: (fr: number) => React.ReactNode }> = ({ f, speed, max = 16, render }) => {
  const span = 0.5 * speed;
  const n = span < 1.5 ? 1 : Math.min(max, Math.ceil(span / 1.2) + 1);
  if (n === 1) return <>{render(f)}</>;
  return (
    <>
      {Array.from({ length: n }, (_, i) => (
        <AbsoluteFill key={i} style={{ opacity: 1 / (i + 1) }}>
          {render(f + 0.5 * (i / (n - 1) - 0.5))}
        </AbsoluteFill>
      ))}
    </>
  );
};
