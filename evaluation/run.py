"""Run with python -m evaluation.run {infer,score} from the repository root."""

import argparse
import copy
import json
from pathlib import Path

from .data import load_benchmark, numeric_series
from .metrics import evaluate
from .relations import DOMAINS

DEFAULT_DATA = Path(__file__).resolve().parents[1] / "data"


def write_json(path, value):
    with path.open("w", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")


def read_predictions(path, requests):
    predictions = {}
    if not path.exists():
        return predictions
    with path.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            row = json.loads(line)
            key = row["request_id"]
            if key not in requests or key in predictions:
                raise ValueError(f"{path}:{line_number}: unknown or duplicate request ID {key}")
            predictions[key] = numeric_series(row["forecast"], key, requests[key]["horizon"])
    return predictions


def infer(args):
    benchmark = load_benchmark(args.data_dir, args.domains, args.limit)
    config = {"backend": args.backend, "model": args.model,
              "domains": args.domains, "limit": args.limit,
              "moirai_repo": str(args.moirai_repo.resolve()) if args.moirai_repo else None}
    run_dir = args.run_dir
    benchmark_path, config_path = run_dir / "benchmark.json", run_dir / "config.json"
    if args.resume:
        saved_benchmark = json.loads(benchmark_path.read_text(encoding="utf-8"))
        saved_config = json.loads(config_path.read_text(encoding="utf-8"))
        if benchmark != saved_benchmark or config != saved_config:
            raise ValueError("Resume requires the same data, subset, and model configuration")
    elif run_dir.exists():
        raise ValueError(f"{run_dir} already exists; use --resume or choose a new directory")

    prediction_path = run_dir / "predictions.jsonl"
    predictions = read_predictions(prediction_path, benchmark["requests"])
    pending = [(key, inputs) for key, inputs in benchmark["requests"].items() if key not in predictions]
    print(f"{len(benchmark['requests'])} unique requests; {len(pending)} remaining", flush=True)
    if pending:
        if args.backend == "gpt-4o":
            from .LLMs import GPT4o
            model = GPT4o(args.model)
        elif args.backend == "moirai-agent":
            from .CAF import MoiraiAgent
            model = MoiraiAgent(args.moirai_repo, llm_model=args.model)
        else:
            from .LLMs import Naive
            model = Naive()
    if not args.resume:
        run_dir.mkdir(parents=True)
        write_json(benchmark_path, benchmark)
        write_json(config_path, config)
    with prediction_path.open("a", encoding="utf-8") as stream:
        for index, (key, inputs) in enumerate(pending, len(predictions) + 1):
            # Only these four input fields reach either model adapter.
            forecast = model.predict(**copy.deepcopy(inputs))
            values = numeric_series(forecast, key, inputs["horizon"])
            stream.write(json.dumps({"request_id": key, "forecast": values}, allow_nan=False) + "\n")
            stream.flush()
            if index == 1 or index % 25 == 0 or index == len(benchmark["requests"]):
                print(f"Saved {index}/{len(benchmark['requests'])} forecasts", flush=True)
    print(f"Predictions saved to {prediction_path}")


def score(args):
    benchmark = json.loads((args.run_dir / "benchmark.json").read_text(encoding="utf-8"))
    config = json.loads((args.run_dir / "config.json").read_text(encoding="utf-8"))
    predictions = read_predictions(args.run_dir / "predictions.jsonl", benchmark["requests"])
    report = evaluate(benchmark, predictions, restraint_tolerance=args.restraint_tolerance)
    report["config"] = config
    write_json(args.run_dir / "metrics.json", report)
    print(json.dumps({domain: {kind: {key: value for key, value in result.items() if key != "details"}
                             for kind, result in values.items()}
                      for domain, values in report["domains"].items()}, indent=2))
    print(f"Full report saved to {args.run_dir / 'metrics.json'}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    inference = commands.add_parser("infer", help="Load data and save model forecasts")
    inference.add_argument("--data-dir", type=Path, default=DEFAULT_DATA)
    inference.add_argument("--domains", nargs="+", choices=DOMAINS, default=list(DOMAINS))
    inference.add_argument("--limit", type=int, help="First N anchors/sets per comparison and domain")
    inference.add_argument("--backend", choices=("gpt-4o", "moirai-agent", "naive"), required=True)
    inference.add_argument("--model", default="gpt-4o", help="LLM ID for GPT-4o or MoiraiAgent")
    inference.add_argument("--moirai-repo", type=Path, help="Official uni2ts checkout or ctx_forecast directory")
    inference.add_argument("--run-dir", type=Path, required=True)
    inference.add_argument("--resume", action="store_true")
    scoring = commands.add_parser("score", help="Evaluate a complete saved run without API calls")
    scoring.add_argument("--run-dir", type=Path, required=True)
    scoring.add_argument("--restraint-tolerance", type=float,
                         help="Optional maximum path MAE from neutral, in native domain units")
    args = parser.parse_args()
    if args.command == "infer" and args.backend == "moirai-agent" and not args.moirai_repo:
        parser.error("moirai-agent requires --moirai-repo")
    try:
        (infer if args.command == "infer" else score)(args)
    except (ValueError, KeyError, OSError, ImportError) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    main()
