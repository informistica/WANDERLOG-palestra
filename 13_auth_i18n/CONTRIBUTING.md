# Come contribuire a Wanderlog

## 1. Un branch per ogni modifica

`main` e' sempre verde e nessuno ci committa direttamente.

```bash
git switch main && git pull
git switch -c feat/mappa-cluster      # nuova funzionalita'
git switch -c fix/invito-scaduto      # correzione di un bug
```

Nomi: `feat/<cosa>`, `fix/<cosa>`, `docs/<cosa>`; minuscole e trattini.

## 2. Prima del primo commit: pre-commit

```bash
pip install -r requirements-dev.txt
pre-commit install            # da ora ruff gira a ogni git commit
pre-commit run --all-files    # prima passata su tutto il progetto
```

## 3. Prima di aprire la Pull Request

```bash
ruff check .
cd palestra
lint-imports
pytest                        # include la soglia di coverage (80%)
```

## 4. Pull Request e review

1. `git push -u origin feat/mappa-cluster` e apri la Pull Request verso `main`.
2. Compila il template (cosa cambia, come verificarla, checklist).
3. Aspetta che la CI sia verde e chiedi la review a un compagno.
4. Chi fa review commenta, chiede modifiche o approva: almeno **1 approvazione**.
5. Merge con **Squash and merge**, poi cancella il branch.

## Messaggi di commit

Imperativo e breve: `Aggiungi filtro per tag ai luoghi`, `Correggi invito scaduto`.