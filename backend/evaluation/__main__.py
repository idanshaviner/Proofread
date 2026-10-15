"""Run without network or credentials: python -m evaluation run --output /tmp/run.json."""
import argparse
import asyncio
import json
from pathlib import Path

from app.provider import MockProvider
from .runner import blind_comparison, evaluate


def write_json(path, value):
    # Avoid overwriting an existing evaluation or review artifact.
    with Path(path).open("x") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def main():
    parser = argparse.ArgumentParser(description="Synthetic-only offline evaluation")
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run", help="Run fixed mock; never reads provider environment")
    run.add_argument("--output", required=True)
    compare = commands.add_parser("compare", help="Prepare blind review and separate answer key")
    compare.add_argument("left")
    compare.add_argument("right")
    compare.add_argument("--output", required=True)
    compare.add_argument("--key", required=True)
    compare.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    if args.command == "run":
        report = asyncio.run(evaluate(MockProvider()))
        write_json(args.output, report)
        return int(report["summary"]["contract_pass"] != report["summary"]["cases"])
    if Path(args.output).resolve() == Path(args.key).resolve():
        parser.error("Review and key must use separate paths")
    try:
        review, key = blind_comparison(json.loads(Path(args.left).read_text()),
                                     json.loads(Path(args.right).read_text()), args.seed)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    # Check both destinations first to avoid a partial pair for ordinary misuse.
    if Path(args.output).exists() or Path(args.key).exists():
        parser.error("Review/key destinations must not already exist")
    write_json(args.output, review)
    write_json(args.key, key)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
