#!/usr/bin/env python3
"""Offline validation of the public Smart 453 reference.

No vehicle, no proprietary DDT database, no firmware image is required.
Exit code 0 means the public candidate passes the checks in this file.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
LEVELS = {"L1", "L2", "L3", "L4", "L5"}
STATUSES = {"CONFIRMED", "UNCONFIRMED", "CONTRADICTED", "NOT_TESTED", "NOT_APPLICABLE"}
PUB_DECISIONS = {"PUBLIC_DERIVED", "PUBLIC_FULL", "PUBLIC_METADATA", "INTERNAL_ONLY"}
RAW_DECISIONS = {"BLOCK", "BLOCK_NO_ARCHIVE", "ALLOW_EXISTING_CASE", "METADATA_ONLY"}
QUALITY = {"A", "B", "C", "D", "E"}

REQUIRED = [
    "README.md",
    "methodology/evidence-levels.md",
    "methodology/reproducibility.md",
    "evidence/evidence-register.md",
    "evidence/phase6-7-validation.md",
    "evidence/phase8-4-consolidation.md",
    "evidence/claims-register.md",
    "sources/sources.md",
    "ecu/edison/overview.md",
    "ecu/edison/firmware.md",
    "ecu/edison/dump-feasibility.md",
    "ecu/tomtom-headunit/overview.md",
    "ecu/tomtom-headunit/firmware.md",
    "ecu/tomtom-headunit/dump-feasibility.md",
    "diagnostics/README.md",
    "diagnostics/edison.md",
    "diagnostics/headunit.md",
    "configuration/README.md",
    "configuration/edison.md",
    "configuration/headunit.md",
    "firmware/README.md",
    "compatibility/README.md",
    "research-gaps/README.md",
    "schemas/README.md",
    "tools/validate_public.py",
    "data/evidence.json",
    "data/claims.csv",
    "data/sources.csv",
    "data/counts.json",
    "data/phase6_7_evidence.json",
    "data/phase6_7_claims.csv",
    "data/phase6_7_sources.csv",
    "data/phase6_7_counts.json",
    "data/phase8_4_evidence.json",
    "data/phase8_4_claims.csv",
    "data/phase8_4_sources.csv",
    "data/phase8_4_counts.json",
    "data/firmware_metadata.csv",
    "data/obd_dump_feasibility.csv",
]

# Patterns that must not appear in public documentation/data.
# The validator excludes its own source from the scan so its regex strings
# do not flag themselves.
FORBIDDEN = [
    (re.compile(r"/home/[A-Za-z0-9._-]+"), "absolute home path"),
    (re.compile(r"/Users/[A-Za-z0-9._-]+"), "absolute macOS home path"),
    (re.compile(r"~/\.[A-Za-z0-9._-]+"), "home-relative hidden path"),
    (re.compile(r"\b(?:10\.\d{1,3}|192\.168|172\.(?:1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}\b"), "RFC 1918 address"),
    (re.compile(r"\b[0-9A-F]{2}(?::[0-9A-F]{2}){5}\b"), "MAC address"),
    (re.compile(r"\b(?:WME|WDD|VF1|VF3|TCC)[A-Z0-9]{14}\b"), "VIN pattern"),
    (re.compile(r"(?i)\b(password|passwd|token|secret|api[_-]?key)\s*[:=]\s*\S+"), "credential assignment"),
    (re.compile(r"BEGIN [A-Z ]*PRIVATE KEY"), "private key"),
    (re.compile(r"\b(?:10|21|22|2E|30|3B)\s+[0-9A-F]{2}\b"), "raw diagnostic request/response pair"),
]

ALLOWED_SUFFIXES = {".md", ".json", ".csv", ".py", ".txt"}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_csv(path: Path):
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-links", action="store_true", help="skip relative-link resolution")
    ap.add_argument("--out", default="validation_report.json")
    args = ap.parse_args()

    errors: list[str] = []
    warnings: list[str] = []
    checks = Counter()

    for rel in REQUIRED:
        if not (ROOT / rel).exists():
            errors.append(f"missing required file: {rel}")
        checks["required_files"] += 1

    # Parse public data.
    try:
        evidence = load_json(DATA / "evidence.json")["evidence"]
        claims = load_csv(DATA / "claims.csv")
        sources = load_csv(DATA / "sources.csv")
        counts = load_json(DATA / "counts.json")
        fw = load_csv(DATA / "firmware_metadata.csv")
        feas = load_csv(DATA / "obd_dump_feasibility.csv")
        p67_evidence = load_json(DATA / "phase6_7_evidence.json")["evidence"]
        p67_claims = load_csv(DATA / "phase6_7_claims.csv")
        p67_sources = load_csv(DATA / "phase6_7_sources.csv")
        p67_counts = load_json(DATA / "phase6_7_counts.json")
        p84_evidence = load_json(DATA / "phase8_4_evidence.json")["evidence"]
        p84_claims = load_csv(DATA / "phase8_4_claims.csv")
        p84_sources = load_csv(DATA / "phase8_4_sources.csv")
        p84_counts = load_json(DATA / "phase8_4_counts.json")
    except Exception as exc:
        errors.append(f"cannot parse public data: {exc}")
        evidence, claims, sources, counts, fw, feas = [], [], [], {}, [], []
        p67_evidence, p67_claims, p67_sources, p67_counts = [], [], [], {}
        p84_evidence, p84_claims, p84_sources, p84_counts = [], [], [], {}

    source_ids = {s.get("source_id") for s in sources if s.get("source_id")}
    source_ids |= {s.get("source_id") for s in p67_sources if s.get("source_id")}
    source_ids |= {s.get("source_id") for s in p84_sources if s.get("source_id")}
    evidence_ids = {e.get("evidence_id") for e in evidence if e.get("evidence_id")}
    evidence_ids |= {e.get("evidence_id") for e in p67_evidence if e.get("evidence_id")}
    evidence_ids |= {e.get("evidence_id") for e in p84_evidence if e.get("evidence_id")}

    # Evidence checks.
    for e in evidence:
        eid = e.get("evidence_id", "<missing>")
        checks["evidence"] += 1
        if not eid or eid == "<missing>":
            errors.append("evidence entry without evidence_id")
            continue
        if e.get("level") not in LEVELS:
            errors.append(f"{eid}: invalid level {e.get('level')!r}")
        if e.get("status") not in STATUSES:
            errors.append(f"{eid}: invalid status {e.get('status')!r}")
        if not e.get("statement"):
            errors.append(f"{eid}: empty statement")
        if not e.get("hardware_scope") or not e.get("software_scope"):
            errors.append(f"{eid}: missing hardware/software scope")
        ids = e.get("source_ids") or []
        if not ids:
            errors.append(f"{eid}: no source_ids")
        for sid in ids:
            if sid not in source_ids:
                errors.append(f"{eid}: unknown source_id {sid}")
        if e.get("level") == "L1":
            if not e.get("measurement_ref"):
                errors.append(f"{eid}: L1 without measurement_ref")
        if e.get("level") == "L2":
            if not e.get("artifact_ref"):
                errors.append(f"{eid}: L2 without artifact_ref")
        if e.get("level") == "L5" and not e.get("residual_uncertainty"):
            errors.append(f"{eid}: L5 without residual_uncertainty")
        if e.get("publication_decision") not in PUB_DECISIONS:
            errors.append(f"{eid}: invalid publication_decision")
        if e.get("raw_publication") not in RAW_DECISIONS:
            errors.append(f"{eid}: invalid raw_publication")

    if len({e.get("evidence_id") for e in evidence}) != len(evidence):
        errors.append("duplicate evidence_id in evidence.json")

    for e in p67_evidence:
        eid = e.get("evidence_id", "<missing>")
        checks["phase6_7_evidence"] += 1
        if not eid or eid == "<missing>":
            errors.append("Phase 6.7 evidence entry without evidence_id")
            continue
        if e.get("level") not in LEVELS:
            errors.append(f"{eid}: invalid level {e.get('level')!r}")
        if e.get("status") not in STATUSES:
            errors.append(f"{eid}: invalid status {e.get('status')!r}")
        if not e.get("statement"):
            errors.append(f"{eid}: empty statement")
        if not e.get("hardware_scope") or not e.get("software_scope"):
            errors.append(f"{eid}: missing hardware/software scope")
        ids = e.get("source_ids") or []
        if not ids:
            errors.append(f"{eid}: no source_ids")
        for sid in ids:
            if sid not in source_ids:
                errors.append(f"{eid}: unknown source_id {sid}")
        if e.get("level") == "L1" and not e.get("measurement_ref"):
            errors.append(f"{eid}: L1 without measurement_ref")
        if e.get("level") == "L2" and not e.get("artifact_ref"):
            errors.append(f"{eid}: L2 without artifact_ref")
        if e.get("level") == "L5" and not e.get("residual_uncertainty"):
            errors.append(f"{eid}: L5 without residual_uncertainty")
        if e.get("publication_decision") not in PUB_DECISIONS:
            errors.append(f"{eid}: invalid publication_decision")
        if e.get("raw_publication") not in RAW_DECISIONS:
            errors.append(f"{eid}: invalid raw_publication")

    if len({e.get("evidence_id") for e in p67_evidence}) != len(p67_evidence):
        errors.append("duplicate evidence_id in phase6_7_evidence.json")

    for e in p84_evidence:
        eid = e.get("evidence_id", "<missing>")
        checks["phase8_4_evidence"] += 1
        if not eid or eid == "<missing>":
            errors.append("Phase 8.4 evidence entry without evidence_id")
            continue
        if e.get("level") not in LEVELS:
            errors.append(f"{eid}: invalid level {e.get('level')!r}")
        if e.get("status") not in STATUSES:
            errors.append(f"{eid}: invalid status {e.get('status')!r}")
        if not e.get("statement"):
            errors.append(f"{eid}: empty statement")
        if not e.get("hardware_scope") or not e.get("software_scope"):
            errors.append(f"{eid}: missing hardware/software scope")
        ids = e.get("source_ids") or []
        if not ids:
            errors.append(f"{eid}: no source_ids")
        for sid in ids:
            if sid not in source_ids:
                errors.append(f"{eid}: unknown source_id {sid}")
        if e.get("level") == "L1" and not e.get("measurement_ref"):
            errors.append(f"{eid}: L1 without measurement_ref")
        if e.get("level") == "L2" and not e.get("artifact_ref"):
            errors.append(f"{eid}: L2 without artifact_ref")
        if e.get("level") == "L5" and not e.get("residual_uncertainty"):
            errors.append(f"{eid}: L5 without residual_uncertainty")
        if e.get("publication_decision") not in PUB_DECISIONS:
            errors.append(f"{eid}: invalid publication_decision")
        if e.get("raw_publication") not in RAW_DECISIONS:
            errors.append(f"{eid}: invalid raw_publication")

    if len({e.get("evidence_id") for e in p84_evidence}) != len(p84_evidence):
        errors.append("duplicate evidence_id in phase8_4_evidence.json")

    # Claim checks.
    for c in claims:
        cid = c.get("claim_id", "<missing>")
        checks["claims"] += 1
        if not cid or cid == "<missing>":
            errors.append("claim without claim_id")
            continue
        if c.get("status") not in STATUSES:
            errors.append(f"{cid}: invalid status {c.get('status')!r}")
        ids = [x for x in (c.get("evidence_ids") or "").split(";") if x]
        if not ids:
            errors.append(f"{cid}: no evidence_ids")
        for eid in ids:
            if eid not in evidence_ids:
                errors.append(f"{cid}: unknown evidence_id {eid}")
        if not c.get("explanation"):
            errors.append(f"{cid}: empty explanation")

    if len({c.get("claim_id") for c in claims}) != len(claims):
        errors.append("duplicate claim_id in claims.csv")

    for c in p67_claims:
        cid = c.get("claim_id", "<missing>")
        checks["phase6_7_claims"] += 1
        if not cid or cid == "<missing>":
            errors.append("Phase 6.7 claim without claim_id")
            continue
        if c.get("status") not in STATUSES:
            errors.append(f"{cid}: invalid status {c.get('status')!r}")
        ids = [x for x in (c.get("evidence_ids") or "").split(";") if x]
        if not ids:
            errors.append(f"{cid}: no evidence_ids")
        for eid in ids:
            if eid not in evidence_ids:
                errors.append(f"{cid}: unknown evidence_id {eid}")
        if not c.get("explanation"):
            errors.append(f"{cid}: empty explanation")

    if len({c.get("claim_id") for c in p67_claims}) != len(p67_claims):
        errors.append("duplicate claim_id in phase6_7_claims.csv")

    for c in p84_claims:
        cid = c.get("claim_id", "<missing>")
        checks["phase8_4_claims"] += 1
        if not cid or cid == "<missing>":
            errors.append("Phase 8.4 claim without claim_id")
            continue
        if c.get("status") not in STATUSES:
            errors.append(f"{cid}: invalid status {c.get('status')!r}")
        ids = [x for x in (c.get("evidence_ids") or "").split(";") if x]
        if not ids:
            errors.append(f"{cid}: no evidence_ids")
        for eid in ids:
            if eid not in evidence_ids:
                errors.append(f"{cid}: unknown evidence_id {eid}")
        if not c.get("explanation"):
            errors.append(f"{cid}: empty explanation")

    if len({c.get("claim_id") for c in p84_claims}) != len(p84_claims):
        errors.append("duplicate claim_id in phase8_4_claims.csv")

    # Source checks.
    for s in sources:
        sid = s.get("source_id", "<missing>")
        checks["sources"] += 1
        if not sid or sid == "<missing>":
            errors.append("source without source_id")
            continue
        if s.get("quality_class") not in QUALITY:
            errors.append(f"{sid}: invalid quality_class")
        if s.get("publication_decision") not in {"CITE", "CITE_CAVEAT", "INTERNAL_ONLY", "DO_NOT_CITE"}:
            errors.append(f"{sid}: invalid publication_decision")
        if s.get("availability") == "public" and s.get("publication_decision") == "DO_NOT_CITE":
            warnings.append(f"{sid}: public but marked DO_NOT_CITE")

    if len({s.get("source_id") for s in sources}) != len(sources):
        errors.append("duplicate source_id in sources.csv")

    for s in p67_sources:
        sid = s.get("source_id", "<missing>")
        checks["phase6_7_sources"] += 1
        if not sid or sid == "<missing>":
            errors.append("Phase 6.7 source without source_id")
            continue
        if s.get("quality_class") not in QUALITY:
            errors.append(f"{sid}: invalid quality_class")
        if s.get("publication_decision") not in {"CITE", "CITE_CAVEAT", "INTERNAL_ONLY", "DO_NOT_CITE"}:
            errors.append(f"{sid}: invalid publication_decision")

    if len({s.get("source_id") for s in p67_sources}) != len(p67_sources):
        errors.append("duplicate source_id in phase6_7_sources.csv")

    for s in p84_sources:
        sid = s.get("source_id", "<missing>")
        checks["phase8_4_sources"] += 1
        if not sid or sid == "<missing>":
            errors.append("Phase 8.4 source without source_id")
            continue
        if s.get("quality_class") not in QUALITY:
            errors.append(f"{sid}: invalid quality_class")
        if s.get("publication_decision") not in {"CITE", "CITE_CAVEAT", "INTERNAL_ONLY", "DO_NOT_CITE"}:
            errors.append(f"{sid}: invalid publication_decision")

    if len({s.get("source_id") for s in p84_sources}) != len(p84_sources):
        errors.append("duplicate source_id in phase8_4_sources.csv")

    # Counts must match the public files.
    for key, actual in [
        ("evidence", len(evidence)),
        ("claims", len(claims)),
        ("sources", len(sources)),
    ]:
        if counts.get(key) != actual:
            errors.append(f"counts.json {key}={counts.get(key)} but file has {actual}")

    for key, actual in [
        ("evidence", len(p67_evidence)),
        ("claims", len(p67_claims)),
        ("sources", len(p67_sources)),
    ]:
        if p67_counts.get(key) != actual:
            errors.append(f"phase6_7_counts.json {key}={p67_counts.get(key)} but file has {actual}")

    for key, actual in [
        ("evidence", len(p84_evidence)),
        ("claims", len(p84_claims)),
        ("sources", len(p84_sources)),
    ]:
        if p84_counts.get(key) != actual:
            errors.append(f"phase8_4_counts.json {key}={p84_counts.get(key)} but file has {actual}")

    # File types and sizes.
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        if ".git" in p.parts:
            continue
        checks["files"] += 1
        if p.suffix.lower() not in ALLOWED_SUFFIXES:
            errors.append(f"disallowed file type: {p.relative_to(ROOT)}")
        if p.stat().st_size > 5_000_000:
            errors.append(f"file too large for public candidate: {p.relative_to(ROOT)}")

    # Forbidden content in docs/data (not in this validator or schemas).
    scan_suffixes = {".md", ".csv", ".json"}
    for p in ROOT.rglob("*"):
        if not p.is_file() or ".git" in p.parts:
            continue
        if p.suffix.lower() not in scan_suffixes:
            continue
        if p.name in {"validation_report.json", "VALIDATION_REPORT.md"}:
            continue
        if p.name == "validate_public.py":
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        for pattern, label in FORBIDDEN:
            m = pattern.search(text)
            if m:
                errors.append(f"{p.relative_to(ROOT)}: {label}: {m.group(0)!r}")

    # Relative links.
    if not args.no_links:
        link_re = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
        for p in ROOT.rglob("*.md"):
            text = p.read_text(encoding="utf-8", errors="replace")
            for target in link_re.findall(text):
                target = target.strip()
                if target.startswith(("http://", "https://", "#", "mailto:")):
                    continue
                target = target.split("#", 1)[0].strip()
                if not target:
                    continue
                resolved = (p.parent / target).resolve()
                checks["links"] += 1
                if not resolved.exists():
                    errors.append(f"{p.relative_to(ROOT)}: broken link {target}")

    status = "OK" if not errors else "FAILED"
    report = {
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": str(ROOT),
        "checks": dict(checks),
        "errors": errors,
        "warnings": warnings,
        "counts": counts,
        "public_files": {
            "firmware_metadata_rows": len(fw),
            "feasibility_rows": len(feas),
        },
    }
    out = Path(args.out)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md = Path(args.out).with_name("VALIDATION_REPORT.md")
    lines = [
        "# Public reference validation",
        "",
        f"Status: **{status}**",
        f"Generated: {report['generated_at']}",
        "",
        "## Checks",
        "",
        "| Check | Count |",
        "|---|---:|",
    ]
    for k, v in sorted(checks.items()):
        lines.append(f"| {k} | {v} |")
    lines += ["", "## Errors", ""]
    lines += [f"- {e}" for e in errors] if errors else ["None."]
    lines += ["", "## Warnings", ""]
    lines += [f"- {w}" for w in warnings] if warnings else ["None."]
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"{status}: {len(errors)} error(s), {len(warnings)} warning(s)")
    for e in errors:
        print(f" - {e}")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
