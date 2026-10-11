---
name: audio-pipeline
description: Use for music and sound effects - sourcing permissively licensed music, procedural Web Audio SFX, normalising, looping, and wiring the mixer.
---
# Audio pipeline (budget {{BUDGET_USD}} USD; see CLAUDE.md section 6)

- **Music.**
  - Source only CC0 or CC-BY tracks from libraries with a clear licence page. Prefer the instrumentation named in TASK.md section 14.
  - For each track, log the source URL, author, licence and local path in `Docs/LICENSES.md` and the in-game Credits, and write an `asset.json` with route `external`.
  - Store under `assets/external/<source>/`.
  - Never use tracks ripped from games or films, or "free for personal use" tracks without a stated licence.
- **Convert and normalise:**
  - `ffmpeg -i in.wav -af loudnorm=I=-16:TP=-1.5:LRA=11 -c:a libopus -b:a 96k out.ogg`
  - Each track ≤ 1.5 MB, ≤ 8 MB in total. Lazy-load the music after the first user input.
- **Seamless loop:** crossfade the tail into the head (ffmpeg `acrossfade` on two trimmed copies), keep the loop point on a zero crossing, and listen at the loop point. If you cannot listen, check that the waveform energy is continuous.
- **No fitting track?** Build a procedural drone/ostinato in `src/audio/` (Web Audio oscillators plus filtered noise) and log the decision.
- **SFX are procedural** (Web Audio, no files): one small function per cue, with parameters (pitch, decay, noise mix) in data. The cue list is in TASK.md section 14.
- **Mixer:** groups for music and SFX (and UI), a master slider, mute, and a respectful default level. Nothing plays before the first user gesture.
- Every action with feedback needs a sound; list the gaps in TODO.md.
