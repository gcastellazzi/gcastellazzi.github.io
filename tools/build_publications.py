#!/usr/bin/env python3
"""Genera _publications.md a partire da publications.bib.

Le voci vengono raggruppate per tipologia (il campo `type` dell'export Scopus)
e, dentro ogni gruppo, ordinate dall'anno piu' recente al piu' antico.
Il nome dell'autore del sito viene messo in grassetto.

Uso:  python3 tools/build_publications.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BIB = ROOT / "publications.bib"
OUT = ROOT / "_publications.md"

# Nome da evidenziare, come cognome in minuscolo.
SELF = "castellazzi"

# Ordine e titoli delle sezioni; ogni valore di `type` finisce in un gruppo.
GROUPS = [
    ("Journal articles", {"article"}),
    ("Conference papers", {"conference paper"}),
    ("Book chapters", {"book chapter"}),
    ("Editorials and letters", {"editorial", "letter"}),
]
FALLBACK = "Other publications"


def parse(text: str) -> list[dict]:
    entries = []
    for body in re.findall(r"@\w+\{[^,]+,(.*?)\n\}", text, re.S):
        fields = {}
        for name, value in re.findall(r"(\w+)\s*=\s*\{(.*?)\}\s*,?\s*\n", body, re.S):
            fields[name.lower()] = " ".join(value.split())
        if fields.get("title"):
            entries.append(fields)
    return entries


def strip_braces(s: str) -> str:
    return s.replace("{", "").replace("}", "")


def format_authors(raw: str) -> str:
    out = []
    for person in raw.split(" and "):
        person = strip_braces(person).strip()
        if "," in person:
            surname, given = person.split(",", 1)
            surname, given = surname.strip(), given.strip()
            initials = " ".join(
                f"{part[0]}." for part in re.split(r"[\s.]+", given) if part
            )
            name = f"{initials} {surname}".strip()
        else:
            surname, name = person, person
        if surname.lower() == SELF:
            name = f"**{name}**"
        out.append(name)
    if len(out) > 2:
        return ", ".join(out[:-1]) + ", and " + out[-1]
    if len(out) == 2:
        return " and ".join(out)
    return out[0] if out else ""


def format_pages(raw: str) -> str:
    raw = raw.replace("--", "–").replace(" – ", "–").replace(" - ", "–")
    return raw.strip()


def format_entry(e: dict) -> str:
    bits = [f"**{e.get('year', 'n.d.')}** · {format_authors(e.get('author', ''))}"]
    bits.append(f'"{strip_braces(e["title"]).rstrip(".")},"')
    venue = strip_braces(e.get("journal", ""))
    if venue:
        bits.append(f"*{venue}*")
    detail = []
    if e.get("volume"):
        detail.append(f"vol. {e['volume']}")
    if e.get("number"):
        detail.append(f"no. {e['number']}")
    if e.get("pages"):
        detail.append(f"pp. {format_pages(e['pages'])}")
    line = " ".join(bits[:1]) + ", " + " ".join(bits[1:])
    if detail:
        line += ", " + ", ".join(detail)
    line += "."
    if e.get("doi"):
        line += f" [doi:{e['doi']}](https://doi.org/{e['doi']})"
    return line


def main() -> None:
    entries = parse(BIB.read_text(encoding="utf-8"))
    buckets: dict[str, list[dict]] = {name: [] for name, _ in GROUPS}
    buckets[FALLBACK] = []
    for e in entries:
        kind = e.get("type", "").strip().lower()
        target = next((name for name, kinds in GROUPS if kind in kinds), FALLBACK)
        buckets[target].append(e)

    lines = ["<!-- Generato da tools/build_publications.py — non modificare a mano. -->", ""]
    total = 0
    for name in [n for n, _ in GROUPS] + [FALLBACK]:
        group = buckets[name]
        if not group:
            continue
        group.sort(key=lambda e: (e.get("year", "0"), e.get("title", "")), reverse=True)
        lines.append(f"## {name} <span class='pub-count'>{len(group)}</span>")
        lines.append("")
        for e in group:
            lines.append(f"- {format_entry(e)}")
        lines.append("")
        total += len(group)

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"{OUT.name}: {total} voci")
    for name in [n for n, _ in GROUPS] + [FALLBACK]:
        if buckets[name]:
            print(f"  {name}: {len(buckets[name])}")
    if total != len(entries):
        sys.exit(f"ERRORE: {len(entries)} voci lette ma {total} scritte")


if __name__ == "__main__":
    main()
