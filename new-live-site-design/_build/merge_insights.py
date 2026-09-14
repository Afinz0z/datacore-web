# -*- coding: utf-8 -*-
"""Merge the 3 subagent draft files (insights-A/B/C.json from the scratchpad) into
insights.json, in value order A->B->C. Assigns each new post its branded image
(dc-insight-<slug>.webp) and validates schema + related-service slugs before saving."""
import os, json, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
SCRATCH = sys.argv[1] if len(sys.argv) > 1 else "."
INS_P = os.path.join(HERE, "insights.json")

REQ = ["slug", "title", "date", "team", "iso", "dek", "meta", "blocks", "faq", "related"]

def valid_service(slug):
    return os.path.exists(os.path.join(ROOT, "service-" + slug + ".html"))

ins = json.load(open(INS_P, encoding="utf-8"))
existing = {p["slug"] for p in ins["en"]["posts"]}
problems = []
added = 0

for grp in ["A", "B", "C"]:
    fp = os.path.join(SCRATCH, "insights-" + grp + ".json")
    if not os.path.exists(fp):
        problems.append("MISSING FILE: " + fp); continue
    d = json.load(open(fp, encoding="utf-8"))
    en, ar = d["en"], d["ar"]
    if len(en) != len(ar):
        problems.append(grp + ": en/ar length mismatch %d/%d" % (len(en), len(ar)))
    for i, ep in enumerate(en):
        ap = ar[i]
        slug = ep["slug"]
        if slug != ap["slug"]:
            problems.append(grp + "[%d]: slug mismatch %s / %s" % (i, slug, ap["slug"]))
        if slug in existing:
            problems.append(grp + ": duplicate slug " + slug); continue
        for r in REQ:
            if r not in ep: problems.append(grp + " " + slug + ": en missing " + r)
            if r not in ap: problems.append(grp + " " + slug + ": ar missing " + r)
        # image
        ep["img"] = "dc-insight-" + slug + ".webp"
        # validate related slugs (fix on en+ar), drop invalid
        for post in (ep, ap):
            good = []
            for pair in post.get("related", []):
                if valid_service(pair[0]):
                    good.append(pair)
                else:
                    problems.append(grp + " " + slug + ": DROP bad related '" + pair[0] + "'")
            post["related"] = good
        ins["en"]["posts"].append(ep)
        ins["ar"]["posts"].append(ap)
        existing.add(slug)
        added += 1

json.dump(ins, open(INS_P, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("added", added, "posts; total en posts:", len(ins["en"]["posts"]))
print("slugs:", [p["slug"] for p in ins["en"]["posts"]])
if problems:
    print("\n--- ISSUES (", len(problems), ") ---")
    for p in problems[:40]:
        print(" ", p)
else:
    print("no issues")
