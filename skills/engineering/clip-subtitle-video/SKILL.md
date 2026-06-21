---
name: clip-subtitle-video
description: Clip public or local source videos into precise MP4 excerpts and add styled burned-in subtitles. Use when the user asks to find a video source, cut a speech/talk/interview segment by phrase or timestamp, create an MP4 clip, add Chinese/English bilingual subtitles, generate ASS/SRT subtitles, apply documentary or short-video subtitle styles, highlight subtitle keywords, or verify a rendered video deliverable.
---

# Clip Subtitle Video

Use this skill to turn a source video into a verified MP4 excerpt, optionally with burned-in bilingual subtitles.

## Workflow

1. Clarify only missing high-risk inputs:
   - source: local file, user-uploaded file, or public URL; if absent, find an official or authoritative public source
   - cut boundary: exact timestamps or semantic phrase boundary
   - subtitle mode: default to burned-in subtitles for reliable playback; create soft subtitle files only when requested
2. Keep artifacts separated:
   - use a scratch/work directory for downloads, captions, frames, and scripts
   - put final deliverables in the user-facing output directory
   - never overwrite the original source video
3. Prefer authoritative sources:
   - official institution/archive/channel first
   - higher-quality remaster only if it is authoritative enough and its timeline is re-verified
   - do not bypass DRM, paywalls, login walls, or access controls
4. Use subtitles/transcripts to locate semantic cuts:
   - download available subtitles with `yt-dlp --skip-download --write-subs --sub-langs ... --sub-format vtt`
   - search captions with `rg -i "phrase|nearby phrase" file.vtt`
   - inspect surrounding caption rows and record exact source timestamps
   - if switching to another source version, repeat timing against that version's captions
5. Clip precisely:
   - use `yt-dlp --download-sections '*START-END' --force-keyframes-at-cuts` for public downloadable streams
   - use ffmpeg directly for local files
   - for exact starts, allow re-encoding instead of keyframe-only stream copy
6. Add subtitles when requested:
   - translate meaningfully and concisely; keep English close to the source transcript
   - use ASS for burned-in bilingual subtitles; Chinese above English is the default
   - choose a subtitle preset before rendering; default to `documentary`, use `short-video` for social clips
   - use a legible CJK font such as `PingFang SC` on macOS, white text, black outline, bottom alignment
7. Verify before finishing:
   - decode the final MP4 with ffmpeg to `null`
   - inspect duration, codecs, resolution, and file size
   - extract first/mid/last frames and visually check cut boundaries and subtitle placement
   - report source URL, cut range, output path, and validation result

## Tool Setup

If `yt-dlp` or `ffmpeg` is missing, install local workspace tools rather than changing global state:

```bash
python3 -m venv work/.venv
work/.venv/bin/python -m pip install --upgrade pip setuptools wheel
work/.venv/bin/python -m pip install yt-dlp imageio-ffmpeg
FFMPEG_PATH=$(work/.venv/bin/python - <<'PY'
import imageio_ffmpeg
print(imageio_ffmpeg.get_ffmpeg_exe())
PY
)
```

Quote URLs containing `?` in zsh. Use `noglob` for cleanup commands that contain unmatched `*`.

## Common Commands

List formats and subtitles:

```bash
work/.venv/bin/yt-dlp --list-formats 'https://example.com/video'
work/.venv/bin/yt-dlp --skip-download --list-subs 'https://example.com/video'
```

Download subtitles:

```bash
work/.venv/bin/yt-dlp \
  --skip-download \
  --write-subs --sub-langs en --sub-format vtt \
  -o 'work/source.%(ext)s' \
  'https://example.com/video'
```

Clip a public source to MP4:

```bash
work/.venv/bin/yt-dlp \
  --ffmpeg-location "$FFMPEG_PATH" \
  -f 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best' \
  --download-sections '*00:12:49.520-00:14:25.500' \
  --force-keyframes-at-cuts \
  -o 'work/clip.%(ext)s' \
  'https://example.com/video'
```

Clip a local file exactly:

```bash
"$FFMPEG_PATH" -hide_banner -y \
  -ss 00:12:49.520 -to 00:14:25.500 \
  -i source.mp4 \
  -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p \
  -c:a aac -b:a 128k \
  outputs/clip.mp4
```

Burn subtitles into an MP4:

```bash
"$FFMPEG_PATH" -hide_banner -y \
  -i work/clip.mp4 \
  -vf "subtitles=work/subtitles.ass" \
  -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p \
  -c:a copy \
  -movflags +faststart \
  outputs/clip_bilingual.mp4
```

Verify and extract review frames:

```bash
"$FFMPEG_PATH" -hide_banner -i outputs/clip_bilingual.mp4 -f null -
"$FFMPEG_PATH" -hide_banner -y -ss 2.5 -i outputs/clip_bilingual.mp4 -frames:v 1 -update 1 work/frame_start.jpg
"$FFMPEG_PATH" -hide_banner -y -ss 60 -i outputs/clip_bilingual.mp4 -frames:v 1 -update 1 work/frame_mid.jpg
"$FFMPEG_PATH" -hide_banner -y -sseof -1 -i outputs/clip_bilingual.mp4 -frames:v 1 -update 1 work/frame_end.jpg
```

## Subtitle Style Presets

Use these defaults unless the user asks for a different style.

**Documentary preset**

- Use for speeches, lectures, archival clips, and professional playback.
- Keep Chinese prominent but restrained; keep English similar or slightly smaller.
- Use white text with black outline and bottom-center placement.
- Avoid color emphasis unless the user explicitly asks for it.

**Short-video preset**

- Use when the user asks for short-video, social-media, more eye-catching, punchier, or "option 2" style.
- Make Chinese the primary reading line and English a smaller auxiliary line.
- Shorten Chinese lines for scanability while preserving meaning.
- Highlight only high-value keywords, names, numbers, and the final quote in warm yellow.
- Keep highlights sparse: usually 1 keyword per cue, or the whole final catchphrase.
- Inspect frames after rendering; reduce size or split cues if text spans nearly the full width.

## ASS Subtitle Helper

Use `scripts/build_bilingual_ass.py` to generate ASS subtitles from JSON cues.

Input schema:

```json
[
  {
    "start": "00:12:49.520",
    "end": "00:12:55.280",
    "zh": "有一本很了不起的出版物，叫《全球概览》。",
    "en": "there was an amazing publication called The Whole Earth Catalog,",
    "highlight": ["《全球概览》"]
  }
]
```

If cue times are source timestamps, pass `--offset` with the clip start timestamp so output starts at `0:00:00`.

```bash
python3 scripts/build_bilingual_ass.py \
  --cues work/cues.json \
  --offset 00:12:49.520 \
  --preset short-video \
  --output work/subtitles.ass \
  --width 1444 --height 1080
```

Cue fields:

- `zh`, `en`: Chinese and English subtitle lines.
- `highlight`: terms to highlight in the Chinese line.
- `highlight_zh`, `highlight_en`: language-specific highlight terms.
- `zh_size`, `en_size`: optional cue-level size overrides for final quotes or long lines.

For short-video style, use cues like:

```json
[
  {
    "start": "0:01:00.00",
    "end": "0:01:03.90",
    "zh": "照片下面写着：求知若饥，虚心若愚",
    "en": "Beneath it were the words, “Stay hungry. Stay foolish.”",
    "highlight": ["求知若饥，虚心若愚"],
    "zh_size": 66
  }
]
```

## Gotchas

- A remastered video may have different timing from the official upload; never reuse timestamps without re-checking that source.
- YouTube may expose only low-resolution formats unless `yt-dlp` has enough runtime support. If a better authoritative source exists, prefer it and revalidate captions.
- `yt-dlp` warnings about missing ffmpeg usually mean it is not seeing the local binary; pass `--ffmpeg-location "$FFMPEG_PATH"`.
- Hard subtitles require video re-encoding. Keep the no-subtitle clip when useful, and create a separate `_bilingual.mp4` output.
