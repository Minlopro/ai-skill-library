#!/usr/bin/env python3
"""Ranked search over the Minlopro product library's asset manifests and READMEs.

Usage: search.py --library <repo dir> TERM [TERM ...] [--cloud C] [--category C] [--metadata T] [--top N] [--json]
Terms can be phrases ("record type"). Stdlib only; read-only.
"""
import argparse, json, os, re, sys

WEIGHTS = {"title": 6, "tags": 5, "metadata": 4, "summary": 3, "name": 3, "configuration": 1, "readme": 1}

def load(lib):
    root = os.path.join(lib, "assets")
    if not os.path.isdir(root):
        sys.exit(f"No assets/ folder in {lib}. Is this the product library?")
    out = []
    for cat in sorted(os.listdir(root)):
        cdir = os.path.join(root, cat)
        if not os.path.isdir(cdir):
            continue
        for name in sorted(os.listdir(cdir)):
            adir = os.path.join(cdir, name)
            mf = os.path.join(adir, "asset.json")
            if not os.path.isfile(mf):
                continue
            try:
                m = json.load(open(mf, encoding="utf-8"))
            except ValueError as e:
                print(f"skip {cat}/{name}: bad asset.json ({e})", file=sys.stderr)
                continue
            readme = os.path.join(adir, "README.md")
            m["_readme"] = open(readme, encoding="utf-8").read() if os.path.isfile(readme) else ""
            m["_path"] = f"assets/{cat}/{name}"
            m.setdefault("name", name)
            m.setdefault("category", cat)
            files = []
            for d, _, fs in os.walk(os.path.join(adir, "force-app")):
                files += [os.path.relpath(os.path.join(d, f), adir) for f in fs]
            m["_files"] = len(files)
            out.append(m)
    return out

def field_text(m, f):
    v = m.get("_readme") if f == "readme" else m.get(f, "")
    return " ".join(v) if isinstance(v, list) else str(v or "")

def score(m, terms):
    total, why = 0.0, []
    for t in terms:
        rx = re.compile(r"\b" + r"\W*".join(map(re.escape, t.lower().split())) + r"\w*", re.I)
        hit = []
        for f, w in WEIGHTS.items():
            n = len(rx.findall(field_text(m, f)))
            if n:
                total += w * (1 + min(n, 5) * 0.2 if f == "readme" else 1)
                hit.append(f)
        if hit:
            why.append(f"{t} ({', '.join(hit)})")
    return total, why

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("terms", nargs="+")
    ap.add_argument("--library", default=os.path.expanduser("~/.helm/library/mirror"))
    ap.add_argument("--cloud"); ap.add_argument("--category")
    ap.add_argument("--metadata", action="append", default=[])
    ap.add_argument("--top", type=int, default=8)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    rows = []
    for m in load(a.library):
        if a.category and m.get("category") != a.category:
            continue
        if a.cloud and a.cloud.lower() not in [c.lower() for c in m.get("clouds", [])]:
            continue
        if a.metadata and not all(t.lower() in [x.lower() for x in m.get("metadata", [])] for t in a.metadata):
            continue
        s, why = score(m, a.terms)
        if s > 0:
            rows.append({"score": round(s, 1), "asset": f"{m['category']}/{m['name']}", "version": m.get("version", "?"),
                         "title": m.get("title", m["name"]), "matched": len(why), "of": len(a.terms), "why": why,
                         "dependencies": m.get("dependencies", []), "configuration": m.get("configuration", []), "files": m["_files"], "path": m["_path"]})
    # Weighted score, with a smaller bonus for covering more of the terms (README mentions alone
    # shouldn't outrank an asset whose title, tags, and metadata match).
    for r in rows:
        r["rank"] = round(r["score"] * (0.5 + 0.5 * r["matched"] / r["of"]), 1)
    rows.sort(key=lambda r: -r["rank"])
    rows = rows[: a.top]
    if a.json:
        print(json.dumps(rows, indent=1)); return
    if not rows:
        print("No match. Build new, or try synonyms (see SKILL.md step 2)."); return
    print(f"{'rank':>5}  {'terms':>5}  asset (version)  ·  why")
    for r in rows:
        print(f"{r['rank']:>5}  {r['matched']}/{r['of']:<3}  {r['asset']} ({r['version']})  ·  {'; '.join(r['why'])}")
        if r["dependencies"]:
            print(f"{'':>14}needs: {', '.join(r['dependencies'])}")

if __name__ == "__main__":
    main()
