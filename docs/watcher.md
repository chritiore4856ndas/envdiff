# File Watcher

The `envdiff watch` feature lets you monitor two `.env` files and automatically
re-run the comparison whenever either file changes on disk.

## How it works

`envdiff.watcher` uses a simple **polling** strategy: it records the `mtime` of
each watched file and checks for changes every `interval` seconds (default 1 s).
When a change is detected the user-supplied callback is invoked.

## Python API

```python
from pathlib import Path
from envdiff.watcher import watch
from envdiff.parser import parse_env_file
from envdiff.comparator import compare
from envdiff.reporter import emit_report, build_report

def on_change():
    a = parse_env_file(Path(".env.development"))
    b = parse_env_file(Path(".env.production"))
    result = compare(a, b)
    emit_report(build_report(result, fmt="text"))

watch(
    paths=[Path(".env.development"), Path(".env.production")],
    callback=on_change,
    interval=2.0,
)
```

## CLI usage

```
envdiff watch .env.development .env.production
envdiff watch .env.development .env.production --interval 0.5
```

## Notes

- The watcher performs an **initial snapshot** before entering the loop, so the
  callback is *not* called on startup — only on subsequent changes.
- If a watched file does not exist yet the watcher records its mtime as `-1`
  and will fire the callback once the file is created.
- For large projects consider combining `--include` / `--exclude` filters so
  that noisy keys don't clutter the live output.
