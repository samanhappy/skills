#!/usr/bin/env python3
"""Build ASS subtitles for burned-in bilingual video captions."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


TIMESTAMP_RE = re.compile(
    r"^(?:(?P<hours>\d+):)?(?P<minutes>\d{1,2}):(?P<seconds>\d{1,2}(?:\.\d+)?)$"
)

STYLE_PRESETS = {
    "documentary": {
        "font": "PingFang SC",
        "zh_size": 54,
        "en_size": 38,
        "outline": 4,
        "shadow": 1,
        "margin_l": 80,
        "margin_r": 80,
        "margin_v": 72,
        "zh_color": "#FFFFFF",
        "en_color": "#FFFFFF",
        "highlight_color": "#FFD84A",
        "back_color": "&HAA000000&",
    },
    "short-video": {
        "font": "PingFang SC",
        "zh_size": 62,
        "en_size": 34,
        "outline": 5,
        "shadow": 2,
        "margin_l": 70,
        "margin_r": 70,
        "margin_v": 86,
        "zh_color": "#FFFFFF",
        "en_color": "#EAEAEA",
        "highlight_color": "#FFD84A",
        "back_color": "&H90000000&",
    },
}


def parse_time(value: str | int | float) -> float:
    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip()
    try:
        return float(text)
    except ValueError:
        pass

    match = TIMESTAMP_RE.match(text)
    if not match:
        raise ValueError(f"invalid timestamp: {value!r}")

    hours = int(match.group("hours") or 0)
    minutes = int(match.group("minutes"))
    seconds = float(match.group("seconds"))
    return hours * 3600 + minutes * 60 + seconds


def format_ass_time(seconds: float) -> str:
    seconds = max(0.0, seconds)
    centiseconds = int(round(seconds * 100))
    hours, remainder = divmod(centiseconds, 3600 * 100)
    minutes, remainder = divmod(remainder, 60 * 100)
    secs, cents = divmod(remainder, 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{cents:02d}"


def ass_text(value: Any) -> str:
    text = "" if value is None else str(value)
    text = text.replace("\\", "\\\\")
    text = text.replace("{", "｛").replace("}", "｝")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text.replace("\n", r"\N")


def ass_color(value: str) -> str:
    text = value.strip()
    if text.startswith("&H"):
        return text if text.endswith("&") else f"{text}&"
    if text.startswith("#"):
        text = text[1:]
    if len(text) != 6 or not re.fullmatch(r"[0-9a-fA-F]{6}", text):
        raise ValueError(f"invalid RGB or ASS color: {value!r}")
    rr, gg, bb = text[0:2], text[2:4], text[4:6]
    return f"&H00{bb}{gg}{rr}&".upper()


def cue_terms(cue: dict[str, Any], *keys: str) -> list[str]:
    terms: list[str] = []
    for key in keys:
        value = cue.get(key)
        if value is None:
            continue
        if isinstance(value, str):
            terms.append(value)
        elif isinstance(value, list):
            terms.extend(str(item) for item in value)
        else:
            raise ValueError(f"{key!r} must be a string or list")
    return [term for term in terms if term]


def highlight_text(
    text: str, terms: list[str], base_color: str, highlight_color: str
) -> str:
    escaped = ass_text(text)
    for term in sorted(terms, key=len, reverse=True):
        escaped_term = ass_text(term)
        escaped = escaped.replace(
            escaped_term,
            rf"{{\c{highlight_color}}}{escaped_term}{{\c{base_color}}}",
        )
    return escaped


def load_cues(path: str) -> list[dict[str, Any]]:
    if path == "-":
        data = json.load(sys.stdin)
    else:
        data = json.loads(Path(path).read_text(encoding="utf-8"))

    if not isinstance(data, list):
        raise ValueError("cue JSON must be a list")
    for index, cue in enumerate(data):
        if not isinstance(cue, dict):
            raise ValueError(f"cue {index} must be an object")
        for key in ("start", "end"):
            if key not in cue:
                raise ValueError(f"cue {index} missing {key!r}")
    return data


def build_ass(cues: list[dict[str, Any]], args: argparse.Namespace) -> str:
    zh_color = ass_color(args.zh_color)
    en_color = ass_color(args.en_color)
    highlight_color = ass_color(args.highlight_color)
    back_color = ass_color(args.back_color)
    header = f"""[Script Info]
Title: Bilingual subtitles
ScriptType: v4.00+
WrapStyle: 2
ScaledBorderAndShadow: yes
PlayResX: {args.width}
PlayResY: {args.height}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{args.font},{args.zh_size},{zh_color},&H000000FF,&H00000000,{back_color},-1,0,0,0,100,100,0,0,1,{args.outline},{args.shadow},2,{args.margin_l},{args.margin_r},{args.margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [header]
    offset = parse_time(args.offset)

    for index, cue in enumerate(cues):
        start = parse_time(cue["start"]) - offset
        end = parse_time(cue["end"]) - offset
        if end <= start:
            raise ValueError(f"cue {index} has non-positive duration")

        zh_size = int(cue.get("zh_size", args.zh_size))
        en_size = int(cue.get("en_size", args.en_size))
        zh = highlight_text(
            cue.get("zh", ""),
            cue_terms(cue, "highlight", "highlight_zh"),
            zh_color,
            highlight_color,
        )
        en = highlight_text(
            cue.get("en", ""),
            cue_terms(cue, "highlight_en"),
            en_color,
            highlight_color,
        )
        if zh and en:
            text = rf"{{\fs{zh_size}\c{zh_color}}}{zh}\N{{\fs{en_size}\c{en_color}}}{en}"
        elif zh:
            text = rf"{{\fs{zh_size}\c{zh_color}}}{zh}"
        elif en:
            text = rf"{{\fs{en_size}\c{en_color}}}{en}"
        else:
            continue

        lines.append(
            "Dialogue: 0,"
            f"{format_ass_time(start)},{format_ass_time(end)},"
            f"Default,,0,0,0,,{text}\n"
        )

    return "".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate ASS subtitles from bilingual JSON cues."
    )
    parser.add_argument("--cues", required=True, help="JSON cues path, or '-' for stdin")
    parser.add_argument("--output", required=True, help="ASS output path")
    parser.add_argument(
        "--preset",
        choices=sorted(STYLE_PRESETS),
        default="documentary",
        help="Subtitle style preset",
    )
    parser.add_argument(
        "--offset",
        default="0",
        help="Timestamp to subtract from cue times, usually the clip start",
    )
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--font")
    parser.add_argument("--zh-size", type=int)
    parser.add_argument("--en-size", type=int)
    parser.add_argument("--outline", type=int)
    parser.add_argument("--shadow", type=int)
    parser.add_argument("--margin-l", type=int)
    parser.add_argument("--margin-r", type=int)
    parser.add_argument("--margin-v", type=int)
    parser.add_argument("--zh-color")
    parser.add_argument("--en-color")
    parser.add_argument("--highlight-color")
    parser.add_argument("--back-color")
    args = parser.parse_args()

    preset = STYLE_PRESETS[args.preset]
    for key, value in preset.items():
        if getattr(args, key) is None:
            setattr(args, key, value)

    cues = load_cues(args.cues)
    ass = build_ass(cues, args)
    Path(args.output).write_text(ass, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
