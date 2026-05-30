# Claude Research PKM

> A complete research workflow system for graduate students,
> built on top of [Obsidian](https://obsidian.md) and [Claude Code](https://claude.com/claude-code).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Built with Claude Code](https://img.shields.io/badge/built%20with-Claude%20Code-D97757)](https://claude.com/claude-code)

---

## What is this?

This repository is a **personal operating system** for a graduate research life,
integrating Obsidian's knowledge management with Claude Code's automation. It
covers the *full lifecycle* — from lecture recording to paper review to
experiment processing to company research.

The system is built around three pillars:

1. **Workflows** — Six reusable PKM modules (`M-001` through `M-006`) that
   define repeatable procedures, from lecture-note generation to experiment
   data pipelines.
2. **Automation** — Custom slash commands, subagents, and hooks that handle
   the mechanical parts (Whisper transcription, PDF extraction, Vault linting,
   index updates).
3. **Data integrity** — Read-only raw experiment data, standard 4-function
   measurement modules, automatic Obsidian sync, and full reproducibility logs.

---

## Features

- 📝 **Lecture transcription pipeline** — MP4 → Whisper (large-v3-turbo) →
  slide-segmented transcript → structured Obsidian note (1,100–1,500 lines for
  a 90-minute lecture, with quotations, math, embedded slide PNGs).
- 📚 **Paper review** — PDF → structured analysis → Zotero Synth callout.
- 🔬 **Experiment pipeline** — Raw data → automatic fit & plot → Obsidian
  note with frontmatter, fit metrics, and embedded plots. Raw directory is
  enforced read-only.
- 🏢 **Company research** — Web search → structured 12-section note
  (600–900 lines) with SWOT, market analysis, glossary.
- 🤖 **Domain-specific subagents** — `note-organizer`, `paper-reviewer`,
  `literature-searcher`, `wiki-curator`.
- 🪝 **Hooks for safety & automation** — Wikilink lint, Spec sync, automatic
  index updates, guard against bypassing standard scripts.
- 📊 **Six PKM modules (M-001 ~ M-006)** as canonical workflow definitions.

---

## Repository structure

```
claude-research-pkm/
├── README.md                                ← You are here
├── LICENSE                                  ← MIT
├── CHANGELOG.md
├── .gitignore                               ← Blocks PII, lecture PDFs, raw data
│
├── .claude/                                 ← Claude Code configuration
│   ├── commands/                            ← Slash commands (13)
│   ├── agents/                              ← Subagents (4)
│   ├── hooks/                               ← Hook scripts (2)
│   ├── workflows/                           ← Workflow specs (7)
│   ├── scripts/                             ← Python utilities (3)
│   ├── skills/                              ← (placeholder)
│   └── settings.example.json                ← Template (copy + customize)
│
├── pkm-modules/                             ← Six PKM modules (M-001~006)
│   └── M-00X_*.md
│
├── experiment-pipeline/                      ← Standalone experiment automation
│   ├── README.md                            ← Design doc
│   ├── modules/                             ← Reusable Python modules
│   │   ├── common.py
│   │   └── amr.py
│   ├── templates/                            ← Notebook & Obsidian templates
│   └── scripts/                              ← CLI scripts
│       ├── import_raw.py
│       ├── process_data.py
│       ├── sync_to_obsidian.py
│       └── sync_readmes_to_vault.py
│
└── docs/
    ├── 00-overview.md
    └── 08-setup-guide.md
```

---

## Quick start

### Prerequisites

- [Obsidian](https://obsidian.md) (free)
- [Claude Code](https://claude.com/claude-code) (Pro or Max subscription
  recommended; some features require Opus 4.x)
- Python 3.10+
- (Optional) Whisper, ffmpeg for lecture transcription
- (Optional) Pandoc, XeLaTeX for PDF exports

### Install

```bash
# 1. Clone
git clone https://github.com/<your-username>/claude-research-pkm.git
cd claude-research-pkm

# 2. Copy Claude Code configuration to your home directory
cp -r .claude/agents       ~/.claude/
cp -r .claude/commands     ~/.claude/
cp -r .claude/hooks        ~/.claude/
cp -r .claude/scripts      ~/.claude/
cp -r .claude/workflows    ~/.claude/

# 3. Configure your settings
cp .claude/settings.example.json ~/.claude/settings.json
#    Edit ~/.claude/settings.json to point at your own Vault path.

# 4. (Optional) Install experiment-pipeline as a local Python package
cd experiment-pipeline
pip install -r requirements.txt    # if provided
```

See [`docs/08-setup-guide.md`](docs/08-setup-guide.md) for the detailed setup.

---

## The six PKM modules

| ID    | Title                              | What it automates                                  |
|-------|-----------------------------------|----------------------------------------------------|
| M-001 | Lecture note routine              | MP4 + PDF → 1,100–1,500-line Obsidian note         |
| M-002 | Lecture transcribe routine        | MP4 → Whisper → slide-segmented transcript         |
| M-003 | Slide PNG extract routine         | Video → annotated slide PNGs for note anchors      |
| M-004 | Claude Design process-flow routine | Process steps → claude.ai/design prompt → PDF/PPTX |
| M-005 | Company research routine          | Company name → 12-section company note             |
| M-006 | Experiment data pipeline routine  | Raw measurements → fit & plot → Obsidian sync      |

Each module follows the same skeleton: trigger, source principle, step list,
folder structure, depth guidelines, language policy, and an example reference.

---

## Experiment pipeline highlights

```
experiment-pipeline/
└── modules/                               ← Standard 4-function interface:
    ├── common.py                          ←    load(), fit(), plot(), export()
    └── <measurement>.py                   ← e.g. amr.py
```

The standard interface lets `scripts/process_data.py` dynamically dispatch to
any measurement type — adding a new measurement (AHE, MOKE, XRD) requires only
a single new `<measurement>.py` file; no CLI changes.

Raw data integrity is enforced at the OS level (`chmod` read-only) and tracked
with SHA-256 checksums to prevent duplicate import.

---

## Anonymization & privacy

This repository is a **sanitized** snapshot of the author's private system.

- Personal identifiers, lab names, professor names, file paths, and sample IDs
  are systematically replaced with placeholders (`USER`, `Advisor`,
  `Spintronics Lab`, `$VAULT`, `sample-A`, etc.).
- Course content (lecture PDFs, recorded transcripts) is excluded entirely.
- Research data (`00_raw/`, `01_processed/`) is excluded.
- Personal memory (`~/.claude/projects/.../memory/`) is excluded.

You are free to fork and adapt — the templates and module skeletons are
designed to work for any researcher, in any field.

---

## Documentation

- [Overview](docs/00-overview.md) — System philosophy and high-level architecture
- [Setup guide](docs/08-setup-guide.md) — Step-by-step installation for new users

---

## License

[MIT](LICENSE)

---

## Acknowledgments

Built with:

- [Anthropic Claude Code](https://claude.com/claude-code)
- [Obsidian](https://obsidian.md)
- [OpenAI Whisper](https://github.com/openai/whisper)
- [Dataview](https://github.com/blacksmithgu/obsidian-dataview)
- [pypdfium2](https://github.com/pypdfium2-team/pypdfium2)
