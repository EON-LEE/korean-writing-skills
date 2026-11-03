#!/usr/bin/env python3
"""korean-clear-writing 스킬의 기준·후보 버전 비교 평가 도구.

출력 폴더 구조: <outputs>/<variant>/<run>/<case>.md

  python evals/score.py packet --outputs OUT --out packet.md --map map.json [--seed N]
  python evals/score.py score --outputs OUT --grades grades.json --map map.json \
      --baseline NAME --candidate NAME [--json result.json]
"""
import argparse
import json
import math
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CASES = ROOT / "cases"
LIST_MARKER = re.compile(r"^\s*\d+[.)]\s", re.M)
NUMBER = re.compile(r"(?<![A-Za-z0-9])\d+")
IMPROVEMENT_MIN_RATE = 0.8


def read(path):
    return Path(path).read_text(encoding="utf-8")


def load_criteria():
    return json.loads(read(ROOT / "criteria.json"))["cases"]


def numbers(text):
    return set(NUMBER.findall(LIST_MARKER.sub("", text)))


def auto_check(spec, output, prompt):
    if "contains_all" in spec:
        missing = [item for item in spec["contains_all"] if item not in output]
        return not missing, ("누락: " + " | ".join(missing)) if missing else "모두 포함"
    if spec.get("no_new_numbers"):
        new = sorted(numbers(output) - numbers(prompt))
        return not new, ("새 숫자: " + ", ".join(new)) if new else "새 숫자 없음"
    raise ValueError(f"알 수 없는 자동 검사: {spec}")


def collect(outputs):
    return [
        (f.parent.parent.name, f.parent.name, f.stem, f)
        for f in sorted(Path(outputs).glob("*/*/*.md"))
    ]


def cmd_packet(args):
    criteria = load_criteria()
    rng = random.Random(args.seed)
    by_case = {}
    for variant, run, case, path in collect(args.outputs):
        by_case.setdefault(case, []).append((variant, run, path))

    lines = [
        "# 블라인드 채점 자료",
        "",
        "각 응답을 판정 항목 문장만 기준으로 통과(true) 또는 실패(false)로 판정한다.",
        "응답의 문체 선호나 길이는 판정 항목에 없으면 고려하지 않는다.",
        "",
    ]
    mapping = {}
    for case in sorted(by_case):
        manual = [c for c in criteria[case] if "auto" not in c]
        if not manual:
            continue
        entries = by_case[case][:]
        rng.shuffle(entries)
        lines += [f"## 사례 {case}", "", "### 사용자 요청", "", read(CASES / f"{case}.md").strip(), ""]
        lines += ["### 판정 항목", ""] + [f"- `{c['id']}`: {c['text']}" for c in manual]
        for index, (variant, run, path) in enumerate(entries, 1):
            label = f"{case}-O{index}"
            mapping[label] = {"variant": variant, "run": run, "case": case}
            lines += ["", f"### 응답 {label}", "", "<<<응답 시작>>>", read(path).strip(), "<<<응답 끝>>>"]
        lines.append("")

    Path(args.out).write_text("\n".join(lines), encoding="utf-8")
    Path(args.map).write_text(json.dumps(mapping, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"채점 자료: {args.out} (응답 {len(mapping)}개)")


def evaluate(rows, baseline, candidate):
    def summary(variant):
        mine = [r for r in rows if r["variant"] == variant]
        result = {"runs": sorted({r["run"] for r in mine})}
        for group in ("improvement", "regression"):
            items = [r for r in mine if r["group"] == group]
            result[group] = [sum(1 for r in items if r["ok"]), len(items)]
        result["critical_failures"] = [
            f"{r['run']}/{r['id']}" for r in mine if r["critical"] and r["ok"] is False
        ]
        result["missing"] = [f"{r['run']}/{r['id']}" for r in mine if r["ok"] is None]
        return result

    base, cand = summary(baseline), summary(candidate)
    imp_pass, imp_total = cand["improvement"]
    checks = {
        "1_candidate_no_critical_failure": not cand["critical_failures"],
        "2_regression_not_worse": cand["regression"][0] >= base["regression"][0],
        "3_improvement_rate_and_gain": imp_total > 0
        and imp_pass >= math.ceil(IMPROVEMENT_MIN_RATE * imp_total)
        and imp_pass > base["improvement"][0],
        "4_no_missing_grades": not base["missing"] and not cand["missing"],
    }
    return {"baseline": {baseline: base}, "candidate": {candidate: cand}, "checks": checks,
            "passed": all(checks.values())}


def cmd_score(args):
    criteria = load_criteria()
    grades = json.loads(read(args.grades)) if args.grades else {}
    mapping = json.loads(read(args.map)) if args.map else {}
    labels = {(m["variant"], m["run"], m["case"]): label for label, m in mapping.items()}

    rows = []
    seen = set()
    for variant, run, case, path in collect(args.outputs):
        seen.add((variant, run, case))
        output, prompt = read(path), read(CASES / f"{case}.md")
        for item in criteria[case]:
            if "auto" in item:
                ok, reason = auto_check(item["auto"], output, prompt)
                source = "auto"
            else:
                grade = grades.get(labels.get((variant, run, case), ""), {}).get(item["id"])
                if grade is None:
                    ok, reason, source = None, "채점 없음", "missing"
                else:
                    ok, reason, source = bool(grade["pass"]), grade.get("reason", ""), "grader"
            rows.append({"variant": variant, "run": run, "case": case, "id": item["id"],
                         "group": item["group"], "critical": item.get("critical", False),
                         "ok": ok, "reason": reason, "source": source})

    for variant in {v for v, _, _ in seen}:
        for run in {r for v, r, _ in seen if v == variant}:
            for case in criteria:
                if (variant, run, case) not in seen:
                    for item in criteria[case]:
                        rows.append({"variant": variant, "run": run, "case": case, "id": item["id"],
                                     "group": item["group"], "critical": item.get("critical", False),
                                     "ok": None, "reason": "출력 없음", "source": "missing"})

    result = evaluate(rows, args.baseline, args.candidate)
    for row in rows:
        if row["ok"] is not True:
            print(f"[{'실패' if row['ok'] is False else '누락'}] {row['variant']}/{row['run']}/{row['id']}: {row['reason']}")
    print(json.dumps({k: v for k, v in result.items()}, ensure_ascii=False, indent=2))
    if args.json:
        Path(args.json).write_text(json.dumps({"rows": rows, "result": result}, ensure_ascii=False, indent=2),
                                   encoding="utf-8")
    return 0 if result["passed"] else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    packet = sub.add_parser("packet")
    packet.add_argument("--outputs", required=True)
    packet.add_argument("--out", required=True)
    packet.add_argument("--map", required=True)
    packet.add_argument("--seed", type=int, default=20261103)
    score = sub.add_parser("score")
    score.add_argument("--outputs", required=True)
    score.add_argument("--grades")
    score.add_argument("--map")
    score.add_argument("--baseline", required=True)
    score.add_argument("--candidate", required=True)
    score.add_argument("--json")
    args = parser.parse_args()
    if args.command == "packet":
        cmd_packet(args)
        return 0
    return cmd_score(args)


if __name__ == "__main__":
    sys.exit(main())
