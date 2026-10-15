// Word-timed captions: bold capitals built word by word from voice timestamps (elevenlabs_tools.py tts output),
// stacking downward in pages of up to 3 lines. Each word rises 0.32 em, fades in over 6 frames and un-blurs over
// 5 frames; a page leaves by rising and fading over 5 frames. In display text, *word* = emphasis colour and
// _word_ = outline letters (use outline only over dark, quiet backgrounds).
import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";

export type Word = [string, number, number]; // spoken word, start s, end s (voice time)
export type CaptionBlock = {
  words: Word[];        // spoken words of this sentence, from the timestamps file
  text?: string;        // what to show; defaults to the spoken words. Use non-breaking spaces to keep "1 955" together
  y: number;            // top of the block in px
  size?: number;        // font size in px (default 92 at 1080 wide)
  until?: number;       // voice seconds when the block must be gone (default: last word end + 0.45 s)
  ink?: boolean;        // dark text for light backgrounds
};

const ease = (x: number) => 1 - Math.pow(1 - Math.min(1, Math.max(0, x)), 3);
type Tok = { w: string; t: number; em: boolean; outline: boolean };

export const WordCaptions: React.FC<{
  blocks: CaptionBlock[];
  toFrame?: (voiceSeconds: number) => number; // map voice time to film frames (include inserted pauses here)
  font?: string;
  emphasis?: string;
  shadow?: string;
  maxWidth?: number;
}> = ({ blocks, toFrame, font = "InterTight, Arial, sans-serif", emphasis = "rgb(240,200,21)", shadow = "0 4px 18px rgba(0,0,0,0.45), 0 2px 4px rgba(0,0,0,0.5)", maxWidth = 960 }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const fr = toFrame ?? ((s: number) => Math.round(s * fps));
  const out: React.ReactNode[] = [];
  blocks.forEach((b, bi) => {
    const size = b.size ?? 92;
    const parts = (b.text ?? b.words.map((w) => w[0]).join(" ")).split(" ");
    const m = b.words.length;
    // map each shown token to a spoken word's start (proportionally when the counts differ)
    const toks: Tok[] = parts.map((p, i) => ({
      w: p.replace(/[*_]/g, "").toUpperCase(),
      t: fr(b.words[parts.length === m ? i : Math.round((i * (m - 1)) / Math.max(1, parts.length - 1))][1]),
      em: p.includes("*"), outline: p.includes("_"),
    }));
    // greedy line wrap (about 0.6 em per capital), then pages of 3 lines
    const lines: Tok[][] = [[]];
    let wNow = 0;
    for (const tk of toks) {
      const ww = tk.w.length * size * 0.6, sp = size * 0.28;
      if (lines[lines.length - 1].length && wNow + sp + ww > maxWidth) { lines.push([]); wNow = 0; }
      lines[lines.length - 1].push(tk);
      wNow += (wNow ? sp : 0) + ww;
    }
    const pages: Tok[][][] = [];
    for (let i = 0; i < lines.length; i += 3) pages.push(lines.slice(i, i + 3));
    const end = fr(b.until ?? b.words[m - 1][2] + 0.45);
    pages.forEach((pg, pi) => {
      const a = pg[0][0].t;
      const z = pi + 1 < pages.length ? pages[pi + 1][0][0].t - 1 : end;
      if (f < a || f >= z) return;
      const exit = ease((f - (z - 5)) / 5);
      out.push(
        <div key={`${bi}-${pi}`} style={{ position: "absolute", left: 40, right: 40, top: b.y, textAlign: "center", fontFamily: font, fontWeight: 800, fontSize: size, lineHeight: 1.02, letterSpacing: "-0.01em" }}>
          {pg.map((ln, li) => (
            <div key={li} style={{ whiteSpace: "nowrap" }}>
              {ln.map((tk, j) => {
                const p = ease((f - tk.t) / 9);
                const o = f < tk.t ? 0 : Math.min(1, (f - tk.t) / 6) * (1 - exit);
                const bl = f < tk.t ? 8 : Math.max(0, 8 * (1 - (f - tk.t) / 5));
                const base = b.ink ? "#141210" : "#fff";
                return (
                  <span key={j} style={{ display: "inline-block", padding: "0.05em 0.03em 0.1em", marginRight: j < ln.length - 1 ? "0.24em" : 0 }}>
                    <span style={{ display: "inline-block", opacity: o, transform: `translateY(${(1 - p) * 0.32 - exit * 0.22}em)`, filter: bl > 0.3 ? `blur(${bl}px)` : undefined,
                      color: tk.outline ? "transparent" : tk.em ? emphasis : base, WebkitTextStroke: tk.outline ? `${Math.max(2, size * 0.028)}px ${base}` : undefined,
                      textShadow: tk.outline || b.ink ? "none" : shadow }}>{tk.w}</span>
                  </span>
                );
              })}
            </div>
          ))}
        </div>,
      );
    });
  });
  return <>{out}</>;
};
