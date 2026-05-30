# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-05-29

### Added — Initial release

- **`.claude/`** — Sanitized Claude Code configuration
  - `commands/` (13 slash commands: lecture transcription, paper review, literature search, etc.)
  - `agents/` (4 subagents: note-organizer, paper-reviewer, literature-searcher, wiki-curator)
  - `hooks/` (2 hooks: whisper guard, compaction suggester)
  - `workflows/` (7 workflow specs)
  - `scripts/` (3 Python scripts: lecture transcribe, slide extract, zotero audit)
  - `skills/README.md` (placeholder — third-party skills not bundled)

- **`pkm-modules/`** — Six reusable PKM modules
  - `M-001` Lecture note routine
  - `M-002` Lecture transcribe routine
  - `M-003` Slide PNG extract routine
  - `M-004` Claude Design process-flow routine
  - `M-005` Company research routine
  - `M-006` Experiment data pipeline routine

- **`experiment-pipeline/`** — Standalone Python package for experiment data automation
  - `modules/` (common, amr — standard 4-function interface)
  - `templates/` (notebook & Obsidian note)
  - `scripts/` (import_raw, process_data, sync_to_obsidian, sync_readmes_to_vault)

- **`docs/`** — Overview & setup guide

- **License**: MIT
