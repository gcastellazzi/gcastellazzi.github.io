# gcastellazzi.github.io

Sito personale di Giovanni Castellazzi, generato con [Quarto](https://quarto.org)
e pubblicato su GitHub Pages.

## Anteprima locale

```bash
quarto preview
```

Apre il sito su <http://localhost:4200> e si aggiorna a ogni salvataggio.

## Pubblicare

```bash
git add -A && git commit -m "update" && git push
```

Il workflow `.github/workflows/publish.yml` rende il sito e lo pubblica sul branch
`gh-pages`. Online su <https://gcastellazzi.github.io>.

## Dove mettere le cose

| Cosa | Dove |
|---|---|
| Bio, home | `index.qmd` |
| Temi di ricerca | `research.qmd` |
| Pubblicazioni | `publications.bib` (export da Scopus/Scholar/ORCID) |
| Album di immagini | un file in `gallery/` + immagini in `assets/img/` |
| Post / news | un file in `posts/` |
| CV | `cv.qmd`, PDF in `assets/cv.pdf` |
| Colori e stile | `assets/css/theme.scss`, `theme-dark.scss` |
| Menu, titolo, link | `_quarto.yml` |
