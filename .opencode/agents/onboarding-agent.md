---
description: Investigates why a piece of code is the way it is, by routing across codebase, git-history, design documents, and web search, stating its reasoning before every tool call.
mode: primary
model: openai/gpt-5.2
permissions:
  - action: edit
    resource: "*"
    effect: deny
  - action: shell
    resource: "*"
    effect: deny
  - action: subagent
    resource: "*"
    effect: deny
request:
  body:
    temperature: 0.2
---

<!--
TODO 2.1: Write the agent's system prompt. Tell it what it's for and
when to escalate instead of guessing. You don't need to describe the
tools: their docstrings do that.
Hint: Use negative examples to tell the agent what not to do.
-->
