from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


MICROSECONDS = 1_000_000


def load_draft_library() -> Any:
    try:
        import pyJianYingDraft as draft  # type: ignore
    except ImportError as exc:
        installer = Path(__file__).resolve().parent / "install_dependencies.py"
        raise SystemExit(
            f'Missing pyJianYingDraft. Run: "{sys.executable}" "{installer}"'
        ) from exc
    return draft


def as_seconds(value: Any, field: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be numeric, got {value!r}") from exc
    if result < 0:
        raise ValueError(f"{field} must be non-negative")
    return result


def load_segments(edl_path: Path) -> list[dict[str, Any]]:
    data = json.loads(edl_path.read_text(encoding="utf-8-sig"))
    raw_segments = data.get("segments") if isinstance(data, dict) else data
    if not isinstance(raw_segments, list) or not raw_segments:
        raise ValueError("EDL must be a non-empty list or contain a segments list")

    segments: list[dict[str, Any]] = []
    output_cursor = 0.0
    for index, raw in enumerate(raw_segments, start=1):
        if not isinstance(raw, dict):
            raise ValueError(f"segment {index} must be an object")
        source_value = raw.get("source_path", raw.get("path"))
        if not source_value:
            raise ValueError(f"segment {index} is missing source_path")
        source_path = Path(str(source_value)).expanduser()
        if not source_path.is_absolute():
            source_path = (edl_path.parent / source_path).resolve()
        if not source_path.is_file():
            raise FileNotFoundError(f"segment {index} source not found: {source_path}")

        source_start = as_seconds(
            raw.get("source_start", raw.get("start", 0)),
            f"segment {index} source_start",
        )
        if "duration" in raw:
            duration = as_seconds(raw["duration"], f"segment {index} duration")
        else:
            end_value = raw.get("source_end", raw.get("end"))
            if end_value is None:
                raise ValueError(f"segment {index} needs duration or source_end")
            duration = as_seconds(end_value, f"segment {index} source_end") - source_start
        if duration <= 0:
            raise ValueError(f"segment {index} duration must be greater than zero")

        output_start = as_seconds(
            raw.get("output_start", output_cursor),
            f"segment {index} output_start",
        )
        segments.append(
            {
                "source_path": source_path,
                "source_start": source_start,
                "duration": duration,
                "output_start": output_start,
            }
        )
        output_cursor = max(output_cursor, output_start + duration)
    return segments


def choose_name(draft_root: Path, requested: str) -> str:
    if not (draft_root / requested).exists():
        return requested
    version = 2
    while (draft_root / f"{requested}_v{version}").exists():
        version += 1
    return f"{requested}_v{version}"


def build_draft(
    segments: list[dict[str, Any]],
    draft_root: Path,
    draft_name: str,
    srt_path: Path | None,
    width: int,
    height: int,
    fps: int,
) -> Path:
    draft = load_draft_library()
    draft_root.mkdir(parents=True, exist_ok=True)
    final_name = choose_name(draft_root, draft_name)
    script = draft.DraftFolder(str(draft_root)).create_draft(
        final_name, width, height, fps=fps, allow_replace=False
    )
    track_name = "rough_main"
    script.add_track(draft.TrackType.video, track_name)

    for item in segments:
        output_range = draft.Timerange(
            round(item["output_start"] * MICROSECONDS),
            round(item["duration"] * MICROSECONDS),
        )
        source_range = draft.Timerange(
            round(item["source_start"] * MICROSECONDS),
            round(item["duration"] * MICROSECONDS),
        )
        segment = draft.VideoSegment(
            str(item["source_path"]), output_range, source_timerange=source_range
        )
        script.add_segment(segment, track_name)

    if srt_path is not None:
        script.import_srt(str(srt_path), "rough_subtitles")
    script.save()
    return draft_root / final_name


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a Jianying/CapCut draft from a JSON EDL and optional SRT."
    )
    parser.add_argument("--edl", type=Path, required=True)
    parser.add_argument("--srt", type=Path)
    parser.add_argument("--name", required=True)
    parser.add_argument("--draft-root", type=Path, default=Path(r"D:\JianyingPro Drafts"))
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--validate-only", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    edl_path = args.edl.expanduser().resolve()
    if not edl_path.is_file():
        raise SystemExit(f"EDL not found: {edl_path}")
    srt_path = args.srt.expanduser().resolve() if args.srt else None
    if srt_path is not None and not srt_path.is_file():
        raise SystemExit(f"SRT not found: {srt_path}")
    segments = load_segments(edl_path)
    if args.validate_only:
        print(json.dumps({"valid": True, "segments": len(segments)}, ensure_ascii=False))
        return 0
    output = build_draft(
        segments,
        args.draft_root.expanduser().resolve(),
        args.name,
        srt_path,
        args.width,
        args.height,
        args.fps,
    )
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
