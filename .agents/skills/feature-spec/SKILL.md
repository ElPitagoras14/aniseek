---
name: feature-spec
description: "Use when the user asks to define, plan or spec a new view, page, dashboard or feature. Triggers when the request includes phrases like 'define una vista', 'armar el spec de X', 'planear la página Y', 'dashboard de Z', or when the user explicitly invokes the skill with `/skill feature-spec`. Always use this skill for new view/feature spec authoring, end to end, from assumptions validation to writing the spec document. Do NOT use for bug fixes, refactors, maintenance, or any task that is not authoring a spec for a new view or feature."
---

# feature-spec

End-to-end workflow to author a **spec document** for a new view, page, dashboard or feature. The skill produces a single markdown file under `tasks/` and stops there; **implementation is out of scope** and is triggered by the user in a separate request.

The workflow is **strictly sequential** with mandatory pause points between phases. The agent never advances to the next phase without an explicit user response. The skill is **stack-agnostic** — it discovers the project's framework, conventions and data sources during exploration.

## When to use

- User asks to define, plan or spec a new view/page/dashboard/feature.
- User explicitly invokes the skill (`/skill feature-spec`).
- User provides a request that implies authoring a new view ("quiero una vista de...", "necesito una página que muestre...").

## When NOT to use

- Bug fixes, refactors, maintenance, chores, docs updates.
- Pure research or exploration without a spec deliverable.
- Implementation tasks. The spec is the deliverable; code is for later.

---

## The 10-phase workflow

The phases are numbered and **must run in order**. **PAUSA OBLIGATORIA** markers are hard gates.

### Phase 1 — Receive the request

Read the user's request carefully. Note any ambiguity, missing context, or implicit constraints. Do not start exploring yet.

### Phase 2 — Surface explicit assumptions about the request

Before doing any exploration, **enumerate in a numbered list** what the agent is assuming about the request. Examples of typical assumptions:

- "The user wants a single new view, not a redesign of multiple existing pages."
- "The view belongs to the authenticated app shell (`/app/...` or similar)."
- "The user wants a bento/dashboard layout with multiple cards."
- "The user wants the spec written in Spanish."
- "The user does not want backend changes (frontend-only spec)."
- "The user wants the spec at `tasks/<N>-<name>.md`."

Push back on anything that is not stated explicitly in the request. If the request is clear, surface the assumptions anyway — making them explicit prevents rework.

**Output format for this phase**: a numbered list of assumptions, plain text, one per line. No tool calls yet.

### Phase 3 — Validate assumptions with the user

**PAUSA OBLIGATORIA**

Ask the user in **plain text** (no `question` tool) to confirm or correct the assumptions. A single sentence is enough, in the language the user has been writing:

> "Estas son mis asunciones. Si alguna es incorrecta, escribe la corrección. Si todas están bien, responde `OK` o `continuar`."

Why plain text and not `question`: the user often needs to correct a foundational aspect of the request (e.g. "the stack is not Next.js") that does not map cleanly to "uncheck this option". A free-form response lets them write the correction in one message and unblocks the workflow in a single turn.

Do not advance to phase 4 until the user has responded. If the user pushes back, re-do the assumptions list and re-validate.

### Phase 4 — Iterate 1 by 1 on the rejected assumptions

**PAUSA OBLIGATORIA** (per assumption)

For each rejected assumption, open **one turn at a time**:

1. Quote the rejected assumption and ask in plain text how it should read: "¿Cómo debería leer esta asunción? (o `skip` para descartarla)".
2. Wait for the user's correction. Do not use `question` here — the answer is a free-form rewrite, not a pickable option.
3. Repeat for the next rejected assumption.

Do **not** batch multiple assumptions into a single turn. Do **not** advance to phase 5 with rejected assumptions still open.

Once all rejected assumptions are resolved, **list the final validated assumptions** in a single numbered list. If the user introduced new assumptions during iteration, include them in this list.

### Phase 5.0 — Pre-flight: codegraph availability

**PAUSA OBLIGATORIA** (and **MANDATORY**)

Before exploration, verify whether the `codegraph_*` tools are present in the current tool list. Codegraph is the project's first-class exploration tool and is significantly more token-efficient than `read`/`grep`/`glob`.

**Decision tree:**

1. Inspect the tool list available in the current turn.
2. If `codegraph_*` tools are present → you **MUST** use them as the primary exploration tool in phase 5. Start every exploration turn with `codegraph_explore`. Fall back to `codegraph_search` → `codegraph_node` → `codegraph_files` before considering `grep`/`read`/`glob`. Direct `read`/`grep` are reserved for very targeted lookups (an exact file path, a known line number, or a specific text snippet) when codegraph has already returned the surrounding context. Proceed.
3. If `codegraph_*` tools are **not** present → emit a warning to the user in plain text and wait for an explicit `Sí` / `Yes` to continue without codegraph. Any other response (silence, "no", "stop") terminates the flow and the agent reports back to the user without writing a spec.

**Self-check before advancing from phase 5**: if the exploration log shows zero `codegraph_*` calls while the tools were available, the skill has been violated. Acknowledge this to the user and ask whether to redo the exploration with codegraph before continuing.

### Phase 5 — Exploration

Explore the codebase to map what exists. Goals:

- Identify the data sources available (endpoints, models, queries, stores).
- Identify the existing components and UI primitives that can be reused.
- Identify the conventions of the project (folder structure, naming, formatting, type style, response envelopes, etc.).
- Identify the routes/navigation layout and where the new view will live.
- Identify any constraints (auth, layouts, providers, themes).

Prefer (in order): `codegraph_explore` → `codegraph_search` → `codegraph_files` → `codegraph_node` → `grep` → `glob` → `read`. Use the most targeted tool first.

**Do not present a plan yet.** The output of this phase is internal knowledge for the next phases.

### Phase 6 — Present options

**PAUSA OBLIGATORIA**

Present the candidate widgets, sections or features the new view could include. For each option, document briefly the data source it would use.

**Tooling rule:**

- If the options are **truly discrete and well-defined** (binary choices, "which of these widgets", "which of these sections to enable"), the `question` tool with `multiple: true` is acceptable. The first option, if there is a recommendation, should be labeled with "(Recommended)" at the end.
- If the question is **open-ended, layered, or might invite a multi-line correction** (e.g. "what does this dropdown mean?", "how should the auto-login behave?", "which URLs should the footer use?"), ask in **plain text** in the chat. The user's response will be prose, not a pickable option.
- When in doubt, **prefer plain text** over `question`. The default for this skill is: write the question in chat, wait for the user's next message.

**Wait for the user's response** before proceeding to phase 7. Do not start planning based on assumptions.

### Phase 7 — Propose a plan

**PAUSA OBLIGATORIA**

Based on the user's selection in phase 6, propose a plan covering:

- High-level layout / composition of the view.
- Files to create and files to modify, with full paths.
- Reusable existing components, hooks, utilities, types.
- External dependencies (if any) and whether they are already in the project.
- Backend changes required (if any), with the affected endpoints and the minimal diff.
- Conventions of the project that the implementation must respect.

The plan should be detailed enough that the user can challenge it, but not yet a step-by-step implementation guide. The spec is written in phase 10.

Wait for the user's feedback. The user may accept, reject, or request adjustments.

### Phase 8 — Open questions

**PAUSA OBLIGATORIA**

Enumerate any remaining decisions that the plan does not cover and that the user must resolve. Examples:

- Visual style (bento vs uniform grid, dark/light defaults, etc.).
- Scope of a data field (user-scoped vs global).
- Defaults for empty states.
- Click destinations and routing.
- Whether to enable or disable a navigation item that was previously disabled.
- Hardcoded values vs env-driven config.
- Behavior of feature flags in specific edge cases.

Write the questions as a **numbered list in the chat** (no `question` tool). Open questions are nuanced and the user's answer is typically prose, not a pickable option. If there are no open questions, state explicitly "No quedan puntos abiertos" and proceed.

### Phase 9 — Final consolidated plan

**PAUSA OBLIGATORIA**

Re-present the plan in **full** (not a summary) with all decisions from phases 7 and 8 integrated. Include the final file list (create + modify) with paths, the final layout, the final open/closed questions, the final flag/feature behavior table, and the acceptance criteria.

**Approval gate**: ask for an explicit green light in **plain text** in the chat:

> "¿Apruebas el plan? Si necesitas cambios, escríbelos en tu siguiente mensaje y los integro antes de escribir el spec. Si todo está bien, responde `apruebo` / `OK` / `procede`."

**Do NOT use `question` for the approval gate.** This is the worst offender in the previous version: the option-based approval ("Approve / Approve with adjustments / Reject") forces a multi-turn ping-pong where the user picks "Approve with adjustments" and then has to navigate a follow-up "which adjustments?" question, and possibly more. Plain text lets the user write the decision and any corrections in a single message, and the agent integrates them in one turn.

**End of phase 9 — instruction to the user (not a question)**: after showing the full plan, close with a clear, **imperative** instruction, not a meta-question. The user controls the opencode tooling (plan mode, etc.) and knows what they need to do; the agent must not ask them to confirm a meta-action.

Recommended closing line:

> "Plan listo. **Sal del modo plan** y responde `procede` (o cualquier frase confirmativa como `apruebo`, `OK`, `dale`, `escribe el spec`) en tu siguiente mensaje para que escriba `tasks/<N>-<name>.md`."

Do **not** add a follow-up `question` after the plan. Do **not** ask "¿salgo de plan mode?" or "¿procedo a escribir?". End the turn with the instruction and stop.

Loop back to the relevant earlier phase if the user requests changes before approval. Do not advance to phase 10 without an explicit approval.

### Phase 10 — Write the spec

Only after the explicit green light from phase 9, write the spec to `tasks/<N>-<kebab-case>.md`.

- `N` is the next available number in the `tasks/` directory.
- `<kebab-case>` is a short slug derived from the request (e.g. `home-page`, `user-settings`, `storage-overview`).
- The skill lists the candidate filename and asks the user to confirm in phase 9.

After writing, the skill's job is done. **Do not start implementing.** The implementation is a separate request the user will make later.

---

## The spec template

The spec document follows this structure, in order. The skill fills it in; the user reviews and approves before implementation.

```markdown
# <Feature or page name>

> <One-line context from the user's request, quoted verbatim if possible>

<Main file path or orchestrator path>

## Restricciones

- <Stylistic / technical / scope constraints>
- <Use the project's component library when applicable>
- <Responsive / a11y / performance constraints>
- <Any other constraints surfaced in the spec process>

## Vista

<One or more subsections describing the view composition. For each section:>

### <Section name>

- Purpose.
- Data source (endpoint, store, derived value).
- Layout / Tailwind class sketch.
- Components used (from shadcn or project).
- Copy for empty state, error state, and (if relevant) loading state.

(Repeat for each section.)

<If the view has a responsive layout, include a breakpoint table or grid map.>

## General

<Per-endpoint section with method, path, auth, response JSON example. Repeat for each endpoint the view consumes.>

<If backend changes are required, list them here with the affected files, functions and the minimal diff (or diff-style bullet points).>

## Estructura de archivos

### Crear

- `<absolute path>` — <purpose>

### Modificar

- `<absolute path>:<line>` — <change>

## Utilidades

<Helpers, hooks, formatters, mappers that the implementation will need. With signatures but no bodies.>

## Query keys / data fetching

<Per query: key, staleTime, refetch policy.>

## Tipos

<TS interfaces / types the implementation will define or extend.>

## Patrones a respetar

<Conventions of the project that the implementation must follow: file layout, naming, state management, error handling, etc.>

## Criterios de aceptación

<Numbered, verifiable list. Each item should be testable in the browser or via the API.>

Escribir los resultados en este documento

## Resultados

(Por completar después de la implementación)
```

The "Resultados" section is intentionally empty in the initial spec. The implementation agent fills it in after the work is done, following the same convention used by other specs in the project.

---

## Hard rules (do not violate)

- **PAUSA OBLIGATORIA** between every phase. The agent never advances without an explicit user response.
- **No implementation** in the spec-writing skill. Code, commits, PRs are for later.
- **No assumptions about the stack** inside the skill. Discover the project conventions in phase 5.
- **`question` is the exception, not the default.** Use it only for binary or fully-discrete choices. For nuanced, layered, or prose-shaped answers (assumption validation, plan approval, open questions, anything that might invite a multi-line correction), ask in **plain text** in the chat.
- **codegraph is mandatory in phase 5** when the tools are available. Start every exploration turn with `codegraph_explore`. Direct `read`/`grep` are reserved for targeted lookups (exact line numbers, specific snippets) after codegraph has returned the surrounding context. If the tools are missing, abort unless the user explicitly says `Sí` / `Yes` to continue without them.
- **The spec is approved before it is written**. Phase 9 is a hard gate before phase 10. Approval is requested in plain text, not via `question`.
- **Hard rules are marked with bold** in the skill body. Treat them as non-negotiable.

---

## Common frictions to avoid (lessons learned)

These patterns were observed to produce friction in real sessions of this skill. Avoid them.

1. **Bypassing codegraph in phase 5.** When `codegraph_*` tools are available, they are mandatory as the first call. Falling back to `read`/`grep`/`glob` from the start is the #1 most common violation.

2. **Over-using `question` for open-ended decisions.** `question` is good for binary or pickable options. For nuanced answers ("what is the role of this dropdown?", "how should the auto-login behave?", "which URLs should the footer use?"), the user typically has a multi-line correction in mind, and `question`'s options force them to map their intent to predefined labels. Use plain text.

3. **Asking the user to approve the plan with `question` options.** This is the worst offender. Options like "Approve / Approve with adjustments / Reject" create a 3-4 turn ping-pong. Replace with a single plain text ask: "¿Apruebas el plan? Si hay cambios, escríbelos aquí."

4. **Showing only a summary of the plan in phase 9.** When the plan is the deliverable, present it in full. A summary forces the user to ask "muéstrame el plan completo", wasting a turn.

5. **Forcing a meta-correction into a checkbox.** When the user wants to correct a foundational aspect (e.g. "the stack is not Next.js", "the spec is for a different repo"), do not make them pick from a list of assumptions to uncheck. Let them write the correction in plain text and re-do the assumptions.

6. **Asking the user to confirm a meta-action that they control at the tool level** (e.g. "exit plan mode?", "should I write the file now?"). The user already knows what they need to do at the opencode level. Replace the meta-question with a clear **imperative instruction** in plain text: "Sal del modo plan y responde `procede` en tu siguiente mensaje para que escriba el spec." End the turn there; do not add a `question` to confirm.

7. **Multiple `question` calls in a row.** Each `question` is a tool turn. Three `question` calls in a row is three turns of friction. Prefer batching related choices into a single plain text ask, or — if the choice is genuinely discrete — a single `question` with `multiple: true` and comprehensive options.

8. **Repeating the assumption list verbatim in phase 3.** The user already saw the assumptions in phase 2. In phase 3, just ask "¿alguna incorrecta?"; do not re-list them.

---

## Example: minimal generic walkthrough

The following is a **shape example** only. The actual values depend on the user's request.

> User: "I want a settings page where the user can change their avatar and password."

**Phase 2 (assumptions):**
1. The user wants a single new view, not a redesign of the auth flow.
2. The view lives under the authenticated app shell.
3. The view requires two form sections: avatar selection and password change.
4. The spec is stack-agnostic; it should call out the form library already used in the project.
5. The user wants the spec at `tasks/<N>-user-settings.md`.

**Phase 3 (plain text):**
- "¿Alguna de estas asunciones es incorrecta? Si sí, escribe la corrección. Si todas están bien, responde `OK`."

**Phase 6 (plain text for nuanced choices, `question` only for discrete ones):**
- Para opciones discretas como "qué secciones incluir": `question` con `multiple: true` y opciones etiquetadas.
- Para opciones matizadas (estilo, copy, comportamiento): lista numerada en el chat y esperar respuesta en prosa.

**Phase 7 (plan):**
- Files to create: `features/settings/api.ts`, `features/settings/components/settings-form.tsx`, `features/settings/lib/validate-password.ts`.
- Files to modify: `routes/_app/settings.tsx`.
- Backend changes: none (assumes endpoints already exist).

**Phase 10 (write spec):** write to `tasks/<N>-user-settings.md` using the template above.
