---
name: jianying-srt-export
description: Use this project-local skill when the user wants to convert video or audio into a Jianying or CapCut compatible SRT subtitle file, especially by using Jianying auto captions, exporting only SRT, and moving the SRT into this video_process project folder.
---

# Jianying SRT Export

This skill is scoped to `D:\Code\myvlog\video_process`. Use it to produce an SRT file that Jianying can import, without exporting a rendered video unless the user explicitly asks for one.

## Inputs

- Source media: video or audio files named by the user, the currently open Jianying project, or media under this repo.
- Destination folder: default to `D:\Code\myvlog\video_process` unless the user names a more specific project folder.
- Desired output: one `.srt` file, UTF-8 readable, ready for Jianying/CapCut import.

## Preferred Workflow

1. Locate the source media and destination folder. If the user says Jianying is already open, inspect the desktop with the `computer-use` skill.
2. If Jianying UI is available and the user asked for Jianying auto captions, use Jianying's auto-caption flow:
   - Open or focus the target draft.
   - Use the text/caption panel and run auto caption or speech-to-text on the spoken track.
   - Export subtitles only. Do not export video.
   - Choose SRT when export options are shown.
3. Move the newest exported `.srt` into the destination folder. If there are multiple plausible SRTs, compare modified time, size, and draft title before moving.
4. Normalize/check the SRT:
   - Preserve cue numbering and `HH:MM:SS,mmm --> HH:MM:SS,mmm` timing.
   - Read/write as UTF-8 when editing. Avoid PowerShell default encoding surprises.
   - Fix obvious encoding damage or tiny transcript typos only when evidence is clear.
5. Verify the final file:
   - `Get-Item` shows a non-empty `.srt` in the destination folder.
   - A quick text read shows valid SRT timing lines and expected dialogue.
   - Report the absolute path.

## Fallback Workflow

If Jianying is unavailable or foreground automation fails, use the repo's video transcription path instead:

1. Prefer `.codex/skills/video-use/helpers/transcribe.py` or the existing `video-use` transcript cache when source media is local.
2. Convert word/phrase timings to SRT manually or through existing helper scripts.
3. Place the output SRT in the same destination folder and verify it as above.

Use this fallback only when it is acceptable to generate ASR outside Jianying. If the user specifically requires Jianying's own auto-caption result and the UI cannot be operated, report that blocker clearly.

## Guardrails

- Do not export a video unless explicitly requested.
- Do not overwrite an existing SRT unless the user requested replacement or the new filename is unambiguous.
- Do not edit existing media files.
- When controlling Jianying, keep actions reversible: export/copy/move files, avoid deleting drafts or changing existing project content unless asked.
- If SRT timing is later used for editing, keep subtitle text close to the spoken words; cosmetic rewriting belongs in the rough-cut or review pass.
