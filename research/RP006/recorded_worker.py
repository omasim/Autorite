"""Single computation child. It cannot proceed without a parent guard lease."""
import importlib.util
import json
import os
from pathlib import Path
import resource
import sys


def no_network_or_children(event, args):
    if event.startswith(('socket.', 'subprocess.', 'os.system', 'os.exec', 'os.fork')):
        raise PermissionError('Recorded RP006 worker prohibits network and child processes')


def main(root, output):
    root, output = Path(root), Path(output)
    sys.path.insert(0, str(root))
    sys.addaudithook(no_network_or_children)
    spec = importlib.util.spec_from_file_location('rp006_recorded_producer', root / 'research/RP006/producer.py')
    producer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(producer)

    def guard():
        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        if sys.platform == 'darwin':
            rss = int(rss)
        elif sys.platform.startswith('linux'):
            rss = int(rss * 1024)
        else:
            raise RuntimeError('Unsupported worker RSS unit')
        sys.stdout.write('GUARD ' + str(rss) + '\n')
        sys.stdout.flush()
        answer = sys.stdin.readline()
        if answer != 'OK\n':
            raise RuntimeError('Parent supervisor revoked lease')

    domain = json.loads((root / 'research/RP006/DOMAIN.json').read_text())
    bundle = producer.produce(domain, guard)
    payload = json.dumps(bundle, sort_keys=True, indent=2, allow_nan=False) + '\n'
    guard()
    temporary = output / 'worker.json.partial'
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, output / 'worker.json')
    guard()


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
