# Minimal reference for background generation and factual annotation in new domains.

import argparse
from datetime import date
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROMPTS = {
    "background": "domain_background_context_construction_prompt.txt",
    "extraction": "event_extraction_prompt.txt",
    "composition": "scenario_composition_prompt.txt",
    "review": "source_and_semantic_review_prompt.txt",
}


def call(client, model, stage, inputs):
    prompt = (HERE / PROMPTS[stage]).read_text(encoding="utf-8")
    response = client.responses.create(
        model=model,
        instructions=prompt + "\nReturn a JSON object using the OUTPUT fields.",
        input=json.dumps(inputs, ensure_ascii=False),
        text={"format": {"type": "json_object"}},
        store=False,
    )
    if response.status != "completed" or not response.output_text:
        raise ValueError(f"{stage}: incomplete or refused response")
    return json.loads(response.output_text)


def build_background(client, model, packet):
    inputs = {key: packet[key] for key in (
        "target_definition", "units", "reference_documents"
    )}
    if not inputs["reference_documents"]:
        raise ValueError("Supply reference documents")
    result = call(client, model, "background", inputs)
    return {**inputs, "status": "draft", "result": result}


def freeze_background(background):
    if background["status"] != "draft":
        raise ValueError("Review a draft before freezing it")
    result = background["result"]
    if not result["background_text"] or not result["mechanism_map"]:
        raise ValueError("Background text and mechanisms are required")
    if result.get("unresolved_items") or any(m.get("unresolved_items") for m in result["mechanism_map"]):
        raise ValueError("Resolve background issues before freezing")
    return {**background, "status": "frozen"}


def annotate(client, model, background, packet):
    if background["status"] != "frozen":
        raise ValueError("Review and freeze the background first")
    interval = {key: packet["forecast_interval"][key] for key in ("start", "end")}
    start, end = (date.fromisoformat(interval[key]) for key in ("start", "end"))
    if end < start:
        raise ValueError("Invalid forecast interval")
    common = {
        "target_definition": background["target_definition"],
        "units": background["units"],
        "domain_background": background["result"],
        "forecast_interval": interval,
        "scope": packet["scope"],
    }
    result = {"candidate_id": packet["candidate_id"], "status": "HOLD_SAMPLE", "scenario_text": None}
    extraction = call(client, model, "extraction", {**common, "source_passages": packet["source_passages"]})
    result["extraction"] = extraction
    events = [event for event in extraction.get("extracted_events", [])
              if event.get("support_status") != "UNRESOLVED"
              and not event.get("unresolved_items") and not event.get("conflicting_evidence")]
    if extraction["evidence_status"] == "INSUFFICIENT" or not events:
        return result
    composition = call(client, model, "composition", {**common, "source_supported_events": events})
    result["composition"] = composition
    if (composition["status"] == "HOLD_SAMPLE" or not composition.get("scenario_text")
            or not 1 <= len(composition.get("selected_event_ids", [])) <= 2):
        return result
    review = call(client, model, "review", {
        **common,
        "proposed_scenario": composition,
        "source_supported_events": extraction["extracted_events"],
        "source_passages": packet["source_passages"],
    })
    result["review"] = review
    # PASS reflects automated review; verify source support and ID links before accepting the scenario.
    claims = review.get("claim_verdicts", [])
    if (review["verdict"] == "PASS" and not review.get("required_corrections")
            and not review.get("unresolved_items") and claims
            and all(claim.get("verdict") == "PASS" for claim in claims)):
        result.update(status="PASS", scenario_text=composition["scenario_text"])
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=("background", "freeze-background", "factual"))
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--background", type=Path)
    parser.add_argument("--model")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Choose a new output file")
    if args.stage != "factual" and args.output.with_suffix(".txt").exists():
        parser.error("Choose a new output path for the review TXT")
    if args.stage == "factual" and not args.background:
        parser.error("factual requires --background")
    if args.stage != "freeze-background" and not args.model:
        parser.error("API stages require --model")
    packet = json.loads(args.input.read_text(encoding="utf-8"))
    if args.stage == "freeze-background":
        result = freeze_background(packet)
    else:
        from openai import OpenAI
        client = OpenAI()
        result = (build_background(client, args.model, packet) if args.stage == "background" else
                  annotate(client, args.model, json.loads(args.background.read_text(encoding="utf-8")), packet))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    if args.stage != "factual":
        preview = args.output.with_suffix(".txt")
        with preview.open("x", encoding="utf-8") as stream:
            stream.write(result["result"]["background_text"] + "\n\n")
            stream.write(json.dumps({key: value for key, value in result["result"].items()
                                     if key != "background_text"}, ensure_ascii=False, indent=2) + "\n")
    print(args.output)


if __name__ == "__main__":
    main()
