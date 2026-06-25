# Why Agent GitHub Worknet

Agent GitHub Worknet exists because AI coding agents are becoming good at
isolated execution, but weak at durable organization.

An agent can edit files. A better agent can run tests, open a branch, and draft
a pull request. But real software work is not only editing files. It also needs
ownership, boundaries, state, review, memory, escalation, and release judgment.

GitHub already contains many of the right objects:

- issues
- branches
- pull requests
- reviews
- labels
- milestones
- comments
- checks
- releases

Agent GitHub Worknet treats those objects as a work network for agents, then
adds the missing organizational layer above them.

## The Short Version

Agent GitHub Worknet turns GitHub issues into an auditable operating system for
AI coding teams.

It is not another coding agent.

It is a governance and workflow layer for coding agents.

## The Problem

Most coding agents are optimized for the moment of execution:

```text
prompt -> edit files -> run checks -> open PR
```

That loop is useful, but it leaves several hard questions under-specified:

- Who owns the route?
- Who owns verification?
- Who decides whether the task is too large?
- Who handles security and publication boundaries?
- Which actions require human approval?
- Where does the agent record decisions?
- How does another agent resume the work later?
- How do multiple agents avoid corrupting shared state?

As agents become faster, these questions become more important, not less.

Without an operating layer, a fast agent can produce code while the project
ledger, approval trail, and organizational memory fall apart.

## What GNW Adds

Agent GitHub Worknet has two layers.

### 1. GitHub Worknet

The worknet layer maps local work objects to GitHub-style objects:

```text
local issue -> task -> branch -> work session -> verification -> PR-ready record
```

It gives agents a local, file-based work network before any remote action is
performed. Remote GitHub operations are explicit and reviewable.

This layer answers:

- what issue is active
- what branch or route belongs to it
- what verification was run
- whether a remote issue exists
- whether local and remote state agree
- what should be synced, skipped, or reported

### 2. Agent Organization Runtime

The organization layer treats agents as accountable workers inside a lightweight
company structure.

It adds:

- CEO route ownership
- CTO implementation ownership
- COO process and state ownership
- CSO security and boundary ownership
- CFO scope and cost control
- CRO user/readability risk checks
- QA and docs role reports
- P-level permissions
- approval gates
- roundtable meetings
- weighted votes
- organization applications
- publication gates

This layer answers:

- who is allowed to decide
- who is allowed to act
- who must report
- which actions require approval
- when humans take over
- what happened if the workflow fails

## What GNW Is Not

Agent GitHub Worknet is not trying to replace:

- GitHub
- GitHub Actions
- Copilot coding agent
- Codex
- Claude Code
- OpenHands
- SWE-agent
- mini-swe-agent
- Sweep
- project management tools

Those tools can be worker runtimes.

GNW is the layer that gives them a shared task ledger, authority model, audit
trail, and publication boundary.

## Related Systems

GNW is part of a broader shift toward GitHub-native agent work.

- GitHub Copilot coding agent can take assigned issues and produce draft pull
  requests.
- GitHub Agentic Workflows brings coding agents into GitHub Actions for
  repository automation.
- SWE-agent takes GitHub issues and attempts to fix them automatically.
- OpenHands provides a full AI-driven development environment.
- MAGIS proposes a multi-agent research framework with Manager, Repository
  Custodian, Developer, and QA Engineer roles.
- Some teams already use GitHub issues as a persistence layer for agent plans,
  decisions, and review context.

GNW differs by combining both halves:

```text
GitHub-native work substrate
        +
agent organization runtime
```

That combination is the project.

## Why The Company Metaphor

The company model is not decoration.

It is a practical way to prevent all uncertainty from collapsing into one
overloaded agent.

For a tiny issue, one agent can usually finish the work directly.

For a medium issue, the useful behavior changes. The CEO should not personally
turn every uncertainty into one script. The CEO should assign ownership:

- CTO: implementation route and technical verification
- CSO: permissions, secrets, hooks, and remote-write risk
- CFO: scope control and cost
- CRO: reader or user risk
- COO: workflow state and handoff

The point is not bureaucracy. The point is accountable decomposition.

## Demo Traces

The repository keeps real traces under `experimental/closure/`.

Current traces include:

- `REAL_TRACE_2026-06-16.md`: early closure path from local issue to GitHub
  state reconciliation.
- `REAL_TRACE_2026-06-25_SERFBOUND_GNW_TRIAL.md`: a small documentation issue
  completed through a company-style GNW trial. It showed that the model can
  preserve boundaries, but also exposed the need for atomic object allocation
  before parallel role writes are safe.
- `REAL_TRACE_2026-06-25_SOROKIT_UI_129_INCIDENT.md`: a governance failure where
  technical work passed but remote publication happened without the correct
  board/P13 gate. This directly motivated stronger gate checks and role reports.

These traces are intentionally public. GNW is built from real workflow pressure,
not only from imagined diagrams.

## When GNW Is Too Much

GNW is not needed for every task.

Use a simple coding agent directly when:

- the issue is tiny
- there is one obvious file target
- the risk is low
- no remote publication decision is needed
- no role split would improve the outcome

Use GNW when:

- the issue has real uncertainty
- multiple judgments need owners
- verification and security are separate concerns
- remote publication must be gated
- several agents or tools may work on the same task
- the work needs to be resumed later with a durable audit trail

Small tasks test the GitHub workflow layer.

Medium tasks test the worknet.

Large tasks test the company.

## The Direction

The long-term direction is simple:

```text
AI agents should not only generate code.
They should work inside durable, reviewable, human-governed organizations.
```

Agent GitHub Worknet is an early attempt to build that organization layer on top
of the developer platform that already exists: GitHub.
