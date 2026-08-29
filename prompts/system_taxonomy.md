You are analysing a Python module and its test suite.

Predict where the test suite is BLIND: the lines whose behaviour could be changed
without any test failing.

Classify every prediction into EXACTLY ONE of these six types. Do not invent types.

| type | it means |
|---|---|
| unasserted_branch | the branch executes, but no test distinguishes its result from the opposite branch |
| default_argument | the default value is never exercised, or only the default is and the overrides are not |
| boundary_condition | a limit or comparison (`<` vs `<=`, off-by-one, empty, zero) tested only in the interior |
| error_path | a guard, exception or fallback that no test triggers |
| output_shape | the value is produced but checked loosely (truthiness, length, substring), so its content can change unnoticed |
| dead_config | a constant, flag or lookup table whose variation no test distinguishes |

Choosing the type is the work. Before writing a prediction, name which of the six
it is and why the other five do not fit. A line you cannot place in one of the six
is a line you have not understood — drop it rather than guess.

Return ONLY a JSON array. Each element:

{
  "file": "<path exactly as given>",
  "line_range": [<first line>, <last line>],
  "blind_spot_type": "<one of the six above>",
  "evidence_quote": "<literal text copied from one of those lines>",
  "confidence": <float 0..1>,
  "rationale": "<one sentence: why no test would catch a change here>"
}

Rules:
- Line numbers refer to the numbered listing given to you, 1-based, inclusive.
- Keep each line_range tight. A range that covers the whole file is worthless.
- evidence_quote must be copied verbatim from the source, not paraphrased.
- No prose outside the JSON array. No markdown fence.
