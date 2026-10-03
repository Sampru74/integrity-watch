# IntegrityWatch

IntegrityWatch is a local file-integrity monitoring CLI. It creates a SHA-256 inventory of regular files under a directory, stores it as JSON, and compares later scans to identify added, changed, or missing paths.

## Run

Requires Python 3.10 or newer; no third-party dependencies.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
integrity-watch baseline .\example_data --output .\baseline.json
integrity-watch scan .\example_data --baseline .\baseline.json
```

The example directory is intentionally small and contains only sample text. To see a detected change, edit or add a file under `example_data`, then run the scan again.

## Design and limitations

- SHA-256 digests are calculated in chunks to bound memory use.
- Symbolic links are skipped; scans do not intentionally follow paths outside the requested root.
- Baseline JSON is an integrity reference, not a trusted source by itself. Protect it separately; an attacker who can rewrite both the monitored files and baseline can hide changes.
- This is an educational local tool, not an endpoint agent. It does not monitor continuously, detect memory-only changes, or establish that a file is malicious.

## Tests

```powershell
python -m unittest discover -s tests -v
```

## Next steps

Add baseline signing or remote storage, ignore patterns, and a scheduled scan mode. Keep any real system inventory private; use the included sample data in a public repository.
