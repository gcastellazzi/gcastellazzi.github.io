#!/usr/bin/env python3
"""Rende utilizzabile da Quarto/pandoc un file .bib esportato da Scopus.

Scopus produce chiavi di citazione che BibTeX non accetta (apostrofi diritti o
tipografici, spazi) e a volte chiavi duplicate: in entrambi i casi le voci
vengono silenziosamente perse in fase di rendering. Questo script:

  1. commenta le righe di intestazione dell'export ("Scopus", "EXPORT DATE: ...")
  2. traslittera le chiavi in puro ASCII e toglie i caratteri non ammessi
  3. rende univoche le chiavi ripetute aggiungendo un suffisso b, c, ...
  4. protegge con {} maiuscole e acronimi nei titoli, che gli stili di
     citazione in sentence case (IEEE fra questi) altrimenti abbassano
     ("Reissner-Mindlin" -> "reissner-mindlin")

Uso:  python3 tools/fix_scopus_bib.py publications.bib
"""
import collections
import re
import sys
import unicodedata


def protect_case(title: str) -> str:
    """Wrap in braces every word after the first that carries a capital."""
    words = title.split(" ")
    out = []
    for i, w in enumerate(words):
        bare = w.strip(".,;:()[]")
        needs = (
            i > 0
            and bare
            and "{" not in w
            and "$" not in w
            and any(c.isupper() for c in bare)
        )
        out.append(w.replace(bare, "{" + bare + "}", 1) if needs else w)
    return " ".join(out)


def protect_title(match: "re.Match[str]") -> str:
    return f"{match.group(1)}{{{protect_case(match.group(2))}}}{match.group(3)}"


def fix(path: str) -> None:
    text = open(path, encoding="utf-8-sig").read()

    lines = []
    for line in text.split("\n"):
        bare = line.strip()
        is_header = (
            bare
            and not bare.startswith(("@", "%"))
            and not any(ch in line for ch in "={}")
        )
        lines.append("% " + line if is_header else line)
    text = "\n".join(lines)

    cleaned, seen = [], collections.Counter()

    def rewrite(match: "re.Match[str]") -> str:
        entry_type, key = match.group(1), match.group(2)
        ascii_key = unicodedata.normalize("NFKD", key).encode("ascii", "ignore").decode()
        ascii_key = re.sub(r"[^A-Za-z0-9_:.-]", "", ascii_key)
        seen[ascii_key] += 1
        if seen[ascii_key] > 1:
            ascii_key = f"{ascii_key}{chr(96 + seen[ascii_key])}"
        if ascii_key != key:
            cleaned.append((key, ascii_key))
        return f"@{entry_type}{{{ascii_key},"

    text = re.sub(r"@(\w+)\{([^,]+),", rewrite, text)
    text = re.sub(r"(?im)^(\s*title\s*=\s*)\{(.*)\}(,?)\s*$", protect_title, text)
    open(path, "w", encoding="utf-8").write(text)

    total = len(re.findall(r"^@", text, re.M))
    print(f"{path}: {total} voci, {len(cleaned)} chiavi corrette")
    for old, new in cleaned:
        print(f"  {old!r} -> {new!r}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    fix(sys.argv[1])
