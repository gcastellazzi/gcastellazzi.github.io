#!/usr/bin/env python3
"""Genera _metrics.md dai conteggi di citazione contenuti in publications.bib.

L'export BibTeX di Scopus porta in ogni voce un campo `note` con "Cited by: N".
Da li' si ricavano, senza chiamare nessun servizio esterno, esattamente gli
stessi numeri della pagina Scopus dell'autore: documenti, citazioni totali,
h-index e i10-index.

Due cose *non* sono ricavabili e la pagina non le mostra: quanti documenti
distinti citano l'autore, e l'andamento delle citazioni ricevute anno per anno.
L'export dice quante citazioni ha un lavoro oggi, non quando sono arrivate.

I grafici sono SVG scritti qui dentro: nessuna libreria, nessuna richiesta a
servizi di terze parti, e i colori seguono il tema chiaro o scuro del sito
perche' usano `currentColor`.

Uso:  python3 tools/build_metrics.py
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BIB = ROOT / "publications.bib"
OUT = ROOT / "_metrics.md"

SELF = "castellazzi"


def parse(text: str) -> list[dict[str, str]]:
    entries = []
    for body in re.findall(r"@\w+\{[^,]+,(.*?)\n\}", text, re.S):
        fields: dict[str, str] = {}
        # Il ritorno a capo finale e' opzionale: l'ultimo campo della voce —
        # in un export Scopus e' proprio `note` — non ne ha uno.
        for name, value in re.findall(r"(\w+)\s*=\s*\{(.*?)\}\s*,?\s*(?:\n|$)", body, re.S):
            fields[name.lower()] = " ".join(value.replace("{", "").replace("}", "").split())
        if fields.get("title"):
            entries.append(fields)
    return entries


def citations(entry: dict[str, str]) -> int:
    match = re.search(r"Cited by:\s*(\d+)", entry.get("note", ""))
    return int(match.group(1)) if match else 0


def h_index(counts: list[int]) -> int:
    """Il massimo h per cui esistono h lavori con almeno h citazioni."""
    return sum(1 for rank, value in enumerate(sorted(counts, reverse=True), 1) if value >= rank)


def export_date(text: str) -> str:
    match = re.search(r"EXPORT DATE:\s*(.+)", text)
    return match.group(1).strip() if match else ""


def bar_chart(pairs: list[tuple[str, int]], height: int = 190) -> str:
    """Istogramma dei documenti per anno."""
    if not pairs:
        return ""
    width, pad_l, pad_b, pad_t = 760, 28, 26, 14
    top = max(value for _, value in pairs)
    slot = (width - pad_l) / len(pairs)
    bar_w = min(slot * 0.68, 34)
    plot_h = height - pad_b - pad_t

    bars = []
    for index, (label, value) in enumerate(pairs):
        bar_h = plot_h * value / top
        x = pad_l + slot * index + (slot - bar_w) / 2
        y = pad_t + plot_h - bar_h
        bars.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" '
            f'rx="2" fill="currentColor" opacity=".78"><title>{label}: {value}</title></rect>'
        )
        if value:
            bars.append(
                f'<text x="{x + bar_w / 2:.1f}" y="{y - 3:.1f}" text-anchor="middle" '
                f'font-size="9" fill="currentColor" opacity=".75">{value}</text>'
            )
        # Un anno su due, per non impastare le etichette.
        if index % 2 == 0 or index == len(pairs) - 1:
            bars.append(
                f'<text x="{x + bar_w / 2:.1f}" y="{height - 8}" text-anchor="middle" '
                f'font-size="9.5" fill="currentColor" opacity=".65">{label}</text>'
            )

    axis = (
        f'<line x1="{pad_l - 6}" y1="{pad_t + plot_h:.1f}" x2="{width}" y2="{pad_t + plot_h:.1f}" '
        f'stroke="currentColor" opacity=".25"/>'
    )
    return (
        f'<svg viewBox="0 0 {width} {height}" width="100%" role="img" '
        f'aria-label="Documents per year">{axis}{"".join(bars)}</svg>'
    )


def h_curve(counts: list[int], h: int, height: int = 210) -> str:
    """Citazioni per lavoro in ordine decrescente, con la soglia dell'h-index.

    E' il grafico che spiega l'h-index meglio di una definizione: la curva
    scende, la diagonale sale, e il punto in cui si incrociano e' h.
    """
    counts = sorted(counts, reverse=True)
    if not counts:
        return ""
    width, pad_l, pad_b, pad_t = 760, 34, 26, 12
    shown = min(len(counts), 60)
    plot_w, plot_h = width - pad_l - 8, height - pad_b - pad_t
    top = max(counts[0], 1)

    def sx(i: float) -> float:
        return pad_l + plot_w * i / shown

    def sy(v: float) -> float:
        # Scala radice: senza, i 581 del lavoro di punta schiacciano tutto il resto.
        return pad_t + plot_h - plot_h * (v / top) ** 0.5

    area = " ".join(f"{sx(i):.1f},{sy(v):.1f}" for i, v in enumerate(counts[:shown]))
    polygon = f"{pad_l},{pad_t + plot_h:.1f} {area} {sx(shown):.1f},{pad_t + plot_h:.1f}"

    diagonal = " ".join(f"{sx(i):.1f},{sy(i):.1f}" for i in range(shown + 1))
    hx, hy = sx(h), sy(h)

    return f"""<svg viewBox="0 0 {width} {height}" width="100%" role="img" \
aria-label="Citations per work in descending order, with the h-index threshold">
  <polygon points="{polygon}" fill="currentColor" opacity=".16"/>
  <polyline points="{area}" fill="none" stroke="currentColor" stroke-width="1.8" opacity=".85"/>
  <polyline points="{diagonal}" fill="none" stroke="currentColor" stroke-width="1"
            stroke-dasharray="4 3" opacity=".45"/>
  <circle cx="{hx:.1f}" cy="{hy:.1f}" r="4.5" fill="currentColor"/>
  <text x="{hx + 9:.1f}" y="{hy - 6:.1f}" font-size="11" fill="currentColor">h = {h}</text>
  <line x1="{pad_l}" y1="{pad_t + plot_h:.1f}" x2="{width - 8}" y2="{pad_t + plot_h:.1f}"
        stroke="currentColor" opacity=".25"/>
  <text x="{pad_l}" y="{height - 8}" font-size="9.5" fill="currentColor" opacity=".65">1</text>
  <text x="{width - 8}" y="{height - 8}" text-anchor="end" font-size="9.5"
        fill="currentColor" opacity=".65">work no. {shown}, ranked by citations</text>
</svg>"""


def main() -> None:
    text = BIB.read_text(encoding="utf-8-sig")
    entries = parse(text)
    counts = [citations(entry) for entry in entries]
    total = sum(counts)
    h = h_index(counts)
    i10 = sum(1 for value in counts if value >= 10)
    date = export_date(text)

    years = Counter(entry.get("year", "") for entry in entries if entry.get("year"))
    span = [str(y) for y in range(int(min(years)), int(max(years)) + 1)]
    per_year = [(y, years.get(y, 0)) for y in span]

    kinds = Counter(entry.get("type", "Other") for entry in entries)

    ranked = sorted(
        ((citations(e), e.get("year", ""), e.get("title", ""), e.get("doi", "")) for e in entries),
        reverse=True,
    )

    lines = [
        "<!-- Generato da tools/build_metrics.py — non modificare a mano. -->",
        "",
        "::: {.grid}",
    ]
    stats = [
        ("Documents", f"{len(entries)}"),
        ("Citations", f"{total:,}".replace(",", " ")),
        ("h-index", f"{h}"),
        ("i10-index", f"{i10}"),
    ]
    for label, value in stats:
        lines += [
            '::: {.g-col-6 .g-col-md-3}',
            '<div class="metric-card">',
            f'<span class="metric-value">{value}</span>',
            f'<span class="metric-label">{label}</span>',
            "</div>",
            ":::",
            "",
        ]
    lines += [":::", ""]

    if date:
        lines += [
            f"Figures computed from the Scopus BibTeX export of **{date}**; citation",
            "counts are a snapshot at that date. The page is regenerated from",
            "`publications.bib`, so it moves whenever the bibliography does.",
            "",
        ]

    lines += [
        "## Documents per year",
        "",
        bar_chart(per_year),
        "",
        "## Citations per work",
        "",
        h_curve(counts, h),
        "",
        "The solid curve is every work ordered by citations received; the dashed",
        "diagonal is the rank. Where they cross is the h-index: "
        f"**{h} works with at least {h} citations each**. The vertical scale is a",
        "square root, otherwise the most cited work flattens everything behind it.",
        "",
        "## Most cited",
        "",
        "| Citations | Year | |",
        "|---:|---|---|",
    ]
    for cited, year, title, doi in ranked[:10]:
        link = f"[{title}](https://doi.org/{doi})" if doi else title
        lines.append(f"| {cited} | {year} | {link} |")
    lines += ["", ': {tbl-colwidths="[12,10,78]"}', ""]

    lines += ["## By document type", "", "| Type | Documents | Citations |", "|---|---:|---:|"]
    for kind, number in kinds.most_common():
        cited = sum(citations(e) for e in entries if e.get("type", "Other") == kind)
        lines.append(f"| {kind} | {number} | {cited} |")
    lines += ["", ': {tbl-colwidths="[50,25,25]"}', ""]

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(
        f"{OUT.name}: {len(entries)} documenti · {total} citazioni · "
        f"h-index {h} · i10 {i10} · export {date or 'data assente'}"
    )


if __name__ == "__main__":
    main()
