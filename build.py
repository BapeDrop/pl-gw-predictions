#!/usr/bin/env python3
"""Build the GW predictions tracker page from the official FPL feed.

Usage:  python3 build.py            -> writes gw-predictions.html next to this file
Then publish with the Artifact tool using the URL in README.md.
"""
import json, os, sys, urllib.request, datetime

BASE = "https://fantasy.premierleague.com/api/"
START_GW = 4           # first gameweek the group tracked
HERE = os.path.dirname(os.path.abspath(__file__))

def get(path):
    req = urllib.request.Request(BASE + path, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

b = get("bootstrap-static/")
fixtures_all = get("fixtures/")
teams = {t["id"]: t for t in b["teams"]}
pos = {p["id"]: p["singular_name_short"] for p in b["element_types"]}
events = {e["id"]: e for e in b["events"]}

# Which gameweeks to include: START_GW .. the next unfinished one (the one being predicted)
next_gw = next((e["id"] for e in b["events"] if e["is_next"]), None)
current_gw = next((e["id"] for e in b["events"] if e["is_current"]), None)
last_gw = next_gw or current_gw or START_GW
# If the current GW is still in progress (not finished), it is the one being played; also show next.
gw_ids = list(range(START_GW, last_gw + 1))

# League table from finished fixtures
tab = {t: {"p": 0, "w": 0, "d": 0, "l": 0, "gf": 0, "ga": 0, "pts": 0, "form": []} for t in teams}
for f in sorted(fixtures_all, key=lambda x: (x["event"] or 99, x["kickoff_time"] or "")):
    if not f["finished"]:
        continue
    h, a, hs, as_ = f["team_h"], f["team_a"], f["team_h_score"], f["team_a_score"]
    for t, gf, ga in ((h, hs, as_), (a, as_, hs)):
        r = tab[t]; r["p"] += 1; r["gf"] += gf; r["ga"] += ga
        if gf > ga: r["w"] += 1; r["pts"] += 3; r["form"].append("W")
        elif gf == ga: r["d"] += 1; r["pts"] += 1; r["form"].append("D")
        else: r["l"] += 1; r["form"].append("L")
order = sorted(tab, key=lambda t: (-tab[t]["pts"], -(tab[t]["gf"] - tab[t]["ga"]), -tab[t]["gf"]))
rank = {t: i + 1 for i, t in enumerate(order)}
out_teams = {}
for t, tt in teams.items():
    r = tab[t]
    out_teams[t] = {"name": tt["name"], "short": tt["short_name"], "rank": rank[t], "p": r["p"], "w": r["w"],
                    "d": r["d"], "l": r["l"], "gf": r["gf"], "ga": r["ga"], "pts": r["pts"], "form": "".join(r["form"][-5:])}

players = []
for e in b["elements"]:
    if e["minutes"] == 0 and float(e["selected_by_percent"]) < 1:
        continue
    players.append({"id": e["id"], "n": e["web_name"], "full": e["first_name"] + " " + e["second_name"],
                    "pos": pos[e["element_type"]], "t": e["team"], "price": e["now_cost"] / 10,
                    "pts": e["total_points"], "form": e["form"], "g": e["goals_scored"], "a": e["assists"],
                    "cs": e["clean_sheets"], "min": e["minutes"], "sel": e["selected_by_percent"]})

gameweeks = []
for g in gw_ids:
    ev = events[g]
    fx = [f for f in fixtures_all if f["event"] == g]
    fx.sort(key=lambda x: (x["kickoff_time"] or "", x["id"]))
    entry = {"id": g, "deadline": ev["deadline_time"], "finished": ev["finished"],
             "fixtures": [{"id": f["id"], "ko": f["kickoff_time"], "h": f["team_h"], "a": f["team_a"],
                           "hs": f["team_h_score"], "as": f["team_a_score"], "fin": bool(f["finished"]),
                           "started": bool(f["started"])} for f in fx],
             "live": {}}
    if any(f["started"] for f in fx):
        live = get(f"event/{g}/live/")
        entry["live"] = {str(e["id"]): e["stats"]["total_points"] for e in live["elements"] if e["stats"]["minutes"] > 0 or e["stats"]["total_points"]}
    gameweeks.append(entry)

data = {"teams": out_teams, "players": players, "gameweeks": gameweeks,
        "built": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}
payload = json.dumps(data, separators=(",", ":")).replace("</", "<\\/")
tpl = open(os.path.join(HERE, "template.html")).read()
out = os.path.join(HERE, "gw-predictions.html")
open(out, "w").write(tpl.replace("__DATA__", payload))
print("gameweeks:", gw_ids, "| players:", len(players), "| wrote", out, os.path.getsize(out), "bytes")
for gw in gameweeks:
    print(f"  GW{gw['id']}: {len(gw['fixtures'])} fixtures, {sum(f['fin'] for f in gw['fixtures'])} finished, live pts for {len(gw['live'])} players")
