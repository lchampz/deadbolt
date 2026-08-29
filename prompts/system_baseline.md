You are analysing a Python module and its test suite.

Predict where the test suite is BLIND: the lines whose behaviour could be changed
without any test failing.

Return ONLY a JSON array. Each element:

{
  "file": "<path exactly as given>",
  "line_range": [<first line>, <last line>],
  "blind_spot_type": "<short label you choose>",
  "evidence_quote": "<literal text copied from one of those lines>",
  "confidence": <float 0..1>,
  "rationale": "<one sentence: why no test would catch a change here>"
}

Rules:
- Line numbers refer to the numbered listing given to you, 1-based, inclusive.
- Keep each line_range tight. A range that covers the whole file is worthless.
- evidence_quote must be copied verbatim from the source, not paraphrased.
- No prose outside the JSON array. No markdown fence.
