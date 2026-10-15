# Footage, licences, facts and ad rules

## Footage and data

| Source | How | Licence and credit |
|---|---|---|
| **Wikimedia Commons** | API at `commons.wikimedia.org/w/api.php` with a descriptive User-Agent: event categories, a photographer's uploads (`list=usercontribs`), `filetype:video` / `audio` searches; `prop=imageinfo&iiprop=url|size|mime|extmetadata` for licence and author | Mostly CC BY-SA 4.0. Credit the author and Commons. Full-size downloads hit HTTP 429: retry with a 1920 px thumbnail (`/thumb/…/1920px-<name>`) with pauses. |
| **Pexels** | Video file URLs from the page (`videos.pexels.com/video-files/...`) | Pexels licence; credit is courtesy ("Name / Pexels") |
| **EFFIS** burned areas | WFS layer `modis.ba.poly` with a bbox | CC BY 4.0, "© European Union, EFFIS"; say that perimeters were simplified |
| **OpenStreetMap** | Overpass API queries | ODbL, "© OpenStreetMap contributors" |
| **Freesound** | CC0 / CC BY recordings | Downloading the original needs a login, but the HQ preview MP3 is public |
| **ElevenLabs** output | Voice, music, sound effects | Under your plan's terms |

- **Downloads:** approve each one explicitly (file, source, size). Save into a new folder and record credits in `CREDITS.md` next to the files (a small download script that also writes the credits file is worth the five minutes).
- **Honest images:** real photos and footage only. Maps must come from data. No AI-generated images of the real event, place or people.
- **When nothing exists from the event:** say so, and offer a labelled proxy (a real recording of a similar event) or a designed sound. Never pass a proxy off as the event.

## Fact routine

1. Take every number from a primary source and keep the source next to the script.
2. **Re-read live sources on delivery day** (donation totals change). Check that every label is exact. Example: a donation page showed both "donations collected" and a higher "total raised" (which included corporate sponsorship); the on-screen label had to match the figure used.
3. Avoid claims you can't check: "€X plants a tree", "your gift is doubled", blame for the fire.
4. Measure distances and areas from the geometry yourself (a local metric frame), and keep the calculation with the script.

## Meta ad constraints (as of Oct 2026)

- **EU social-issue ads:** since October 2025, Meta no longer runs political, electoral or social-issue ads in the EU. Talk about a place, its damage and its repair, not climate policy. Avoid clips of parliament.
- **Reels layout:** 9:16; keep text between 14% and 65% of the height and away from the right-hand edge.
- **Thumbnail:** upload a custom 9:16 thumbnail, the strongest single frame or the image creative re-laid out for 9:16.
- **Detailed targeting:**
  - Use only options that exist. Demographics are Education, Financial (income is **US-only**), Life events, Parents (by children's age), Relationship and Work. Behaviours are travel, mobile device, purchase behaviour, digital activities, anniversary and expats. Donor categories went in 2018 and cause-related options in 2022.
  - Interests combine with **OR**, and Advantage+ may widen them.
- **Course briefs:** match the deliverable formats exactly (Word means .docx, not PDF), the exact file names, the length window and the character limits. Commit to single choices, such as one button label.
