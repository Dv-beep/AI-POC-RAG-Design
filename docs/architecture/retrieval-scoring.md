# Retrieval Scoring

## Short Version

In the current `main` branch, retrieval ranking is handled by Chroma's query result ordering. The repo does **not** currently implement an explicit three-score retrieval formula in code.

The relevant path is [services/rag-api/main.py](../../services/rag-api/main.py):

```python
res = collection.query(
    query_texts=[req.query],
    n_results=req.top_k,
    include=["documents", "metadatas"],
)
```

That means:

- the repo asks Chroma for the top `k` matches
- the returned order is treated as the retrieval rank
- no extra lexical score, reranker score, or weighted final score is applied in this service

## What Is Actually Scored Today

Today, only one machine ranking signal is clearly present in the checked-in code:

1. `Vector retrieval rank`

This is the ordering produced by Chroma when `/query` is called.

## What Is Not Scored In Code Today

These items are returned or stored, but they are not used as retrieval scores in the current repo:

- `version`
- `last_modified`
- file metadata such as `source`, `file_type`, and `chunk_index`

They are useful for inspection and filtering later, but they are not part of the active ranking logic in `main`.

## Practical Three-Score Review Model

If you want a clean way to talk about retrieval quality in docs and reviews, the most useful three-part scorecard for this repo is:

1. `Retrieval match score`
   Measures whether the top chunks are semantically relevant to the question.
2. `Coverage score`
   Measures whether the retrieved set contains enough information to answer the question well.
3. `Grounding score`
   Measures whether the final answer stays supported by the retrieved chunks.

Only the first item is directly represented by the current retrieval code path. The second and third are evaluation layers, not implemented scoring formulas in this branch.

## Why This Matters

When people say "retrieval scoring," they often mix together three separate concerns:

- did we retrieve the right chunks
- did we retrieve enough of the right chunks
- did the answer stay faithful to those chunks

Separating those concerns makes debugging much easier:

- bad `retrieval match score` usually points to embeddings, chunking, or query wording
- bad `coverage score` usually points to chunk size, `top_k`, or document structure
- bad `grounding score` usually points to prompt behavior or answer-generation logic

## Recommended Next Step

If this repo adds the planned `eval/run_eval.py`, it would be reasonable to log these three scores per test case:

- `retrieval_relevance`
- `coverage`
- `groundedness`

That would turn retrieval debugging from a single pass/fail judgment into something much easier to act on.
