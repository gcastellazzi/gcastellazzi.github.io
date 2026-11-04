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

Il workflow `.github/workflows/publish.yml` rigenera le pagine derivate, rende il
sito e lo carica come artefatto di GitHub Pages (la sorgente di Pages è impostata
su «GitHub Actions», non su un branch). Online su <https://gcastellazzi.github.io>.

## Dove mettere le cose

| Cosa | Dove |
|---|---|
| Bio, home | `index.qmd` |
| Temi di ricerca | `research.qmd` |
| Pubblicazioni | `publications.bib` (export da Scopus) — vedi sotto |
| Album di immagini | un file in `gallery/` + immagini in `assets/img/` |
| Post / news | un file in `posts/` |
| CV breve | `cv.qmd` (inglese), `cv-it.qmd` (italiano) — vedi sotto |
| CV esteso | `assets/cv/*.pdf`, compilati altrove — vedi sotto |
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

## Le due versioni del CV

Il **CV breve** è `cv.qmd` / `cv-it.qmd`. Quarto le rende in tre formati dalla
stessa sorgente — HTML, PDF e LaTeX — quindi il PDF scaricabile non può divergere
da quello che si legge in pagina, e riporta la data dell'ultima build.

Attenzione a una cosa: nel PDF un collegamento scritto come `publications.qmd`
resta tale e quale e non porta da nessuna parte, perché la riscrittura in `.html`
Quarto la fa solo per l'HTML. I rimandi ad altre pagine del sito vanno quindi
scritti per esteso, `https://gcastellazzi.github.io/publications.html`: in HTML
Quarto riconosce il proprio dominio e li tratta come interni, nel PDF funzionano.

Il **CV esteso** è il documento moderncv che vive in
`~/Dropbox/Curriculum/CV-LaTeX/CV_Castellazzi/`: una ventina di pagine con
l'elenco completo delle pubblicazioni, i progetti e le attività editoriali. Non
lo compiliamo in CI — servirebbero moderncv, la bibliografia e le figure — quindi
lo si compila in locale e poi:

```bash
python3 tools/sync_full_cv.py
```

Lo script prende l'ultima versione datata per ciascuna lingua, la ricomprime con
Ghostscript (da 2,4 MB a circa 300 kB, verificando che nessun collegamento vada
perso) e la scrive in `assets/cv/`. Si ferma con un avviso se il `.tex` è più
recente del PDF, cioè se hai dimenticato di ricompilare.

I due PDF sono versionati nel repository: il sito li serve come file statici e
il numero di pagine è scritto a mano nell'etichetta del pulsante, in `cv.qmd` e
`cv-it.qmd`.
