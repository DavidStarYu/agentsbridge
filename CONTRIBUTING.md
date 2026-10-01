# Contributing

Thanks for your interest in improving agentsbridge! The project is
deliberately small — PRs should be too.

## Ground rules

- **Zero runtime dependencies.** Standard library only. If a feature needs a
  dependency, it probably belongs in a separate tool.
- **One target = one dataclass entry** in `agentsbridge/targets.py`. Most
  "add tool X" PRs are ~10 lines.
- Every behavior change needs a test in `tests/`.

## Setup

```bash
git clone https://github.com/DavidStarYu/agentsbridge
cd agentsbridge
pip install -e . pytest ruff
```

## Before you open a PR

```bash
pytest -q
ruff check agentsbridge/ tests/
ruff format --check agentsbridge/ tests/
```

## Adding a new target

1. Add a `Target(...)` to `TARGETS` in `agentsbridge/targets.py`.
2. If the tool needs a new rendering style (beyond `markdown` / `mdc`),
   add it to `render()` — keep styles minimal.
3. Add tests: creation, marker presence, drift detection.
4. Update the table in `README.md` and this file's version of the table if needed.

## Reporting bugs

Open an issue with the output of `agentsbridge --version`, the exact command
you ran, and (if possible) a minimal `AGENTS.md` that reproduces it.
