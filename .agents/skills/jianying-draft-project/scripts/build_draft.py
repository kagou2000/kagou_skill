from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


SKILL_DIR = Path(__file__).resolve().parents[1]
LOCAL_RUNTIME = SKILL_DIR / ".runtime"
if LOCAL_RUNTIME.is_dir():
    sys.path.insert(0, str(LOCAL_RUNTIME))


def positive_seconds(value: Any, field: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be a number") from exc
    if number < 0:
        raise ValueError(f"{field} must be non-negative")
    return number


def load_pieces(edl_path: Path) -> list[dict[str, Any]]:
    data = json.loads(edl_path.read_text(encoding="utf-8-sig"))
    raw_pieces = None
    source_map: dict[str, Any] = {}
    if isinstance(data, dict):
        raw_pieces = data.get("pieces") or data.get("segments") or data.get("ranges")
        raw_sources = data.get("sources")
        if isinstance(raw_sources, dict):
            source_map = raw_sources
        elif isinstance(raw_sources, list):
            for item in raw_sources:
                if isinstance(item, dict):
                    key = item.get("name") or item.get("id") or item.get("source")
                    value = item.get("path") or item.get("source_path")
                    if key and value:
                        source_map[str(key)] = value
    else:
        raw_pieces = data
    if not isinstance(raw_pieces, list) or not raw_pieces:
        raise ValueError("EDL must be a non-empty list or contain pieces, segments, or ranges")

    pieces: list[dict[str, Any]] = []
    cursor = 0.0
    for index, raw in enumerate(raw_pieces, 1):
        if not isinstance(raw, dict):
            raise ValueError(f"piece #{index} must be an object")
        source_value = raw.get("source_path") or raw.get("path") or raw.get("file")
        if not source_value and raw.get("source") is not None:
            source_value = source_map.get(str(raw["source"]), raw.get("source"))
        if not source_value:
            raise ValueError(f"piece #{index} is missing source_path")
        source = Path(str(source_value)).expanduser().resolve()
        if not source.is_file():
            raise FileNotFoundError(f"piece #{index} source does not exist: {source}")
        source_start = positive_seconds(raw.get("source_start", raw.get("start", 0)), f"piece #{index} source_start")
        duration_value = raw.get("duration")
        if duration_value is None and raw.get("end") is not None:
            duration_value = positive_seconds(raw["end"], f"piece #{index} end") - source_start
        duration = positive_seconds(duration_value, f"piece #{index} duration")
        if duration == 0:
            raise ValueError(f"piece #{index} duration must be greater than zero")
        output_start = positive_seconds(raw.get("output_start", cursor), f"piece #{index} output_start")
        if output_start < cursor - 0.001:
            raise ValueError(f"piece #{index} overlaps the previous output segment")
        pieces.append(
            {
                "source_path": str(source),
                "source_start": source_start,
                "duration": duration,
                "output_start": output_start,
            }
        )
        cursor = output_start + duration
    return pieces


def load_library():
    try:
        import pyJianYingDraft as draft  # type: ignore
    except ImportError as exc:
        install_script = SKILL_DIR / "scripts" / "install_dependencies.py"
        raise RuntimeError(
            "pyJianYingDraft is unavailable. Run: "
            f'"{sys.executable}" "{install_script}"'
        ) from exc
    return draft


def unique_draft_name(root: Path, requested: str) -> str:
    if not (root / requested).exists():
        return requested
    suffix = 2
    while (root / f"{requested}_{suffix:02d}").exists():
        suffix += 1
    return f"{requested}_{suffix:02d}"


def build(args: argparse.Namespace, pieces: list[dict[str, Any]]) -> Path:
    draft = load_library()
    draft_root = args.draft_root.expanduser().resolve()
    draft_root.mkdir(parents=True, exist_ok=True)
    draft_name = unique_draft_name(draft_root, args.name)
    folder = draft.DraftFolder(str(draft_root))
    script = folder.create_draft(
        draft_name,
        args.width,
        args.height,
        fps=args.fps,
        allow_replace=False,
    )
    script.add_track(draft.TrackType.video, "main_video")
    for piece in pieces:
        target = draft.Timerange(
            int(round(piece["output_start"] * 1_000_000)),
            int(round(piece["duration"] * 1_000_000)),
        )
        source = draft.Timerange(
            int(round(piece["source_start"] * 1_000_000)),
            int(round(piece["duration"] * 1_000_000)),
        )
        segment = draft.VideoSegment(piece["source_path"], target, source_timerange=source)
        script.add_segment(segment, "main_video")
    if args.srt:
        srt = args.srt.expanduser().resolve()
        if not srt.is_file():
            raise FileNotFoundError(f"SRT does not exist: {srt}")
        script.import_srt(str(srt), "subtitles")
    script.save()
    return draft_root / draft_name


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a new Jianying/CapCut draft from a JSON EDL.")
    parser.add_argument("--edl", type=Path, required=True, help="JSON list or object with a pieces list")
    parser.add_argument("--name", required=True, help="New draft name")
    parser.add_argument("--draft-root", type=Path, default=Path(r"D:\JianyingPro Drafts"))
    parser.add_argument("--srt", type=Path)
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    pieces = load_pieces(args.edl.expanduser().resolve())
    if args.validate_only:
        print(json.dumps({"valid": True, "pieces": len(pieces)}, ensure_ascii=False))
        return 0
    draft_path = build(args, pieces)
    print(json.dumps({"draft_path": str(draft_path), "pieces": len(pieces)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
