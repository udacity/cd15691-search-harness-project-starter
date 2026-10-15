# Starter Bundle

The fixed set of materials The Onboarding Agent is built and evaluated
against: a synthetic codebase with real (backdated) git history, plus the
other evidence sources the agent's four search tools will search across. It
also holds the template for the results file you submit.


## Files

### `sample_repo.bundle`
A [git bundle](https://git-scm.com/docs/git-bundle): a single file containing
a complete git repository (all commits, all history) that isn't a live repo
until you unpack it.

Contains **`csvcheck`**: a small, synthetic CLI tool that validates CSV
files before bulk import, with 12 backdated commits (2025-06-02 →
2026-07-10) and 3 passing tests.


### `scripts/clone_sample_repo.sh`
To clone the sample repo
```bash
bash scripts/clone_sample_repo.sh
```
Unpacks `sample_repo.bundle` into a working checkout at `sample_repo/` (full
history intact. `git log` works normally once cloned).

### `test_questions.json`
The three pre-designed test questions run against the cloned sample repo,
each with its expected evidence path and expected agent behavior (resolve
vs. escalate).

### `results_template.md`
The template for your results file, which you submit with your code. It has
a section each for the evaluation, the Langfuse traces and the codebase-only
baseline. From the repo root, copy it to `RESULTS.md` and fill it in as you
work through tasks 6 and 7:
```bash
cp starter_bundle/results_template.md RESULTS.md
```
