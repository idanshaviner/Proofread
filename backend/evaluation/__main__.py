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
    summarize = commands.add_parser("summarize", help="Validate blinded ratings and count preferences")
    summarize.add_argument("review")
    summarize.add_argument("left")
    summarize.add_argument("right")
    summarize.add_argument("--key")
    summarize.add_argument("--seed", type=int, default=0)
    summarize.add_argument("--output", required=True)
    args = parser.parse_args()
    if args.command == "run":
        report = asyncio.run(evaluate(MockProvider()))
        write_json(args.output, report)
        return int(report["summary"]["contract_pass"] != report["summary"]["cases"])
    if args.command == "summarize":
        from .reviews import summarize_review

        if Path(args.output).exists():
            parser.error("Summary output already exists; overwrite is not supported")
        try:
            key = json.loads(Path(args.key).read_text()) if args.key else None
            if args.key and not isinstance(key, dict):
                raise ValueError("Invalid comparison key")
            summary = summarize_review(
                json.loads(Path(args.review).read_text()),
                json.loads(Path(args.left).read_text()),
                json.loads(Path(args.right).read_text()),
                seed=args.seed,
                key=key,
            )
        except (ValueError, OSError):
            parser.error("Invalid review or source artifacts; check originals, ratings, seed and key")
        try:
            write_json(args.output, summary)
        except OSError:
            parser.error("Cannot create summary output; existing files are never overwritten")
        return 0
    if Path(args.output).resolve() == Path(args.key).resolve():
        parser.error("Review and key must use separate paths")
    try:
        review, key = blind_comparison(json.loads(Path(args.left).read_text()),
                                     json.loads(Path(args.right).read_text()), args.seed)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    from .artifacts import write_review_pair

    try:
        write_review_pair(args.output, review, args.key, key)
    except (ValueError, OSError):
        parser.error("Cannot create review/key pair; check distinct writable paths and existing files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
