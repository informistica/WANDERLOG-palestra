## Cosa cambia

<!-- Una o due frasi: cosa fa questa PR e perche'. Collega la issue: "Closes #12" -->

## Come verificarla

<!-- I passi per provarla a mano (URL, utente, dati di esempio). -->

## Checklist

- [ ] Il branch parte da `main` aggiornato e si chiama `feat/...` (o `fix/...`)
- [ ] `pytest` passa in locale (soglia di coverage compresa)
- [ ] `lint-imports` passa (nessuna dipendenza tra layer vietata)
- [ ] `ruff check .` pulito (`pre-commit` installato)
- [ ] Nuove migrazioni create e committate (`makemigrations --check` pulito)
- [ ] Nessun segreto o file `.env` nel commit