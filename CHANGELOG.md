# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-10-02

### Added

- Five new targets: **Roo Code / Zoo Code** (`.roo/rules/agentsbridge.md`),
  **Kilo Code** (`.kilocode/rules/agentsbridge.md`), **JetBrains Junie**
  (`.junie/guidelines.md`), **Amazon Q Developer**
  (`.amazonq/rules/agentsbridge.md`), and legacy **Gemini CLI** (`GEMINI.md`).
- `agentsbridge list` — show all supported targets, generated paths, and
  native-AGENTS.md tools in the terminal.
- `AGENTSBRIDGE_TARGETS` environment variable — pin a target subset for CI
  without repeating `-t`; explicit `--targets` takes precedence.
- `check` drift summary now includes per-status counts
  (e.g. `drift detected (3 drifted, 2 missing)`).

### Changed

- CLI output shows paths relative to the project root with forward slashes,
  consistent across Windows/macOS/Linux.

## [0.1.0] - 2026-10-01

### Added

- `agentsbridge sync` — generate rules files for Claude Code, GitHub Copilot,
  Cursor, Windsurf, Cline, and Aider from a single `AGENTS.md`.
- `agentsbridge check` — CI-friendly drift detection (exit 1 when any
  generated file is out of date), plus an official
  [GitHub Action](action/action.yml).
- `agentsbridge import` — seed `AGENTS.md` from an existing `CLAUDE.md`,
  `.cursorrules`, `.clinerules`, `.windsurfrules`, `CONVENTIONS.md`, or
  `.github/copilot-instructions.md`.
- `agentsbridge init` — starter template.
- Safety: generated files carry a marker; hand-written files are never
  overwritten without `--force`.
- `--targets` subsets, `--dry-run`, zero runtime dependencies.
