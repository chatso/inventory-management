# Design tokens

Contents: tokens file, theme switching, hex-to-token mapping, component recipes.

Adapt the values to the project's existing palette. The structure (names, scale, light/dark pairing) is what matters, because later steps and future edits refer to tokens by name.

## Tokens file

Save as `src/styles/tokens.css` (or next to the project's global CSS) and import once in the entry file (`import './styles/tokens.css'`).

```css
:root {
  /* Spacing: 4px base. Use these for every margin, padding and gap. */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-5: 1.25rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  --space-10: 2.5rem;

  /* Radius */
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;

  /* Type */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 0.938rem;
  --text-lg: 1.125rem;
  --text-xl: 1.5rem;
  --text-2xl: 1.875rem;

  /* Layout */
  --sidebar-width: 15.5rem;
  --sidebar-width-collapsed: 4.5rem;
  --content-max-width: 1600px;
  --toolbar-height: 3.5rem;

  /* Motion */
  --transition: 150ms ease;

  /* Stacking: keep gaps so new layers can slot in. Modals must exceed the drawer. */
  --z-sticky: 90;
  --z-sidebar: 200;
  --z-drawer-overlay: 300;
  --z-drawer: 310;
  --z-dropdown: 400;
  --z-modal: 500;

  /* Color: light theme (default) */
  --bg: #f8fafc;
  --surface: #ffffff;
  --surface-muted: #f8fafc;
  --surface-hover: #f1f5f9;
  --border: #e2e8f0;
  --border-strong: #cbd5e1;
  --text-strong: #0f172a;
  --text: #1e293b;
  --text-secondary: #475569;
  --text-muted: #64748b;
  --text-faint: #94a3b8;

  --primary: #2563eb;
  --primary-hover: #1d4ed8;
  --primary-soft: #eff6ff;
  --primary-soft-text: #1e40af;
  --on-primary: #ffffff;

  --success: #059669;
  --success-soft: #d1fae5;
  --success-soft-text: #065f46;
  --warning: #ea580c;
  --warning-soft: #fed7aa;
  --warning-soft-text: #92400e;
  --danger: #dc2626;
  --danger-soft: #fecaca;
  --danger-soft-text: #991b1b;

  --sidebar-bg: #ffffff;
  --sidebar-border: var(--border);
  --sidebar-link: var(--text-secondary);
  --sidebar-link-hover-bg: var(--surface-hover);
  --sidebar-link-active-bg: var(--primary-soft);
  --sidebar-link-active-text: var(--primary);

  --shadow-sm: 0 1px 2px rgba(15, 23, 42, 0.06);
  --shadow-md: 0 4px 12px rgba(15, 23, 42, 0.08);
  --shadow-lg: 0 12px 32px rgba(15, 23, 42, 0.16);
  --focus-ring: 0 0 0 3px rgba(37, 99, 235, 0.35);

  color-scheme: light;
}

:root[data-theme='dark'] {
  --bg: #0b1220;
  --surface: #111a2e;
  --surface-muted: #0f172a;
  --surface-hover: #1a2540;
  --border: #243049;
  --border-strong: #33425f;
  --text-strong: #f8fafc;
  --text: #e2e8f0;
  --text-secondary: #cbd5e1;
  --text-muted: #94a3b8;
  --text-faint: #64748b;

  --primary: #60a5fa;
  --primary-hover: #93c5fd;
  --primary-soft: rgba(96, 165, 250, 0.14);
  --primary-soft-text: #bfdbfe;
  --on-primary: #0b1220;

  --success: #34d399;
  --success-soft: rgba(52, 211, 153, 0.16);
  --success-soft-text: #6ee7b7;
  --warning: #fb923c;
  --warning-soft: rgba(251, 146, 60, 0.16);
  --warning-soft-text: #fdba74;
  --danger: #f87171;
  --danger-soft: rgba(248, 113, 113, 0.16);
  --danger-soft-text: #fca5a5;

  --sidebar-bg: #0d1526;

  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.4);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.45);
  --shadow-lg: 0 12px 32px rgba(0, 0, 0, 0.6);
  --focus-ring: 0 0 0 3px rgba(96, 165, 250, 0.45);

  color-scheme: dark;
}
```

If the project has no dark-mode requirement, still keep the semantic names: they are what makes later restyling a one-file change.

## Theme switching

Set `document.documentElement.dataset.theme = 'dark' | 'light'`. Resolve the initial value as: saved choice, else `matchMedia('(prefers-color-scheme: dark)')`. To avoid a flash, put this in `index.html` `<head>` before the app script:

```html
<script>
  try {
    var t = localStorage.getItem('theme');
    if (!t && window.matchMedia('(prefers-color-scheme: dark)').matches) t = 'dark';
    if (t) document.documentElement.dataset.theme = t;
  } catch (e) {}
</script>
```

## Hex-to-token mapping (slate/blue palettes)

Use for the scoped-style sweep. Match case-insensitively, including 3-digit forms and `white`.

| Literal | Token | Notes |
| --- | --- | --- |
| `#ffffff`, `white` | `var(--surface)` | Card/panel backgrounds. For text on a primary button use `var(--on-primary)`. |
| `#f8fafc` | `var(--surface-muted)` or `var(--bg)` | Page background -> `--bg`; table header / subtle panel -> `--surface-muted`. |
| `#f1f5f9` | `var(--surface-hover)` | Hover rows, row separators may use `--border`. |
| `#e2e8f0` | `var(--border)` | Borders, dividers. |
| `#cbd5e1` | `var(--border-strong)` | Input borders, hover borders. |
| `#94a3b8` | `var(--text-faint)` | Placeholder, disabled. |
| `#64748b` | `var(--text-muted)` | Secondary text. |
| `#475569` | `var(--text-secondary)` | Table headers, labels. |
| `#334155`, `#1e293b` | `var(--text)` | Body text. |
| `#0f172a` | `var(--text-strong)` | Headings, key numbers. |
| `#2563eb`, `#3b82f6` | `var(--primary)` | Links, active states. |
| `#eff6ff`, `#dbeafe` | `var(--primary-soft)` | Active backgrounds, info badges. |
| `#1e40af` | `var(--primary-soft-text)` | Text on soft blue. |
| `#d1fae5` / `#065f46` | `var(--success-soft)` / `var(--success-soft-text)` | Badge pairs, keep together. |
| `#fed7aa` / `#92400e` | `var(--warning-soft)` / `var(--warning-soft-text)` | |
| `#fecaca`, `#fef2f2` / `#991b1b` | `var(--danger-soft)` / `var(--danger-soft-text)` | |
| `#059669`, `#10b981` | `var(--success)` | Solid status text/icons. |
| `#ea580c` | `var(--warning)` | |
| `#dc2626`, `#ef4444` | `var(--danger)` | |

Unknown literals: leave them, list them in the report. Guessing a token for an unfamiliar color is how a chart quietly changes meaning.

Spacing literals (`1.25rem`, `20px`) map to the nearest `--space-*`. Only change those inside the shared styles and the shell. Rewriting every padding in every view is churn with regression risk and little visual payoff.

## Component recipes (shared styles)

Write these in the shared stylesheet, keeping the project's existing class names.

```css
body { font-family: var(--font-sans); background: var(--bg); color: var(--text); -webkit-font-smoothing: antialiased; }

.card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: var(--space-5); margin-bottom: var(--space-5); }
.card-header { display: flex; justify-content: space-between; align-items: center; gap: var(--space-4); margin-bottom: var(--space-4); padding-bottom: var(--space-4); border-bottom: 1px solid var(--border); }
.card-title { font-size: var(--text-lg); font-weight: 600; color: var(--text-strong); letter-spacing: -0.01em; }

.page-header { margin-bottom: var(--space-6); }
.page-header h2 { font-size: var(--text-2xl); font-weight: 700; color: var(--text-strong); letter-spacing: -0.02em; }
.page-header p { color: var(--text-muted); font-size: var(--text-base); margin-top: var(--space-1); }

.stat-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: var(--space-5); }
.stat-label { font-size: var(--text-xs); font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); }
.stat-value { font-size: var(--text-2xl); font-weight: 700; color: var(--text-strong); font-variant-numeric: tabular-nums; }

th { font-size: var(--text-xs); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); text-align: left; padding: var(--space-3) var(--space-4); background: var(--surface-muted); }
td { padding: var(--space-3) var(--space-4); border-top: 1px solid var(--border); font-size: var(--text-sm); color: var(--text); font-variant-numeric: tabular-nums; }
tbody tr:hover { background: var(--surface-hover); }

.badge { display: inline-flex; align-items: center; padding: 0.125rem var(--space-2); border-radius: 999px; font-size: var(--text-xs); font-weight: 600; }
.badge.success { background: var(--success-soft); color: var(--success-soft-text); }
.badge.warning { background: var(--warning-soft); color: var(--warning-soft-text); }
.badge.danger  { background: var(--danger-soft);  color: var(--danger-soft-text); }
.badge.info    { background: var(--primary-soft); color: var(--primary-soft-text); }

:focus-visible { outline: none; box-shadow: var(--focus-ring); border-radius: var(--radius-sm); }
```

Buttons and form controls: if the project has no shared button class, do not invent one that views will not use. Style native `button`/`select`/`input` only where the app already relies on bare elements, and leave class-based buttons in their scoped styles (they get the token sweep).
