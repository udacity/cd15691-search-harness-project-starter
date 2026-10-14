#!/usr/bin/env bash
# Checks that everything the Onboarding Agent needs is installed, configured,
# and running, before you spend anything on a real agent run.
#
#   bash scripts/smoke_test.sh                 # every check, including two tiny API calls
#   bash scripts/smoke_test.sh --no-api-calls  # skip the API calls
#
# Exits 0 when every check passes, 1 otherwise.

set -uo pipefail

OPENCODE_VERSION="2.0.26"
WEB_API_URL="http://127.0.0.1:8000"      # DEFAULT_BASE_URL in tools/web_search/core.py
EMBEDDING_MODEL="text-embedding-3-small" # _EMBEDDING_MODEL_NAME in tools/design_doc_search/core.py
MCP_START_TIMEOUT_S=60                   # importing chromadb makes design-doc-search the slowest
SAMPLE_REPO="starter_bundle/sample_repo" # SAMPLE_REPO in tools/shared/sandbox.py
SAMPLE_REPO_BUNDLE="starter_bundle/sample_repo.bundle" # unpacked by starter_bundle/scripts/clone_sample_repo.sh

cd "$(dirname "$0")/.." || exit 1

api_calls=1
for arg in "$@"; do
    case "$arg" in
        --no-api-calls) api_calls=0 ;;
        -h | --help)
            sed -n '2,8p' "$0" | sed 's/^# \{0,1\}//'
            exit 0
            ;;
        *)
            echo "Unknown option: $arg (see --help)" >&2
            exit 2
            ;;
    esac
done

failures=0

pass() { printf '  PASS  %s\n' "$1"; }
fail() {
    printf '  FAIL  %s\n' "$1"
    shift
    for hint in "$@"; do printf '        %s\n' "$hint"; done
    failures=$((failures + 1))
}
skip() { printf '  SKIP  %s\n' "$1"; }
heading() { printf '\n%s\n' "$1"; }

# Shared by every Python block below: the same PASS/FAIL output as the bash
# helpers above, and an exit status equal to the number of failures.
PY_HELPERS='
import json, os, re, shutil, subprocess, sys, urllib.error, urllib.request
failures = 0
def ok(msg): print(f"  PASS  {msg}")
def bad(msg, *hints):
    global failures
    failures += 1
    print(f"  FAIL  {msg}")
    for hint in hints: print(f"        {hint}")
def skipped(msg): print(f"  SKIP  {msg}")
def done(): sys.exit(min(failures, 255))
def load_config():
    # opencode.jsonc, read the way OpenCode reads it: JSON plus comments and
    # trailing commas. Strings are matched first so a "https://" stays whole.
    text = open("opencode.jsonc", encoding="utf-8").read()
    string = r"(\"(?:\\.|[^\"\\])*\")"
    text = re.sub(string + r"|//[^\n]*|/\*.*?\*/", lambda m: m.group(1) or "", text, flags=re.S)
    text = re.sub(string + r"|,(\s*[}\]])", lambda m: m.group(1) or m.group(2), text)
    return json.loads(text)
'

# Runs the Python block on stdin with $PY and adds its failures to the total.
run_py() {
    { printf '%s\n' "$PY_HELPERS"; cat; } | "$PY" - "$@"
    failures=$((failures + $?))
}

echo "Onboarding Agent smoke test"

# --- Python packages ---------------------------------------------------------
# Lists the packages of the first python3 on PATH, the one OpenCode starts
# the MCP servers with.
PY=""
packages_json=""
lister=""
if command -v python3 >/dev/null 2>&1 && packages_json=$(python3 -m pip list --format json 2>/dev/null); then
    PY=python3
    lister="python3 -m pip list"
fi

heading "Python packages${lister:+ (via $lister)}"
if [ -z "$lister" ]; then
    fail "Couldn't list installed packages with python3 -m pip" \
        "Install the dependencies first: see \"Getting Started\" in README.md."
    PY=$(command -v python3 || true)
    if [ -z "$PY" ]; then
        echo
        echo "python3 isn't on PATH, so the remaining checks can't run."
        exit 1
    fi
else
    PACKAGES_JSON="$packages_json" run_py <<'PY'
version = ".".join(map(str, sys.version_info[:3]))
pyproject = open("pyproject.toml", encoding="utf-8").read()
needs_python = re.search(r'requires-python\s*=\s*"([^"]+)"', pyproject).group(1)

try:
    from packaging.specifiers import SpecifierSet

    def satisfies(installed, spec):
        return SpecifierSet(spec).contains(installed, prereleases=True)
except ImportError:
    # A rough stand-in for `packaging`, in case it isn't installed:
    # compares only the numeric release part (1.2.3) of each version.
    def release(v):
        m = re.match(r"\d+(?:\.\d+)*", v)
        return tuple(int(x) for x in m.group().split(".")) if m else ()

    def satisfies(installed, spec):
        have = release(installed)
        for clause in filter(None, (c.strip() for c in spec.split(","))):
            op, want = re.match(r"(~=|===|==|!=|<=|>=|<|>)\s*(.+)", clause).groups()
            want_r = release(want.rstrip(".*"))
            n = max(len(have), len(want_r))
            a, b = have + (0,) * (n - len(have)), want_r + (0,) * (n - len(want_r))
            c = (a > b) - (a < b)
            holds = {
                "==": c == 0, "===": c == 0, "!=": c != 0, "<=": c <= 0,
                ">=": c >= 0, "<": c < 0, ">": c > 0,
                "~=": c >= 0 and have[: len(want_r) - 1] == want_r[:-1],
            }[op]
            if not holds:
                return False
        return True

if satisfies(version, needs_python):
    ok(f"Python {version} (needs {needs_python})")
else:
    bad(f"Python {version}, but the project needs {needs_python}",
        "Use Python 3.12 or newer as python3. On your own machine, recreate the virtual",
        "environment with it: see step 2 in README.md.")
    done()

import tomllib

project = tomllib.loads(pyproject)["project"]
requirements = project["dependencies"] + project["optional-dependencies"]["web-api"]

def canonical(name):
    return re.sub(r"[-_.]+", "-", name).lower()

installed = {canonical(p["name"]): p["version"] for p in json.loads(os.environ["PACKAGES_JSON"])}
for requirement in dict.fromkeys(requirements):
    name, spec = re.match(r"\s*([A-Za-z0-9][A-Za-z0-9._-]*)(?:\[[^\]]*\])?\s*([^;]*)", requirement).groups()
    spec = spec.strip()
    have = installed.get(canonical(name))
    if have is None:
        bad(f"{name} isn't installed (needs {spec or 'any version'})")
    elif spec and not satisfies(have, spec):
        bad(f"{name} {have} is installed, but the project needs {spec}")
    else:
        ok(f"{name} {have}" + (f" (needs {spec})" if spec else ""))
if failures:
    print("        Install the dependencies: see step 2 in README.md. On your own machine,")
    print("        activate your virtual environment first.")
done()
PY
fi

# --- API key and base URL ----------------------------------------------------
heading "API key and base URL"
run_py <<'PY'
key = os.environ.get("OPENAI_API_KEY", "")
if not key:
    bad("OPENAI_API_KEY isn't set", "export OPENAI_API_KEY=<your key>")
elif re.search(r"\s|[\"']", key):
    bad("OPENAI_API_KEY contains spaces or quotes", "Export it again with just the key.")
else:
    ok("OPENAI_API_KEY is set")

base_url = os.environ.get("OPENAI_BASE_URL", "")
if not base_url:
    bad("OPENAI_BASE_URL isn't set", "The agent and design-doc search both read it.",
        "Set it for your key. A Udacity (Vocareum) key:",
        "export OPENAI_BASE_URL=https://openai.vocareum.com/v1",
        "Your own OpenAI key:",
        "export OPENAI_BASE_URL=https://api.openai.com/v1")
elif not re.fullmatch(r"https?://[^\s/]+(/\S*)?/v1", base_url):
    bad(f"OPENAI_BASE_URL is {base_url}, which isn't an http(s) URL ending in /v1",
        "Set it for your key. A Udacity (Vocareum) key:",
        "export OPENAI_BASE_URL=https://openai.vocareum.com/v1",
        "Your own OpenAI key:",
        "export OPENAI_BASE_URL=https://api.openai.com/v1")
else:
    ok(f"OPENAI_BASE_URL is {base_url}")

    # The agent's requests go to opencode.jsonc's baseURL, which should read
    # OPENAI_BASE_URL. Without one, OpenCode uses OpenAI's endpoint and ignores
    # the variable.
    config = load_config()
    settings = config.get("providers", {}).get("openai", {}).get("settings", {})
    agent_url = settings.get("baseURL", "https://api.openai.com/v1")
    if agent_url == "{env:OPENAI_BASE_URL}" or agent_url.rstrip("/") == base_url.rstrip("/"):
        ok("The agent's baseURL in opencode.jsonc matches")
    else:
        bad(f"opencode.jsonc sends the agent to {agent_url}, but OPENAI_BASE_URL is {base_url}",
            "The agent and design-doc search would call different endpoints. Make them match.")
done()
PY

# --- OpenCode ----------------------------------------------------------------
heading "OpenCode"
if ! command -v opencode >/dev/null 2>&1; then
    fail "opencode isn't on PATH" "Install OpenCode $OPENCODE_VERSION: see \"Install OpenCode\" in README.md."
else
    installed=$(opencode --version 2>/dev/null | grep -Eo '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
    if [ "$installed" = "$OPENCODE_VERSION" ]; then
        pass "opencode $installed"
    else
        fail "opencode is ${installed:-an unknown version}, but this project needs $OPENCODE_VERSION" \
            "Install OpenCode $OPENCODE_VERSION: see \"Install OpenCode\" in README.md."
    fi
fi
# There's no check that OpenCode loads onboarding-agent: `opencode debug agents`
# answers for the background service's folder, not this one, and has no
# --standalone flag.

# Starts each MCP server exactly as opencode.jsonc does and sends it the MCP
# handshake, so a missing command or a crash on startup shows up here.
run_py "$MCP_START_TIMEOUT_S" <<'PY'
import select, signal, time

timeout_s = int(sys.argv[1])
config = load_config()
servers = config.get("mcp", {}).get("servers", {})
handshake = json.dumps({
    "jsonrpc": "2.0", "id": 1, "method": "initialize",
    "params": {"protocolVersion": "2025-06-18", "capabilities": {},
               "clientInfo": {"name": "smoke-test", "version": "0"}},
}) + "\n"

for name, server in servers.items():
    if server.get("disabled") or server.get("type") != "local":
        continue
    command = server["command"]
    if shutil.which(command[0]) is None:
        bad(f"MCP server {name}: `{command[0]}` isn't on PATH",
            f"opencode.jsonc starts it with: {' '.join(command)}")
        continue
    # Its own session, so the kill below also reaches anything the command
    # starts in turn. A server left running holds the pipes open.
    proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, start_new_session=True)
    reply, buffer, deadline = None, b"", time.monotonic() + timeout_s
    try:
        proc.stdin.write(handshake.encode())
        proc.stdin.flush()
        while reply is None and time.monotonic() < deadline:
            ready, _, _ = select.select([proc.stdout], [], [], deadline - time.monotonic())
            if not ready:
                break
            chunk = os.read(proc.stdout.fileno(), 65536)
            if not chunk:
                break  # the server exited
            buffer += chunk
            *lines, buffer = buffer.split(b"\n")
            for line in lines:
                try:
                    message = json.loads(line)
                except ValueError:
                    continue
                if isinstance(message, dict) and message.get("id") == 1:
                    reply = message
    except BrokenPipeError:
        pass  # the server exited before reading the handshake
    finally:  # also on Ctrl-C, which the server's own session doesn't receive
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass  # it already exited (macOS refuses to signal it)
        proc.wait()
    stderr_tail = proc.stderr.read().decode(errors="replace").strip().splitlines()[-3:]
    if reply and "result" in reply:
        ok(f"MCP server {name} starts")
    elif reply:
        bad(f"MCP server {name} rejected the handshake: {reply.get('error')}",
            f"Its log is .logs/{name}.log.")
    else:
        bad(f"MCP server {name} didn't answer within {timeout_s}s", *stderr_tail)
done()
PY

# --- Sample repo -------------------------------------------------------------
# The codebase the agent investigates. Git-history search needs its full
# history, so a shallow or out-of-date checkout fails too.
heading "Sample repo"
unpack_hint="Unpack it from the repo root, which replaces starter_bundle/sample_repo/: bash starter_bundle/scripts/clone_sample_repo.sh"
bundle_head=$(git bundle list-heads "$SAMPLE_REPO_BUNDLE" 2>/dev/null | awk '$2 == "HEAD" {print $1}')
if [ -z "$bundle_head" ]; then
    fail "Couldn't read $SAMPLE_REPO_BUNDLE" "It's part of the repo. Restore it with: git checkout -- $SAMPLE_REPO_BUNDLE"
elif [ ! -d "$SAMPLE_REPO/.git" ]; then
    fail "$SAMPLE_REPO/ isn't unpacked" "$unpack_hint"
elif [ "$(git -C "$SAMPLE_REPO" rev-parse --is-shallow-repository 2>/dev/null)" != "false" ]; then
    fail "$SAMPLE_REPO/ has only part of its git history" "$unpack_hint"
elif [ "$(git -C "$SAMPLE_REPO" rev-parse HEAD 2>/dev/null)" != "$bundle_head" ]; then
    fail "$SAMPLE_REPO/ isn't at the bundle's latest commit, ${bundle_head:0:7}" "$unpack_hint"
else
    pass "$SAMPLE_REPO/ at ${bundle_head:0:7}, with $(git -C "$SAMPLE_REPO" rev-list --count HEAD) commits of history"
fi

# --- Web search API ----------------------------------------------------------
heading "Web search API"
run_py "$WEB_API_URL" <<'PY'
# "field length" matches the fixture page in web_api/external_sources/.
url = f"{sys.argv[1]}/search?q=field+length&max_results=1"
try:
    with urllib.request.urlopen(url, timeout=10) as response:
        results = json.load(response)["results"]
    if results:
        ok(f"{sys.argv[1]} answers /search")
    else:
        bad(f"{sys.argv[1]} is up, but /search found no fixture page",
            "Check that web_api/external_sources/ has its .html files.")
except (urllib.error.URLError, OSError, KeyError, ValueError) as e:
    bad(f"{sys.argv[1]} isn't answering /search ({e})",
        "Start it from the repo root and leave it running (step 4 in README.md):",
        "python3 -m web_api.server")
done()
PY

# --- API calls ---------------------------------------------------------------
heading "API calls"
if [ "$api_calls" -eq 0 ]; then
    skip "API calls (--no-api-calls)"
else
    run_py "$EMBEDDING_MODEL" <<'PY'
key = os.environ.get("OPENAI_API_KEY", "")
base_url = os.environ.get("OPENAI_BASE_URL", "").rstrip("/")
if not key or not base_url:
    skipped("API calls need OPENAI_API_KEY and OPENAI_BASE_URL")
    done()

def post(url, body):
    request = urllib.request.Request(url, data=json.dumps(body).encode(), headers={
        "Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.status, None
    except urllib.error.HTTPError as e:
        try:
            message = json.load(e)["error"]["message"]
        except (ValueError, KeyError, TypeError):
            message = e.reason
        return e.code, message
    except (urllib.error.URLError, OSError) as e:
        return None, str(e)

# Design-doc search's embeddings, through OPENAI_BASE_URL.
embedding_model = sys.argv[1]
status, error = post(f"{base_url}/embeddings", {"model": embedding_model, "input": "smoke test"})
if status == 200:
    ok(f"Embeddings with {embedding_model}")
else:
    bad(f"Embeddings with {embedding_model} failed{f' ({status})' if status else ''}: {error}",
        "Check OPENAI_API_KEY, and that OPENAI_BASE_URL is the right one for your key:",
        "see step 1 in README.md.")

# The agent's model, through opencode.jsonc's baseURL, as OpenCode calls it.
agent_file = open(".opencode/agents/onboarding-agent.md", encoding="utf-8").read()
config = load_config()
match = re.search(r"^model:\s*(\S+)", agent_file, re.MULTILINE)
model = (match.group(1) if match else config["model"]).split("/", 1)[1]
agent_url = config.get("providers", {}).get("openai", {}).get("settings", {}).get("baseURL", "https://api.openai.com/v1")
agent_url = re.sub(r"\{env:(\w+)\}", lambda m: os.environ.get(m.group(1), ""), agent_url).rstrip("/")
status, error = post(f"{agent_url}/responses",
                     {"model": model, "input": "Reply with OK.", "max_output_tokens": 16})
if status == 200:
    ok(f"The agent's model, {model}")
else:
    bad(f"The agent's model, {model}, failed{f' ({status})' if status else ''}: {error}",
        f"Check OPENAI_API_KEY and OPENAI_BASE_URL, and that your key can use {model}.")
done()
PY
fi

echo
if [ "$failures" -eq 0 ]; then
    echo "All checks passed."
    exit 0
fi
echo "$failures check(s) failed."
exit 1
