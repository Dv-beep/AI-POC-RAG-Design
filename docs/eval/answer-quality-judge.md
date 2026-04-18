# Answer Quality Judge

## What This Eval Does

This judge checks whether the final answer is useful to the user, not just technically grounded.

It focuses on answer quality traits such as:

- completeness
- clarity
- directness
- actionable structure
- appropriate use of citations or source references

This eval matters because a response can be factually grounded but still be hard to use.

## Current Repo Limitation

The current `rag-api` implementation in [services/rag-api/main.py](../../services/rag-api/main.py) returns retrieved chunks rather than a fully composed answer. Because of that, answer quality must be reviewed on the downstream chat response, not on the raw `/query` output alone.

## What Good Looks Like

A high-quality answer:

- responds directly to the question
- includes the important steps or facts
- is easy to scan
- avoids unnecessary filler
- references source material when helpful

## What This Judge Should Flag

This eval should fail or warn when:

- the answer is vague even though the context is strong
- the answer leaves out key steps present in the retrieved chunks
- the answer buries the conclusion
- the answer is overly long without adding value
- the answer does not help the user act on the information

## How To Run It Now

1. Run the question through the full user-facing flow that produces a final answer.
2. Save the answer and the retrieved chunks used for context.
3. Review the answer for completeness, clarity, and usability.
4. Mark it as `high_quality`, `mixed_quality`, or `low_quality`.

Recommended checklist:

- Did it answer the exact question asked?
- Did it include the most important details from the source material?
- Would an internal user know what to do next after reading it?

## Suggested Manual Scorecard

Use a simple 0-2 rubric per test case:

- `0`: answer is incomplete, confusing, or not useful
- `1`: answer is usable but missing polish or important detail
- `2`: answer is clear, complete, and operationally useful

## Planned Automated Workflow

Once an eval runner exists, the future command shape could be:

```bash
python eval/run_eval.py --judge answer_quality --cases eval/eval_cases.yaml
```

That command is included here as the intended workflow, not as a currently available repo command.
