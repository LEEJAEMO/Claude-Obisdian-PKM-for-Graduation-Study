# 08 — Setup guide

> Step-by-step instructions for installing the system on your own machine.

## Prerequisites

| Tool                                                              | Purpose                                  | Required? |
|-------------------------------------------------------------------|------------------------------------------|-----------|
| [Obsidian](https://obsidian.md)                                   | Knowledge management                     | Yes       |
| [Claude Code](https://claude.com/claude-code)                     | Agent + automation layer                 | Yes       |
| Python 3.10+                                                      | Scripts                                  | Yes       |
| `pypdfium2`, `numpy`, `pandas`, `matplotlib`, `scipy`             | Experiment pipeline + utilities          | Yes       |
| [OpenAI Whisper](https://github.com/openai/whisper) + `ffmpeg`    | Lecture transcription                    | Optional  |
| [Dataview](https://github.com/blacksmithgu/obsidian-dataview)     | Live indexes inside Obsidian             | Recommended |
| Pandoc + XeLaTeX                                                  | Markdown → PDF exports                   | Optional  |

## Installation

### 1. Clone

```bash
git clone https://github.com/<your-username>/claude-research-pkm.git
cd claude-research-pkm
```

### 2. Pick a project root

Decide where you will keep this repository on your machine — Claude Code
hooks will reference paths inside it. For example:

```bash
# macOS / Linux
mv claude-research-pkm ~/projects/claude-research-pkm
export PROJECT_ROOT=~/projects/claude-research-pkm

# Windows (PowerShell)
Move-Item .\claude-research-pkm "C:\projects\claude-research-pkm"
$env:PROJECT_ROOT = "C:\projects\claude-research-pkm"
```

### 3. Copy Claude Code configuration

```bash
# macOS / Linux
mkdir -p ~/.claude
cp -r $PROJECT_ROOT/.claude/agents       ~/.claude/
cp -r $PROJECT_ROOT/.claude/commands     ~/.claude/
cp -r $PROJECT_ROOT/.claude/hooks        ~/.claude/
cp -r $PROJECT_ROOT/.claude/scripts      ~/.claude/
cp -r $PROJECT_ROOT/.claude/workflows    ~/.claude/

# Windows (PowerShell) — equivalent
Copy-Item -Recurse $env:PROJECT_ROOT\.claude\agents     $HOME\.claude\
# ... etc.
```

### 4. Configure settings

```bash
cp $PROJECT_ROOT/.claude/settings.example.json ~/.claude/settings.json
```

Open `~/.claude/settings.json` and:

- Replace every `$PROJECT_ROOT` with your actual absolute path.
- Fill in API keys (`ZOTERO_API_KEY`, etc.) if you use those tools.

### 5. Set up your Vault

If you don't already have an Obsidian Vault:

1. Open Obsidian → "Create new vault" → pick a folder.
2. Create the following folder structure (you can use any layout you like —
   these names match what the modules and scripts assume):
   ```
   <YourVault>/
   ├── 0. Inbox/
   ├── 1. Project/
   ├── 2. Area/
   ├── 3. Resource/
   ├── 4. Archive/
   └── 999. Claude guideline/
       └── 1. Claude PKM/
           ├── 11. Modules/        ← copy pkm-modules/* here
           ├── 12. Research/
           ├── 13. Troubleshooting/
           └── 14. Specs/
   ```
3. Copy the six PKM modules into `11. Modules/`:
   ```bash
   cp $PROJECT_ROOT/pkm-modules/*.md "<YourVault>/999. Claude guideline/1. Claude PKM/11. Modules/"
   ```
4. Create a `CLAUDE.md` at the Vault root using `CLAUDE.md.example` as a
   starting point.

### 6. Install Python dependencies

```bash
pip install pypdfium2 numpy pandas matplotlib scipy
# Optional (lecture transcription)
pip install openai-whisper
# Make sure ffmpeg is installed:
#   macOS:    brew install ffmpeg
#   Windows:  scoop install ffmpeg
#   Linux:    apt install ffmpeg
```

### 7. Install the experiment pipeline (optional)

```bash
cd $PROJECT_ROOT/experiment-pipeline
# Use the standard 4-function interface:
#   modules/{measurement_type}.py  with load, fit, plot, export functions
```

See [`experiment-pipeline/README.md`](../experiment-pipeline/README.md) for
details on the four-function interface.

### 8. Sanity check

Open a new Claude Code session in your project directory and try one of the
slash commands:

```text
/lit-search spintronics SiC
```

You should see the Claude session pick up the workflow specification from
`.claude/workflows/lit-search.md` and the corresponding command from
`.claude/commands/lit-search.md`.

## Troubleshooting

| Symptom                                                | Likely cause                                          | Fix                                                  |
|--------------------------------------------------------|-------------------------------------------------------|------------------------------------------------------|
| Hooks fail with "command not found"                    | `$PROJECT_ROOT` not substituted in `settings.json`    | Edit `settings.json` and replace placeholders        |
| Whisper segmentation fault                             | ffmpeg missing or wrong PATH                          | Install ffmpeg and ensure it's on `PATH`             |
| Slash commands don't appear                            | `.claude/commands/` not copied to `~/.claude/`         | Re-run the copy step                                 |
| Wikilink lint hook errors on `SessionStart`             | Vault path mismatch                                   | Update `lint_wikilinks.py` or remove the hook        |
| PKM index doesn't update on file write                  | `pkm_update_index.py` path wrong in `settings.json`    | Fix path                                             |

## Customization tips

- **Different languages**: The modules and templates use placeholder language
  policies. Edit `M-001` (and the others) to set your preferred response
  language and terminology mappings.
- **Different research domain**: `M-006` is written for measurement-type data
  (AMR, AHE, etc.). To adapt to other domains (sequencing, microscopy,
  simulations), copy `modules/amr.py` as a template and implement the
  standard 4-function interface.
- **Disable hooks selectively**: Remove the entire entry from `settings.json`
  — hooks are opt-in.

## Next steps

- Read [`00-overview.md`](00-overview.md) for the design philosophy.
- Read [`pkm-modules/M-001`](../pkm-modules/M-001_lecture-note-routine.md)
  as the canonical example of a PKM module.
- Read [`experiment-pipeline/README.md`](../experiment-pipeline/README.md)
  for the experiment data system.
