"""Independent event-log replay and pair/partition certificates; no producer import."""
import importlib.util
import json
from pathlib import Path

spec = importlib.util.spec_from_file_location('rp006_independent_log', Path(__file__).resolve().parents[1] / 'RP004/replay.py')
log = importlib.util.module_from_spec(spec)
spec.loader.exec_module(log)
NAMES = ('same_state', 'ancestor', 'shared_root', 'parents', 'birth_kind', 'alive')


def text(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def reconstruct(domain, guard=lambda: None):
    guard()
    cases = domain['cases']
    if not cases or any(set(c) != {'id', 'events'} or not isinstance(c['id'], str) or not c['id'] for c in cases):
        raise ValueError('Independent case inventory')
    identifiers = [c['id'] for c in cases]
    if len(set(identifiers)) != len(identifiers):
        raise ValueError('Independent duplicate identifier')
    world = {c['id']: log.rebuild(c['events']) for c in cases}
    universe = sorted(world[identifiers[0]]['state'])
    if any(sorted(w['state']) != universe for w in world.values()):
        raise ValueError('Independent common universe')
    query_list = []
    for kind in NAMES:
        for x in universe:
            if kind in NAMES[:3]:
                for y in universe:
                    query_list.append({'kind': kind, 'args': [x, y]})
            else:
                query_list.append({'kind': kind, 'args': [x]})
    answers, truth = {}, []
    for name in identifiers:
        answers[name] = []
        for query in query_list:
            guard()
            value = log.evaluate(world[name], query)
            answers[name].append(value)
            truth.append({'ordinal': len(truth), 'case': name, 'query': query, 'truth': value})
    masks = [f'{i:03b}' for i in range(8)]
    families = ('FULL', 'TOPOLOGY_STATE')
    allowed = {'FULL': set(NAMES), 'TOPOLOGY_STATE': set(NAMES[:4])}
    projections, packed = [], {}
    for mask in masks:
        for name in identifiers:
            guard()
            w, fields = world[name], {}
            if mask[0] == '1':
                fields['state'] = {x: w['state'][x] for x in universe}
            if mask[1] == '1':
                fields['parents'] = {x: sorted(w['direct'][x]) for x in universe}
            if mask[2] == '1':
                fields['birth_kind'] = {x: w['birth'][x] for x in universe}
            encoded = {'entities': universe, 'fields': fields}
            packed[mask, name] = encoded
            projections.append({'ordinal': len(projections), 'mask': mask, 'case': name, 'projection': encoded})
    pairs, conflicts = [], []
    compatible = {(m, f): True for m in masks for f in families}
    for mask in masks:
        for i in range(len(identifiers)):
            for j in range(i + 1, len(identifiers)):
                guard()
                left, right = identifiers[i], identifiers[j]
                identical = text(packed[mask, left]) == text(packed[mask, right])
                counts = {f: 0 for f in families}
                evidence = {f: [] for f in families}
                for f in families:
                    if identical:
                        for n, query in enumerate(query_list):
                            if query['kind'] in allowed[f]:
                                guard()
                                counts[f] += 1
                                if text(answers[left][n]) != text(answers[right][n]):
                                    compatible[mask, f] = False
                                    evidence[f].append(len(conflicts))
                                    conflicts.append({'ordinal': len(conflicts), 'mask': mask, 'family': f,
                                        'cases': [left, right], 'query': query,
                                        'left_truth': answers[left][n], 'right_truth': answers[right][n]})
                pairs.append({'ordinal': len(pairs), 'mask': mask, 'cases': [left, right],
                    'projections_equal': identical, 'checked_queries': counts, 'conflict_ordinals': evidence})
    certificates = []
    for mask in masks:
        number = int(mask, 2)
        smaller = [m for m in masks if m != mask and int(m, 2) & number == int(m, 2)]
        for f in families:
            guard()
            # Scan equivalence classes explicitly; no producer bucket/group code.
            remaining = list(identifiers)
            groups = []
            while remaining:
                representative = remaining[0]
                members = [n for n in remaining if text(packed[mask, n]) == text(packed[mask, representative])]
                remaining = [n for n in remaining if n not in members]
                vectors = [[answers[n][k] for k, q in enumerate(query_list) if q['kind'] in allowed[f]] for n in members]
                vector = vectors[0] if all(text(v) == text(vectors[0]) for v in vectors) else None
                groups.append({'projection': packed[mask, representative], 'cases': members, 'common_truth_vector': vector})
            groups.sort(key=lambda g: text(g['projection']))
            certificates.append({'ordinal': len(certificates), 'mask': mask, 'family': f,
                'sufficient': compatible[mask, f],
                'inclusion_minimal': compatible[mask, f] and all(not compatible[m, f] for m in smaller),
                'partitions': groups,
                'proper_submasks': [{'mask': m, 'sufficient': compatible[m, f],
                    'conflict_ordinals': [c['ordinal'] for c in conflicts if c['mask'] == m and c['family'] == f]}
                    for m in smaller]})
    summary = {'cases': len(identifiers), 'entities': len(universe), 'truth_rows': len(truth),
        'projections': len(projections), 'pair_mask_comparisons': len(pairs), 'conflict_rows': len(conflicts),
        'family_mask_verdicts': len(certificates),
        'families': {f: {'sufficient_masks': [m for m in masks if compatible[m, f]],
            'minimal_masks': [c['mask'] for c in certificates if c['family'] == f and c['inclusion_minimal']],
            'equality_gated_query_checks': sum(p['checked_queries'][f] for p in pairs),
            'conflict_rows': sum(c['family'] == f for c in conflicts)} for f in families}}
    return {'truth': truth, 'projections': projections, 'pairs': pairs, 'conflicts': conflicts,
            'certificates': certificates, 'summary': summary}


def verify(actual, domain, guard=lambda: None):
    expected = reconstruct(domain, guard)
    if set(actual) != set(expected):
        raise ValueError('Independent artifact inventory')
    for kind in expected:
        guard()
        if text(actual[kind]) != text(expected[kind]):
            raise ValueError('Independent ' + kind + ' mismatch; coverage/types/values/certificates differ')
    return {'status': 'PASS', 'verified_artifacts': list(expected), 'counts': expected['summary'],
            'basis': 'Independent RP004 log/matrix truth and separately implemented RP006 projection/classification; no producer imports'}
