# AGENTS.md

Local Codex rules for the `CMS` repository.

## Governing Playbook

- `CMS` belongs to the Actum working contour and is governed by the sibling repository
  `gcp-infra-playbook` for GCP, IAM, secret management, runtime changes, deployment discipline, and
  rollback.
- Local expected path: `G:\работа\Actum\develop\gcp-infra-playbook`.
- Before any task touching GCP, cloud runtime, deployment, secrets, IAM, Cloud SQL, Cloud Run, Cloud
  Storage, or Cloud Build, read the relevant `gcp-infra-playbook` context first.
- If actual cloud state must be read or changed, run the playbook preflight before doing that work.
- If local CMS rules conflict with `gcp-infra-playbook`, stop and document the discrepancy. Treat the
  playbook as the higher-priority source until the conflict is resolved.

## Relationship To notstrapitest

- `notstrapitest` is the validated prototype and reference polygon.
- `CMS` is the clean implementation project.
- Do not copy experimental code blindly from `notstrapitest`; first decide whether each part is a proven
  product decision, a temporary prototype shortcut, or a candidate for rewrite.
- Keep architecture and runtime decisions explicit in markdown when porting lessons from the prototype.

## Mandatory Doubt

- Do not automatically agree with every requested change.
- If a request looks fragile, premature, excessive, risky, or based on an inaccurate premise, state the
  concern first.
- Offer a safer or more systemic alternative when appropriate.
- If the user accepts a known risk, implement carefully and document the consequence.

## Safety Boundaries

- Do not store real secrets, tokens, passwords, private keys, or live credential values in git, markdown,
  logs, or chat.
- Do not create or change production-like runtime, shared GCP resources, IAM, Cloud Run env/secrets,
  Cloud SQL schema/data, or deployment pipelines without explicit user confirmation.
- Treat GitHub push as source-control publication only. It is not a runtime deploy unless a deploy-bearing
  branch or trigger has been explicitly configured.

## Development Cycle

- Keep changes scoped and documented.
- When architecture, runtime, integrations, or workflow change, update markdown context together with code.
- After a completed change, commit and push the current working branch when the user asks for the normal
  project cycle.
- After push, run relevant local tests, smoke checks, or build checks for the changed surface.
- In the final response, state what changed, how behavior changed, and how the result can be manually
  verified.

