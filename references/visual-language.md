# Visual language

Choose **one** language in your style brief (`making-it-yours.md`), then put every element into it. In the case study, cutting between paper illustration and real footage looked cheap until everything moved into a single language.

## Principles that hold for any language

- **No empty frames.** A lone element on a flat background reads as AI-made. Add the detail that belongs to your language:
  - for maps: grid, scale, ticks, brackets, cartouche;
  - for type: a real layout grid;
  - for collage: layered texture and paper edges.
- **Show the subject, not a sentence about it.** Point at the thing itself (the photo, the map, the chart) rather than putting up text-only cards or coloured label chips: a marker, a pointer line, a pinned photo, a highlight.
- **Real images only.** Use real photos and footage for real events and places. Never AI-generate them. Maps and charts must come from data.
- **Keep things consistent.** One grade across all footage, one set of easings, one caption style.

## Technical notes that hold for any language

- **Maps:** for comparing areas or distances, use a **local equal-scale metric frame** (x east, y south, metres) per area, not Web Mercator. Good sources:
  - burned areas: the EU fire service's EFFIS WFS;
  - context layers: OpenStreetMap via Overpass.
- **Map over footage** (the case study's language, shown here only as an example of executing one fully):
  - linework at 0.2–0.9 white alpha by rank;
  - the subject as a hatched fill with a glowing edge;
  - labels with a dark halo (`paint-order: stroke`);
  - the footage dimmed (`brightness ~0.4`, `saturate ~0.5`, slight blur);
  - a radial mask so the edge of the data never shows;
  - a moving grid and corner brackets so the frame never looks empty.
- **Captions** (a starting point; change the faces and colours to your palette):
  - one bold face at about 8.5% of the frame width (92 px at 1080), tracking -0.01em;
  - at most 3 lines, built word by word from the voice timestamps;
  - entrance: rise 0.32 em, fade over 6 frames, blur from 8 to 0 px over 5 frames;
  - one emphasis colour; outline letters only over dark, quiet backgrounds;
  - shadow `0 4px 18px rgba(0,0,0,.45), 0 2px 4px rgba(0,0,0,.5)`;
  - a soft scrim behind captions on bright footage;
  - keep text between 14% and 65% of the frame height (Reels interface);
  - no "eyebrow" text above titles.
- **Footage:**
  - pre-crop 4K landscape clips to 1080×1920 at 30 fps;
  - give every still a camera move (push 1.0 → 1.12, eased, or a pull);
  - collages should be about twice as dense as feels safe, never a wall.
