#!/usr/bin/env python3
"""Profile the bounded pipeline on a separate 55-case synthetic stress domain.

This test generates synthetic event logs and synthetic answer artifacts only.
It never reads the proposed F4/F5 case inventory or outcome-bearing controls.
All files are temporary and removed on exit. macOS process-tree RSS is sampled
through libproc; inherited RLIMIT_FSIZE/RLIMIT_NOFILE/RLIMIT_CPU and a sampled
process-group RSS stop are applied. macOS does not expose a cgroups/prlimit
aggregate process-tree memory controller to this process, so the RSS stop is a
fail-closed sampled guard, not a kernel-enforced aggregate memory ceiling.
"""
from __future__ import annotations

import ctypes
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import resource
import signal
import struct
import subprocess
import sys
import tempfile
import time


ROOT = Path(__file__).resolve().parents[1]
TEMP_ROOT = Path("/private/tmp")
PYTHON = sys.executable
HASH_SEED = "0"
TREE_RSS_CAP = 512 * 1024 * 1024
FILE_SIZE_CAP = 640 * 1024 * 1024
NOFILE_CAP = 256
CPU_SECONDS_CAP = 1_800
WALL_SECONDS_CAP = 1_200
SAMPLE_INTERVAL = 0.025
TOPOLOGIES = {
    "F4": [
        [("root", (), ("a",)), ("copy", ("a",), ("b",)), ("fork", ("b",), ("c", "d"))],
        [("root", (), ("a",)), ("fork", ("a",), ("b", "c")), ("continue", ("b",), ("d",))],
        [("root", (), ("a",)), ("continue", ("a",), ("b",)), ("fork", ("b",), ("c", "d"))],
        [("root", (), ("a",)), ("root", (), ("b",)), ("continue", ("a",), ("c",)), ("merge", ("b", "c"), ("d",))],
    ],
    "F5": [
        [("root", (), ("a",)), ("copy", ("a",), ("b",)), ("continue", ("b",), ("c",)), ("fork", ("c",), ("d", "e"))],
        [("root", (), ("a",)), ("continue", ("a",), ("b",)), ("fork", ("b",), ("c", "d")), ("continue", ("c",), ("e",))],
        [("root", (), ("a",)), ("fork", ("a",), ("b", "c")), ("continue", ("b",), ("d",)), ("continue", ("d",), ("e",))],
        [("root", (), ("a",)), ("continue", ("a",), ("b",)), ("fork", ("b",), ("c", "d")), ("merge", ("c", "d"), ("e",))],
        [("root", (), ("a",)), ("fork", ("a",), ("b", "c")), ("merge", ("b", "c"), ("d",)), ("continue", ("d",), ("e",))],
    ],
}


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def event(kind: str, parents: tuple[str, ...], *outputs: tuple[str, str]) -> dict:
    return {"kind": kind, "parents": list(parents),
            "outputs": [{"id": ident, "state": state} for ident, state in outputs]}


def synthetic_domain(stratum: str, count: int) -> dict:
    """Create max-depth/max-branching valid logs with synthetic-only IDs."""
    if stratum not in TOPOLOGIES:
        raise ValueError("Unknown synthetic stratum")
    cases = []
    shapes = TOPOLOGIES[stratum]
    for index in range(count):
        shape = shapes[index % len(shapes)]
        state_by_id = {}
        events = []
        for event_index, (kind, parents, outputs) in enumerate(shape):
            output_values = []
            for output_index, ident in enumerate(outputs):
                if kind in {"copy", "fork"}:
                    value = state_by_id[parents[0]]
                else:
                    value = "ABC"[(index + event_index * 2 + output_index) % 3]
                state_by_id[ident] = value
                output_values.append((ident, value))
            events.append(event(kind, parents, *output_values))
        cases.append({"id": f"STRESS-{stratum}-{index + 1:02d}", "events": events})
    return {"cases": cases}


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def apply_inherited_limits() -> dict[str, tuple[int, int]]:
    """Apply portable per-process limits inherited by the whole worker tree."""
    requested = {
        resource.RLIMIT_FSIZE: FILE_SIZE_CAP,
        resource.RLIMIT_NOFILE: NOFILE_CAP,
        resource.RLIMIT_CPU: CPU_SECONDS_CAP,
    }
    applied = {}
    for key, ceiling in requested.items():
        old_soft, old_hard = resource.getrlimit(key)
        soft = min(ceiling, old_soft, old_hard)
        # Preserve the inherited hard limit; all requested limits are lowered.
        resource.setrlimit(key, (soft, old_hard))
        applied[str(key)] = resource.getrlimit(key)
    return applied


def proc_group_rss_bytes(pgid: int) -> tuple[int, int]:
    """Return (sum RSS bytes, process count) for a Darwin process group."""
    if sys.platform != "darwin":
        raise RuntimeError("This process-tree sampler currently supports macOS only")
    libproc = ctypes.CDLL("/usr/lib/libproc.dylib")
    list_pids = libproc.proc_listallpids
    list_pids.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
    list_pids.restype = ctypes.c_int
    pid_info = libproc.proc_pidinfo
    pid_info.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_uint64,
                         ctypes.c_void_p, ctypes.c_int]
    pid_info.restype = ctypes.c_int

    pids = (ctypes.c_int * 32768)()
    used = ctypes.c_int()
    count = list_pids(pids, ctypes.sizeof(pids), ctypes.byref(used))
    if count <= 0:
        raise RuntimeError("libproc did not return a process inventory")
    rss_total = 0
    member_count = 0
    for pid in pids[:count]:
        if pid <= 0:
            continue
        try:
            if os.getpgid(pid) != pgid:
                continue
        except ProcessLookupError:
            continue
        info = ctypes.create_string_buffer(256)
        copied = pid_info(pid, 4, 0, info, ctypes.sizeof(info))  # PROC_PIDTASKINFO
        if copied < 16:
            continue
        # proc_taskinfo begins with pti_virtual_size and pti_resident_size.
        rss_total += struct.unpack("=Q", info.raw[8:16])[0]
        member_count += 1
    return rss_total, member_count


def process_limits_preexec() -> None:
    apply_inherited_limits()


PRODUCER_WORKER = r'''import hashlib, importlib.util, json, pathlib, resource, sys, time
root, domain_path, out_path, witness_path, stratum = sys.argv[1:]
root=pathlib.Path(root); domain_path=pathlib.Path(domain_path)
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
domain=json.loads(domain_path.read_text(encoding="utf-8"))
producer=load("stress_producer",root/"research/RP006/producer.py")
writer=load("stress_writer",root/"research/preparation/finite_lineage_writer.py")
resources=load("stress_resources",root/"research/RP006/resources.py")
case_for_events={}
for c in domain["cases"]: case_for_events.setdefault(json.dumps(c["events"],sort_keys=True,separators=(",",":")),[]).append(c["id"])
construct_seconds={}; truth_seconds={}; graph_case={}
original_construct=producer.lineage.construct
def timed_construct(events):
 start=time.perf_counter(); graph=original_construct(events); elapsed=time.perf_counter()-start
 case=case_for_events[json.dumps(events,sort_keys=True,separators=(",",":"))].pop(0)
 construct_seconds[case]=construct_seconds.get(case,0.0)+elapsed; graph_case[id(graph)]=case; return graph
producer.lineage.construct=timed_construct
original_truth=producer.lineage.truth
def timed_truth(graph,query):
 start=time.perf_counter(); value=original_truth(graph,query); elapsed=time.perf_counter()-start
 case=graph_case[id(graph)]; truth_seconds[case]=truth_seconds.get(case,0.0)+elapsed; return value
producer.lineage.truth=timed_truth
guard=resources.Guard(seconds=1200,memory_bytes=128*1024*1024)
sink=writer.CappedJsonlSink(witness_path,guard=guard)
started=time.perf_counter()
try:
 bundle=producer.produce(domain,guard=guard,retain_conflicts=False,conflict_sink=sink,stratum=stratum)
except BaseException:
 sink.close(complete=False); raise
rows,bytes_written=sink.close(complete=True)
pathlib.Path(out_path).write_text(json.dumps(bundle,sort_keys=True,separators=(",",":"),allow_nan=False),encoding="utf-8")
metrics={case:{"graph_construct_seconds":construct_seconds.get(case,0.0),"truth_query_seconds":truth_seconds.get(case,0.0),"measured_case_work_seconds":construct_seconds.get(case,0.0)+truth_seconds.get(case,0.0)} for case in sorted(c["id"] for c in domain["cases"])}
print(json.dumps({"status":"PASS","stratum":stratum,"case_count":len(domain["cases"]),"conflict_rows":rows,"conflict_bytes":bytes_written,"producer_total_seconds":time.perf_counter()-started,"per_case":metrics,"limits":{"nofile":resource.getrlimit(resource.RLIMIT_NOFILE),"fsize":resource.getrlimit(resource.RLIMIT_FSIZE),"cpu":resource.getrlimit(resource.RLIMIT_CPU)},"candidate_inputs_read":False,"candidate_answers_generated":False},sort_keys=True))
'''


DRIVER = r'''import hashlib, importlib.util, json, pathlib, resource, subprocess, sys, time
root, temp, worker_path = map(pathlib.Path,sys.argv[1:]); temp.mkdir(exist_ok=True)
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
verifier=load("stress_verifier",root/"research/RP006/verifier.py")
writer=load("stress_writer_parent",root/"research/preparation/finite_lineage_writer.py")
resources=load("stress_resources_parent",root/"research/RP006/resources.py")
harness=load("stress_domain_builder",root/"scripts/check-finite-lineage-55-case-synthetic-stress.py")
base_rebuild=verifier.log.rebuild
base_evaluate=verifier.log.evaluate
domains={"F4":(17,4,harness.synthetic_domain("F4",17)),"F5":(38,5,harness.synthetic_domain("F5",38))}
reports=[]
for stratum,(case_count,entity_count,domain) in domains.items():
 domain_path=temp/(stratum+"-domain.json"); bundle_path=temp/(stratum+"-bundle.json"); witness_path=temp/(stratum+"-conflicts.jsonl");
 domain_path.write_text(json.dumps(domain,sort_keys=True),encoding="utf-8")
 # The actual worker body is passed by the outer checker and saved once beside the script.
 worker=worker_path.read_text(encoding="utf-8")
 child_started=time.perf_counter()
 child=subprocess.run([sys.executable,"-c",worker,str(root),str(domain_path),str(bundle_path),str(witness_path),stratum],capture_output=True,text=True,check=False,env={**__import__("os").environ,"PYTHONHASHSEED":"0"})
 child_elapsed=time.perf_counter()-child_started
 if child.returncode: raise RuntimeError("producer worker failed: "+child.stderr[-4000:])
 producer_record=json.loads(child.stdout.strip().splitlines()[-1]); bundle=json.loads(bundle_path.read_text(encoding="utf-8"))
 case_ids={}
 for c in domain["cases"]: case_ids.setdefault(json.dumps(c["events"],sort_keys=True,separators=(",",":")),[]).append(c["id"])
 replay_graph_case={}; rebuild_seconds={}; evaluate_seconds={}
 verifier.log.rebuild=base_rebuild; verifier.log.evaluate=base_evaluate
 def timed_rebuild(events,_original=base_rebuild):
  start=time.perf_counter(); graph=_original(events); elapsed=time.perf_counter()-start
  case=case_ids[json.dumps(events,sort_keys=True,separators=(",",":"))].pop(0); rebuild_seconds[case]=rebuild_seconds.get(case,0.0)+elapsed; replay_graph_case[id(graph)]=case; return graph
 verifier.log.rebuild=timed_rebuild
 def timed_evaluate(graph,query,_original=base_evaluate):
  start=time.perf_counter(); result=_original(graph,query); elapsed=time.perf_counter()-start
  case=replay_graph_case[id(graph)]; evaluate_seconds[case]=evaluate_seconds.get(case,0.0)+elapsed; return result
 verifier.log.evaluate=timed_evaluate
 verify_started=time.perf_counter()
 receipt=verifier.verify_bounded(bundle,witness_path,domain,guard=resources.Guard(seconds=1200,memory_bytes=128*1024*1024),stratum=stratum)
 verify_elapsed=time.perf_counter()-verify_started
 if receipt.get("status")!="PASS": raise RuntimeError("bounded verifier failed")
 oversized=temp/(stratum+"-oversized-row.jsonl"); oversized.write_bytes(b"x"*449+b"\n")
 verifier.log.rebuild=base_rebuild; verifier.log.evaluate=base_evaluate
 try: verifier.verify_bounded(bundle,oversized,domain,guard=resources.Guard(seconds=30,memory_bytes=128*1024*1024),stratum=stratum)
 except ValueError as exc:
  if "byte cap" not in str(exc): raise
 else: raise RuntimeError("independent verifier accepted an over-cap conflict row")
 source_paths=[root/"research/RP006/producer.py",root/"research/RP006/verifier.py",root/"research/preparation/finite_lineage_writer.py",root/"scripts/check-finite-lineage-55-case-synthetic-stress.py"]
 source_hashes={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths}
 write_started=time.perf_counter()
 package=writer.write_bundle(temp/(stratum+"-package"),domain,bundle,receipt,source_hashes,stratum=stratum,source_commit=__import__("subprocess").check_output(["git","rev-parse","HEAD"],cwd=root,text=True).strip(),guard=resources.Guard(seconds=1200,memory_bytes=128*1024*1024),conflicts_path=witness_path)
 write_elapsed=time.perf_counter()-write_started
 per_case={}
 for case in sorted(c["id"] for c in domain["cases"]):
  per_case[case]={"verifier_rebuild_seconds":rebuild_seconds.get(case,0.0),"verifier_truth_query_seconds":evaluate_seconds.get(case,0.0),"verifier_measured_case_work_seconds":rebuild_seconds.get(case,0.0)+evaluate_seconds.get(case,0.0),"producer_graph_construct_seconds":producer_record["per_case"][case]["graph_construct_seconds"],"producer_truth_query_seconds":producer_record["per_case"][case]["truth_query_seconds"],"producer_measured_case_work_seconds":producer_record["per_case"][case]["measured_case_work_seconds"]}
 if len(per_case)!=case_count or (receipt["counts"]["cases"],receipt["counts"]["entities"])!=(case_count,entity_count): raise RuntimeError("stratum inventory mismatch")
 signatures=set(); maximum_depth=0; maximum_branching=0
 for case in domain["cases"]:
  parents={}; children={}
  signature=[]
  for operation in case["events"]:
   ids=tuple(output["id"] for output in operation["outputs"])
   signature.append((operation["kind"],tuple(operation["parents"]),ids))
   for ident in ids:
    parents[ident]=tuple(operation["parents"])
    children.setdefault(ident,0)
   for parent in operation["parents"]: children[parent]=children.get(parent,0)+len(ids)
  memo={}
  def depth(node):
   if node not in memo: memo[node]=0 if not parents[node] else 1+max(depth(parent) for parent in parents[node])
   return memo[node]
  maximum_depth=max(maximum_depth,max(depth(node) for node in parents))
  maximum_branching=max(maximum_branching,max(children.values()))
  signatures.add(tuple(signature))
 reports.append({"stratum":stratum,"cases":case_count,"entities":entity_count,"unique_structural_topologies":len(signatures),"maximum_depth_edges":maximum_depth,"maximum_out_degree":maximum_branching,"producer_worker_wall_seconds":producer_record["producer_total_seconds"],"producer_subprocess_wall_seconds":child_elapsed,"verifier_wall_seconds":verify_elapsed,"writer_wall_seconds":write_elapsed,"conflict_rows":producer_record["conflict_rows"],"conflict_bytes":producer_record["conflict_bytes"],"package_bytes":package["total_bytes"],"summary_counts":receipt["counts"],"per_case_work_seconds":per_case})
print(json.dumps({"status":"PASS","reports":reports,"candidate_inputs_read":False,"candidate_answers_generated":False,"synthetic_answer_artifacts_created_and_removed":True},sort_keys=True))
'''


def darwin_sample_self_test() -> None:
    total, count = proc_group_rss_bytes(os.getpgid(os.getpid()))
    if total <= 0 or count <= 0:
        raise RuntimeError("Could not measure the current process group through libproc")


def run_limited_worker(temp: Path) -> dict:
    worker_path = temp / "producer-worker.py"
    driver_path = temp / "driver.py"
    worker_path.write_text(PRODUCER_WORKER, encoding="utf-8")
    driver_path.write_text(DRIVER, encoding="utf-8")
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = HASH_SEED
    guard = load("stress_execution_guard", ROOT / "scripts/check-finite-lineage-execution-guard.py")
    supervised = guard.supervise(
        [PYTHON, str(driver_path), str(ROOT), str(temp), str(worker_path)],
        timeout_seconds=WALL_SECONDS_CAP,
        environment=env,
        resource_limits={"RLIMIT_FSIZE": FILE_SIZE_CAP,
                         "RLIMIT_NOFILE": NOFILE_CAP,
                         "RLIMIT_CPU": CPU_SECONDS_CAP},
        max_process_group_rss_bytes=TREE_RSS_CAP,
        sample_interval=SAMPLE_INTERVAL,
    )
    if supervised["status"] != "COMPLETE":
        raise RuntimeError(f"Synthetic stress stopped: {supervised['reason']}; peak RSS={supervised['process_group_peak_rss_bytes']}; {supervised['stderr'][-2000:]}")
    lines = supervised["stdout"].splitlines()
    if not lines:
        raise RuntimeError("Synthetic stress worker returned no report")
    report = json.loads(lines[-1])
    if report.get("status") != "PASS":
        raise RuntimeError("Synthetic stress worker did not pass")
    report["process_tree"] = {
        "sampled_peak_rss_bytes": supervised["process_group_peak_rss_bytes"],
        "sample_interval_seconds": SAMPLE_INTERVAL,
        "peak_process_count": supervised["process_group_peak_members"],
        "sample_count": supervised["process_group_rss_samples"],
        "rss_cap_bytes": TREE_RSS_CAP,
        "sampler": "Darwin libproc PROC_PIDTASKINFO; RSS summed across the isolated process group",
    }
    report["host_controls"] = {
        "pythonhashseed": HASH_SEED,
        "rlimit_fsize_bytes_per_file": FILE_SIZE_CAP,
        "rlimit_nofile": NOFILE_CAP,
        "rlimit_cpu_seconds_per_process": CPU_SECONDS_CAP,
        "process_group_wall_timeout_seconds": WALL_SECONDS_CAP,
        "process_group_termination": "SIGTERM then SIGKILL",
        "memory_limit": "sampled process-group RSS stop; macOS sandbox did not permit finite RLIMIT_AS; no cgroups v2 on this host",
    }
    report["temporary_artifacts_removed"] = True
    return report


def main() -> None:
    if sys.platform != "darwin":
        raise RuntimeError("This measurement implementation is scoped to the current macOS host")
    if sys.version_info[:3] != (3, 12, 13):
        raise RuntimeError(f"Expected Python 3.12.13; found {sys.version.split()[0]}")
    if shutil_disk_free(TEMP_ROOT) < 2 * 1024**3:
        raise RuntimeError("Need at least 2 GiB free under /private/tmp")
    darwin_sample_self_test()
    with tempfile.TemporaryDirectory(prefix="autorite-lineage-55-stress-", dir=TEMP_ROOT) as name:
        result = run_limited_worker(Path(name))
    result["python"] = sys.version.split()[0]
    result["platform"] = sys.platform
    result["status"] = "PASS"
    if len(sys.argv) > 1:
        output_path = Path(sys.argv[1])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    concise = {key: value for key, value in result.items() if key != "reports"}
    concise["strata"] = [{key: value for key, value in item.items() if key not in {"summary_counts", "per_case_work_seconds"}}
                         | {"conflict_rows": item["conflict_rows"], "package_bytes": item["package_bytes"]}
                         for item in result["reports"]]
    print(json.dumps(concise, sort_keys=True))


def shutil_disk_free(path: Path) -> int:
    return os.statvfs(path).f_bavail * os.statvfs(path).f_frsize


if __name__ == "__main__":
    main()
