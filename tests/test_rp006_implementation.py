import copy
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location('rp006_' + name, ROOT / 'research/RP006' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


producer, verifier, resources = load('producer'), load('verifier'), load('resources')
DOMAIN = json.loads((ROOT / 'research/RP006/DOMAIN.json').read_text())


class RP006Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = producer.produce(DOMAIN)

    def test_complete_known_domain_replay(self):
        report = verifier.verify(self.outputs, DOMAIN)
        self.assertEqual(report['status'], 'PASS')
        self.assertEqual([len(self.outputs[k]) for k in ('truth', 'projections', 'pairs', 'certificates')], [216, 48, 120, 16])

    def corrupted(self, section, mutate):
        output = copy.deepcopy(self.outputs)
        mutate(output[section])
        with self.assertRaisesRegex(ValueError, 'Independent ' + section + ' mismatch'):
            verifier.verify(output, DOMAIN)

    def test_wrong_truth_value(self):
        self.corrupted('truth', lambda x: x[0].update(truth=False))

    def test_bool_int_coercion_rejected(self):
        self.corrupted('truth', lambda x: x[0].update(truth=1))

    def test_missing_truth_row(self):
        self.corrupted('truth', lambda x: x.pop())

    def test_extra_pair_row(self):
        self.corrupted('pairs', lambda x: x.append(copy.deepcopy(x[0])))

    def test_missing_conflict_witness(self):
        self.corrupted('conflicts', lambda x: x.pop())

    def test_hidden_case_identifier(self):
        self.corrupted('projections', lambda x: x[0]['projection'].update(case_id=x[0]['case']))

    def test_omitted_not_empty_field(self):
        self.corrupted('projections', lambda x: x[0]['projection']['fields'].update(parents={}))

    def test_complete_merge_parent_set(self):
        output = copy.deepcopy(self.outputs)
        row = next(x for x in output['projections'] if x['case'] == 'G4' and x['mask'] == '010')
        self.assertEqual(row['projection']['fields']['parents']['c'], ['a', 'b'])
        row['projection']['fields']['parents']['c'] = ['a']
        with self.assertRaisesRegex(ValueError, 'Independent projections mismatch'):
            verifier.verify(output, DOMAIN)

    def test_false_minimality(self):
        self.corrupted('certificates', lambda x: x[0].update(inclusion_minimal=True))

    def test_corrupt_partition_vector(self):
        self.corrupted('certificates', lambda x: x[0]['partitions'][0].update(common_truth_vector=[]))

    def test_incomplete_submask_certificate(self):
        self.corrupted('certificates', lambda x: x[-1]['proper_submasks'].pop())

    def test_summary_cannot_substitute_for_rows(self):
        self.corrupted('summary', lambda x: x.update(truth_rows=215))

    def test_verifier_does_not_use_producer_truth(self):
        with patch.object(producer.lineage, 'truth', side_effect=AssertionError('Producer truth must not be used')):
            self.assertEqual(verifier.verify(self.outputs, DOMAIN)['status'], 'PASS')

    def test_global_opaque_renaming(self):
        domain = copy.deepcopy(DOMAIN)
        rename = {'a': 'u93', 'b': 'v17', 'c': 'w61'}
        for case in domain['cases']:
            for event in case['events']:
                event['parents'] = [rename[x] for x in event['parents']]
                for output in event['outputs']:
                    output['id'] = rename[output['id']]
        actual = producer.produce(domain)
        verifier.verify(actual, domain)
        self.assertEqual(actual['summary'], self.outputs['summary'])

    def test_parent_order_invariance(self):
        domain = copy.deepcopy(DOMAIN)
        for case in domain['cases']:
            for event in case['events']:
                event['parents'].reverse()
        actual = producer.produce(domain)
        self.assertEqual(actual, self.outputs)
        verifier.verify(actual, domain)

    def test_expected_answer_side_channel_rejected(self):
        domain = copy.deepcopy(DOMAIN)
        domain['cases'][0]['expected'] = True
        for routine in (producer.produce, verifier.reconstruct):
            with self.assertRaises(ValueError):
                routine(domain)

    def test_malformed_consumed_input(self):
        domain = copy.deepcopy(DOMAIN)
        domain['cases'][0]['events'][-1]['parents'] = ['a']
        for routine in (producer.produce, verifier.reconstruct):
            with self.assertRaises(ValueError):
                routine(domain)

    def test_invalid_query(self):
        graph = producer.lineage.construct(DOMAIN['cases'][0]['events'])
        for query in ({'kind': 'ancestor', 'args': ['a']}, {'kind': 'unknown', 'args': ['a']},
                      {'kind': 'parents', 'args': ['absent']}):
            with self.assertRaises(ValueError):
                producer.lineage.truth(graph, query)

    def test_guard_stops_producer_and_verifier(self):
        def fail():
            raise ValueError('Injected stop')
        for routine in (producer.produce, verifier.reconstruct):
            with self.assertRaisesRegex(ValueError, 'Injected stop'):
                routine(DOMAIN, fail)


class ResourceControls(unittest.TestCase):
    def guard(self):
        self.clock = [0.0, 0.0, 1]
        return resources.Guard(monotonic=lambda: self.clock[0], civil=lambda: self.clock[1], rss=lambda: self.clock[2])

    def test_deadline(self):
        guard = self.guard()
        self.clock[:2] = [61, 61]
        with self.assertRaisesRegex(ValueError, 'deadline'):
            guard()

    def test_host_suspension_gap(self):
        guard = self.guard()
        self.clock[:2] = [1, 5]
        with self.assertRaisesRegex(ValueError, 'discrepancy'):
            guard()

    def test_clock_regression(self):
        guard = self.guard()
        self.clock[:2] = [1, 1]
        guard()
        self.clock[1] = 0.5
        with self.assertRaisesRegex(ValueError, 'regression'):
            guard()

    def test_memory_limit(self):
        guard = self.guard()
        self.clock[2] = 134217729
        with self.assertRaisesRegex(ValueError, 'RSS'):
            guard()


if __name__ == '__main__':
    unittest.main()
