
import subprocess
import sys
import time
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
REPO = "Ho11ow-helloworld/steam-games-projects-"

NUMBER_OF_BATCHES = 3

def run_script(name, *args):
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / name), *args],
        cwd=ROOT,
        check=True
    )

def git(*args):
    return subprocess.check_output(
        ["git", *args], cwd=ROOT, text=True
    ).strip()

if git("branch", "--show-current") != "main":
    sys.exit("Please switch to main first.")

if (ROOT / "raw_data" / "pending_batch.txt").exists():
    sys.exit("A previous batch is still pending.")

for i in range(NUMBER_OF_BATCHES):
    print(f"\n=== BATCH {i + 1} ===", flush=True)

    # 1. Generate batch
    run_script("batch_sim.py")

    pending = ROOT / "raw_data" / "pending_batch.txt"
    if not pending.exists():
        print("No more batches to process.")
        break

    # 2. Send to GitHub
    run_script("send_batch.py")
    commit = git("rev-parse", "HEAD")

    # 3. Check GitHub Actions
    url = (
        f"https://api.github.com/repos/{REPO}/actions/"
        f"workflows/batch_pipeline.yml/runs"
        f"?head_sha={commit}&per_page=5"
    )

    success = False

    for attempt in range(20):
        request = Request(
            url, headers={"User-Agent": "Steam-Project"}
        )

        with urlopen(request, timeout=15) as response:
            runs = json.load(response)["workflow_runs"]

        for workflow in runs:
            if workflow["head_sha"] != commit:
                continue

            if workflow["status"] == "completed":
                if workflow["conclusion"] != "success":
                    sys.exit("GitHub Actions failed. Batch not confirmed.")

                success = True
                break

        if success:
            break

        print("Waiting for GitHub Actions...", flush=True)
        time.sleep(15)

    if not success:
        sys.exit("Workflow not confirmed. Batch remains pending.")

    # 4. Confirm only after success
    run_script("batch_sim.py", "confirm")
    print("Batch successfully processed and confirmed!")
