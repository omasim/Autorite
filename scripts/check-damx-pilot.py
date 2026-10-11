"""Check supplied report fidelity, never legacy truth, survival or instruction authority."""
from pathlib import Path
from zipfile import ZipFile
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ID = 'SRC-DAMXREPORT2026'
SOURCE_SHA = '85a7b3752d8f37130dd97e3c0a172a5e340046fd9b6d571832ef61bcccd3a688'
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(root):
    directory = root / 'legacy/damx/sources/LEG-SRC-001'
    receipt = json.loads((directory / 'RECEIPT.json').read_text())
    original = root / receipt['document_path']
    data = original.read_bytes()
    require(hashlib.sha256(data).hexdigest() == receipt['sha256'] == SOURCE_SHA,
            'Original DOCX differs from the supplied source')
    require(len(data) == receipt['size_bytes'] == 49733, 'Source byte count')
    require(receipt['source_id'] == SOURCE_ID and receipt['primary_source_status'] == 'NOT_SUPPLIED',
            'Source classification/identity')
    transcript_path = root / receipt['transcript_path']
    transcript_bytes = transcript_path.read_bytes()
    require(hashlib.sha256(transcript_bytes).hexdigest() == receipt['transcript_sha256'], 'Transcript hash')
    transcript = json.loads(transcript_bytes)
    require(transcript['source_id'] == SOURCE_ID and transcript['document_sha256'] == SOURCE_SHA, 'Transcript source')
    with ZipFile(original) as archive:
        xml = ET.fromstring(archive.read('word/document.xml'))
        body = xml.find('w:body', NS)
        blocks = []
        paragraphs = tables = 0
        for element in body:
            if element.tag == '{' + NS['w'] + '}p':
                paragraphs += 1
                blocks.append({'id': f'P{paragraphs:03d}', 'kind': 'paragraph',
                               'text': ''.join(e.text or '' for e in element.iter('{' + NS['w'] + '}t'))})
            elif element.tag == '{' + NS['w'] + '}tbl':
                tables += 1
                rows = [[''.join(e.text or '' for e in cell.iter('{' + NS['w'] + '}t'))
                         for cell in row.findall('w:tc', NS)] for row in element.findall('w:tr', NS)]
                blocks.append({'id': f'T{tables:02d}', 'kind': 'table', 'rows': rows})
        require(not xml.findall('.//w:ins', NS) and not xml.findall('.//w:del', NS), 'Unaccounted revisions')
        require('word/comments.xml' not in archive.namelist(), 'Unaccounted comments')
        require(not any(p.startswith('word/media/') for p in archive.namelist()), 'Unaccounted image content')
        require(not any(e.tag.endswith('}oMath') for e in xml.iter()), 'Unaccounted native equations')
    require(paragraphs == transcript['paragraph_count'] == 115 and tables == transcript['table_count'] == 24,
            'Transcript coverage')
    require(blocks == transcript['blocks'], 'Transcript is not a complete ordered extraction')
    lookup = {b['id']: b for b in blocks}
    pilot = json.loads((root / 'legacy/damx/PILOT_001.json').read_text())
    require(pilot['source_id'] == SOURCE_ID and pilot['source_sha256'] == SOURCE_SHA, 'Pilot source')
    require(pilot['unit_count'] == len(pilot['units']) == 10 and pilot['scientific_status_promotion'] is False,
            'Pilot scope/status')
    require([u['unit_id'] for u in pilot['units']] == [f'LEG-U{i:02d}' for i in range(1, 11)], 'Unit coverage/order')
    for unit in pilot['units']:
        require(unit['source_id'] == SOURCE_ID, 'Unit source')
        location = unit['locator']
        if location.startswith('P'):
            parent = lookup[location]['text']
        else:
            table_id, row = location.split('/R')
            parent = lookup[table_id]['rows'][int(row) - 1][0]
        start, end = unit['l0_start'], unit['l0_end']
        require(type(start) is int and type(end) is int and 0 <= start < end <= len(parent), 'Invalid L0 bounds')
        require(parent[start:end] == unit['l0_original'] and unit['l0_original'], 'L0 span is not source-exact')
        for field in ('epistemic_type', 'l1_faithful_english', 'l2_decomposition', 'assumptions',
                      'formula_diagram_role', 'mechanism_status', 'evidence_citation_target', 'ambiguities',
                      'prior_art_collision_needed', 'l3_status', 'survival_assessment', 'integration_assessment',
                      'open_questions'):
            require(unit.get(field), f'Missing review field {field}')
    survival = [u['survival_assessment'] for u in pilot['units']]
    require(survival.count('S4_CANDIDATE_ONLY') == 2 and survival.count('S5_CANDIDATE_ONLY') == 1
            and survival.count('UNRESOLVED') == 7, 'Survival candidates changed without review')
    if (root / '.git').exists():
        relative = original.relative_to(root).as_posix()
        commits = subprocess.check_output(['git', 'log', '--reverse', '--format=%H', '--', relative], cwd=root).decode().splitlines()
        if commits:
            first = subprocess.check_output(['git', 'show', commits[0] + ':' + relative], cwd=root)
            require(first == data, 'Original differs from its first committed copy')


if __name__ == '__main__':
    validate(ROOT)
    print('PASS: preserved report bytes, all 115 paragraphs/24 tables and ten exact L0 spans; source fidelity only, no scientific validation.')
