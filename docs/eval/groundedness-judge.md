# Groundedness Judge

## What This Eval Does

This judge checks whether the final answer is supported by the retrieved chunks.

It is different from retrieval relevance:

- retrieval relevance asks whether the system found the right context
- groundedness asks whether the answer stayed inside that context

For a RAG system, groundedness is the main hallucination-control eval.

## Current Repo Limitation

The code in [services/rag-api/main.py](../../services/rag-api/main.py) currently stops at retrieval and returns `results`. It does **not** generate the final grounded answer inside this service yet.

Because of that, groundedness can only be run manually today by pairing:

- retrieved chunks from `/query`
- a final answer from the chat layer or downstream LLM flow

## What Good Looks Like

A grounded answer:

- can be traced back to the retrieved chunks
- does not invent policies, names, steps, or numbers
- stays cautious when the retrieved context is incomplete
- uses wording that matches the source material closely enough to be defensible

## What This Judge Should Flag

This eval should fail or warn when:

- the answer contains claims missing from the retrieved chunks
- the answer overstates certainty
- the answer mixes correct source facts with invented details
- the answer cites a source that does not actually support the claim

## How To Run It Now

1. Run a query against `/query` and save the returned chunks.
2. Ask the same question through the chat flow that produces the final answer.
3. Compare each answer claim against the retrieved chunks.
4. Mark the answer as `grounded`, `partially_grounded`, or `not_grounded`.

Recommended checklist:

- Is every important claim supported by a retrieved chunk?
- Does the answer avoid adding extra unsupported steps?
- If the context is thin, does the answer say so?

## Suggested Manual Scorecard

Use a simple 0-2 rubric per test case:

- `0`: answer contains unsupported or clearly hallucinated claims
- `1`: mostly supported, but has one or more weak or ambiguous claims
- `2`: answer is fully supported by retrieved context

## Planned Automated Workflow

Once an eval runner is added, this judge would ideally take:

- the user question
- the retrieved chunks
- the final answer

Planned command shape:

```bash
python eval/run_eval.py --judge groundedness --cases eval/eval_cases.yaml
```

That command is not implemented in this checkout yet.
