# gstack Absorption Record

Date: 2026-06-29

## Source

- Upstream: https://github.com/garrytan/gstack
- Fork: https://github.com/aceroer/gstack
- Upstream default branch: `main`
- Fork parent: `garrytan/gstack`
- License: MIT
- License copyright: Copyright (c) 2026 Garry Tan
- Checked upstream pushed date: 2026-06-25T16:42:45Z

This record exists because Agent GitHub Worknet is moving toward the broader
Agent Company concept. gstack has useful role and workflow design material, but
GNW should absorb it as a source of office skills, not as the governing runtime
itself.

## Positioning

gstack is best understood as a skill/workflow pack for AI engineering work. It
defines specialist commands such as product office-hours, CEO review, engineering
review, design review, QA, security audit, release, deploy, investigation,
retrospective, and memory/context actions.

Agent Company should sit one layer above that:

```text
Agent Company
  = organization runtime, authority, permissions, offices, gates, audit,
    meetings, metrics, and publication control

Agent GitHub Worknet
  = GitHub-native issue, branch, PR, session, sync, and trace substrate

gstack-like skills
  = office methods that Agent Company can assign, constrain, and audit
```

## Absorption Rule

Do not silently copy gstack skill text into GNW.

Allowed:

- cite gstack as related work
- map gstack role concepts to Agent Company offices
- study gstack skill boundaries, prompts, and workflows
- implement GNW-native office actions inspired by gstack
- keep attribution when any substantial text or logic is adapted
- track upstream changes through the fork

Required if copying or adapting substantial content:

- keep the MIT license notice
- record the upstream commit
- record which GNW file contains adapted material
- distinguish original GNW governance from gstack-derived office method

## Initial Office Mapping

| gstack area | Agent Company office/action | GNW treatment |
| --- | --- | --- |
| `/office-hours` | Product discovery / CEO intake | Convert to a structured intake action before CEO planning. |
| `/plan-ceo-review` | CEO route review | Use as a strategic challenge method, not as final authority by itself. |
| `/plan-eng-review` | CTO architecture review | Bind to CTO role report and verification plan. |
| `/plan-design-review` | Design office review | Optional office; useful for frontend/product work. |
| `/plan-devex-review` and `/devex-review` | CRO / developer experience review | Fold into CRO adoption and readability checks. |
| `/review` | Code review office | Bind to review report, no merge or publication authority. |
| `/qa` and `/qa-only` | QA Lead verification | Bind to verification evidence and browser/device trace. |
| `/cso` | CSO security audit | Bind to security report, secret scan, and gate decision. |
| `/ship` | Release Manager / publication operator | Must pass GNW publication gates before commit, push, PR, tag, or release. |
| `/land-and-deploy` and `/canary` | Release/operations office | Treat as post-merge deployment workflow requiring explicit approval. |
| `/context-save` and `/context-restore` | Continuity office / company memory | Map to GNW session, trace, handoff, and frozen-state records. |
| `/learn` | Company knowledge base | Convert into governed learning records, not hidden prompt drift. |
| `/retro` | COO retrospective | Bind to incident trace, KPI/OKR, and process improvement items. |
| `/careful`, `/freeze`, `/guard` | CSO/COO safety modes | Convert to executable path/command policies where possible. |
| `/pair-agent` | Runtime Hub pairing | Treat paired agents as worker runtimes under GNW spawn specs. |

## GNW Gaps Exposed By gstack

GNW currently has stronger governance than office method depth. The next Agent
Company phase should reduce that gap by adding office method packets:

- CEO: product and strategy challenge, route convergence, stop/continue verdict.
- CTO: architecture lock, implementation route, technical risk table.
- COO: state hygiene, queue health, handoff quality, serialized ledger writes.
- CSO: security audit, dangerous command review, secret/path boundary policy.
- CFO: scope control, token/time budget, small-task overkill prevention.
- CRO: reader/user/developer experience, adoption risk, onboarding clarity.
- QA Lead: test matrix, browser/device verification, regression evidence.
- Release Manager: publication checklist, PR readiness, release/deploy gate.
- Retro Lead: incident classification, lesson extraction, rule updates.

Each office method packet should define:

- inputs
- allowed actions
- forbidden actions
- expected artifact
- required verification
- publication authority, if any
- escalation condition

## Proposed Next Milestone

Agent Company v1.6 should introduce a Company Kernel:

```text
company/
  offices/
  methods/
  authority/
  reports/
  meetings/
  metrics/

worknet/
  issues/
  branches/
  sessions/
  github_export/

runtime_hub/
  spawns/
  events/
  ingested_reports/
```

The name Agent GitHub Worknet remains valid for the GitHub substrate, but the
upper concept should become Agent Company.

## First Implementation Target

Build an office method registry:

```text
office-method-register
office-method-list
office-method-show
office-action-start
office-action-report
```

The registry should support gstack-inspired methods without importing gstack as
a hidden dependency. Each method should be inspectable, attributable, and tied
to GNW authority rules.
