# EDL input format

Use a JSON list or an object containing a `segments` list:

```json
{
  "segments": [
    {
      "source_path": "../media/take-01.mp4",
      "source_start": 12.4,
      "duration": 5.8,
      "output_start": 0.0
    },
    {
      "source_path": "../media/take-01.mp4",
      "source_start": 30.2,
      "source_end": 36.0
    }
  ]
}
```

- Times are seconds.
- Relative media paths resolve from the EDL file directory.
- Omit `output_start` to append after the previous segment.
- Provide either `duration` or `source_end`.
