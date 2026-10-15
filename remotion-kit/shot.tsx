// One full-bleed shot: a photo with a slow Ken Burns move, or a muted video clip, cover-cropped to 9:16 around a focus
// point, lightly graded towards the engraved palette (warm, a touch desaturated), with a soft vignette.
// Footage credits: public/footage/CREDITS.md.
import React from "react";
import { Img, OffthreadVideo, interpolate, staticFile, useCurrentFrame } from "remotion";

export const Shot: React.FC<{
  src: string;               // file in public/footage
  dur: number;               // frames this shot is on screen (for the move)
  focus?: [number, number];  // 0..1 focus point in the source (object-position)
  zoom?: [number, number];   // scale at start and end
  drift?: [number, number];  // px drift over the shot
  start?: number;            // seconds into a video
  grade?: string;
}> = ({ src, dur, focus = [0.5, 0.5], zoom = [1.04, 1.14], drift = [0, -30], start = 0, grade }) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [0, Math.max(1, dur)], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const s = zoom[0] + (zoom[1] - zoom[0]) * p;
  const style: React.CSSProperties = {
    position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover",
    objectPosition: `${focus[0] * 100}% ${focus[1] * 100}%`,
    transform: `translate(${drift[0] * p}px, ${drift[1] * p}px) scale(${s})`,
    filter: grade ?? "contrast(1.06) saturate(0.88) sepia(0.06) brightness(0.97)",
  };
  const isVideo = src.endsWith(".mp4");
  return (
    <div style={{ position: "absolute", inset: 0, overflow: "hidden", background: "#0b0a09" }}>
      {isVideo ? <OffthreadVideo src={staticFile(`footage/${src}`)} startFrom={Math.round(start * 30)} muted style={style} /> : <Img src={staticFile(`footage/${src}`)} style={style} />}
      <div style={{ position: "absolute", inset: 0, background: "radial-gradient(120% 90% at 50% 45%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.42) 100%)" }} />
    </div>
  );
};
