# Sprint Estimator

A small desktop app to estimate development days for sprint tickets, based on
story points and how many Senior/Junior developers are assigned.

## What it does

For each ticket you add (story point, number of Senior devs, number of Junior devs):

- **If Junior = 0** → uses the "Single Member" formula
  `days = story_point / (devs * factor)`, where factor depends on story point
  (1.0 for SP <= 3, 0.9 for 5, 0.85 for 8, 0.8 for SP >= 13).
- **If Junior >= 1** → uses the "Team Estimation" formula
  `days = story_point / (devs * (1 - loss))`, where loss depends on story point
  (0% for SP <= 2, 20% for 3, 30% for 5, 35% for 8, 40% for SP >= 13).
- A ticket with 0 Senior and 0 Junior cannot be added.

The app shows a running table of tickets, total estimated days, and lets you
type in a sprint capacity (in days) to see if the plan is over or under budget.

Nothing is saved between sessions — it's a pure calculator. Close the app and
it resets.

## Requirements

- Ubuntu with Python 3 (already installed by default on modern Ubuntu).
- `python3-tk` — usually needs a one-time install:
  ```
  sudo apt install python3-tk
  ```

## Running it

**Option 1: from a terminal**
```
python3 app.py
```

**Option 2: as a clickable app (recommended)**
```
chmod +x install.sh
./install.sh
```
This adds "Sprint Estimator" to your applications menu and (if you have a
Desktop folder) puts an icon there too. On first double-click, Ubuntu/Nautilus
may ask you to confirm "Allow Launching" for the new `.desktop` file — that's
a one-time security prompt, not an error.

## Files

- `app.py` — the app itself
- `sprint-estimator.desktop` — launcher template (used by install.sh)
- `icon.png` — app icon
- `install.sh` — one-time setup script for the clickable launcher
