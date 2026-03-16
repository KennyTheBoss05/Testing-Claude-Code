# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a minimal test/experimentation project. Currently it contains a single Python script (`hello.py`) used for testing Claude Code features.

## Running Code

```bash
python hello.py
```

## Git Workflow

After every set of code changes, commit and push to GitHub:

1. Stage only the relevant changed files (avoid `git add -A` or `git add .`)
2. Write a concise commit message in imperative mood (e.g. "Add greeting function", "Fix off-by-one error in loop")
3. Push to the remote branch

```bash
git add <specific-files>
git commit -m "Short imperative summary of what changed"
git push
```

Commit messages should say *what* changed and *why* if the reason isn't obvious — never just "update files" or "fix stuff".

## Environment

- Python via conda (configured in `.vscode/settings.json`)
- GitHub CLI available with permissions for `gh auth status` and `gh api` calls (configured in `.claude/settings.local.json`)
