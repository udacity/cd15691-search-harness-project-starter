# Results

<!--
Copy this file to RESULTS.md in the project root, and fill it in as you finish tasks 6 and 7.
Save your screenshots in a screenshots/ folder beside it. Keep both out of .logs/: that
folder is in .gitignore, so nothing in it is submitted.
-->

## 1. Evaluation

<!--
Task 6. Paste the printed output of python3 scripts/run_test_questions.py, from SUMMARY to the
end. Use a run made after you added the Langfuse plugin, so its traces are there for section 2.
-->

```
Paste the output here.
```

## 2. Langfuse traces

<!--
Task 6. For each test question, open its trace from the run in section 1 in Langfuse (Tracing,
then the row whose Input is the question), and take a screenshot that shows the trace's tool
calls and, at the top, its latency, cost and tokens.
If a trace is taller than your screen, the top of it is enough.

**Make sure to include the Metadata panel, so that attributes.session.id is visible. It must match the session: line for that question in section 1.**
-->

### Q1

![Q1 trace](screenshots/q1-trace.png)

### Q2

![Q2 trace](screenshots/q2-trace.png)

### Q3

![Q3 trace](screenshots/q3-trace.png)

## 3. Codebase-only baseline

<!-- Task 7. Paste the printed output of the evaluation you ran with only codebase-search and answer-gate enabled, from SUMMARY to the end. -->

```
Paste the output here.
```

<!-- Copy these from the METRICS block of each run. -->

| | Full run | Baseline |
|---|---|---|
| Pass rate | | |
| Total cost | | |
| Total tokens | | |

<!-- A screenshot of one trace from the baseline run. -->

![Baseline trace](screenshots/baseline-trace.png)

**Why the results differ:** <!-- In one to three sentences: why do the baseline's results differ from the full run's? -->
