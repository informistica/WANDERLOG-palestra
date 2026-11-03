"""Test dei TODO di Dockerfile e compose.yaml (leggono i file, non serve Docker)."""
import os
import re

import yaml

LEVEL_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _dockerfile_instructions():
    with open(os.path.join(LEVEL_ROOT, 'Dockerfile'), encoding='utf-8') as f:
        lines = [l.strip() for l in f if l.strip() and not l.strip().startswith('#')]
    return lines


def _compose():
    with open(os.path.join(LEVEL_ROOT, 'compose.yaml'), encoding='utf-8') as f:
        return yaml.safe_load(f)


def test_dockerfile_base_image():
    lines = _dockerfile_instructions()
    froms = [l for l in lines if l.upper().startswith('FROM ')]
    assert froms, "Manca l'istruzione FROM"
    assert froms[0].split()[1] == 'python:3.12-slim'


def test_dockerfile_installs_requirements_before_code():
    lines = _dockerfile_instructions()
    copy_req = next((i for i, l in enumerate(lines)
                     if l.upper().startswith('COPY ') and 'requirements' in l), None)
    pip = next((i for i, l in enumerate(lines)
                if l.upper().startswith('RUN ') and re.search(r'pip install .*-r requirements', l)), None)
    copy_all = next((i for i, l in enumerate(lines) if re.fullmatch(r'COPY \. \.?/?', l, re.I)), None)
    assert copy_req is not None, "Copia i file requirements prima di installarli"
    assert pip is not None, "Installa le dipendenze con pip install -r requirements..."
    assert copy_all is not None, "Copia il codice con COPY . ."
    assert copy_req < pip < copy_all, "Ordine: COPY requirements, RUN pip install, COPY . ."


def test_dockerfile_installs_dev_requirements():
    lines = _dockerfile_instructions()
    assert any('requirements-dev.txt' in l and 'pip install' in l for l in lines), (
        "Nel container servono anche pytest e pytest-django: installa requirements-dev.txt"
    )


def test_compose_django_uses_env_file():
    env_file = _compose()['services']['django'].get('env_file')
    files = [env_file] if isinstance(env_file, str) else (env_file or [])
    files = [f if isinstance(f, str) else f.get('path') for f in files]
    assert '.env' in files


def test_compose_django_waits_for_healthy_db():
    depends = _compose()['services']['django'].get('depends_on') or {}
    assert isinstance(depends, dict), "Usa la forma estesa di depends_on con condition"
    assert depends.get('db', {}).get('condition') == 'service_healthy'
    assert 'redis' in depends


def test_compose_db_healthcheck():
    hc = _compose()['services']['db'].get('healthcheck') or {}
    test = hc.get('test')
    test = ' '.join(test) if isinstance(test, list) else (test or '')
    assert 'pg_isready' in test
    assert '-d palestra_db' in test
