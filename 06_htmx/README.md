# Livello 06: Template Django + HTMX

## Obiettivo

Implementare template Django con HTMX per aggiornamenti dinamici, come in WANDERLOG (decisione D2).

## Cosa si allena di WANDERLOG

- Template Django + HTMX (§2, D2)
- Partial rendering
- Task 0.9
- No React, no Node build

## Prerequisiti

- Livello 05 completato
- Conoscenza di template Django
- HTML/CSS base

## Cosa devi fare

### Passo 1: Download HTMX

Scarica htmx.min.js in `core/static/core/` (versione 2.0.0)

### Passo 2: Template base

Crea `core/templates/base.html` con HTMX incluso

### Passo 3: View boards

Crea template e view per listare e creare boards con HTMX

### Passo 4: Partial

Crea partial che ritorna solo frammenti HTML

### Passo 5: Test

```bash
docker compose run --rm django pytest
```

## Criteri di successo

- Template base funziona
- HTMX caricato correttamente
- Partial rendering funziona
- Test passano

## Prossimo livello

Passa a `07_mappa/`.
