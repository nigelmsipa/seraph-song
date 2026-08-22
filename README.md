SERAPH SONG - PROJECT OVERVIEW
==============================

REPO: https://github.com/nigelmsipa/seraph-song

PURPOSE
=======
A word-for-word rendition of the King James Version Bible set to music using Suno AI.
Starting with the KJV, covering Genesis through Revelation.

PROGRESS
=========
COMPLETED (needs improvement):
- Genesis (60 songs) — style analysis done
- Exodus (52 songs) — style analysis done
- Leviticus / Lev 3 (45 songs) — style analysis done
- Numbers / Numbers 2 (43 songs) — style analysis done

IN PROGRESS (needs redo):
- Deuteronomy (88 songs in Deutronomy 2, all using one style — too monotonous)

NOT YET STARTED:
- Joshua through Revelation

STRUCTURE
=========
/memory-method-bible/    — Bible Memory Method framework (scene-based pericope divisions)
  /data/base-structure/  — JSON files dividing each book into stories and scenes
  CONVERSION_GUIDE.md    — Master specification for the method
  README.md             — Overview of the framework
  
/source-texts/           — Bible source texts
  KJV.txt               — King James Version full text (4.6MB)

/style_analysis.txt      — Cross-book style analysis (Genesis through Numbers)
/genesis_workspace.txt   — Genesis song details and styles
/deuteronomy_2_workspace.txt — Deuteronomy workspace data (showing single-style problem)
/preferences_and_guidelines.txt — User preferences, what works/doesn't, proven style palette

RELATED REPOS
=============
- nigelmsipa/memory-method-bible — The structural framework (all 66 books, 296 stories, 7,962 scenes)
- nigelmsipa/public-domain-bibles — KJV and 16 other Bible translations as clean plain text
- nigelmsipa/snail-bibles — Word-level Bible audio alignment data
- nigelmsipa/wolf-and-word — The Snail compiler (source docs → playable knowledge artifacts)
- nigelmsipa/snail — Word-precise alignment engine (audio + text → timing data)

WORKFLOW
========
1. Use Memory Method Bible to divide each book into scenes (natural pericopes)
2. Group scenes into chunks that fit Suno's ~4000 character limit
3. Assign appropriate style from proven palette based on scene/story content type
4. Generate in Suno (currently v4.5+/v5/v5.5)
5. Iterate on beats first if needed (separate beat workspaces)
6. Assemble final word-for-word rendition

SUNO WORKSPACES (Bible-related):
- Genesis (60 songs), Genesis Beats (20), Genesis Blitz (18), Gen 2 (0)
- Exodus (52), Exodus 2 (12)
- Lev 3 (45) [Leviticus]
- Numbers 2 (43), Numbers 3 (62), Numbers instrumentals (181), Numbers 0 (38)
- Deutronomy (9), Deutronomy 2 (88)
- Joshua (1)
- Revelation Beat (139)

SUNO LOGIN: nigelmsipa@gmail.com (Google OAuth)
Suno profile: https://suno.com/me