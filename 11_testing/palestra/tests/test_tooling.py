"""Livello 11 (bersaglio): dipendenze di test, configurazione della copertura, matrice parametrizzata."""
import ast
import configparser
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]      # cartella palestra/
LEVEL = ROOT.parent                              # cartella del livello


def _ini(name):
    cp = configparser.ConfigParser()
    assert cp.read(ROOT / name, encoding='utf-8'), f'manca {name}'
    return cp


def _lines(value):
    return [x.strip() for x in re.split(r'[\n,]', value) if x.strip()]


def test_dev_requirements():
    names = {re.split(r'[<>=!~\[ ]', line.strip())[0].lower().replace('_', '-')
             for line in (LEVEL / 'requirements-dev.txt').read_text(encoding='utf-8').splitlines()
             if line.strip() and not line.startswith(('#', '-'))}
    assert {'factory-boy', 'pytest-cov'} <= names


def test_pytest_ini_enables_coverage():
    addopts = _ini('pytest.ini')['pytest'].get('addopts', '').split()
    assert any(o == '--cov' or o.startswith('--cov=') for o in addopts)
    assert '--cov-report=term-missing' in addopts
    assert '--cov-fail-under=80' in addopts


def test_coveragerc_source():
    source = set(_lines(_ini('.coveragerc')['run'].get('source', '')))
    assert {'boards', 'places', 'inbox', 'core'} <= source


def test_coveragerc_omit():
    omit = _lines(_ini('.coveragerc')['run'].get('omit', ''))
    assert any('migrations' in o for o in omit), 'escludi le migrazioni'
    assert any(o.startswith(('tests', '*/tests')) for o in omit), 'escludi i test'


def test_policy_matrix_is_parametrized():
    out = subprocess.run(
        [sys.executable, '-m', 'pytest', '--collect-only', '-q', '-p', 'no:cacheprovider',
         '-o', 'addopts=', 'tests/test_policy_matrix.py'],
        cwd=ROOT, capture_output=True, text=True, timeout=120)
    ids = [line for line in out.stdout.splitlines() if 'test_policy_matrix.py::' in line]
    assert len(ids) >= 12, out.stdout[-1500:] + out.stderr[-1500:]
    assert all('[' in i for i in ids), 'ogni caso deve venire da @pytest.mark.parametrize'
    for role in ('owner', 'collaborator', 'stranger', 'anonymous'):
        assert any(role in i for i in ids), f'manca il ruolo {role}'


def test_policy_matrix_uses_fixtures():
    tree = ast.parse((ROOT / 'tests' / 'test_policy_matrix.py').read_text(encoding='utf-8'))
    calls = {ast.unparse(n.func) for n in ast.walk(tree) if isinstance(n, ast.Call)}
    assert any(c.endswith('parametrize') for c in calls), 'usa @pytest.mark.parametrize'
    assert not any(c.endswith(('create_user', 'objects.create')) for c in calls), 'usa fixture e factory'
    tests = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name.startswith('test')]
    assert tests and any({'board'} <= {a.arg for a in t.args.args} for t in tests)