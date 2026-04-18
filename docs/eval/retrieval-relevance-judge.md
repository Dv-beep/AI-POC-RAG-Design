# Retrieval Relevance Judge

## What This Eval Does

This judge checks whether the chunks returned by retrieval are actually relevant to the user's question.

In this repo, that means evaluating the output of `POST /query` in [services/rag-api/main.py](../../services/rag-api/main.py). The current `/query` endpoint returns:

- retrieved chunk `id`
- chunk `text`
- chunk `metadata`
- stored `version`
- stored `last_modified`

This eval is the best fit for the current implementation because retrieval is the main behavior already present in `main`.

## What Good Looks Like

A strong retrieval result usually has these properties:

- at least one top result directly answers or supports the question
- most returned chunks stay on-topic
- the set of chunks is not dominated by duplicates
- the chunk metadata points back to the expected document family or source

## What This Judge Should Flag

This eval should fail or warn when:

- returned chunks are about a different topic
- the query uses the right words but retrieves the wrong document
- the same document is repeated without adding useful coverage
- top results are too generic to support an answer

## How To Run It Now

The current repo does not ship an automated judge runner, so the present-day workflow is manual:

1. Start the stack so `rag-api` and `chromadb` are available.
2. Send a test query to `/query`.
3. Inspect the `results` array.
4. Mark each chunk as `relevant`, `partially_relevant`, or `not_relevant`.
5. Record whether the overall retrieval pass should be considered a pass.

PowerShell example:

```powershell
$body = @{
  query = "How do I reset a laptop password?"
  top_k = 5
} | ConvertTo-Json

Invoke-RestMethod `
  -Method Post `
  -Uri "http://localhost:9000/query" `
  -ContentType "application/json" `
  -Body $body
```

`curl` example:

```bash
curl -X POST http://localhost:9000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I reset a laptop password?",
    "top_k": 5
  }'
```

## Suggested Manual Scorecard

Use a simple 0-2 rubric per test case:

- `0`: no useful retrieved chunk
- `1`: some useful material, but noisy or incomplete
- `2`: the top results clearly support the question

## Planned Automated Workflow

The structure in [docs/repo-structure-plan.md](../repo-structure-plan.md) suggests a future eval runner:

- `eval/eval_cases.yaml`
- `eval/run_eval.py`

Once those files exist, a clean command shape would look like:

```bash
python eval/run_eval.py --judge retrieval_relevance --cases eval/eval_cases.yaml
```

That command is not available in the current checkout yet; it is documented here as the intended end state.
