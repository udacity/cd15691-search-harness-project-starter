# Tools

This directory holds the tools definitions and MCP servers for The Onboarding
Agent.
Make sure to read this before implementing any one of them and get familiar
with the conventions we use in the project.


## Tool structure

Each tool's folder separates the actual logic from the MCP registration:

- `core.py`: the tool implementation
- `server.py`: a FastMCP wrapper: creates the `FastMCP` server
  instance, sets up logging, and defines the `@mcp.tool`-decorated
  functions that call into `core.py` and shape the return value.

Keep it that way rather than putting search logic directly in `server.py`.

## Tool Required parameters: `sub_question` and `rationale`

To see the agent's search rounting logic, we are instructing it to provide
these two parameters:

- `sub_question: str`: the specific sub-question this call is trying to
  answer, not the user's overall question verbatim.
- `rationale: str`: why this tool is the right way to answer that
  sub-question, given what's already known from prior searches.

To get the agent to actually provide these parameters correctly, we need
to clearly explain what they mean in the tool's own docstring. That's
the only place the model sees a parameter's description (FastMCP derives
it straight from the docstring's `Args:` section, see
`servers/tools#docstring-descriptions`). You can use the following wording.
It is important to keep the description consistent between tools.

```
Args:
    sub_question: The specific sub-question this call is trying to
        answer (not the user's overall question verbatim).
    rationale: Why this tool is the right way to answer that
        sub-question, given what is already known from prior searches.
```

## Logging

Use the shared helper, `tools/shared/logging_setup.py`'s `get_logger()`,
in every server. It writes to `.logs/<tool-name>.log`. This is visibility only (confirming a tool was actually invoked during manual testing).

## Tests

The tests in `tests/` check exact key names and error messages, so read a tool's test before
you write it.
