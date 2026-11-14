"""Run the iris_classifier pipeline WITHOUT Mage (same block files, same @test gates).

    python iris_project/run_local.py --max-depth 3

Reads the DAG from pipelines/iris_classifier/metadata.yaml, runs blocks in dependency
order, runs each block's @test function straight after it and stops if one fails.
"""
import argparse
import importlib
import inspect
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
FOLDERS = {'data_loader': 'data_loaders', 'transformer': 'transformers', 'data_exporter': 'data_exporters'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--max-depth', type=int, default=3)
    args = ap.parse_args()
    meta = yaml.safe_load((ROOT / 'pipelines/iris_classifier/metadata.yaml').read_text())
    blocks = {b['uuid']: b for b in meta['blocks']}
    outputs, done = {}, set()
    while len(done) < len(blocks):
        for uuid, b in blocks.items():
            if uuid in done or not all(u in done for u in b['upstream_blocks']):
                continue
            mod = importlib.import_module(f"iris_project.{FOLDERS[b['type']]}.{uuid}")
            func = next(f for n, f in inspect.getmembers(mod, inspect.isfunction)
                        if f.__module__ == mod.__name__ and not n.startswith('test_') and n not in ('test', *FOLDERS))
            ups = [outputs[u] for u in b['upstream_blocks']]
            outputs[uuid] = func(*ups, max_depth=args.max_depth)
            for n, f in inspect.getmembers(mod, inspect.isfunction):
                if n.startswith('test_') and f.__module__ == mod.__name__:
                    try:
                        f(outputs[uuid])
                    except AssertionError as e:
                        sys.exit(f'TEST FAILED in block {uuid}: {e}  -> pipeline stopped')
                    print(f'[{uuid}] test passed')
            done.add(uuid)


if __name__ == '__main__':
    main()
