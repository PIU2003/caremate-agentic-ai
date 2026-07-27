"""Retrieval evaluation for CareMate RAG (5 queries)."""

from __future__ import annotations

import json
from pathlib import Path

from rag.pipeline import retrieve

EVAL_QUERIES = [
    {
        "query": "What should older adults know about high blood pressure?",
        "expected_sources": ["01_blood_pressure"],
    },
    {
        "query": "How can I prevent falls at home?",
        "expected_sources": ["05_fall_prevention"],
    },
    {
        "query": "Tips for taking medicine safely every day",
        "expected_sources": ["04_medication_safety"],
    },
    {
        "query": "Signs of low blood sugar and what to do",
        "expected_sources": ["02_blood_sugar"],
    },
    {
        "query": "When should I call emergency services for chest pain?",
        "expected_sources": ["03_heart_health", "20_emergency_red_flags"],
    },
]


def evaluate(top_k: int = 4) -> dict:
    rows = []
    hits = 0
    for item in EVAL_QUERIES:
        results = retrieve(item["query"], top_k=top_k)
        sources = [r.get("source", "") for r in results]
        matched = any(
            any(expected in source for source in sources)
            for expected in item["expected_sources"]
        )
        if matched:
            hits += 1
        rows.append(
            {
                "query": item["query"],
                "expected": item["expected_sources"],
                "retrieved_sources": sources,
                "scores": [round(r.get("score", 0.0), 4) for r in results],
                "hit": matched,
            }
        )
    return {
        "total_queries": len(EVAL_QUERIES),
        "hits": hits,
        "hit_rate": hits / len(EVAL_QUERIES),
        "results": rows,
    }


def main():
    report = evaluate()
    out = Path(__file__).resolve().parent.parent / "docs" / "rag_evaluation.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(
        f"Hit rate: {report['hits']}/{report['total_queries']} "
        f"({report['hit_rate']:.0%})"
    )
    for row in report["results"]:
        status = "HIT" if row["hit"] else "MISS"
        print(f"- [{status}] {row['query']}")
        print(f"  retrieved: {row['retrieved_sources']}")
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
