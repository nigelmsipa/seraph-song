---
schema_version: 1
title: "Seraph Song"
date: "2026-04-08"
type: project_overview
project: "seraph-song"
state: stable
tags:
  - "scripture"
  - "music"
  - "karaoke"
summary: "Bible chapters set word-for-word to music (KJV)."
source_date: ""
related: []
---
# Seraph Song

*Bible chapters set word-for-word to music (KJV). One video per book.*

---

## Status (April 2026)

- Genesis through Numbers: done
- Deuteronomy: in progress / starting
- Visual language: **locked** (see below)
- bible_video_gen.py: working local reference exists in `~/Downloads`; pipeline is usable and refinable

---

## The Why

Scripture has an attention and intimacy deficit. People skim it, rush it, treat it like a checklist. Music solves that by changing the relationship to time — you can't rush a song you want to stay inside. Word-for-word KJV set to music, no paraphrase.

---

## Audio

**Suno** generates the songs. Word-for-word KJV. This is the irreducible human step — songs must be fire or no one listens. Everything else is pipeline. Accept this bottleneck.

---

## Visual Language — LOCKED

**Karaoke three-line display:**
- Previous line — faded/ghost, smaller, above
- Current line — full opacity, large, center
- Next line — faded/ghost, smaller, below

Always oriented. Always know where you are and where you're going. Viewer can follow along or sing along.

**Timing and wayfinding are the real UX layer:**
- Shift lyric changes slightly early so the eye arrives before the voice does
- Keep the next line visible so the viewer is never reading reactively
- Hold the last lyric through longer blank stretches so the system never feels lost or absent
- Track chapter and verse changes in the SRT itself so orientation is structural, not hand-waved

The important lesson is that tiny timing and orientation decisions changed usability more than any decorative flourish. This project got better by making the reading experience legible, anticipatory, and calm.

**Background:** flat color per book (one hex value). Not gradient, not grain, not imagery. One variable changes per book — everything else is constant. Cream/warm variants also viable for a single-color-for-all approach.

**Typography:** Lora (serif). Off-black text on colored background. Chapter reference quiet, bottom-left. The Word is the show — nothing competes with it.

**Frames are generated programmatically.** Design the template once in Paper. Python stamps it 1,189 times.

---

## Full Production Pipeline

1. **Create audio** — Suno, word-for-word KJV per chapter (the time cost, non-negotiable)
2. **Upload to YouTube** — auto-captions generate timestamps (free forced-aligner, the clever move)
3. **Fix the SRT** — feed raw auto-captions + actual KJV text to Claude → correct grammar word-for-word, preserve timestamps
4. **Add structure to the SRT** — insert chapter + verse markers so the file knows where the reader is
5. **Push timestamps forward** — shift ~0.5–1s so viewer sees line just before it's sung (anticipatory karaoke)
6. **Hold long silences** — leave the prior lyric on screen when the music pauses so orientation doesn't collapse
7. **Run video generator:**
   ```
   python3 bible_video_gen.py \
     --srt   "Genesis_1_corrected.srt" \
     --audio "Genesis_1.mp3" \
     --book  "Genesis" \
     --chapter 1 \
     --color "#5C4A2A" \
     --out   "Genesis_1_final.mp4"
   ```
8. **Stitch chapters** — terminal concatenates all chapter videos into one book video
9. **Final YouTube upload** — title includes book name, chapter range

---

## bible_video_gen.py

Python + Pillow + FFmpeg. Reads corrected SRT, chapter/verse markers, renders three-line karaoke frames, assembles with audio into MP4.

**Dependencies:** `pip install Pillow`, `xbps-install ffmpeg`

Working local reference exists at `~/Downloads/bible_video_gen.py`. `~/Downloads/build_numbers.py` also contains related production logic.

---

## Key Insight

The YouTube auto-caption step is the cleverest part. Don't fight timestamp generation — borrow it from a system that already does it for free, then correct only the grammar layer. Non-obvious, but it works.

The second insight is subtler: karaoke lives or dies on anticipation and orientation. Showing the next line, nudging the current line early, preserving continuity through silence, and surfacing chapter/verse changes made the experience feel usable in a way styling alone never could.

---

## Future / Out of Scope for Now

- Interactive web version: JS reads SRT timestamps live, highlights current line. No frames, no rendering. Better UX for web. Separate project.
- Spotify / other platforms: later
- Rust bespoke tool: build only after 2+ books deep, when friction points are well-known

---

## Relationship to Other Projects

- Wolf & The Word — same source material; eventually integrate (song playback in memorization app?)
- Portfolio — strong case study because the best decisions are interaction decisions, not just visual ones: anticipatory timing, text wayfinding, and disciplined restraint
