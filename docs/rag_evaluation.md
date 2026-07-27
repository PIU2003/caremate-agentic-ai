# RAG Retrieval Evaluation

Command:

```bash
python -m rag.build_index
python -m rag.evaluate
```

## Summary

| Metric | Result |
|--------|--------|
| Queries | 5 |
| Hits | 5 |
| Hit rate | **100%** |

Machine-readable output: [`rag_evaluation.json`](rag_evaluation.json)

## Query results

| Query | Hit? | Top retrieved sources |
|-------|------|------------------------|
| High blood pressure guidance | Yes | `01_blood_pressure.txt`, ... |
| Prevent falls at home | Yes | `05_fall_prevention.txt`, ... |
| Medicine safety tips | Yes | `04_medication_safety.txt`, ... |
| Low blood sugar signs | Yes | `02_blood_sugar.txt`, ... |
| Chest pain / call emergency | Yes | `20_emergency_red_flags.txt`, `03_heart_health.txt`, ... |

A hit means at least one expected source file appeared in the top-4 FAISS results for that query.
