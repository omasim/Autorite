"""Producer for the predeclared finite query/projection corpus."""
import json
from collections import Counter
from itertools import product, combinations
from lineage import construct, truth, project, answer, score


def queries(config):
    for kind in config['binary_queries']:
        for args in product(config['entities'], repeat=2):
            yield {'kind': kind, 'args': list(args)}
    for kind in config['unary_queries']:
        for ident in config['entities']:
            yield {'kind': kind, 'args': [ident]}


def make_row(graph, case, query, representation, ordinal):
    encoded = project(graph, representation)
    expected, observed = truth(graph, query), answer(encoded, query)
    return {'ordinal': ordinal, 'case': case, 'query': query, 'truth': expected,
            'representation': representation, 'projection': encoded,
            'answer': observed, 'score': score(expected, observed)}


def iter_rows(fixtures, config, guard=lambda: None):
    ordinal = 0
    guard()
    for case in fixtures['cases']:
        graph = construct(case['events'])
        for query in queries(config):
            for representation in config['representations']:
                guard()
                row = make_row(graph, case['id'], query, representation, ordinal)
                if row['score'] == 'wrong':
                    raise ValueError('Unsound answer at ordinal ' + str(ordinal))
                yield row
                ordinal += 1
    if ordinal != config['expected_decoder_rows']:
        raise ValueError('Decoder coverage mismatch')


def iter_collisions(fixtures, config, guard=lambda: None):
    guard()
    graphs = {c['id']: construct(c['events']) for c in fixtures['cases']}
    ordinal = 0
    for left, right in combinations(config['case_ids'], 2):
        for representation in config['representations']:
            guard()
            equal = project(graphs[left], representation) == project(graphs[right], representation)
            witnesses = []
            if equal:
                for query in queries(config):
                    guard()
                    a, b = truth(graphs[left], query), truth(graphs[right], query)
                    if a != b:
                        witnesses.append({'query': query, 'left_truth': a, 'right_truth': b})
            yield {'ordinal': ordinal, 'cases': [left, right], 'representation': representation,
                   'projections_equal': equal, 'witnesses': witnesses}
            ordinal += 1
    if ordinal != config['expected_collision_comparisons']:
        raise ValueError('Collision coverage mismatch')


def summarize(rows, collisions, config):
    family = config['binary_queries'] + config['unary_queries']
    counts = {rep: {kind: Counter() for kind in family} for rep in config['representations']}
    for row in rows:
        counts[row['representation']][row['query']['kind']][row['score']] += 1
    representations = {}
    for rep, families in counts.items():
        by_family = {k: {s: c[s] for s in ('correct', 'unknown', 'wrong')} for k, c in families.items()}
        for value in by_family.values():
            value['total'] = sum(value.values())
        total = {s: sum(v[s] for v in by_family.values()) for s in ('correct', 'unknown', 'wrong', 'total')}
        representations[rep] = {'families': by_family, 'totals': total}
    collision_counts = {}
    for rep in config['representations']:
        selected = [c for c in collisions if c['representation'] == rep]
        collision_counts[rep] = {'comparisons': len(selected),
            'equal_projection_pairs': sum(c['projections_equal'] for c in selected),
            'conflicting_pairs': sum(bool(c['witnesses']) for c in selected),
            'witness_queries': sum(len(c['witnesses']) for c in selected),
            'witnesses_by_family': {k: sum(w['query']['kind'] == k for c in selected for w in c['witnesses']) for k in family}}
    return {'truth_queries': len(rows) // 4, 'decoder_rows': len(rows),
            'collision_comparisons': len(collisions), 'representations': representations,
            'collisions': collision_counts}


def write_jsonl(stream, rows):
    for row in rows:
        stream.write(json.dumps(row, sort_keys=True, separators=(',', ':')) + '\n')
