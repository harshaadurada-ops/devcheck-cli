# DevCheck CLI — Developer Environment Diagnostics

A small, installable Python command-line tool that checks Python version, disk space, selected environment variables, and configured developer tools. It prints a human-readable report or structured JSON, supports report files, and returns useful exit codes.

## Requirements

- Python 3.10 or newer
- `pip`
- Git is optional but is checked by default; configure the tool list if Git is not installed.

## Install from this repository

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -e ".[test]"
```

## Usage

```bash
devcheck
devcheck --format json
devcheck --config config.example.json
devcheck --format json --output sample-reports/my-report.json
```

If the `devcheck` command is not found immediately after installation, run `python -m pip show devcheck-cli`, confirm the virtual environment is activated, and reopen the terminal.

## Configuration

Copy `config.example.json` to `config.json` and edit it:

```json
{
  "required_env": ["PATH", "HOME"],
  "tools": ["git", "python", "pip"],
  "disk_path": "."
}
```

- `required_env`: environment variable names that must be present.
- `tools`: executable names checked using the system PATH.
- `disk_path`: existing file-system path whose disk is inspected.

Only the names and presence of selected environment variables are reported; their values are not exposed.

## Exit codes

| Code | Meaning |
|---|---|
| `0` | All diagnostic checks passed |
| `1` | One or more environment checks failed |
| `2` | Configuration or report-output error |

## Tests

```bash
python -m pytest -v
```

The tests cover a successful report, a missing developer tool, missing configuration paths, invalid JSON, and invalid configuration types.

## Build a distributable package

```bash
python -m build
```

The wheel and source archive will be created in `dist/`.

## Sample data

`diagnostic-events.json` contains illustrative diagnostic event samples. The CLI performs live environment checks; it does not ingest these event samples in this version. Example text and JSON reports are stored in `sample-reports/`.

## Repository checklist

- [ ] Create and activate a virtual environment
- [ ] Install the package in editable mode
- [ ] Run `python -m pytest -v`
- [ ] Run both text and JSON CLI examples
- [ ] Build the package with `python -m build`
- [ ] Commit source, tests, documentation, and sample reports to GitHub
- [ ] Do not commit `.venv/`, `dist/`, or `*.egg-info/`

## License

MIT
