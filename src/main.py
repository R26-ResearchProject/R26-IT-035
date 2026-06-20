"""CLI entrypoint for the recommendation module."""

import argparse
import json
from pathlib import Path

from data_loader import load_json, load_knowledge_base, validate_input
from recommendation_engine import RecommendationEngine


def run(input_path: Path, output_path: Path, top_k: int) -> None:
    """Run recommendation pipeline from input JSON to output JSON."""
    base_dir = Path(__file__).resolve().parent.parent
    data_dir = base_dir / "data"

    user_input = load_json(input_path)
    validate_input(user_input)

    knowledge_base = load_knowledge_base(data_dir)
    engine = RecommendationEngine(knowledge_base)
    output = engine.generate(user_input, top_k=top_k)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(output, file, indent=2)

    grouped = output.get("recommendations_by_category", {})
    total_recommendations = sum(len(items) for items in grouped.values())
    print(f"Output written to: {output_path}")
    print(f"Status: {output['status']}")
    print(f"Recommendations returned: {total_recommendations}")


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Prakriti-aware lifestyle, diet, and home-care recommendation engine"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("sample_input.json"),
        help="Path to JSON input payload",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("sample_output.json"),
        help="Path to output JSON file",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Maximum number of recommendations to return",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run(args.input, args.output, args.top_k)
