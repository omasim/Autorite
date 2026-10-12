"""Pure RP006 engineering computation; no execution authorization or file writes."""
import importlib.util
import itertools
import json
from pathlib import Path

spec = importlib.util.spec_from_file_location('rp006_producer_lineage', Path(__file__).resolve().parents[1] / 'RP004/lineage.py')
lineage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lineage)
FIELDS = ('state', 'parents', 'birth_kind')
MASKS = tuple(format(i, '03b') for i in range(8))
FAMILIES = {'FULL': ('same_state', 'ancestor', 'shared_root', 'parents', 'birth_kind', 'alive'),
            'TOPOLOGY_STATE': ('same_state', 'ancestor', 'shared_root', 'parents')}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def queries(entities):
    return [{'kind': kind, 'args': list(args)} for kind in FAMILIES['FULL']
            for args in itertools.product(entities, repeat=lineage.QUERIES[kind])]


def project(nodes, mask):
    if mask not in MASKS:
        raise ValueError('Whole-field mask')
    maps = {'state': {x: n['state'] for x, n in sorted(nodes.items())},
            'parents': {x: sorted(n['parents']) for x, n in sorted(nodes.items())},
            'birth_kind': {x: n['kind'] for x, n in sorted(nodes.items())}}
    return {'entities': sorted(nodes), 'fields': {f: maps[f] for f, bit in zip(FIELDS, mask) if bit == '1'}}


def proper_submasks(mask):
    return [m for m in MASKS if m != mask and all(a == '0' or b == '1' for a, b in zip(m, mask))]


def produce(domain, guard=lambda: None):
    guard()
    cases = domain['cases']
    if not cases or any(set(c) != {'id', 'events'} or not isinstance(c['id'], str) or not c['id'] for c in cases):
        raise ValueError('Case fields; expected-answer side channels forbidden')
    names = [c['id'] for c in cases]
    if len(set(names)) != len(names):
        raise ValueError('Duplicate case identifiers')
    graphs = {c['id']: lineage.construct(c['events']) for c in cases}
    entities = sorted(graphs[names[0]])
    if any(sorted(g) != entities for g in graphs.values()):
        raise ValueError('Common aligned entity universe required')
    inventory = queries(entities)
    values = {name: [lineage.truth(graphs[name], q) for q in inventory] for name in names}
    truth_rows = []
    for name in names:
        for query, value in zip(inventory, values[name]):
            guard()
            truth_rows.append(dict(ordinal=len(truth_rows), case=name, query=query, truth=value))
    projections = []
    encoded = {}
    for mask in MASKS:
        for name in names:
            guard()
            value = project(graphs[name], mask)
            encoded[mask, name] = value
            projections.append(dict(ordinal=len(projections), mask=mask, case=name, projection=value))
    pairs, conflicts = [], []
    for mask in MASKS:
        for left, right in itertools.combinations(names, 2):
            guard()
            equal = canonical(encoded[mask, left]) == canonical(encoded[mask, right])
            indices, checked = {}, {}
            for family, kinds in FAMILIES.items():
                indices[family], checked[family] = [], 0
                if equal:
                    for i, query in enumerate(inventory):
                        if query['kind'] not in kinds:
                            continue
                        guard()
                        checked[family] += 1
                        a, b = values[left][i], values[right][i]
                        if canonical(a) != canonical(b):
                            ordinal = len(conflicts)
                            indices[family].append(ordinal)
                            conflicts.append(dict(ordinal=ordinal, mask=mask, family=family, cases=[left, right],
                                                  query=query, left_truth=a, right_truth=b))
            pairs.append(dict(ordinal=len(pairs), mask=mask, cases=[left, right],
                              projections_equal=equal, checked_queries=checked, conflict_ordinals=indices))
    sufficient = {(mask, family): not any(c['mask'] == mask and c['family'] == family for c in conflicts)
                  for mask in MASKS for family in FAMILIES}
    certificates = []
    for mask in MASKS:
        for family, kinds in FAMILIES.items():
            guard()
            buckets = {}
            for name in names:
                key = canonical(encoded[mask, name])
                buckets.setdefault(key, []).append(name)
            groups = []
            for key, members in sorted(buckets.items()):
                vectors = [[v for q, v in zip(inventory, values[n]) if q['kind'] in kinds] for n in members]
                same = len({canonical(v) for v in vectors}) == 1
                groups.append(dict(projection=json.loads(key), cases=members,
                                   common_truth_vector=vectors[0] if same else None))
            submasks = proper_submasks(mask)
            certificates.append(dict(ordinal=len(certificates), mask=mask, family=family,
                sufficient=sufficient[mask, family],
                inclusion_minimal=sufficient[mask, family] and not any(sufficient[m, family] for m in submasks),
                partitions=groups,
                proper_submasks=[dict(mask=m, sufficient=sufficient[m, family],
                    conflict_ordinals=[c['ordinal'] for c in conflicts if c['mask'] == m and c['family'] == family])
                    for m in submasks]))
    for mask in MASKS:
        for lower in proper_submasks(mask):
            for family in FAMILIES:
                if sufficient[lower, family] and not sufficient[mask, family]:
                    raise ValueError('Field-retention monotonicity violated')
    summary = dict(cases=len(names), entities=len(entities), truth_rows=len(truth_rows),
        projections=len(projections), pair_mask_comparisons=len(pairs), conflict_rows=len(conflicts),
        family_mask_verdicts=len(certificates),
        families={f: dict(sufficient_masks=[m for m in MASKS if sufficient[m, f]],
            minimal_masks=[c['mask'] for c in certificates if c['family'] == f and c['inclusion_minimal']],
            equality_gated_query_checks=sum(p['checked_queries'][f] for p in pairs),
            conflict_rows=sum(c['family'] == f for c in conflicts)) for f in FAMILIES})
    return dict(truth=truth_rows, projections=projections, pairs=pairs, conflicts=conflicts,
                certificates=certificates, summary=summary)
