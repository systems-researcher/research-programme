"""Extract repos.yml from the plan and run the nine rules against it, ahead of implementation."""
import io
import re
import sys

import yaml

PLAN = r"c:\Users\gower\OneDrive\Documents\GitHub\research-programme\docs\superpowers\plans\2026-08-19-research-programme-map.md"

STRANDS = ("adequacy", "method-validation", "assembly")
STAGES = ("define", "measure", "evidence", "architecture", "assembly")
STATUSES = ("design", "built-runs-pending", "released", "results", "published", "not-applicable")
RENDERS = ("card", "node-only")
REQUIRED = ("key", "owner", "strand", "stage", "objective", "question", "method", "status")
RESULT_STATUSES = ("results", "published")
TERMINUS = "Thesis-Work-Area"
OWNER_RE = re.compile(r"^[A-Za-z0-9-]+$")

text = io.open(PLAN, encoding="utf-8").read()
marker = "`repos.yml`:\n\n```yaml\n"
start = text.index(marker) + len(marker)
end = text.index("\n```", start)
raw = yaml.safe_load(text[start:end])

repos = raw["repos"]
for e in repos:
    e.setdefault("render", "card")
    e.setdefault("depends_on", [])
by_key = {e["key"]: e for e in repos}

errors = []

for i, e in enumerate(repos):  # rule 3
    name = e.get("key") or f"entry #{i+1}"
    for f in REQUIRED:
        if not e.get(f):
            errors.append(f"rule3 {name}: missing '{f}'")

for e in repos:  # rule 1
    for d in e["depends_on"]:
        if d not in by_key:
            errors.append(f"rule1 {e['key']}: unknown dependency '{d}'")

for e in repos:  # rules 2 and 7
    for f, allowed in (("strand", STRANDS), ("stage", STAGES), ("status", STATUSES), ("render", RENDERS)):
        if e.get(f) not in allowed:
            errors.append(f"rule2 {e['key']}: {f}='{e.get(f)}' not permitted")
    if not OWNER_RE.match(str(e.get("owner", ""))):
        errors.append(f"rule7 {e['key']}: owner '{e.get('owner')}' malformed")

seen = set()
for e in repos:
    if e["key"] in seen:
        errors.append(f"rule7 duplicate key '{e['key']}'")
    seen.add(e["key"])

for e in repos:  # rule 4
    if TERMINUS in e["depends_on"]:
        errors.append(f"rule4 {e['key']}: depends on the terminus")

for e in repos:  # rules 5 and 6
    hl = e.get("headline")
    if hl and e["status"] not in RESULT_STATUSES:
        errors.append(f"rule5 {e['key']}: headline with status '{e['status']}'")
    if e["status"] == "not-applicable" and e["render"] != "node-only":
        errors.append(f"rule5 {e['key']}: not-applicable on a card entry")
    if hl:
        for part in ("text", "source"):
            if not hl.get(part):
                errors.append(f"rule6 {e['key']}: headline missing '{part}'")

for e in repos:  # rule 8
    if e["stage"] not in raw["stages"]:
        errors.append(f"rule8 {e['key']}: stage '{e['stage']}' has no explanation line")
    if e["strand"] not in raw["strands"]:
        errors.append(f"rule8 {e['key']}: strand '{e['strand']}' has no heading")
for f in ("title", "question", "move"):
    if not raw.get("programme", {}).get(f):
        errors.append(f"rule8 programme.{f} missing")

visiting, done = [], set()  # rule 9


def walk(key):
    if key in done:
        return
    if key in visiting:
        errors.append("rule9 cycle: " + " -> ".join(visiting[visiting.index(key):] + [key]))
        return
    visiting.append(key)
    for d in by_key.get(key, {}).get("depends_on", []):
        if d in by_key:
            walk(d)
    visiting.pop()
    done.add(key)


for e in repos:
    walk(e["key"])

feeds = {e["key"]: [] for e in repos}
for e in repos:
    for d in e["depends_on"]:
        feeds[d].append(e["key"])

print(f"entries: {len(repos)}")
print(f"headlines: {sum(1 for e in repos if e.get('headline'))}")
print("statuses:", {s: sum(1 for e in repos if e["status"] == s) for s in STATUSES if any(e["status"] == s for e in repos)})
orphans = [k for k, v in feeds.items() if not v and k != TERMINUS]
print("feeds nothing (besides the terminus):", orphans or "none")
if errors:
    print("\nFAIL")
    for x in errors:
        print(" ", x)
    sys.exit(1)
print("\nall nine rules pass")
