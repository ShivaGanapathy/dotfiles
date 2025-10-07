#!/usr/bin/env python3
"""
Truly parallel Claude runner using subprocess.Popen for real concurrency.
Usage: python claude_parallel.py tasks.json
"""

import json
import subprocess
import tempfile
import time
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python claude_parallel.py tasks.json")
        sys.exit(1)

    # Load tasks
    with open(sys.argv[1]) as f:
        config = json.load(f)

    tasks = config['tasks']
    system_prompt = config['system_prompt']
    print(f"\n🚀 Running {len(tasks)} tasks in PARALLEL...\n")

    start_time = time.time()
    processes = []
    temp_files = []

    # Start ALL processes at once
    for task in tasks:
        task_id = task['task_id']
        prompt = task['prompt']

        # Create temp file for this task
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'_task{task_id}.txt') as f:
            temp_file = f.name
            temp_files.append((task_id, temp_file, prompt))

        # Build command
        cmd = ["claude", "--dangerously-skip-permissions", "--model", "sonnet", "--max-turns", "100"]
        if system_prompt:
            cmd.extend(["--append-system-prompt", system_prompt])
        cmd.extend(["-p", prompt])

        print(f"Task {task_id}: Launching...")

        # Start process WITHOUT waiting
        with open(temp_file, 'w') as outfile:
            proc = subprocess.Popen(cmd, stdout=outfile, stderr=subprocess.STDOUT)
            processes.append((task_id, proc))

    print(f"\n⚡ All {len(tasks)} processes launched! Waiting for completion...\n")

    # Wait for all processes to complete
    theoretical_sequential_time = 0
    results = []
    remaining = processes[:]
    while remaining:
        next_remaining = []
        for task_id, proc in remaining:
            rc = proc.poll()
            if rc is None:
                next_remaining.append((task_id, proc))
            else:
               elapsed = time.time() - start_time
               print(f"Task {task_id}: ✓ Done at {elapsed:.1f}s")
               theoretical_sequential_time += elapsed
        remaining = next_remaining
        if remaining:
            time.sleep(0.1)

    # Collect results
    for task_id, temp_file, prompt in temp_files:
        with open(temp_file, 'r') as f:
            output = f.read()
        results.append({
            'id': task_id,
            'prompt': prompt,
            'output': output.strip()
        })
        # Clean up temp file
        import os
        os.unlink(temp_file)

    total_time = time.time() - start_time

    # Save results
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n✅ All tasks completed in {total_time:.1f}s!")
    print(f"   Results saved to {output_file}")
    print(f"   (Sequential would have taken ~{theoretical_sequential_time}s)")

if __name__ == "__main__":
    main()
