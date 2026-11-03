"""Validate skill folders under skills/ using only the Python standard library.

Usage: python scripts/validate_skill.py [SKILL_DIR ...]
Without arguments, every skills/*/SKILL.md in the repository is checked.
Exit code 1 means at least one error was found.
"""

import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
PATH_RE = re.compile(r"`((?:references|assets|scripts)/[^`\s]+)`")
MAX_SKILL_LINES = 500

# Expected ID sets for skills that keep numbered rules and cases.
ID_CHECKS = {
    "korean-clear-writing": [
        ("references/korean-writing-rules.md", r"^## (R\d{2})\b", "R", 15),
        ("references/source-mapping.md", r"^\| (P\d{2}) \|", "P", 14),
        ("references/source-mapping.md", r"^\| (D\d{2}) \|", "D", 18),
        ("references/source-mapping.md", r"^\| (K\d{2}) \|", "K", 11),
        ("assets/acceptance-cases.md", r"^\| (T\d{2}) \|", "T", None),
    ],
}


def parse_frontmatter(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("SKILL.md must start with '---'")
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        raise ValueError("frontmatter closing '---' not found") from None
    data, parent = {}, None
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        nested = line.startswith((" ", "\t"))
        key, sep, value = line.strip().partition(":")
        if not sep:
            raise ValueError(f"invalid frontmatter line: {line!r}")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if nested:
            if parent is None:
                raise ValueError(f"nested key without parent: {line!r}")
            data[parent][key] = value
        elif value == "":
            data[key], parent = {}, key
        else:
            data[key], parent = value, None
    return data, end + 1


def line_endings(raw):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n") - crlf
    return crlf, lf


def check_ids(skill_dir, errors, counts):
    for rel, pattern, prefix, expected in ID_CHECKS.get(skill_dir.name, []):
        path = skill_dir / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        ids = re.findall(pattern, text, flags=re.MULTILINE)
        numbers = [int(i[1:]) for i in ids]
        if numbers != list(range(1, len(numbers) + 1)):
            errors.append(f"{rel}: {prefix} IDs are not continuous from 1: {ids}")
        if expected is not None and len(ids) != expected:
            errors.append(f"{rel}: expected {expected} {prefix} IDs, found {len(ids)}")
        counts[prefix] = len(ids)


def validate(skill_dir):
    errors, warnings, counts = [], [], {}
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return [f"{skill_dir}: SKILL.md not found"], warnings, counts

    files = sorted(p for p in skill_dir.rglob("*") if p.is_file())
    for path in files:
        rel = path.relative_to(skill_dir).as_posix()
        raw = path.read_bytes()
        if path.suffix.lower() not in {".md", ".json", ".py", ".txt", ".yml", ".yaml"}:
            continue
        if raw.startswith(b"\xef\xbb\xbf"):
            errors.append(f"{rel}: UTF-8 BOM found")
        try:
            raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            errors.append(f"{rel}: not valid UTF-8 ({exc})")
            continue
        crlf, lf = line_endings(raw)
        if crlf and lf:
            errors.append(f"{rel}: mixed line endings (CRLF {crlf}, LF {lf})")

    text = skill_md.read_text(encoding="utf-8")
    try:
        meta, _ = parse_frontmatter(text)
    except ValueError as exc:
        return errors + [f"SKILL.md: {exc}"], warnings, counts

    name = meta.get("name")
    if not isinstance(name, str) or not NAME_RE.match(name) or len(name) > 64:
        errors.append(f"SKILL.md: invalid name {name!r}")
    elif name != skill_dir.name:
        errors.append(f"SKILL.md: name {name!r} does not match folder {skill_dir.name!r}")
    description = meta.get("description")
    if not isinstance(description, str) or not 1 <= len(description) <= 1024:
        errors.append("SKILL.md: description must be 1-1024 characters")
    else:
        counts["description"] = len(description)
    if "metadata" in meta and not isinstance(meta["metadata"], dict):
        errors.append("SKILL.md: metadata must be a mapping")
    elif "metadata" in meta:
        counts["version"] = meta["metadata"].get("version", "-")

    line_count = len(text.splitlines())
    counts["SKILL.md lines"] = line_count
    if line_count > MAX_SKILL_LINES:
        warnings.append(f"SKILL.md: {line_count} lines (recommended < {MAX_SKILL_LINES})")

    for path in files:
        if path.suffix.lower() != ".md":
            continue
        rel = path.relative_to(skill_dir).as_posix()
        for ref in PATH_RE.findall(path.read_text(encoding="utf-8")):
            if not (skill_dir / ref).exists():
                errors.append(f"{rel}: referenced path not found: {ref}")

    check_ids(skill_dir, errors, counts)
    counts["files"] = len(files)
    return errors, warnings, counts


def main(argv):
    if argv:
        dirs = [pathlib.Path(a).resolve() for a in argv]
    else:
        dirs = sorted(p.parent for p in (REPO / "skills").glob("*/SKILL.md"))
    if not dirs:
        print("error: no skill folders found")
        return 1
    failed = False
    for skill_dir in dirs:
        errors, warnings, counts = validate(skill_dir)
        summary = ", ".join(f"{k}={v}" for k, v in counts.items())
        print(f"[{'FAIL' if errors else 'OK'}] {skill_dir.name}: {summary}")
        for message in warnings:
            print(f"  warning: {message}")
        for message in errors:
            print(f"  error: {message}")
        failed = failed or bool(errors)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
