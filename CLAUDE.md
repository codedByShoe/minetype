# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the app

```bash
uv run main.py
```

No build step or dependencies beyond the Python standard library — `tkinter` is used for the GUI.

## Architecture

Everything lives in a single file: `main.py`.

**Module-level constants:**
- `LESSONS` — list of dicts, each with `name`, `keys` (list of chars), and `hint`
- `PRAISE` — random positive feedback strings shown on correct keypress
- Color/font constants (`BG`, `CARD_BG`, `ACCENT`, etc.) define the dark theme

**`TypingTutor` class** wraps the entire app:
- `__init__` — sets up state (`lesson_idx`, `score`, `streak`, `best_streak`, `total`) and calls `_build_ui()` + `_new_target()`
- `_build_ui()` — constructs the tkinter widget tree: top bar (lesson label), score strip, main card (hint + giant target character + feedback), bottom nav buttons
- `_new_target()` — picks a random char from the current lesson's `keys` list and displays it
- `on_key(event)` — bound to `<KeyPress>` on root; routes to `_correct()` or `_wrong()`
- `_correct()` / `_wrong()` — update score/streak labels and card highlight color; `_correct` schedules `_new_target` after 420 ms; `_wrong` triggers `_shake()`
- `_shake()` — recursive `root.after()` animation that jiggles the card via `pack_configure(padx=...)`
- `_next_lesson()` / `_prev_lesson()` — increment/decrement `lesson_idx`, reset streak, call `_new_target()`

To add a new lesson, append a dict to the `LESSONS` list. No other changes needed.
