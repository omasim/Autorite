"""Project one validated manifest; archived and current Cycles stay distinct."""
from html import escape


def view(manifest):
    return {'number': f'{manifest["cycle_number"]:02d}', 'title': manifest['title'],
            'status': manifest['status'], 'obligations': [o['description'] for o in manifest['obligations']],
            'resolved_keys': [i for i, o in enumerate(manifest['obligations']) if o['resolved']]}


def fraction(manifest):
    obligations = manifest['obligations']
    return sum(o['weight'] for o in obligations if o['resolved']) / sum(o['weight'] for o in obligations)


def completion(manifest):
    return (f'{sum(o["resolved"] for o in manifest["obligations"])} / '
            f'{len(manifest["obligations"])} obligations resolved ({fraction(manifest)*100:.1f}%).')


def ring(manifest):
    number = f'{manifest["cycle_number"]:02d}'
    label = escape(f'Cycle {number}: {manifest["status"]}, {completion(manifest)}', quote=True)
    return (f'<div class="cycle-ring" role="img" aria-label="{label}">'
            '<svg class="cycle-graphic" viewBox="0 0 100 100" aria-hidden="true">'
            '<circle class="cycle-track" cx="50" cy="50" r="46" fill="none" stroke="currentColor" stroke-width="5"/>'
            f'<circle class="cycle-progress" cx="50" cy="50" r="46" fill="none" stroke="currentColor" stroke-width="5" '
            f'pathLength="100" stroke-dasharray="{fraction(manifest)*100} 100" transform="rotate(-90 50 50)"/>'
            '<circle class="cycle-start" cx="50" cy="4" r="2.5" fill="currentColor"/>'
            f'</svg><span>{number}</span></div>')
