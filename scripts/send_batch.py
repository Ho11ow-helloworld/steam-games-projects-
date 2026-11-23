
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

BATCH_FILE = ROOT / "batch.csv"
PENDING_FILE = ROOT / "raw_data" / "pending_batch.txt"


def git(*args):
    subprocess.run(["git", *args], cwd=ROOT, check=True)


# Check that a batch is waiting
if not PENDING_FILE.exists():
    print("No pending batch to send.")

# Check that the batch file exists
elif not BATCH_FILE.exists():
    print("Batch file not found.")

else:
    # Only send batches from the main branch
    branch = subprocess.check_output(
        ["git", "branch", "--show-current"],
        cwd=ROOT,
        text=True
    ).strip()

    if branch != "main":
        print("Switch to the main branch before sending.")
    else:
        # Send the batch to GitHub
        git("add", "batch.csv")
        git("commit", "--only", "-m", "Add new Steam batch", "--", "batch.csv")
        git("push", "origin", "main")

        print("Batch sent to GitHub!")
        print("Check GitHub Actions before confirming progress.")
