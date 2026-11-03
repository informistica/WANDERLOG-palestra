"""Test della configurazione di import-linter (passo 3)."""
import configparser
import os
import shutil
import subprocess
import sys

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _lint_imports_exe():
    exe = shutil.which('lint-imports')
    if exe:
        return exe
    scripts = os.path.dirname(sys.executable)
    for name in ('lint-imports', 'lint-imports.exe'):
        if os.path.exists(os.path.join(scripts, name)):
            return os.path.join(scripts, name)
    raise AssertionError('lint-imports non trovato: installa requirements-dev.txt')


def test_layers_contract_declared():
    cfg = configparser.ConfigParser()
    assert cfg.read(os.path.join(PROJECT, '.importlinter')), 'Manca palestra/.importlinter'
    contracts = [s for s in cfg.sections() if s.startswith('importlinter:contract:')]
    layers = [cfg[s] for s in contracts if cfg[s].get('type') == 'layers']
    assert layers, 'Serve un contratto con type = layers'
    order = [l.strip() for l in layers[0]['layers'].splitlines() if l.strip()]
    assert order == ['places', 'boards', 'core']


def test_lint_imports_passes():
    result = subprocess.run([_lint_imports_exe(), '--no-cache'], cwd=PROJECT,
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert '1 kept, 0 broken' in result.stdout
