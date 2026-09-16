# PL gameweek predictions tracker (Leo, Jack, Max)

Artifact URL: https://claude.ai/code/artifact/357078a0-88ab-4b6c-a3a6-1c248b5ae9da

Weekly refresh (do this after the previous gameweek finishes, before the next one starts):

    python3 ~/pl-gw-predictions/build.py

then republish `~/pl-gw-predictions/gw-predictions.html` to the artifact URL above
(Artifact tool, pass `url`; capabilities are already stored on the artifact, keep `db`).

Scoring: exact score 3, correct result 1, player pick = that player's FPL points in the gameweek.
Predictions and picks live in the artifact's db (collection `gameweeks`, docs `gw4`, `gw5`, ...).

## Automation
Two-step, because the claude.ai cloud sandbox cannot reach fantasy.premierleague.com:
1. GitHub Actions (`.github/workflows/build.yml`) runs build.py Tue + Fri 10:00 UTC and commits gw-predictions.html.
2. Cloud routine "PL predictions tracker refresh" (trig_01DD82AtyGzTbLsYnopX3DmG) runs Tue + Fri 11:00 UTC:
   clones this repo and republishes the committed gw-predictions.html to the artifact URL above.
   Manage at https://claude.ai/code/routines
The repo is public so the routine can clone it without a GitHub connection on claude.ai.
