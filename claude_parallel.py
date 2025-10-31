#!/usr/bin/env python3
"""
Truly parallel Claude runner using subprocess.Popen with configurable max parallelism.
Usage: python claude_parallel.py tasks.json [results.json]
"""

import json
import subprocess
import tempfile
import time
import sys
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: python claude_parallel.py tasks.json")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        config = json.load(f)

    tasks = config["tasks"]
    system_prompt = config.get("system_prompt", "")
    max_parallel = int(config.get("max_parallel", 50))

    print(f"\n🚀 Running {len(tasks)} tasks with max parallelism = {max_parallel}\n")

    start_time = time.time()
    processes = []
    results = []
    theoretical_sequential_time = 0.0
    prompt_lookup = {}
    task_started = {}

    def launch_task(task):
        task_id = task["task_id"]
        prompt = task["prompt"]
        prompt_lookup[task_id] = prompt
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_task{task_id}.txt") as f:
            temp_file = f.name
        cmd = ["claude", "--dangerously-skip-permissions", "--model", "haiku", "--max-turns", "25"]
        if system_prompt:
            cmd.extend(["--append-system-prompt", system_prompt])
        cmd.extend(["-p", prompt])
        print(f"Task {task_id}: Launching...")
        outfile = open(temp_file, "w")
        proc = subprocess.Popen(cmd, stdout=outfile, stderr=subprocess.STDOUT)
        processes.append((task_id, proc, outfile, temp_file))
        task_started[task_id] = time.time()

    next_index = 0
    try:
        while next_index < len(tasks) or processes:
            while next_index < len(tasks) and len(processes) < max_parallel:
                launch_task(tasks[next_index])
                next_index += 1

            if not processes:
                break

            still_running = []
            for task_id, proc, outfile, temp_file in processes:
                rc = proc.poll()
                if rc is None:
                    still_running.append((task_id, proc, outfile, temp_file))
                else:
                    outfile.flush()
                    outfile.close()
                    finished_at = time.time()
                    duration = finished_at - task_started.get(task_id, finished_at)
                    theoretical_sequential_time += duration
                    try:
                        with open(temp_file, "r") as f:
                            output = f.read()
                    except FileNotFoundError:
                        output = ""
                    results.append(
                        {
                            "id": task_id,
                            "prompt": prompt_lookup.get(task_id, ""),
                            "output": output.strip(),
                            "rc": int(rc),
                            "duration_sec": round(duration, 3),
                        }
                    )
                    try:
                        os.unlink(temp_file)
                    except FileNotFoundError:
                        pass
                    print(f"Task {task_id}: ✓ Done in {duration:.1f}s rc={rc}")
            processes = still_running

            if processes or next_index < len(tasks):
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted — terminating all subprocesses...")
        for _, proc, outfile, _ in processes:
            try:
                proc.terminate()
            except Exception:
                pass
            try:
                outfile.flush()
                outfile.close()
            except Exception:
                pass
        sys.exit(1)

    total_time = time.time() - start_time
    output_file = sys.argv[2] if len(sys.argv) > 2 else "results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n✅ All tasks completed in {total_time:.1f}s!")
    print(f"   Results saved to {output_file}")
    print(f"   (Sequential would have taken ~{theoretical_sequential_time:.1f}s)")

if __name__ == "__main__":
    main()

