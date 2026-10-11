"""Independent log reconstruction and matrix closure; no producer imports."""
import json

EXPECTED_CONFIG = {
    'version': '0.1', 'run_id': 'audit-20261011-001',
    'case_ids': ['G0', 'G1', 'G2', 'G3', 'G4', 'C4'], 'entities': ['a', 'b', 'c'],
    'representations': ['R0', 'R1', 'R2', 'R3'],
    'binary_queries': ['same_state', 'ancestor', 'shared_root'],
    'unary_queries': ['parents', 'birth_kind', 'alive'],
    'expected_truth_queries': 216, 'expected_decoder_rows': 864,
    'expected_collision_comparisons': 60, 'wall_seconds': 60, 'memory_bytes': 134217728,
    'seeds': {'policy': 'none; deterministic finite corpus'}}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def check_config(config):
    if canonical(config) != canonical(EXPECTED_CONFIG):
        raise ValueError('Frozen audit configuration mismatch')


def rebuild(events):
    state, direct, birth, consumed = {}, {}, {}, set()
    if not isinstance(events, list) or not events:
        raise ValueError('Independent event inventory')
    for event in events:
        if not isinstance(event, dict) or set(event) != {'kind', 'parents', 'outputs'}:
            raise ValueError('Independent event fields')
        op, inputs, outputs = event['kind'], event['parents'], event['outputs']
        arity = {'root': (0, 1), 'copy': (1, 1), 'continue': (1, 1), 'fork': (1, 2), 'merge': (2, 1)}
        if not isinstance(op, str) or op not in arity or not isinstance(inputs, list) or not isinstance(outputs, list):
            raise ValueError('Independent operation')
        if any(not isinstance(i, str) for i in inputs):
            raise ValueError('Independent parent type')
        if (len(inputs), len(outputs)) != arity[op] or len(set(inputs)) != len(inputs):
            raise ValueError('Independent arity')
        if any(i not in state or i in consumed for i in inputs):
            raise ValueError('Independent unavailable input')
        names = []
        for output in outputs:
            if not isinstance(output, dict) or set(output) != {'id', 'state'}:
                raise ValueError('Independent output fields')
            ident, value = output['id'], output['state']
            if not isinstance(ident, str) or not ident or ident in state or ident in names:
                raise ValueError('Independent fresh handle')
            if not isinstance(value, str) or not value:
                raise ValueError('Independent state')
            if op in ('copy', 'fork') and value != state[inputs[0]]:
                raise ValueError('Independent equal-state operation')
            names.append(ident)
        for output in outputs:
            ident = output['id']
            state[ident], direct[ident], birth[ident] = output['state'], set(inputs), op
        if len(state) > 12:
            raise ValueError('Independent entity limit')
        if op in ('continue', 'fork', 'merge'):
            consumed.update(inputs)
    return {'state': state, 'direct': direct, 'birth': birth, 'consumed': consumed}


def closure(direct):
    # Parent-to-child adjacency with Floyd-Warshall closure, unlike producer traversal.
    ids = sorted(direct)
    edges = {(x, y): x in direct[y] for x in ids for y in ids}
    for middle in ids:
        for left in ids:
            for right in ids:
                edges[left, right] = edges[left, right] or (edges[left, middle] and edges[middle, right])
    if any(edges[x, x] for x in ids):
        raise ValueError('Independent cycle')
    return edges


def evaluate(graph, query):
    kind, args = query['kind'], query['args']
    x = args[0]
    direct = graph['direct']
    reach = closure(direct)
    if kind == 'same_state':
        return graph['state'][x] == graph['state'][args[1]]
    if kind == 'ancestor':
        return reach[x, args[1]]
    if kind == 'shared_root':
        return any(not direct[r] and (r == x or reach[r, x]) and
                   (r == args[1] or reach[r, args[1]]) for r in direct)
    if kind == 'parents':
        return sorted(direct[x])
    if kind == 'birth_kind':
        return graph['birth'][x]
    if kind == 'alive':
        return x not in graph['consumed']
    raise ValueError('Independent query kind')


def encode(graph, rep):
    nodes = {}
    for ident in sorted(graph['state']):
        item = {'state': graph['state'][ident]}
        if rep != 'R0':
            ordered = sorted(graph['direct'][ident])
            item['parents'] = ordered[:1] if rep == 'R1' else ordered
        if rep == 'R3':
            item['kind'] = graph['birth'][ident]
        nodes[ident] = item
    return {'representation': rep, 'nodes': nodes}


def decode(encoded, query):
    rep, nodes = encoded['representation'], encoded['nodes']
    kind, args = query['kind'], query['args']
    x = args[0]
    if kind == 'same_state':
        return nodes[x]['state'] == nodes[args[1]]['state']
    if kind in ('ancestor', 'shared_root') and x == args[1]:
        return kind == 'shared_root'
    if rep == 'R0':
        return None
    direct = {n: set(v['parents']) for n, v in nodes.items()}
    reach = closure(direct)
    if kind in ('ancestor', 'shared_root'):
        if kind == 'ancestor':
            present = reach[x, args[1]]
        else:
            present = any(not direct[r] and (r == x or reach[r, x]) and
                          (r == args[1] or reach[r, args[1]]) for r in direct)
        return present if rep in ('R2', 'R3') or present else None
    if kind == 'parents':
        return sorted(direct[x]) if rep != 'R1' or not direct[x] else None
    if kind == 'birth_kind':
        return nodes[x]['kind'] if rep == 'R3' else 'root' if not direct[x] else None
    if rep == 'R1':
        return None
    uses = [n for n in nodes if x in direct[n]]
    if rep == 'R2':
        return True if not uses else None
    return all(nodes[n]['kind'] == 'copy' for n in uses)


def query_inventory(config):
    # Explicit nested loops, no import of the producer query generator.
    result = []
    for kind in ('same_state', 'ancestor', 'shared_root'):
        for x in config['entities']:
            for y in config['entities']:
                result.append({'kind': kind, 'args': [x, y]})
    for kind in ('parents', 'birth_kind', 'alive'):
        for x in config['entities']:
            result.append({'kind': kind, 'args': [x]})
    return result


def expected_row(graph, case, query, rep, ordinal):
    encoded = encode(graph, rep)
    value, observed = evaluate(graph, query), decode(encoded, query)
    label = 'unknown' if observed is None else 'correct' if canonical(value) == canonical(observed) else 'wrong'
    if label == 'wrong':
        raise ValueError('Independent decoder unsound')
    return {'ordinal': ordinal, 'case': case, 'query': query, 'truth': value,
            'representation': rep, 'projection': encoded, 'answer': observed, 'score': label}


def verify_row(actual, expected):
    if canonical(actual) != canonical(expected):
        raise ValueError('Independent row mismatch at ' + str(expected['ordinal']))


def read_record(iterator, label):
    try:
        return json.loads(next(iterator))
    except StopIteration:
        raise ValueError('Incomplete ' + label + ' coverage') from None


def ensure_end(iterator, label):
    if next(iterator, None) is not None:
        raise ValueError('Extra ' + label + ' row')


def replay(row_stream, collision_stream, fixtures, config, guard=lambda: None):
    check_config(config)
    if [c['id'] for c in fixtures['cases']] != config['case_ids']:
        raise ValueError('Independent case inventory')
    guard()
    graphs = {c['id']: rebuild(c['events']) for c in fixtures['cases']}
    if any(sorted(g['state']) != config['entities'] for g in graphs.values()):
        raise ValueError('Independent entity inventory')
    kinds = config['binary_queries'] + config['unary_queries']
    reps = config['representations']
    by_rep = {r: {'families': {k: dict(correct=0, unknown=0, wrong=0, total=0) for k in kinds},
                  'totals': dict(correct=0, unknown=0, wrong=0, total=0)} for r in reps}
    rows, count = iter(row_stream), 0
    all_queries = query_inventory(config)
    for ident in config['case_ids']:
        for query in all_queries:
            for rep in reps:
                guard()
                expected = expected_row(graphs[ident], ident, query, rep, count)
                verify_row(read_record(rows, 'decoder'), expected)
                for bucket in (by_rep[rep]['families'][query['kind']], by_rep[rep]['totals']):
                    bucket[expected['score']] += 1
                    bucket['total'] += 1
                count += 1
    ensure_end(rows, 'decoder')
    if count != 864:
        raise ValueError('Independent decoder count')
    by_collision = {r: {'comparisons': 0, 'equal_projection_pairs': 0, 'conflicting_pairs': 0,
                       'witness_queries': 0, 'witnesses_by_family': {k: 0 for k in kinds}} for r in reps}
    saved, comparisons = iter(collision_stream), 0
    for i in range(6):
        for j in range(i + 1, 6):
            left, right = config['case_ids'][i], config['case_ids'][j]
            for rep in reps:
                guard()
                equal = canonical(encode(graphs[left], rep)) == canonical(encode(graphs[right], rep))
                witnesses = []
                if equal:
                    for query in all_queries:
                        guard()
                        a, b = evaluate(graphs[left], query), evaluate(graphs[right], query)
                        if canonical(a) != canonical(b):
                            witnesses.append({'query': query, 'left_truth': a, 'right_truth': b})
                expected = {'ordinal': comparisons, 'cases': [left, right], 'representation': rep,
                            'projections_equal': equal, 'witnesses': witnesses}
                verify_row(read_record(saved, 'collision'), expected)
                bucket = by_collision[rep]
                bucket['comparisons'] += 1
                bucket['equal_projection_pairs'] += int(equal)
                bucket['conflicting_pairs'] += int(bool(witnesses))
                bucket['witness_queries'] += len(witnesses)
                for witness in witnesses:
                    bucket['witnesses_by_family'][witness['query']['kind']] += 1
                comparisons += 1
    ensure_end(saved, 'collision')
    return {'truth_queries': count // 4, 'decoder_rows': count,
            'collision_comparisons': comparisons, 'representations': by_rep, 'collisions': by_collision}
