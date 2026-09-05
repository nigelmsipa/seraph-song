#!/usr/bin/env python3
"""
Two-pass audio analysis for Suno prompt generation.
  Pass 1: aubio + sox + ffprobe  — BPM, pitch classes, dynamics
  Pass 2: librosa                — chroma, H/P ratio, spectral texture, groove
"""

import sys
import subprocess
import json
import numpy as np
from collections import Counter

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

SCALE_TEMPLATES = {
    'major':      [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1],
    'minor':      [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0],
    'dorian':     [1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0],
    'mixolydian': [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0],
    'phrygian':   [1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0],
}


def detect_key(pitch_dist):
    dist = np.array([pitch_dist.get(i, 0) for i in range(12)], dtype=float)
    if dist.sum() > 0:
        dist /= dist.sum()
    best_score, best_key, best_mode = -1, 'C', 'major'
    for mode, template in SCALE_TEMPLATES.items():
        t = np.array(template, dtype=float)
        for root in range(12):
            score = float(np.dot(dist, np.roll(t, root)))
            if score > best_score:
                best_score, best_key, best_mode = score, NOTE_NAMES[root], mode
    return best_key, best_mode, best_score


# ─── PASS 1 ───────────────────────────────────────────────────────────────────

def pass1(filepath):
    print("\n── PASS 1: aubio + sox + ffprobe ─────────────────────────────")
    r = {}

    # ffprobe
    raw = subprocess.check_output(
        ['ffprobe', '-v', 'quiet', '-print_format', 'json',
         '-show_format', '-show_streams', filepath]
    )
    data = json.loads(raw)
    fmt = data['format']
    r['duration'] = float(fmt['duration'])
    r['samplerate'] = int(data['streams'][0]['sample_rate'])
    r['channels'] = int(data['streams'][0]['channels'])
    print(f"Duration:    {r['duration']:.1f}s  ({r['duration']/60:.1f} min)")
    print(f"Sample rate: {r['samplerate']} Hz  |  Channels: {r['channels']}")

    # sox dynamics
    sox = subprocess.run(['sox', filepath, '-n', 'stat'],
                         capture_output=True, text=True).stderr
    rms = peak = 0.0
    for line in sox.splitlines():
        if 'RMS     amplitude' in line:
            rms = abs(float(line.split()[-1]))
        if 'Maximum amplitude' in line:
            peak = abs(float(line.split()[-1]))

    rms_db  = 20 * np.log10(rms)  if rms  > 0 else -99.0
    peak_db = 20 * np.log10(peak) if peak > 0 else -99.0
    crest   = peak_db - rms_db
    r.update(rms_db=rms_db, peak_db=peak_db, crest_db=crest)

    if   crest > 20: dynamic_char = "very dynamic, uncompressed"
    elif crest > 14: dynamic_char = "natural, moderate dynamics"
    else:            dynamic_char = "compressed, dense, punchy"
    r['dynamic_char'] = dynamic_char

    print(f"RMS:         {rms_db:.1f} dBFS")
    print(f"Peak:        {peak_db:.1f} dBFS")
    print(f"Crest:       {crest:.1f} dB  → {dynamic_char}")

    # aubio BPM
    import aubio
    hop_s = 256
    src = aubio.source(filepath, 0, hop_s)
    tempo_o = aubio.tempo('default', 512, hop_s, src.samplerate)
    beats = []
    while True:
        samples, read = src()
        if tempo_o(samples):
            beats.append(tempo_o.get_last_s())
        if read < hop_s:
            break
    bpm = tempo_o.get_bpm()
    r['bpm'] = bpm
    r['beat_count'] = len(beats)

    if len(beats) < 4:
        print(f"BPM:         no strong pulse detected  ({len(beats)} beats)")
    else:
        print(f"BPM:         {bpm:.1f}  ({len(beats)} beats)")

    # aubio pitch classes
    src = aubio.source(filepath, 0, 512)
    pitch_o = aubio.pitch('yin', 2048, 512, src.samplerate)
    pitch_o.set_unit('midi')
    pitch_o.set_silence(-40)
    pitch_o.set_tolerance(0.8)
    pitch_classes = Counter()
    while True:
        samples, read = src()
        p = pitch_o(samples)[0]
        if pitch_o.get_confidence() > 0.6 and p > 0:
            pitch_classes[int(round(p)) % 12] += 1
        if read < 512:
            break

    r['pitch_classes'] = dict(pitch_classes)
    key, mode, score = detect_key(pitch_classes)
    r['key'], r['mode'] = key, mode

    total = sum(pitch_classes.values()) or 1
    print(f"\nPitch distribution (top 6):")
    for pc, cnt in sorted(pitch_classes.items(), key=lambda x: -x[1])[:6]:
        bar = '█' * int(cnt / total * 30)
        print(f"  {NOTE_NAMES[pc]:3s}  {cnt/total*100:5.1f}%  {bar}")
    print(f"\nKey (aubio):   {key} {mode}  (score {score:.3f})")

    return r


# ─── PASS 2 ───────────────────────────────────────────────────────────────────

def pass2(filepath):
    print("\n── PASS 2: librosa ────────────────────────────────────────────")
    r = {}

    try:
        import librosa
    except ImportError:
        print("librosa not available — skipping")
        return r

    y, sr = librosa.load(filepath, sr=None, mono=True)
    print(f"Loaded: {len(y)/sr:.1f}s at {sr} Hz")

    # BPM (.flat[0] workaround for Python 3.14 array return)
    tempo_arr, _ = librosa.beat.beat_track(y=y, sr=sr)
    bpm = float(np.array(tempo_arr).flat[0])
    r['bpm'] = bpm
    print(f"BPM (librosa): {bpm:.1f}")

    # H/P separation
    y_harm, y_perc = librosa.effects.hpss(y)
    hp_ratio = float(np.mean(y_harm**2)) / max(float(np.mean(y_perc**2)), 1e-10)
    r['hp_ratio'] = hp_ratio
    if   hp_ratio > 10: hp_char = "near-zero percussion, almost purely harmonic"
    elif hp_ratio >  3: hp_char = "harmonic-dominant, light percussion"
    elif hp_ratio >  1: hp_char = "balanced harmonic and percussive"
    else:               hp_char = "percussion-dominant"
    r['hp_char'] = hp_char
    print(f"H/P ratio:     {hp_ratio:.2f}  → {hp_char}")

    # Chroma from harmonic component → key
    chroma = librosa.feature.chroma_cqt(y=y_harm, sr=sr)
    chroma_mean = chroma.mean(axis=1)
    chroma_dist = {i: int(float(chroma_mean[i]) * 1000) for i in range(12)}
    key, mode, score = detect_key(chroma_dist)
    r['key'], r['mode'] = key, mode

    print(f"\nChroma distribution (top 6):")
    for i, v in sorted(enumerate(chroma_mean), key=lambda x: -x[1])[:6]:
        bar = '█' * int(float(v) * 30)
        print(f"  {NOTE_NAMES[i]:3s}  {float(v):.3f}  {bar}")
    print(f"Key (librosa): {key} {mode}  (score {score:.3f})")

    # Spectral contrast — timbral texture
    contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
    overall_contrast = float(contrast.mean())
    r['spectral_contrast'] = overall_contrast
    if   overall_contrast > 25: contrast_char = "high contrast, clear frequency separation"
    elif overall_contrast > 15: contrast_char = "moderate contrast, balanced texture"
    else:                       contrast_char = "low contrast, dense or reverb-heavy"
    r['contrast_char'] = contrast_char
    print(f"\nSpectral contrast: {overall_contrast:.1f} dB  → {contrast_char}")

    # Spectral centroid — brightness
    centroid = float(librosa.feature.spectral_centroid(y=y, sr=sr).mean())
    r['spectral_centroid'] = centroid
    if   centroid > 3000: brightness = "bright, airy, high-frequency dominant"
    elif centroid > 1500: brightness = "balanced, mid-forward"
    else:                 brightness = "dark, bass/low-mid dominant"
    r['brightness'] = brightness
    print(f"Spectral centroid: {centroid:.0f} Hz  → {brightness}")

    # Onset strength — groove character
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    onset_mean = float(onset_env.mean())
    onset_std  = float(onset_env.std())
    groove_idx = onset_std / onset_mean if onset_mean > 0 else 0
    r['groove_index'] = groove_idx
    if   groove_idx > 1.5: groove_char = "punchy, strong transients, rhythmically active"
    elif groove_idx > 0.8: groove_char = "moderate groove, some rhythmic emphasis"
    else:                  groove_char = "smooth, flowing, minimal transient emphasis"
    r['groove_char'] = groove_char
    print(f"Groove index:      {groove_idx:.2f}  → {groove_char}")

    return r


# ─── SYNTHESIS ────────────────────────────────────────────────────────────────

def synthesize(p1, p2):
    print("\n══ SYNTHESIS ══════════════════════════════════════════════════")

    # Key — prefer librosa chroma (uses harmonic component only), fall back to aubio
    if p2.get('key'):
        key  = p2['key']
        mode = p2['mode']
        key_note = f"{key} {mode}  [librosa chroma]"
    else:
        key  = p1['key']
        mode = p1['mode']
        key_note = f"{key} {mode}  [aubio pitch]"

    # BPM — flag half/double-time discrepancies
    bpm1 = p1.get('bpm', 0)
    bpm2 = p2.get('bpm', 0)
    if bpm2 and abs(bpm1 - bpm2) > 5:
        bpm_note  = f"{bpm1:.0f} (aubio) / {bpm2:.0f} (librosa) — likely half/double-time discrepancy"
        bpm_suno  = min(bpm1, bpm2)
    else:
        bpm_note = f"{bpm1:.0f} BPM"
        bpm_suno = bpm1

    print(f"Key:      {key_note}")
    print(f"Tempo:    {bpm_note}")
    print(f"Dynamics: {p1['crest_db']:.1f} dB crest  → {p1['dynamic_char']}")
    if p2:
        print(f"H/P:      {p2['hp_ratio']:.2f}  → {p2['hp_char']}")
        print(f"Texture:  {p2['contrast_char']}")
        print(f"Tone:     {p2['brightness']}")
        print(f"Groove:   {p2['groove_char']}")

    # Build Suno prompt from data
    parts = [
        f"{key} {mode}",
        f"{bpm_suno:.0f} BPM",
    ]
    if p2:
        parts.append(p2['hp_char'])
        parts.append(p2['brightness'])
        parts.append(p2['groove_char'])
        parts.append(p2['contrast_char'])
    if p1['crest_db'] < 14:
        parts.append("compressed dense mix")
    elif p1['crest_db'] > 20:
        parts.append("wide dynamic range")
    parts.append("instrumental")

    print("\n── SUNO PROMPT (data layer) ───────────────────────────────────")
    print()
    print(", ".join(p for p in parts if p))
    print()
    print("→ Add your genre / mood / texture description on top of this.")


# ─── ENTRY ────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: analyze_audio.py <audio_file>")
        sys.exit(1)

    fp = sys.argv[1]
    print(f"\nAnalyzing: {fp}")

    p1 = pass1(fp)
    p2 = pass2(fp)
    synthesize(p1, p2)
