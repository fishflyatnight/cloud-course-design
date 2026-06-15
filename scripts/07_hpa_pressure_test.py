#!/usr/bin/env python3
import argparse
import concurrent.futures
import json
import time
import urllib.error
import urllib.request


def request_once(url: str, timeout: float) -> tuple[bool, float, str]:
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
            ok = response.status == 200
            return ok, time.perf_counter() - started, body[:200]
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return False, time.perf_counter() - started, str(exc)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Concurrent /api/ping pressure tool")
    parser.add_argument(
        "--url",
        default="http://[ELB_IP]/api/ping",
        help="Target URL, for example http://1.2.3.4/api/ping",
    )
    parser.add_argument("--requests", type=int, default=10000, help="Total requests")
    parser.add_argument("--concurrency", type=int, default=200, help="Worker threads")
    parser.add_argument("--timeout", type=float, default=5.0, help="Per-request timeout")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if "[ELB_IP]" in args.url:
        raise SystemExit("Replace [ELB_IP] or pass --url before running the pressure test.")
    if args.requests < 1 or args.concurrency < 1:
        raise SystemExit("--requests and --concurrency must both be positive.")

    started = time.perf_counter()
    successes = 0
    latencies: list[float] = []
    first_error = None

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=args.concurrency
    ) as executor:
        futures = [
            executor.submit(request_once, args.url, args.timeout)
            for _ in range(args.requests)
        ]
        for future in concurrent.futures.as_completed(futures):
            ok, latency, detail = future.result()
            latencies.append(latency)
            if ok:
                successes += 1
            elif first_error is None:
                first_error = detail

    elapsed = time.perf_counter() - started
    result = {
        "url": args.url,
        "requests": args.requests,
        "concurrency": args.concurrency,
        "successes": successes,
        "failures": args.requests - successes,
        "elapsed_seconds": round(elapsed, 3),
        "requests_per_second": round(args.requests / elapsed, 3) if elapsed else None,
        "mean_latency_ms": round(sum(latencies) / len(latencies) * 1000, 3),
        "max_latency_ms": round(max(latencies) * 1000, 3),
        "first_error": first_error,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

