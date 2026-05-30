# 00 — System overview

> Why does a graduate research life need an "operating system"?

## The problem

Modern graduate research generates an enormous variety of artifacts:

- 90-minute lectures, multiple per week
- Dozens of papers per month
- Experiments that produce raw data sets at varying cadences
- Application materials (résumés, statements, cover letters)
- Conference notes, seminar slides, lab meeting summaries
- Code, both for analysis and for system automation

Each of these has its own preferred format, location, citation style, and
naming convention. Without a system, *the cost of finding what you wrote last
month* exceeds the cost of writing it the first time.

## The three principles

This project is built around three principles:

### 1. Single source of truth, with explicit interfaces

Every workflow has a *canonical module* (`pkm-modules/M-001` through
`M-006`) that defines:

- What triggers it
- What the inputs are
- What the outputs must look like
- What the language and depth policies are
- What success looks like

Procedural details (CLI commands, scripts, folder paths) live in
*specifications* (`.claude/workflows/*.md`) that mirror the modules.

Code and configuration (`.claude/commands/`, `.claude/scripts/`) implement
the specifications. Each layer has one job, and each can be changed
independently.

### 2. Automate the mechanical, preserve the cognitive

Whisper transcription, PDF rendering, slide extraction, wikilink linting,
index updates, frontmatter validation, fit functions, plot generation —
these are *mechanical*. They should never need to be done by hand.

Designing the right experimental question, choosing the right paper to read
deeply, deciding how to frame a research narrative — these are
*cognitive*. They should never be automated away.

The system draws the line at exactly that boundary.

### 3. Data integrity is non-negotiable

Raw experimental data is **read-only** at the OS level. It is tracked with
SHA-256 checksums on import. Processed outputs always include a
`processing_log.json` with module version, environment, and reproducibility
markers.

This isn't paranoia — it's the only way to make a result *defensible* five
years after the fact.

## The pieces

| Piece                  | Role                                         |
|------------------------|----------------------------------------------|
| **Obsidian Vault**     | Single knowledge repository (notes, links)   |
| **Claude Code**        | Agent layer (commands, agents, hooks)        |
| **Python scripts**     | Mechanical automation                        |
| **PKM modules**        | Canonical workflow definitions               |
| **Experiment pipeline**| Standardized data-processing layer           |
| **Dataview**           | Live indexes inside the Vault                |

## Reading order

1. [`08-setup-guide.md`](08-setup-guide.md) — Set up the system on your machine
2. [`pkm-modules/M-001`](../pkm-modules/M-001_lecture-note-routine.md) — Read the canonical lecture-note module
3. [`experiment-pipeline/README.md`](../experiment-pipeline/README.md) — Read the experiment system design
4. [`.claude/commands/`](../.claude/commands/) — Browse available slash commands
