---
name: jianying-draft-project
description: Generate a Jianying or CapCut recognized draft project from local media, rough-cut decisions, EDL files, SRT subtitles, or review previews. Use for Jianying draft construction and verification while working in this repository with any capable coding or desktop-automation agent.
---

# Jianying Draft Project

Use this repository-local skill to create a draft folder that Jianying Professional can open for review. Treat the repository root as the working directory; do not depend on a particular agent product or absolute checkout path.

## Known Local Baseline

- Jianying Professional `10.6.0.14057` accepted a generated clear-text draft during local UI verification.
- Native Jianying 10.6 draft files may look encoded or binary-like. Do not directly patch an existing encoded native `draft_content.json`.
- A generated clear-text draft with `draft_content.json` and `draft_meta_info.json` is acceptable when created through the pyJianYingDraft-style path and verified in the Jianying UI.
- Reusable cross-agent builder: `scripts/build_draft.py`, resolved relative to this skill directory.
- Python dependencies are declared in `requirements.txt`. Install them into the skill-local `.runtime` directory with `scripts/install_dependencies.py`; do not assume packages are globally installed.
- Previous temporary references may exist at:
  - `.tmp_capcut_mate_zip/capcut-mate-main`
  - `.tmp_jianying_lib`

## Inputs

- Source media folder, EDL, or rough-cut notes.
- Optional SRT for subtitle track import.
- Draft name, or a sensible name derived from the project.
- Target draft root: default to `D:\JianyingPro Drafts`.

## Runtime Setup

1. Resolve the directory containing this `SKILL.md` as `<skill-dir>`.
2. Check the environment:
   - `python <skill-dir>/scripts/check_environment.py`
3. If `pyJianYingDraft` is missing, install the pinned dependencies locally:
   - `python <skill-dir>/scripts/install_dependencies.py`
4. Run the environment check again. The bundled scripts automatically add `<skill-dir>/.runtime` to `sys.path`.
5. Treat `ffmpeg` and `ffprobe` as optional for draft-only generation and required only for preview rendering or media probing.

Do not vendor or copy a machine's `site-packages` directory into the skill. Use `requirements.txt` and the installer so compiled dependencies match the current Python installation.

## EDL Contract

Pass `scripts/build_draft.py` a JSON list, or an object with a `pieces`, `segments`, or `ranges` list. A top-level `sources` mapping may map source IDs to media paths. Each timeline item must resolve to:

- `source_path`: existing local media file; alternatively use `source` with a matching entry in the top-level `sources` mapping.
- `source_start`: source offset in seconds.
- `duration`: positive duration in seconds; `end` may be supplied instead.
- `output_start`: output timeline position in seconds; optional when pieces are contiguous.

Validate without creating a draft:

`python <skill-dir>/scripts/build_draft.py --edl <edl.json> --name <draft-name> --validate-only`

## Workflow

1. Gather source media and timing decisions:
   - For rough cuts, use `video-use` transcript and EDL rules: cut on word boundaries, preserve breath detail, remove long dead air, and keep output-timeline subtitle offsets.
   - Prefer existing artifacts under the media folder's `edit\` directory when present, such as `rough_cut_edl.json`, `rough_cut_review.srt`, or `rough_cut_preview.mp4`.
2. Generate a new draft folder under `D:\JianyingPro Drafts\<draft-name>`.
3. Prefer the bundled builder:
   - `python <skill-dir>/scripts/build_draft.py --edl <edl.json> --srt <subtitles.srt> --name <draft-name>`
4. The builder uses the pyJianYingDraft approach:
   - Create `draft_content.json` and `draft_meta_info.json`.
   - Add source video segments using original media paths and source timeranges.
   - Add audio with matching segments unless the library handles linked media automatically.
   - Import SRT as a text/subtitle track when subtitles are part of the request.
   - Save the draft as a new folder; do not mutate an existing encoded native draft.
5. If an older project-specific generator under `tools/` contains useful editorial logic, use it only to produce the standardized EDL. Use the bundled builder for portable draft construction.
6. Validate the draft in Jianying:
   - Open Jianying Professional and confirm the draft appears in the draft list, or open the draft directly if supported.
   - Confirm the timeline has the expected video track and subtitle track.
   - If possible, scrub the opening and one mid-point to confirm media links resolve.
7. Report the absolute draft folder path and any generated review artifacts.

## Fallback

If generated JSON drafts fail to open in the installed Jianying version:

1. Create or open a Jianying draft through the UI.
2. Import the rough-cut preview video and SRT into the timeline.
3. Save the draft under the requested name.
4. Report that this is a review-import fallback, not a fully segmented source-media draft.

## Guardrails

- Generate new draft folders instead of editing existing encoded native drafts.
- Keep source media untouched.
- Do not delete Jianying drafts.
- Verify in the Jianying UI before claiming the draft is review-ready.
- For rendered previews or SRTs created during the process, place project artifacts under the media folder's `edit\` directory.
