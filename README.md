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
| Pubblicazioni | `publications.bib` (export da Scopus) — vedi sotto |
| Album di immagini | un file in `gallery/` + immagini in `assets/img/` |
| Post / news | un file in `posts/` |
| CV | `cv.qmd`, PDF in `assets/cv.pdf` |
| Colori e stile | `assets/css/theme.scss`, `theme-dark.scss` |
| Menu, titolo, link | `_quarto.yml` |

## Aggiornare le pubblicazioni

1. Scopus → Export → BibTeX, e sovrascrivi `publications.bib`.
2. Ripara l'export (Scopus produce chiavi non valide o duplicate, che farebbero
   sparire delle voci senza alcun errore):

   ```bash
   python3 tools/fix_scopus_bib.py publications.bib
   ```

3. Rigenera la pagina:

   ```bash
   python3 tools/build_publications.py
   ```

Il passo 3 lo esegue comunque anche GitHub Actions a ogni push, quindi in locale
serve solo se vuoi vedere il risultato prima di pubblicare. Il file generato è
`_publications.md`: non modificarlo a mano, viene sovrascritto.

Le voci sono raggruppate per tipologia — journal articles, conference papers,
book chapters, editorials and letters — in base al campo `type` dell'export
Scopus, e ordinate dall'anno più recente al più antico. Per cambiare i gruppi o
il loro ordine, modifica `GROUPS` in `tools/build_publications.py`.
