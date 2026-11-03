---
name: vue-saas-redesign
description: Redesign a Vue 3 application's UI into a modern SaaS-style interface - vertical navigation sidebar on the left instead of a top nav bar, design tokens for consistent spacing/color/type, collapsible icon rail, mobile drawer, dark mode, and polished cards/tables/buttons. Use this skill whenever the user wants to modernize, restyle, rebrand, or "make it look professional/like a SaaS dashboard", asks for a sidebar or left nav, wants to replace a top nav/header navigation, wants consistent spacing or a design system for a Vue app, or asks for dark mode on a Vue app, even if they never say "redesign".
---

# Vue 3 SaaS Redesign

Turn a Vue 3 app with a top navigation bar into a modern SaaS shell: persistent left sidebar, one set of design tokens, and shared components that look the same everywhere. The goal is a change in presentation only. Routes, data loading, filters and business logic must behave exactly as before, because the user asked for a new look, not new behavior, and a redesign that quietly breaks a filter is worse than no redesign.

## Default scope

Unless the user asks for more, change only:

1. The app shell (usually `App.vue`): top nav becomes a left sidebar, content area re-laid out.
2. A tokens file: spacing, radius, shadow, type, color (light + dark), layout sizes.
3. Shared/global styles: cards, tables, buttons, badges, inputs, page headers, stat cards.
4. Scoped styles in views/components, only to swap hardcoded colors and header-coupled offsets for tokens.

Do not rewrite view templates, reorder content, or touch `<script>` logic in views. If a view needs structural work to look right, say so in the final report instead of doing it silently. The user can then opt in to a full per-view redesign.

Sidebar features to include by default: collapsible to an icon rail (remembered), off-canvas drawer on small screens, nav links grouped under section labels with a footer area (language/currency switcher, user menu), and a light/dark toggle.

## Project rules come first

Read the project's `CLAUDE.md` files before designing. Typical rules that change the work: "no emojis in UI" (so icons must be inline SVG, never emoji or icon fonts), "delegate `.vue` edits to a specialist subagent" (do that), color palette constraints, comment conventions. A project rule beats anything in this skill. Also never add a UI library or icon package unless asked: inline SVG and plain CSS keep the diff reviewable and the bundle small.

## Workflow

### 1. Discover

Run the audit script against the app's `src` directory. Use the script's own path (this skill's base directory is shown when it loads; it lives at `~/.claude/skills/vue-saas-redesign/` or `<repo>/.claude/skills/vue-saas-redesign/`) and `python3`, since macOS often has no `python`. It lists routes, hardcoded colors per file, header-coupled offsets, fixed z-indexes, container max-widths and emoji in templates:

```bash
python3 <skill-dir>/scripts/audit_ui.py <path-to-app>/src
```

Then read the shell file and the one or two components that sit under the old header (filter bars, breadcrumbs, tab strips). Note: the nav source (hardcoded links or router-driven), the i18n mechanism (nav labels must keep going through it), script style (Options `setup()` vs `<script setup>`; match it), and where global CSS lives.

The audit exists because the failures in this kind of redesign are mechanical and easy to miss by eye: a sticky filter bar with `top: 70px` that now floats over content, a modal at `z-index: 100` that now renders under the sidebar, a scoped `#f8fafc` that stays bright white in dark mode.

### 2. State the plan in chat

Before editing, give the user 5 to 8 lines: which files change, the nav grouping you will use, the sidebar width/breakpoints, and anything you will deliberately leave alone. This is a cheap checkpoint that catches wrong assumptions (e.g. which links belong in which group) before they are baked into the diff.

### 3. Tokens

Create the tokens file from `references/design-tokens.md` and import it once at the app entry. Adapt values to the project's existing palette instead of imposing a new one: if the app is slate + blue, keep slate + blue and make it consistent. Tokens are the product here; every later step is about replacing literals with them.

### 4. Shell

Build the sidebar shell from `references/sidebar-shell.md`. Key requirements:

- Derive nav items from the existing links or router so no route disappears. After editing, every route path must have a sidebar entry (or an explicit reason).
- Keep the existing active-state logic and i18n keys. Add new i18n keys for section labels in every locale file, not just English.
- Existing header widgets (language switcher, profile menu, tasks) move to the sidebar footer. Keep their components and events untouched; only their container changes.
- Content column: sticky filter/toolbar row at `top: 0` of the content column, then page content with a max-width and tokenized padding.
- Collapse state and theme persist in `localStorage`, wrapped in try/catch because storage can throw (private windows, blocked storage). Theme defaults to `prefers-color-scheme`.
- Icons are small inline SVG components, 20px, `stroke="currentColor"` so they follow text color in both themes.

### 5. Shared styles

Restyle the global classes the views already use (`.card`, `.stat-card`, `.page-header`, table, `.badge`, buttons, `.loading`, `.error`) using tokens. Keep class names unchanged: views reference them, and renaming would force template edits across the app. Aim for the visual traits that read as "SaaS": generous consistent spacing from the 4px scale, 1px borders over heavy shadows, 8 to 12px radii, one accent color, small uppercase table headers, tabular numerals for figures, visible focus rings, and restrained transitions (150ms, color/background/border only).

### 6. Sweep scoped styles

For each file the audit flags, replace hardcoded colors with tokens using the mapping table in `references/design-tokens.md`, and replace header-coupled offsets (`top: 70px`, `calc(100vh - 70px)`) with token-driven values. Do it file by file and read each diff. Keep data-series colors in charts (the meaning is the color), but tokenize axis lines, gridlines and labels. Status colors (green/yellow/red) stay semantic; use the `-soft` token pairs so badges stay readable in dark mode.

Inline `:style` colors computed in script (e.g. a function returning `'#10b981'`) are logic, not styling. Leave them alone unless they are unreadable in dark mode, then mention them in the report.

### 7. Verify

Do not report done on the strength of the edit alone.

- `npm run build` in the client directory must pass.
- Run the audit again: hardcoded neutral colors and `70px`-style couplings should be gone or justified.
- Every route has a sidebar entry; every nav i18n key exists in every locale.
- If a browser tool is available (Playwright/Chrome DevTools MCP, or headless Chrome), load at least the home route and one table-heavy route at desktop and mobile widths, in light and dark, and look at them. Check that modals and dropdowns still render above the sidebar and that the sticky toolbar does not overlap content.
- If no browser is available, say plainly that the visual result was not seen, and list what was verified instead.

## Pitfalls worth remembering

- **Stacking order.** Sidebar sits below modals and dropdown menus, above content. Read the existing modal z-index and keep a clear scale (see tokens). The drawer overlay must sit above the sticky toolbar.
- **Dropdowns inside the sidebar footer** (profile menu, language switcher) open upward or sideways; a dropdown that opens downward from the bottom of the viewport is clipped. The sidebar needs `overflow: visible` on the footer, or the menu must be teleported.
- **Collapsed rail hides text.** Give every link a `title` and `aria-label` so icon-only mode is still usable and accessible.
- **`100vh` on mobile** includes the browser chrome; use `100dvh` for the sidebar/drawer height.
- **Locale length.** Japanese or German labels can be longer or shorter than English. Truncate with `text-overflow: ellipsis` in the sidebar rather than letting width jump.
- **Layout shift on load.** Apply the saved theme before first paint (a tiny inline script in `index.html`) or users see a light flash on dark mode.
- **Reduced motion.** Wrap sidebar width/drawer transitions in `@media (prefers-reduced-motion: no-preference)`.

## Final report

Keep it short: files changed, what each change does, anything left alone on purpose (and why), and an explicit line on what was and was not visually verified. Do not commit unless asked.
