#!/usr/bin/env python3
"""Client-detail scan for a product library asset. Exit 0 = clean, 1 = findings.

Usage: scan.py <asset dir> [--terms "Acme,Riverside"] [--terms-file terms.txt] [--prefix ACME_] [--json]

Scans every file (including inside .zip / static resources) for: client terms (any casing, at
word starts), the client's API prefix, Salesforce org and record IDs, emails, org URLs, phone
numbers, the "MLP" abbreviation in names or labels, and patient-data patterns. Excerpts are
masked so the report itself never repeats the client detail. Stdlib only; read-only.
"""
import argparse, io, json, os, re, sys, zipfile

PATTERNS = [
    ("Org ID", re.compile(r"\b00D[A-Za-z0-9]{12}(?:[A-Za-z0-9]{3})?\b")),
    ("Record ID", re.compile(r"\b(?:001|003|005|006|00G|00Q|00e|00E|012|500|701|a0[0-9A-Za-z])[A-Za-z0-9]{12}(?:[A-Za-z0-9]{3})?\b")),
    ("Email", re.compile(r"\b[A-Za-z0-9._%+-]+@(?!example\.(?:com|org|net)\b)[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("Org URL", re.compile(r"https?://[A-Za-z0-9.-]+\.(?:my\.salesforce|lightning\.force|force|my\.site|salesforce-sites)\.com\S*", re.I)),
    ("Phone number", re.compile(r"(?<!\d)(?:\(\d{3}\)\s?|\b\d{3}[-. ])\d{3}[-. ]\d{4}\b(?!-)")),
    ("MLP in a name or label", re.compile(r"(?:\bMLP(?:_|\b)|\bmlp[A-Z_])")),
]
DATE = r"(?:\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}|\d{4}-\d{2}-\d{2}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4})"
NAME = r"[A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z'-]+"
PHI = [
    ("Possible PHI: named patient", re.compile(r"\b(?:[Pp]atient|PATIENT|[Pp]t\.?)(?:\s+[Nn]ame)?(?:\s*:\s*|\s+[-–]\s+)" + NAME)),
    ("Possible PHI: date of birth", re.compile(r"\b(?:DOB|D\.O\.B\.?|date of birth|born on)\b[:\s]*" + DATE, re.I)),
    ("Possible PHI: medical record number", re.compile(r"\b(?:MRN|medical record (?:number|no\.?|#))\b[:#\s]*(?=[A-Z0-9-]*\d{4})[A-Z0-9-]{4,}", re.I)),
    ("Possible PHI: member ID", re.compile(r"\b(?:member|subscriber|policy)\s*(?:id|#|number)[:#\s]*(?=[A-Z0-9-]*\d{4})[A-Z0-9-]{5,}", re.I)),
    ("Possible PHI: SSN", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
]
TEXT_EXT = {".xml", ".cls", ".trigger", ".js", ".html", ".css", ".json", ".md", ".txt", ".csv", ".page", ".component", ".cmp", ".app", ".evt", ".design", ".svg", ".yaml", ".yml", ".apex", ".soql", ".sh", ".py", ".labels", ".resource"}

def mask(s):
    s = s.strip()
    return "*" * len(s) if len(s) <= 6 else s[:4] + "*" * min(12, len(s) - 4)

def files_in(root):
    for d, dirs, fs in os.walk(root):
        dirs[:] = [x for x in dirs if not x.startswith(".")]
        for f in fs:
            p = os.path.join(d, f)
            rel = os.path.relpath(p, root)
            data = open(p, "rb").read()
            if zipfile.is_zipfile(io.BytesIO(data)):
                with zipfile.ZipFile(io.BytesIO(data)) as z:
                    for n in z.namelist():
                        if not n.endswith("/"):
                            yield f"{rel}!{n}", z.read(n)
            else:
                yield rel, data

def scan(root, terms, prefix):
    term_res = [(t, re.compile(r"\b" + re.escape(t), re.I)) for t in terms if len(t) >= 3]
    if prefix:
        term_res.append((f"prefix {prefix}", re.compile(re.escape(prefix), re.I)))
    out = []
    for rel, data in files_in(root):
        # The file's own path can carry the client too.
        for label, rx in term_res:
            if rx.search(rel):
                out.append({"file": rel, "line": 0, "rule": f"Client term in file name: {label if label.startswith('prefix') else 'term'}", "excerpt": mask(rel)})
        ext = os.path.splitext(rel.split("!")[-1])[1].lower()
        if ext and ext not in TEXT_EXT:
            if b"\x00" in data[:2048]:
                continue  # binary (images, fonts): open and check them by eye
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            text = data.decode("latin-1")
        for i, line in enumerate(text.splitlines(), 1):
            for label, rx in term_res:
                m = rx.search(line)
                if m:
                    out.append({"file": rel, "line": i, "rule": "Client " + ("prefix" if label.startswith("prefix") else "term"), "excerpt": mask(m.group(0))})
            for label, rx in PATTERNS:
                m = rx.search(line)
                # Placeholder IDs (long runs of zeros, e.g. 001000000000001AAA) are obviously fake.
                if m and not (label == "Record ID" and "0000000" in m.group(0)):
                    out.append({"file": rel, "line": i, "rule": label, "excerpt": mask(m.group(0))})
        for label, rx in PHI:
            for m in rx.finditer(text):
                # Synthetic test identifiers carry TEST (MRN-TEST-0001, "Test Patient 1"): allowed.
                if re.search(r"test", m.group(0), re.I):
                    continue
                out.append({"file": rel, "line": text[: m.start()].count("\n") + 1, "rule": label, "excerpt": mask(m.group(0))})
    return out

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("asset")
    ap.add_argument("--terms", default="")
    ap.add_argument("--terms-file")
    ap.add_argument("--prefix")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    terms = [t.strip() for t in a.terms.split(",") if t.strip()]
    if a.terms_file:
        terms += [l.strip() for l in open(a.terms_file, encoding="utf-8") if l.strip() and not l.startswith("#")]
    if not os.path.isdir(a.asset):
        sys.exit(f"{a.asset} isn't a folder.")
    findings = scan(a.asset, terms, a.prefix)
    if a.json:
        print(json.dumps({"findings": findings, "count": len(findings)}, indent=1))
    elif findings:
        print(f"{len(findings)} finding(s). Fix each, then scan again; the asset can't be contributed until this is zero.\n")
        for f in findings:
            print(f"  {f['file']}{':' + str(f['line']) if f['line'] else ''}  {f['rule']}  [{f['excerpt']}]")
    else:
        print(f"Clean: 0 findings ({len(terms)} client terms{', prefix ' + a.prefix if a.prefix else ''}). Now read every file yourself (SKILL.md step 5).")
    sys.exit(1 if findings else 0)

if __name__ == "__main__":
    main()
