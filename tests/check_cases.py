"""Compare one-request-per-line actual results against independent expectations."""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from test_algorithms import valid_dag, valid_scc, valid_topo, validate_forest


def lines(path):
    return [json.loads(s) for s in path.read_text(encoding='utf-8').splitlines() if s]


def accepted(request, actual, expected):
    task = request['task']
    if task in ('dsu', 'ping'):
        return actual == expected
    if task in ('kruskal', 'prim'):
        return all(actual.get(k) == expected[k] for k in ('cost', 'components')) and \
            validate_forest(request['n'], request['edges'], actual)
    if task == 'scc':
        return valid_scc(request['n'], request['edges'], actual) and \
            all((actual['component'][u] == actual['component'][v]) ==
                (expected['component'][u] == expected['component'][v])
                for u in range(request['n']) for v in range(request['n']))
    if task == 'topo':
        return actual['acyclic'] == expected['acyclic'] and \
            valid_topo(request['n'], request['edges'], actual)
    if task == 'dag':
        return actual['acyclic'] == expected['acyclic'] and \
            (not expected['acyclic'] or actual['distance'] == expected['distance']) and \
            valid_dag(request, actual)
    return False


def main():
    requests = lines(HERE / 'my_cases.jsonl')
    expected = lines(HERE / 'expected.jsonl')
    assert len(requests) == len(expected)
    command = ['java', '-Xmx384m', '-cp', str(ROOT / '.build/Java'), 'Main']
    stream = '\n'.join(json.dumps(x) for x in requests) + '\n'
    proc = subprocess.run(command, input=stream, text=True, capture_output=True, check=True)
    actual = [json.loads(s) for s in proc.stdout.splitlines()]
    assert len(actual) == len(requests)
    # Run same mixed stream twice in a single process to test state reset.
    proc2 = subprocess.run(command, input=stream + stream, text=True, capture_output=True, check=True)
    twice = [json.loads(s) for s in proc2.stdout.splitlines()]
    assert twice == actual + actual, 'state was not reset between requests'
    (HERE / 'actual_outputs.jsonl').write_text(
        ''.join(json.dumps(x, ensure_ascii=False) + '\n' for x in actual), encoding='utf-8')
    bad = [i+1 for i, (req, act, exp) in enumerate(zip(requests, actual, expected))
           if not accepted(req, act, exp)]
    if bad:
        raise SystemExit(f'FAIL cases: {bad}')
    print(f'PASS {len(requests)} documented cases; mixed request state reset PASS')


if __name__ == '__main__':
    main()
