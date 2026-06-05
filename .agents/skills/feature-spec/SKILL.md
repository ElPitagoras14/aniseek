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

Use the `question` tool with `multiple: true` so the user can mark every assumption they consider incorrect. The label of the question should be: "¿Cuáles de estas asunciones NO son correctas?" (or English equivalent if the user is writing in English).

- Each assumption becomes an option label.
- The `custom` option (added automatically by opencode) lets the user add free-form corrections.
- Do not advance to phase 4 until the user has responded.

### Phase 4 — Iterate 1 by 1 on the rejected assumptions

**PAUSA OBLIGATORIA** (per assumption)

For each assumption the user marked as incorrect, open **one turn at a time**:

1. Open a turn that quotes the rejected assumption and asks the user how it should read.
2. Wait for the user's correction (or for them to say "descarta y pasa a la siguiente" / "skip").
3. Repeat for the next rejected assumption.

Do **not** batch multiple assumptions into a single turn. Do **not** advance to phase 5 with rejected assumptions still open.

Once all rejected assumptions are resolved, **list the final validated assumptions** to the user as confirmation. If the user introduced new assumptions during iteration, include them in this list.

### Phase 5.0 — Pre-flight: codegraph availability

**PAUSA OBLIGATORIA**

Before exploration, verify whether the `codegraph_*` tools are present in the current tool list. Codegraph is preferred for token-efficient exploration; if it is missing, exploration falls back to `grep` / `glob` / `read` which is more expensive.

**Decision tree:**

1. Inspect the tool list available in the current turn.
2. If `codegraph_*` tools are present → use them as the default for exploration in phase 5. Proceed.
3. If `codegraph_*` tools are **not** present → emit a warning to the user:
   > "codegraph no está disponible en este proyecto. La exploración se hará con `grep` / `glob` / `read` y consumirá significativamente más tokens. ¿Deseas continuar?"

   Then call `question` with two options:
   - `Sí, continuar sin codegraph` (not recommended, but allowed)
   - `No, detener` (default selection)

   The skill **must not advance to phase 5** until the user answers. The user's response must be an explicit `Sí` / `Yes` (or a clear affirmative). Any other response — silence, ambiguous answer, "no", "stop" — terminates the flow and the agent reports back to the user without writing a spec.

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

- If options are discrete and selectable (e.g. "which widgets to include", "which sections to enable"), use the `question` tool with `multiple: true`. The first option, if there is a recommendation, should be labeled with "(Recommended)" at the end.
- If options are open-ended, descriptive or too many to enumerate (e.g. "show me everything you can extract from the codebase"), fall back to a numbered markdown list in the chat.

**Wait for the user's selection** before proceeding to phase 7. Do not start planning based on assumptions.

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

Use a numbered list. Wait for answers. If there are no open questions, state explicitly "No quedan puntos abiertos" and proceed.

### Phase 9 — Final consolidated plan

**PAUSA OBLIGATORIA**

Re-present the plan with all decisions from phases 7 and 8 integrated. Include the final file list (create + modify) with paths, the final layout, the final open/closed questions, and the acceptance criteria preview.

Ask the user for an **explicit green light** ("¿Apruebas el plan?") before writing. The user's response must be affirmative. If the user requests changes, loop back to the relevant earlier phase.

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
- **The `question` tool is the default** for selectable options and assumption validation. Fall back to numbered lists only when options are open-ended.
- **The codegraph pre-flight gate is mandatory**. If codegraph is missing and the user does not explicitly say `Sí` / `Yes` to continue, abort.
- **The spec is approved before it is written**. Phase 9 is a hard gate before phase 10.
- **Hard rules are marked with bold** in the skill body. Treat them as non-negotiable.

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

**Phase 3 (`question` with `multiple: true`):**
- "¿Cuáles de estas asunciones NO son correctas?"
- Options: one per assumption.

**Phase 6 (`question` with `multiple: true`):**
- "¿Qué secciones debe incluir la página?"
- Options: `Avatar selector (Recommended)`, `Password change`, `Email change`, `Delete account`.

**Phase 7 (plan):**
- Files to create: `features/settings/api.ts`, `features/settings/components/settings-form.tsx`, `features/settings/lib/validate-password.ts`.
- Files to modify: `routes/_app/settings.tsx`.
- Backend changes: none (assumes endpoints already exist).

**Phase 10 (write spec):** write to `tasks/<N>-user-settings.md` using the template above.
