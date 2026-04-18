# Judge Evals

This folder documents the recommended judge-based evaluation approach for this repo's RAG workflow.

## Current Repo State

As of this checkout, the code in [services/rag-api/main.py](../../services/rag-api/main.py) exposes retrieval endpoints and admin/status endpoints, but it does **not** include a checked-in automated judge-eval runner yet.

The planned repo structure in [docs/repo-structure-plan.md](../repo-structure-plan.md) references future files such as:

- `eval/eval_cases.yaml`
- `eval/run_eval.py`

These docs give you a clean baseline for:

- what each judge eval is supposed to measure
- how to run each eval manually against the current repo
- how the workflow should look once an automated runner is added

## Judge Eval Docs

- [retrieval-relevance-judge.md](./retrieval-relevance-judge.md)
- [groundedness-judge.md](./groundedness-judge.md)
- [answer-quality-judge.md](./answer-quality-judge.md)

## Related Doc

- [retrieval-scoring.md](../architecture/retrieval-scoring.md)
