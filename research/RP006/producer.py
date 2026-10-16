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


def produce(domain, guard=lambda: None, *, retain_conflicts=True, conflict_sink=None):
    """Produce the RP006 bundle.

    Bounded mode (`retain_conflicts=False`) sends each conflict row to the
    caller-provided sink as it is found and retains only per-pair and
    per-mask/family counts plus first ordinals. The default preserves the
    historical in-memory result shape for the original RP006 workflow.
    """
    if not retain_conflicts and conflict_sink is None:
        raise ValueError('Bounded mode requires a conflict sink')
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
    conflict_counts = {(mask, family): 0 for mask in MASKS for family in FAMILIES}
    conflict_first = {(mask, family): None for mask in MASKS for family in FAMILIES}
    conflict_ordinal = 0
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
                            ordinal = conflict_ordinal
                            row = dict(ordinal=ordinal, mask=mask, family=family, cases=[left, right],
                                       query=query, left_truth=a, right_truth=b)
                            if conflict_sink is not None:
                                conflict_sink(row)
                            if retain_conflicts:
                                conflicts.append(row)
                            conflict_ordinal += 1
                            conflict_counts[mask, family] += 1
                            if conflict_first[mask, family] is None:
                                conflict_first[mask, family] = ordinal
                            indices[family].append(ordinal)
            if retain_conflicts:
                pair = dict(ordinal=len(pairs), mask=mask, cases=[left, right],
                            projections_equal=equal, checked_queries=checked, conflict_ordinals=indices)
            else:
                pair = dict(ordinal=len(pairs), mask=mask, cases=[left, right],
                            projections_equal=equal, checked_queries=checked,
                            conflict_index={family: {'count': len(indices[family]),
                                'first_ordinal': indices[family][0] if indices[family] else None}
                                for family in sorted(FAMILIES)})
            pairs.append(pair)
    sufficient = {(mask, family): conflict_counts[mask, family] == 0
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
            submask_rows = []
            for submask in submasks:
                if retain_conflicts:
                    ordinals = [c['ordinal'] for c in conflicts
                                if c['mask'] == submask and c['family'] == family]
                    submask_rows.append(dict(mask=submask, sufficient=sufficient[submask, family],
                                             conflict_ordinals=ordinals))
                else:
                    submask_rows.append(dict(mask=submask, sufficient=sufficient[submask, family],
                        conflict_index={'count': conflict_counts[submask, family],
                                        'first_ordinal': conflict_first[submask, family]}))
            certificates.append(dict(ordinal=len(certificates), mask=mask, family=family,
                sufficient=sufficient[mask, family],
                inclusion_minimal=sufficient[mask, family] and not any(sufficient[m, family] for m in submasks),
                partitions=groups,
                proper_submasks=submask_rows))
    for mask in MASKS:
        for lower in proper_submasks(mask):
            for family in FAMILIES:
                if sufficient[lower, family] and not sufficient[mask, family]:
                    raise ValueError('Field-retention monotonicity violated')
    summary = dict(cases=len(names), entities=len(entities), truth_rows=len(truth_rows),
        projections=len(projections), pair_mask_comparisons=len(pairs),
        conflict_rows=sum(conflict_counts[m, f] for m in MASKS for f in FAMILIES),
        family_mask_verdicts=len(certificates),
        families={f: dict(sufficient_masks=[m for m in MASKS if sufficient[m, f]],
            minimal_masks=[c['mask'] for c in certificates if c['family'] == f and c['inclusion_minimal']],
            equality_gated_query_checks=sum(p['checked_queries'][f] for p in pairs),
            conflict_rows=sum(conflict_counts[m, f] for m in MASKS)) for f in FAMILIES})
    return dict(truth=truth_rows, projections=projections, pairs=pairs,
                conflicts=conflicts if retain_conflicts else [],
                certificates=certificates, summary=summary)
