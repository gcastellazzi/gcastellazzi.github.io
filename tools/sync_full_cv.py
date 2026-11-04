#!/usr/bin/env python3
"""Porta nel sito la versione estesa del CV compilata con moderncv.

Il CV lungo vive fuori da questo repository, nella cartella LaTeX in Dropbox:
e' un documento di una ventina di pagine con l'elenco completo delle
pubblicazioni, i progetti e le attivita' editoriali. Non lo compiliamo in CI
— servirebbero moderncv, la bibliografia e le figure, tutta roba che sta
altrove — quindi lo copiamo qui gia' compilato e il sito lo serve come file
statico.

Ogni PDF di moderncv pesa circa 2,3 MB: quasi tutto immagini a risoluzione
piena. Ghostscript lo riporta sotto i 300 kB senza toccare il testo ne' i
collegamenti, e in un repository che si versiona a ogni aggiornamento la
differenza conta. Se Ghostscript non c'e', il file viene copiato tale e quale.

Uso:  python3 tools/sync_full_cv.py [--source CARTELLA]
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "assets" / "cv"
SOURCE = Path.home() / "Dropbox" / "Curriculum" / "CV-LaTeX" / "CV_Castellazzi"

# suffisso del sorgente -> nome pubblicato
LANGUAGES = {"ENG": "Castellazzi-CV-full-en.pdf", "ITA": "Castellazzi-CV-full-it.pdf"}

# Le versioni sono datate nel nome: CV_Castellazzi_2026_11_ENG.pdf.
PATTERN = re.compile(r"CV_Castellazzi_(\d{4})_(\d{2})_(ENG|ITA)\.pdf$")


def newest(source: Path, language: str) -> Path | None:
    """L'ultima versione datata per quella lingua."""
    found = [
        (match.group(1), match.group(2), path)
        for path in source.glob(f"CV_Castellazzi_*_{language}.pdf")
        if (match := PATTERN.search(path.name)) and path.stat().st_size > 0
    ]
    return max(found)[2] if found else None


def pages(pdf: Path) -> int | None:
    """Numero di pagine, letto dal PDF senza dipendenze esterne."""
    data = pdf.read_bytes()
    chunks = [data]
    for match in re.finditer(rb"stream\r?\n", data):
        end = data.find(b"endstream", match.end())
        try:
            chunks.append(zlib.decompress(data[match.end() : end]))
        except zlib.error:
            pass
    counts = [
        int(n)
        for chunk in chunks
        for n in re.findall(rb"/Type\s*/Pages[^>]*?/Count\s+(\d+)", chunk)
    ]
    return max(counts) if counts else None


def links(pdf: Path) -> int:
    """Quanti collegamenti ipertestuali contiene: serve a verificare la compressione."""
    data = pdf.read_bytes()
    found = set(re.findall(rb"/URI\s*\((.*?)\)", data))
    for match in re.finditer(rb"stream\r?\n", data):
        end = data.find(b"endstream", match.end())
        try:
            found |= set(re.findall(rb"/URI\s*\((.*?)\)", zlib.decompress(data[match.end() : end])))
        except zlib.error:
            pass
    return len(found)


def compress(src: Path, dst: Path) -> bool:
    """Ricomprime con Ghostscript; torna False se non e' disponibile o fallisce."""
    if not shutil.which("gs"):
        return False
    result = subprocess.run(
        [
            "gs", "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.7",
            "-dPDFSETTINGS=/ebook", "-dDetectDuplicateImages=true",
            "-dNOPAUSE", "-dQUIET", "-dBATCH", f"-sOutputFile={dst}", str(src),
        ],
        capture_output=True,
    )
    return result.returncode == 0 and dst.exists() and dst.stat().st_size > 0


def stale(pdf: Path) -> bool:
    """Vero se il sorgente .tex e' piu' recente del PDF: il PDF va ricompilato."""
    tex = pdf.with_suffix(".tex")
    return tex.exists() and tex.stat().st_mtime > pdf.stat().st_mtime


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE, help="cartella dei sorgenti LaTeX")
    args = parser.parse_args()

    if not args.source.is_dir():
        sys.exit(f"ERRORE: cartella non trovata: {args.source}")

    DEST.mkdir(parents=True, exist_ok=True)
    problems = []

    for language, published in LANGUAGES.items():
        src = newest(args.source, language)
        if src is None:
            problems.append(f"{language}: nessun PDF compilato in {args.source}")
            continue
        if stale(src):
            problems.append(f"{src.name}: il .tex e' piu' recente del PDF, ricompilalo prima")
            continue

        dst = DEST / published
        before, before_links = src.stat().st_size, links(src)
        if compress(src, dst):
            if links(dst) != before_links:
                shutil.copy2(src, dst)  # la compressione ha perso collegamenti: meglio l'originale
                note = "copiato senza comprimere (gs perdeva collegamenti)"
            else:
                note = f"compresso da {before / 1e6:.1f} MB"
        else:
            shutil.copy2(src, dst)
            note = "copiato senza comprimere (Ghostscript assente)"

        print(
            f"{published}: {src.name} · {pages(dst) or '?'} pagine · "
            f"{dst.stat().st_size / 1e3:.0f} kB · {before_links} collegamenti · {note}"
        )

    for problem in problems:
        print(f"  ATTENZIONE  {problem}", file=sys.stderr)
    if problems:
        sys.exit(1)


if __name__ == "__main__":
    main()
