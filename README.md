# PL gameweek predictions tracker (Leo, Jack, Max)

Artifact URL: https://claude.ai/code/artifact/357078a0-88ab-4b6c-a3a6-1c248b5ae9da

Weekly refresh (do this after the previous gameweek finishes, before the next one starts):

    python3 ~/pl-gw-predictions/build.py

then republish `~/pl-gw-predictions/gw-predictions.html` to the artifact URL above
(Artifact tool, pass `url`; capabilities are already stored on the artifact, keep `db`).

Scoring: exact score 3, correct result 1, player pick = that player's FPL points in the gameweek.
Predictions and picks live in the artifact's db (collection `gameweeks`, docs `gw4`, `gw5`, ...).
