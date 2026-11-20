"""Freeze small inputs and upstream provisional code, never large raw sources."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/qa/agent2/baseline'


def digest(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(2**20), b''):
            h.update(b)
    return h.hexdigest()


def main():
    if (OUT / 'capture.json').exists():
        raise SystemExit('Baseline already captured; refusing to replace it.')
    OUT.mkdir(parents=True, exist_ok=True)
    record = {'utc': datetime.now(timezone.utc).isoformat(), 'workspaces': {}, 'copies': []}
    for name in ('jakarta-heat', 'jakarta-heat-agent1', 'jakarta-heat-agent2', 'jakarta-heat-agent3'):
        p = ROOT.parent / name
        def git(*args):
            return subprocess.check_output(['git', '-C', str(p), *args], text=True, encoding='utf-8')
        record['workspaces'][name] = {k: git(*args).strip() for k, args in {
            'branch': ['branch', '--show-current'], 'sha': ['rev-parse', 'HEAD'],
            'status': ['status', '--short', '--untracked-files=all']}.items()}
    sources = [(ROOT / 'data/processed' / f, OUT / 'person2' / f) for f in
               ('grid_master.csv', 'spatial_features.csv', 'accessibility_grid.csv',
                'population_grid.csv', 'vulnerability_grid.csv', 'qa_problem_grids.csv')]
    for agent in ('agent1', 'agent3'):
        src = ROOT.parent / ('jakarta-heat-' + agent)
        for p in (src / 'handoff').glob('*.md'):
            sources.append((p, OUT / agent / 'handoff' / p.name))
        if agent == 'agent1':
            for p in (src / 'data/processed').glob('remote_sensing_grid.*'):
                sources.append((p, OUT / agent / 'data/processed' / p.name))
        else:
            for sub, pattern in [('jhim', '*.py'), ('data/processed/modeling', '*'),
                                 ('outputs/tables', '*'), ('outputs/gis', '*.gpkg')]:
                for p in (src / sub).glob(pattern):
                    if p.is_file():
                        sources.append((p, OUT / agent / sub / p.name))
    for p, target in sources:
        before = digest(p)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, target)
        if before != digest(target) or before != digest(p):
            raise RuntimeError(f'Upstream changed during snapshot: {p}')
        record['copies'].append({'source': str(p), 'copy': str(target.relative_to(ROOT)), 'sha256': before})
    (OUT / 'capture.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
    print(f'Frozen {len(sources)} small input/code artifacts; upstream files untouched.')


if __name__ == '__main__':
    main()
