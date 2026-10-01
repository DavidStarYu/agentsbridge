# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
