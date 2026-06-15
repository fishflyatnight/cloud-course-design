#!/usr/bin/env python3
"""Train a small MNIST CNN with one process or two-process PyTorch DDP."""

from __future__ import annotations

import argparse
import os
import time

import torch
import torch.distributed as dist
from torch import nn
from torch.nn.parallel import DistributedDataParallel
from torch.utils.data import DataLoader, DistributedSampler, Subset
from torchvision import datasets, transforms


class MnistCnn(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 16, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(32 * 7 * 7, 64),
            nn.ReLU(),
            nn.Linear(64, 10),
        )

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        return self.classifier(self.features(inputs))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("single", "ddp"), required=True)
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--train-samples", type=int, default=12000)
    parser.add_argument("--test-samples", type=int, default=2000)
    parser.add_argument("--batch-size", type=int, default=64)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    distributed = args.mode == "ddp"
    rank = int(os.environ.get("RANK", "0"))
    world_size = int(os.environ.get("WORLD_SIZE", "1"))

    torch.manual_seed(2026)
    torch.set_num_threads(1)

    if distributed:
        dist.init_process_group(backend="gloo", init_method="env://")

    transform = transforms.ToTensor()
    train_full = datasets.MNIST("/data", train=True, download=False, transform=transform)
    test_full = datasets.MNIST("/data", train=False, download=False, transform=transform)
    train_data = Subset(train_full, range(min(args.train_samples, len(train_full))))
    test_data = Subset(test_full, range(min(args.test_samples, len(test_full))))

    sampler = (
        DistributedSampler(
            train_data,
            num_replicas=world_size,
            rank=rank,
            shuffle=True,
            seed=2026,
        )
        if distributed
        else None
    )
    train_loader = DataLoader(
        train_data,
        batch_size=args.batch_size,
        sampler=sampler,
        shuffle=sampler is None,
        num_workers=0,
    )
    test_loader = DataLoader(test_data, batch_size=256, shuffle=False, num_workers=0)

    model: nn.Module = MnistCnn()
    if distributed:
        # DDP registers gradient hooks. During backward(), every parameter
        # gradient is AllReduced across ranks and divided by world_size, so
        # every worker applies the same globally averaged update.
        model = DistributedDataParallel(model)

    optimizer = torch.optim.SGD(model.parameters(), lr=0.08, momentum=0.9)
    loss_function = nn.CrossEntropyLoss()

    if distributed:
        dist.barrier()
    start = time.perf_counter()

    for epoch in range(args.epochs):
        if sampler is not None:
            sampler.set_epoch(epoch)
        model.train()
        loss_sum = 0.0
        examples = 0
        for inputs, labels in train_loader:
            optimizer.zero_grad(set_to_none=True)
            predictions = model(inputs)
            loss = loss_function(predictions, labels)
            loss.backward()
            optimizer.step()
            loss_sum += loss.item() * labels.size(0)
            examples += labels.size(0)
        print(
            f"EPOCH rank={rank} epoch={epoch + 1}/{args.epochs} "
            f"local_examples={examples} local_loss={loss_sum / examples:.6f}",
            flush=True,
        )

    if distributed:
        dist.barrier()
    train_seconds = time.perf_counter() - start

    model.eval()
    correct = torch.tensor(0, dtype=torch.long)
    total = torch.tensor(0, dtype=torch.long)
    with torch.no_grad():
        for inputs, labels in test_loader:
            predictions = model(inputs).argmax(dim=1)
            correct += (predictions == labels).sum()
            total += labels.numel()

    if distributed:
        # Evaluation is intentionally performed on every rank, then averaged
        # with AllReduce to demonstrate a second collective operation.
        dist.all_reduce(correct, op=dist.ReduceOp.SUM)
        dist.all_reduce(total, op=dist.ReduceOp.SUM)

    accuracy = correct.item() / total.item()
    print(
        f"RESULT mode={args.mode} rank={rank} world_size={world_size} "
        f"epochs={args.epochs} train_samples={len(train_data)} "
        f"train_seconds={train_seconds:.6f} accuracy={accuracy:.6f}",
        flush=True,
    )

    if distributed:
        dist.destroy_process_group()


if __name__ == "__main__":
    main()

