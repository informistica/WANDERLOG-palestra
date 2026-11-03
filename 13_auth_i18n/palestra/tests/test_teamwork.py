"""Livello 12 - lavoro in team: workflow CI, pre-commit, ruff, PR template, CONTRIBUTING.

Questi test non usano il database: leggono e validano i file del progetto.
"""
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest
import yaml

LEVEL = Path(__file__).resolve().parents[2]
WORKFLOW = LEVEL / ".github" / "workflows" / "ci.yml"
PR_TEMPLATE = LEVEL / ".github" / "pull_request_template.md"
CONTRIBUTING = LEVEL / "CONTRIBUTING.md"
PRECOMMIT = LEVEL / ".pre-commit-config.yaml"
RUFF = LEVEL / "ruff.toml"


def load_workflow():
    assert WORKFLOW.exists(), "manca .github/workflows/ci.yml"
    data = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    assert isinstance(data, dict), "ci.yml non e' una mappa YAML"
    return data


def triggers(data):
    # PyYAML legge la chiave `on:` come booleano True (YAML 1.1)
    on = data.get("on", data.get(True))
    if isinstance(on, str):
        return {on: None}
    if isinstance(on, list):
        return {k: None for k in on}
    return on or {}


def single_job(data):
    jobs = data.get("jobs") or {}
    assert len(jobs) >= 1, "nessun job nel workflow"
    return next(iter(jobs.values()))


def steps_of(job):
    return job.get("steps") or []


def find_step(job, needle):
    return [s for s in steps_of(job) if needle in str(s.get("run", ""))]


# ---------------------------------------------------------------- workflow CI

def test_workflow_triggers_push_and_pull_request():
    on = triggers(load_workflow())
    assert "push" in on, "la CI deve partire a ogni push"
    assert "pull_request" in on, "la CI deve partire su ogni pull request"


def test_workflow_has_postgres_and_redis_services():
    job = single_job(load_workflow())
    services = job.get("services") or {}
    images = {name: str(svc.get("image", "")) for name, svc in services.items()}
    assert any(i.startswith("postgres") for i in images.values()), "serve il servizio postgres"
    assert any(i.startswith("redis") for i in images.values()), "serve il servizio redis"
    for svc in services.values():
        assert "--health-cmd" in str(svc.get("options", "")), (
            "ogni servizio deve avere un health check (options: --health-cmd ...)"
        )


def test_workflow_env_points_to_services():
    data = load_workflow()
    job = single_job(data)
    env = {**(data.get("env") or {}), **(job.get("env") or {})}
    for key in ("DJANGO_SECRET_KEY", "DATABASE_URL", "REDIS_URL", "CELERY_BROKER_URL"):
        assert key in env, f"manca la variabile {key} nell'env del job"
    assert str(env["DATABASE_URL"]).startswith("postgres"), "DATABASE_URL deve usare postgres"


def test_workflow_sets_up_python_312_and_installs_dev_requirements():
    job = single_job(load_workflow())
    uses = [str(s.get("uses", "")) for s in steps_of(job)]
    assert any(u.startswith("actions/checkout") for u in uses), "manca actions/checkout"
    setup = [s for s in steps_of(job) if str(s.get("uses", "")).startswith("actions/setup-python")]
    assert setup, "manca actions/setup-python"
    assert str((setup[0].get("with") or {}).get("python-version")) == "3.12"
    assert find_step(job, "requirements-dev.txt"), "installa requirements-dev.txt"


def test_workflow_runs_ruff_lint_imports_and_pytest_with_coverage_gate():
    job = single_job(load_workflow())
    assert find_step(job, "ruff check"), "manca lo step ruff check"
    lint = find_step(job, "lint-imports")
    assert lint, "manca lo step lint-imports"
    tests = find_step(job, "pytest")
    assert tests, "manca lo step pytest"
    for step in lint + tests:
        assert step.get("working-directory") == "palestra", (
            "lint-imports e pytest vanno lanciati dentro palestra/"
        )
    pytest_ini = (LEVEL / "palestra" / "pytest.ini").read_text(encoding="utf-8")
    gate = "--cov-fail-under" in str(tests[0].get("run")) or "--cov-fail-under" in pytest_ini
    assert gate, "pytest in CI deve avere una soglia di coverage"


def test_workflow_order_lint_before_tests():
    job = single_job(load_workflow())
    runs = [str(s.get("run", "")) for s in steps_of(job)]
    pos = {k: next((i for i, r in enumerate(runs) if k in r), None)
           for k in ("pip install", "ruff check", "lint-imports", "pytest")}
    assert None not in pos.values(), f"step mancanti: {pos}"
    assert pos["pip install"] < pos["ruff check"] < pos["pytest"]
    assert pos["lint-imports"] < pos["pytest"], "prima i controlli veloci, poi i test"

# ---------------------------------------------------------------- pre-commit e ruff

def test_precommit_config_runs_ruff():
    assert PRECOMMIT.exists(), "manca .pre-commit-config.yaml nella root del progetto"
    data = yaml.safe_load(PRECOMMIT.read_text(encoding="utf-8"))
    repos = data.get("repos") or []
    ruff = [r for r in repos if "astral-sh/ruff-pre-commit" in str(r.get("repo", ""))]
    assert ruff, "aggiungi il repo astral-sh/ruff-pre-commit"
    assert str(ruff[0].get("rev", "")).startswith("v"), "fissa la versione con rev: vX.Y.Z"
    ids = {h.get("id") for h in ruff[0].get("hooks") or []}
    assert ids & {"ruff", "ruff-check"}, "serve l'hook ruff-check"


def test_precommit_config_has_generic_hooks():
    data = yaml.safe_load(PRECOMMIT.read_text(encoding="utf-8")) if PRECOMMIT.exists() else {}
    ids = {h.get("id") for r in (data or {}).get("repos", []) for h in r.get("hooks") or []}
    assert "check-yaml" in ids, "aggiungi l'hook check-yaml (pre-commit-hooks)"
    assert ids & {"detect-private-key", "check-added-large-files"}, (
        "aggiungi almeno un hook di sicurezza (detect-private-key o check-added-large-files)"
    )


def test_ruff_config_is_valid():
    assert RUFF.exists(), "manca ruff.toml nella root del progetto"
    cfg = tomllib.loads(RUFF.read_text(encoding="utf-8"))
    assert cfg.get("line-length"), "imposta line-length"
    assert cfg.get("lint", {}).get("select"), "imposta [lint] select"
    excluded = " ".join(cfg.get("exclude", []) + cfg.get("extend-exclude", []))
    assert "migrations" in excluded, "escludi le migrazioni generate da Django"


def test_dev_requirements_include_team_tools():
    req = (LEVEL / "requirements-dev.txt").read_text(encoding="utf-8").lower()
    lines = [ln.split("#")[0].strip() for ln in req.splitlines()]
    names = {ln.split(">")[0].split("=")[0].split("<")[0].strip() for ln in lines if ln}
    assert "ruff" in names, "aggiungi ruff a requirements-dev.txt"
    assert "pre-commit" in names, "aggiungi pre-commit a requirements-dev.txt"


def test_ruff_passes_on_project():
    assert RUFF.exists(), "manca ruff.toml nella root del progetto"
    pytest.importorskip("ruff", reason="installa requirements-dev.txt")
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "--config", str(RUFF), "--no-cache", "."],
        cwd=LEVEL, capture_output=True, text=True,
    )
    assert result.returncode == 0, "ruff check fallisce:\n" + result.stdout[-2000:]


# ---------------------------------------------------------------- PR e CONTRIBUTING

def test_pull_request_template_has_checklist():
    assert PR_TEMPLATE.exists(), "manca .github/pull_request_template.md"
    text = PR_TEMPLATE.read_text(encoding="utf-8")
    assert text.count("- [ ]") >= 3, "servono almeno 3 caselle '- [ ]' nella checklist"
    for word in ("pytest", "lint-imports", "migrazion"):
        assert word in text.lower(), f"la checklist deve citare {word}"


def test_contributing_documents_branch_and_pr_workflow():
    assert CONTRIBUTING.exists(), "manca CONTRIBUTING.md"
    text = CONTRIBUTING.read_text(encoding="utf-8").lower()
    assert "feat/" in text, "spiega la convenzione dei branch feat/..."
    assert "pull request" in text, "spiega come si apre una pull request"
    assert "review" in text, "spiega come funziona la review"
    assert "todo" not in text, "CONTRIBUTING contiene ancora dei TODO"


def test_contributing_lists_local_checks():
    text = CONTRIBUTING.read_text(encoding="utf-8") if CONTRIBUTING.exists() else ""
    for cmd in ("pre-commit install", "pytest", "lint-imports", "ruff check"):
        assert cmd in text, f"CONTRIBUTING deve indicare il comando `{cmd}`"