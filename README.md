# The Onboarding Agent

In this project you build an agent that answers **"why is this code the way
it is?"** questions about an unfamiliar codebase. To do that, it combines four
kinds of search:

- **Codebase search:** find where something is defined and used.
- **Git history search:** find the commit that introduced a change and read
  why it was made.
- **Semantic (RAG) search over design docs:** find the design decisions
  behind the code.
- **Web search:** find the external documentation the code depends on.

The agent should give a confident answer only when independent sources agree.
When the evidence is thin, it should **escalate to a human** instead of
guessing.

## Architecture

```
               ┌──────────────────────────────┐
  question ──▶ │  OpenCode  (agent harness)   │ ──▶ traces ──▶ Langfuse
               │  .opencode/agents/           │
               │    onboarding-agent.md       │
               └──────────────┬───────────────┘
                              │ MCP
      ┌──────────────┬────────┴──────┬───────────────┬──────────────┐
      ▼              ▼               ▼               ▼              ▼
 codebase-search  git-history-   design-doc-     web-search     answer-gate
 (ripgrep +       search         search          (HTTP client)  (submit_answer:
  tree-sitter)    (git log -S,   (Chroma +            │          confidence
                   git blame)    OpenAI               ▼          gate)
                                 embeddings)     (local
                                                 search API)
```

- **Harness:** [OpenCode](https://opencode.ai), a pre-built agent CLI.
  `opencode.jsonc` configures the model, the permissions, the MCP servers and
  tracing.
- **Agent:** `.opencode/agents/onboarding-agent.md`. The body of this markdown
  file is the agent's system prompt. `opencode.jsonc` sets it as the
  `default_agent`.
- **Tools:** five Python MCP servers built with FastMCP, under `tools/`. Four
  of them are search tools. The fifth, `answer-gate`, provides
  `submit_answer`, which the agent must call at the end of every
  investigation.
- **Evidence:** everything the agent searches is in `starter_bundle/`: a
  small synthetic codebase (`csvcheck`) with real git history and design
  docs. It ships as a git bundle, which you unpack in Setup. `web_api/`
  serves one fabricated external web page, so web-search results are more
  controlled.

## Project structure

The files you work in are marked with their TODO numbers. Everything else is
provided.

```
.opencode/agents/onboarding-agent.md   The agent's system prompt (TODO 2.1)
.vscode/tasks.json                     Starts the web search API when the folder opens in VS Code
opencode.jsonc                         Harness config: model, permissions, MCP servers, tracing
                                         (TODO 1.13, 2.2, 3.4, 6.1, 7.1)
pyproject.toml                         Python dependencies (pinned) and pytest settings
tools/                                 The five MCP servers (read tools/README.md first)
  codebase_search/                       search_code (ripgrep), query_code (tree-sitter): TODO 1.1-1.3
  git_history_search/                    search_commits (pickaxe), blame_line: TODO 1.4-1.6
  design_doc_search/                     search_docs (RAG over markdown design docs): TODO 1.7-1.9
  web_search/                            search_web, fetch_page (calls web_api/): TODO 1.10-1.12
  answer_gate/                           submit_answer (the confidence gate): TODO 3.1-3.3
  shared/logging_setup.py                Shared file logger for every server
  shared/sandbox.py                      Keeps the search tools inside starter_bundle/sample_repo/
web_api/                               Local stand-in for a web search API (FastAPI)
starter_bundle/                        Sample repo bundle, test questions and results template (see its README)
scripts/
  smoke_test.sh                          Checks your setup before you run the agent
  run_test_questions.py                  Evaluation: runs the agent on the test questions: TODO 5.1-5.2
  helpers.py                             Provided helpers for run_test_questions.py
tests/                                 pytest suite for the tools
```

## Setup

### Prerequisites

- Python 3.12+ with pip, as `python3`
- OpenCode 2.0.26 (see [Install OpenCode](#install-opencode))
- Git
- Docker, only to run Langfuse on your own machine (see
  [Tracing with Langfuse](#tracing-with-langfuse))

### Install OpenCode

This project needs OpenCode **2.0.26**. Other versions, 1.x especially, read
`opencode.jsonc` differently. Install it in one of these ways, then check that
`opencode --version` prints `opencode v2.0.26`.

- **Install script** (Linux, macOS). Installs to `~/.opencode/bin` and adds it
  to your PATH:
  ```bash
  curl -fsSL https://opencode.ai/v2/install | bash -s -- --version 2.0.26
  ```
- **npm** (needs Node.js). The 2.x package is `@opencode/cli`. `opencode-ai`
  is the old 1.x package:
  ```bash
  npm install -g @opencode/cli@2.0.26
  ```

### Getting Started
1- Setup API keys
```bash
export OPENAI_API_KEY=
export OPENAI_BASE_URL="https://openai.vocareum.com/v1"
```
Using your own OpenAI key instead of a Udacity one? Set the base URL to
OpenAI's: `export OPENAI_BASE_URL="https://api.openai.com/v1"`. The agent and
design-doc search both read `OPENAI_BASE_URL`, and the agent won't start
without it.

2- Install the Python dependencies

In the Udacity workspace they're already installed, so skip this step. On your
own machine, install them into a virtual environment, and activate it in every
terminal you use for this project. OpenCode starts the agent's tools with
`python3`, so `python3` has to be the one with these packages.
```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e ".[dev]"
```

3- Unpack the sample repo

The agent investigates `starter_bundle/sample_repo/`, a small codebase with
real git history. It ships as a git bundle, `starter_bundle/sample_repo.bundle`.
Unpack it into `starter_bundle/sample_repo/`:
```bash
bash starter_bundle/scripts/clone_sample_repo.sh
```

4- Start the web search API

The web-search tool calls a local stand-in for a web search API at
`http://127.0.0.1:8000`, so the API must be running whenever you use the agent.

- **In the Udacity workspace, it starts on its own** when the workspace opens,
  in a terminal panel called *Start web search API*. If that panel isn't there,
  run `python3 -m web_api.server` from the repo root and leave it running.
- **On your own machine,** run it yourself, from the repo root, in a terminal
  where your virtual environment is activated, and leave it running:
  ```bash
  python3 -m web_api.server
  ```
  If VS Code asks whether to allow automatic tasks, click **Disallow**. That
  task uses the first `python3` on your PATH rather than your virtual
  environment, so on your own machine it usually fails with
  `No module named 'uvicorn'`.

5- Run the smoke test to make sure everything is set up
```bash
bash scripts/smoke_test.sh
```
It checks the Python packages, the API key and base URL, OpenCode, the sample
repo, and the web search API. Then it makes two tiny API calls, one embedding
and one short reply from the agent's model. Add `--no-api-calls` to skip them.
Every failed check says how to fix it. It also starts each MCP server you've
registered in `opencode.jsonc`, so run it again after TODO 1.13 and 3.4.

### Tracing with Langfuse

The agent sends a trace of every run to [Langfuse](https://langfuse.com),
through the Langfuse plugin you add to `opencode.jsonc` in task 6.

- **In the Udacity workspace,** Langfuse is already running, so there's nothing
  to set up. Open it on port 3000 and sign in as `student@example.com` with the
  password `onboarding-agent`. Your traces are in the project *Onboarding
  Agent*, in the organization *Udacity*.
- **On your own machine,** self-host it with Docker Compose. This project was
  tested with Langfuse **4.54.0**. Follow
  [Langfuse's Docker Compose guide](https://langfuse.com/self-hosting/deployment/docker-compose),
  using [its compose file at v4.54.0](https://github.com/langfuse/langfuse/blob/v4.54.0/docker-compose.yml).
  Then create a project in Langfuse, and export its keys and address in the
  terminal where you run the agent:
  ```bash
  export LANGFUSE_PUBLIC_KEY=<your project's public key>
  export LANGFUSE_SECRET_KEY=<your project's secret key>
  export LANGFUSE_BASE_URL="http://localhost:3000"
  ```
  Use `LANGFUSE_BASE_URL`, not `LANGFUSE_HOST`, which the plugin ignores.
  Without `LANGFUSE_BASE_URL`, traces go to Langfuse Cloud instead. Without the
  keys, the agent still runs, but nothing is traced.

## Project tasks

Work through the tasks in order. Each one names the TODO numbers it covers;
the TODO comments in the code say what each step needs. Tasks 6 and 7 fill in
your results file, which you submit with your code: copy
`starter_bundle/results_template.md` to `RESULTS.md` before you start them
(see the [starter bundle README](starter_bundle/README.md)).

### Task 1: Build the four search tools (TODO 1.1-1.13)

Read `tools/README.md` first: it explains how each tool is split between
`core.py` and `server.py`, and the `sub_question` and `rationale` parameters
every tool takes. Then build the tools in this order, `core.py` before
`server.py` each time:

1. Codebase search, with ripgrep and tree-sitter (TODO 1.1-1.3)
2. Git history search, with `git log -S` and `git blame` (TODO 1.4-1.6)
3. Design doc search, with Chroma and OpenAI embeddings (TODO 1.7-1.9)
4. Web search, against the local web search API (TODO 1.10-1.12)

Check each tool with its tests as you finish it, for example
`pytest tests/test_codebase_search.py`. Then register the four servers in
`opencode.jsonc` (TODO 1.13), and run the smoke test to check that each one
starts.

### Task 2: Write the system prompt (TODO 2.1-2.2)

Write the agent's system prompt, in the body of
`.opencode/agents/onboarding-agent.md`. Tell the agent what it's for, how to
route its searches, and when to escalate instead of guessing. You don't need
to describe the tools: their
docstrings do that. Every tool call already
says which sub-question it's answering and why that tool fits, through its
`sub_question` and `rationale` parameters. Then set it as the default
agent in `opencode.jsonc` (TODO 2.2), and try it:
```bash
opencode run --standalone --agent onboarding-agent "Why is MAX_FIELD_LENGTH set to 240 in csvcheck/validators.py?"
```
Read its tool calls. Do they ask sensible sub-questions, and do later calls
build on what earlier ones found?

`--standalone` starts OpenCode from this terminal, so the agent and its tools
get this terminal's `python3`, API key and base URL. Without it, `opencode`
goes through a background service that keeps the environment it first started
with. If that was before you exported the key, the agent can't call the model
or use its tools.

### Task 3: Build the confidence gate (TODO 3.1-3.4)

The agent ends every investigation by calling `submit_answer`. Build it in
`tools/answer_gate/`: two or more independent, non-contradicting source types
let the agent answer with confidence; fewer, or a disagreement it can't
resolve, mean it escalates. Check it with `pytest tests/test_answer_gate.py`,
then register the server in `opencode.jsonc` (TODO 3.4).

### Task 4: Run the test questions

Run the agent on each question in `starter_bundle/test_questions.json`, the same way
as in task 2. Q1 and Q3 should be answered with confidence. Q2 should be
escalated, not guessed.

### Task 5: Write the evaluation (TODO 5.1-5.2)

`scripts/run_test_questions.py` runs the agent on every test question and
checks what it did against what the question expects: which source types it
used, and whether it answered or escalated. It also collects cost, tokens,
latency and tool-call counts from OpenCode's exported session data. The
helpers it needs are in `scripts/helpers.py`. Run it with:
```bash
python3 scripts/run_test_questions.py
```
It prints a pass/fail summary and metrics, and saves the full results under
`.logs/test_runs/`.

### Task 6: Trace the agent in Langfuse (TODO 6.1)

Add the Langfuse plugin to `opencode.jsonc` and turn on OpenCode's
OpenTelemetry export. Then run the evaluation again, so every test question is
traced, and find each question's trace in Langfuse (see
[Tracing with Langfuse](#tracing-with-langfuse)). Each trace shows every tool
call, with its tokens, latency and result. Paste this run's output into
section 1 of `RESULTS.md`, and a screenshot of each question's trace into
section 2. Include the trace's Metadata panel, so its `attributes.session.id`
shows: it must match that question's `session:` line in section 1.

### Task 7: Compare with a codebase-search-only baseline (TODO 7.1)

Switch off every server except `codebase-search` and `answer-gate` in
`opencode.jsonc`, then run the evaluation again. Fill in section 3 of
`RESULTS.md`: this run's output, both runs' pass rate, total cost and total
tokens, a screenshot of one trace from this run, and why the results differ.
Then switch the servers back on.

## Tests

Run the tools' tests from the repo root:
```bash
pytest
```
They fail until you implement the tools, so run each tool's own test file as
you go. The three design-doc search tests call OpenAI's embeddings API, so
they need `OPENAI_API_KEY` and `OPENAI_BASE_URL` exported, and they make a few
tiny embedding calls. The tests unpack the sample repo themselves if it's
missing.

## License

[License](LICENSE.txt)
