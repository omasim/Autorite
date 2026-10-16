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


def reconstruct(domain, guard=lambda: None, *, retain_conflicts=True, conflict_sink=None):
    """Independently reconstruct RP006 artifacts, optionally streaming witnesses.

    Bounded mode emits each expected conflict to `conflict_sink` and retains
    only compact pair/certificate indexes. It intentionally implements this
    path here, separately from the producer's logic.
    """
    if not retain_conflicts and conflict_sink is None:
        raise ValueError('Bounded replay requires a conflict sink')
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
    conflict_counts = {(m, f): 0 for m in masks for f in families}
    conflict_first = {(m, f): None for m in masks for f in families}
    conflict_ordinal = 0
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
                                    row = {'ordinal': conflict_ordinal, 'mask': mask, 'family': f,
                                           'cases': [left, right], 'query': query,
                                           'left_truth': answers[left][n], 'right_truth': answers[right][n]}
                                    if conflict_sink is not None:
                                        conflict_sink(row)
                                    if retain_conflicts:
                                        conflicts.append(row)
                                    evidence[f].append(conflict_ordinal)
                                    conflict_counts[mask, f] += 1
                                    if conflict_first[mask, f] is None:
                                        conflict_first[mask, f] = conflict_ordinal
                                    conflict_ordinal += 1
                if retain_conflicts:
                    pair = {'ordinal': len(pairs), 'mask': mask, 'cases': [left, right],
                        'projections_equal': identical, 'checked_queries': counts, 'conflict_ordinals': evidence}
                else:
                    pair = {'ordinal': len(pairs), 'mask': mask, 'cases': [left, right],
                        'projections_equal': identical, 'checked_queries': counts,
                        'conflict_index': {f: {'count': len(evidence[f]),
                            'first_ordinal': evidence[f][0] if evidence[f] else None} for f in sorted(families)}}
                pairs.append(pair)
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
                'proper_submasks': ([{'mask': m, 'sufficient': compatible[m, f],
                    'conflict_ordinals': [c['ordinal'] for c in conflicts if c['mask'] == m and c['family'] == f]}
                    for m in smaller] if retain_conflicts else
                    [{'mask': m, 'sufficient': compatible[m, f],
                      'conflict_index': {'count': conflict_counts[m, f],
                                         'first_ordinal': conflict_first[m, f]}}
                     for m in smaller])})
    summary = {'cases': len(identifiers), 'entities': len(universe), 'truth_rows': len(truth),
        'projections': len(projections), 'pair_mask_comparisons': len(pairs),
        'conflict_rows': sum(conflict_counts[m, f] for m in masks for f in families),
        'family_mask_verdicts': len(certificates),
        'families': {f: {'sufficient_masks': [m for m in masks if compatible[m, f]],
            'minimal_masks': [c['mask'] for c in certificates if c['family'] == f and c['inclusion_minimal']],
            'equality_gated_query_checks': sum(p['checked_queries'][f] for p in pairs),
            'conflict_rows': sum(conflict_counts[m, f] for m in masks)} for f in families}}
    return {'truth': truth, 'projections': projections, 'pairs': pairs,
            'conflicts': conflicts if retain_conflicts else [],
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


def verify_bounded(actual, conflict_path, domain, guard=lambda: None):
    """Verify compact artifacts and compare every witness in a streaming pass."""
    import hashlib
    from pathlib import Path

    if set(actual) != {'truth', 'projections', 'pairs', 'conflicts', 'certificates', 'summary'}:
        raise ValueError('Bounded artifact inventory')
    if actual['conflicts'] not in (None, []):
        raise ValueError('Bounded handoff must not retain conflicts in memory')
    path = Path(conflict_path)
    conflict_hash = hashlib.sha256()
    with path.open('r', encoding='utf-8') as stream:
        def compare_expected(row):
            guard()
            line = stream.readline()
            if not line:
                raise ValueError('Independent conflict stream ended early')
            encoded = line.encode('utf-8')
            conflict_hash.update(encoded)
            try:
                observed = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError('Malformed conflict JSONL row') from exc
            if text(observed) != text(row):
                raise ValueError('Independent conflict witness mismatch')
            if encoded != (text(row) + '\n').encode('utf-8'):
                raise ValueError('Conflict witness row is not canonically serialized')

        expected = reconstruct(domain, guard, retain_conflicts=False, conflict_sink=compare_expected)
        if stream.readline():
            raise ValueError('Independent conflict stream has extra rows')
    for kind in ('truth', 'projections', 'pairs', 'certificates', 'summary'):
        guard()
        if text(actual[kind]) != text(expected[kind]):
            raise ValueError('Independent ' + kind + ' mismatch; coverage/types/values/certificates differ')
    return {'status': 'PASS',
            'verified_artifacts': ['truth', 'projections', 'pairs', 'conflicts', 'certificates', 'summary'],
            'verified_artifact_sha256': {'conflicts.jsonl': conflict_hash.hexdigest()},
            'counts': expected['summary'],
            'basis': 'Independent RP004 log/matrix replay; conflicts compared row-by-row without retaining the witness set'}
