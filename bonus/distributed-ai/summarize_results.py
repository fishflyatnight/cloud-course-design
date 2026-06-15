#!/usr/bin/env python3
"""Create report-ready DDP comparison artifacts from real CCE logs."""

from __future__ import annotations

import csv
import re
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "evidence" / "06_bonus" / "03_distributed_ai"
RESULT_PATTERN = re.compile(
    r"RESULT mode=(?P<mode>\w+).*?world_size=(?P<workers>\d+).*?"
    r"train_seconds=(?P<seconds>\d+\.\d+).*?accuracy=(?P<accuracy>\d+\.\d+)"
)


def read_result(filename: str) -> dict[str, str | float | int]:
    text = (EVIDENCE / filename).read_text(encoding="utf-8-sig")
    match = RESULT_PATTERN.search(text)
    if not match:
        raise ValueError(f"No RESULT line found in {filename}")
    return {
        "mode": match.group("mode"),
        "workers": int(match.group("workers")),
        "train_seconds": float(match.group("seconds")),
        "accuracy": float(match.group("accuracy")),
    }


single = read_result("single-result.txt")
ddp = read_result("ddp-rank0-result.txt")
speedup = float(single["train_seconds"]) / float(ddp["train_seconds"])
efficiency = speedup / int(ddp["workers"])

rows = [
    {**single, "speedup": 1.0, "parallel_efficiency": 1.0},
    {**ddp, "speedup": speedup, "parallel_efficiency": efficiency},
]

with (EVIDENCE / "performance-results.csv").open(
    "w", encoding="utf-8-sig", newline=""
) as handle:
    writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

plt.style.use("seaborn-v0_8-whitegrid")
fig, axes = plt.subplots(1, 2, figsize=(10, 4.4))
labels = ["Single worker", "2-worker DDP"]
colors = ["#4c78a8", "#f58518"]

axes[0].bar(labels, [row["train_seconds"] for row in rows], color=colors)
axes[0].set_ylabel("Training time (seconds)")
axes[0].set_title(f"MNIST CNN training time\nSpeedup = {speedup:.2f}x")
for index, row in enumerate(rows):
    axes[0].text(
        index,
        float(row["train_seconds"]) + 0.08,
        f'{float(row["train_seconds"]):.3f}s',
        ha="center",
    )

axes[1].bar(labels, [float(row["accuracy"]) * 100 for row in rows], color=colors)
axes[1].set_ylim(90, 100)
axes[1].set_ylabel("Accuracy (%)")
axes[1].set_title("Evaluation accuracy")
for index, row in enumerate(rows):
    axes[1].text(
        index,
        float(row["accuracy"]) * 100 + 0.12,
        f'{float(row["accuracy"]) * 100:.2f}%',
        ha="center",
    )

fig.suptitle("PyTorch DDP on Huawei Cloud CCE (real run)", fontsize=14)
fig.tight_layout()
fig.savefig(EVIDENCE / "performance-comparison.png", dpi=180, bbox_inches="tight")

print(
    f"single={single['train_seconds']:.6f}s, ddp={ddp['train_seconds']:.6f}s, "
    f"speedup={speedup:.4f}, efficiency={efficiency:.4f}"
)
