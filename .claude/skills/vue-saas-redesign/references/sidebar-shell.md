# Sidebar shell

Contents: file layout, navigation config, shell state composable, icons, sidebar component, App.vue layout, CSS, checklist.

The examples use `setup()` returning bindings, which matches Options-style Vue 3 codebases. If the project uses `<script setup>`, translate the script blocks and keep everything else. Replace class names, i18n keys and paths with the project's own. The structure is the contract, not the exact text.

## File layout

```
src/
  navigation.js              # nav sections: data only
  composables/useShell.js    # collapsed / mobile drawer / theme state (module singleton)
  components/NavIcon.js      # inline SVG icons via render function
  components/AppSidebar.vue  # brand + nav + footer slot
  App.vue                    # grid: sidebar | column(toolbar, content)
```

Component edits are `.vue` work. If the project requires delegating `.vue` files to a specialist subagent, hand over this whole reference plus the plan from the workflow.

## navigation.js

Build from the project's real links. Keep each item's existing i18n key. Grouping should follow how people use the app (overview, operations, finance, insights), not the old tab order.

```js
export const navSections = [
  {
    labelKey: 'nav.sections.main',
    items: [
      { to: '/', labelKey: 'nav.overview', icon: 'dashboard' },
      { to: '/inventory', labelKey: 'nav.inventory', icon: 'box' },
      { to: '/orders', labelKey: 'nav.orders', icon: 'list' }
    ]
  },
  {
    labelKey: 'nav.sections.planning',
    items: [
      { to: '/demand', labelKey: 'nav.demandForecast', icon: 'trend' },
      { to: '/restocking', labelKey: 'nav.restocking', icon: 'restock' }
    ]
  },
  {
    labelKey: 'nav.sections.finance',
    items: [
      { to: '/spending', labelKey: 'nav.finance', icon: 'wallet' },
      { to: '/reports', labelKey: 'nav.reports', icon: 'file' }
    ]
  }
]
```

Links with hardcoded English text in the old nav (e.g. a literal "Reports") get a new i18n key in every locale file; do not carry the literal over.

## useShell.js

Module-level refs make the state shared without a store, the same pattern as a shared filters composable.

```js
import { ref, watch } from 'vue'

const read = (key, fallback) => {
  try {
    const value = localStorage.getItem(key)
    return value === null ? fallback : value
  } catch (err) {
    return fallback
  }
}
const write = (key, value) => {
  try {
    localStorage.setItem(key, value)
  } catch (err) {
    // Storage can be blocked; the UI still works, it just will not remember.
  }
}

const collapsed = ref(read('sidebar-collapsed', 'false') === 'true')
const mobileOpen = ref(false)
const theme = ref(
  document.documentElement.dataset.theme ||
    (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
)

watch(collapsed, (value) => write('sidebar-collapsed', String(value)))

// Only an explicit toggle is persisted, so an unset theme keeps following the OS.
const applyTheme = (value) => {
  theme.value = value
  document.documentElement.dataset.theme = value
}

export function useShell() {
  return {
    collapsed,
    mobileOpen,
    theme,
    toggleCollapsed: () => { collapsed.value = !collapsed.value },
    openDrawer: () => { mobileOpen.value = true },
    closeDrawer: () => { mobileOpen.value = false },
    toggleTheme: () => {
      const next = theme.value === 'dark' ? 'light' : 'dark'
      applyTheme(next)
      write('theme', next)
    }
  }
}
```

## NavIcon.js

A render function over data keeps icons out of `v-html` and lets them inherit `currentColor`. Stroke icons at 24x24 viewBox, drawn small (20px) in the UI. Add icons by adding entries; the fallback prevents a missing name from breaking the sidebar.

```js
import { h } from 'vue'

const ICONS = {
  dashboard: [['rect', { x: 3, y: 3, width: 7, height: 9, rx: 1.5 }], ['rect', { x: 14, y: 3, width: 7, height: 5, rx: 1.5 }], ['rect', { x: 14, y: 12, width: 7, height: 9, rx: 1.5 }], ['rect', { x: 3, y: 16, width: 7, height: 5, rx: 1.5 }]],
  box: [['path', { d: 'M21 8l-9-5-9 5v8l9 5 9-5V8z' }], ['path', { d: 'M3 8l9 5 9-5M12 13v8' }]],
  list: [['path', { d: 'M8 6h13M8 12h13M8 18h13' }], ['circle', { cx: 4, cy: 6, r: 1 }], ['circle', { cx: 4, cy: 12, r: 1 }], ['circle', { cx: 4, cy: 18, r: 1 }]],
  wallet: [['rect', { x: 3, y: 6, width: 18, height: 14, rx: 2 }], ['path', { d: 'M3 10h18M16 15h2' }]],
  trend: [['path', { d: 'M3 17l6-6 4 4 8-8' }], ['path', { d: 'M15 7h6v6' }]],
  restock: [['path', { d: 'M20 11a8 8 0 0 0-14.9-3M4 4v4h4' }], ['path', { d: 'M4 13a8 8 0 0 0 14.9 3M20 20v-4h-4' }]],
  file: [['path', { d: 'M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8l-5-5z' }], ['path', { d: 'M14 3v5h5M9 13h6M9 17h6' }]],
  menu: [['path', { d: 'M4 6h16M4 12h16M4 18h16' }]],
  close: [['path', { d: 'M6 6l12 12M18 6L6 18' }]],
  chevronLeft: [['path', { d: 'M15 6l-6 6 6 6' }]],
  chevronRight: [['path', { d: 'M9 6l6 6-6 6' }]],
  moon: [['path', { d: 'M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z' }]],
  sun: [['circle', { cx: 12, cy: 12, r: 4 }], ['path', { d: 'M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4' }]],
  dot: [['circle', { cx: 12, cy: 12, r: 3 }]]
}

export default {
  name: 'NavIcon',
  props: { name: { type: String, required: true }, size: { type: Number, default: 20 } },
  setup(props) {
    return () =>
      h(
        'svg',
        {
          width: props.size, height: props.size, viewBox: '0 0 24 24', fill: 'none',
          stroke: 'currentColor', 'stroke-width': 1.75, 'stroke-linecap': 'round',
          'stroke-linejoin': 'round', 'aria-hidden': 'true', focusable: 'false'
        },
        (ICONS[props.name] || ICONS.dot).map(([tag, attrs]) => h(tag, attrs))
      )
  }
}
```

## AppSidebar.vue

```vue
<template>
  <aside class="sidebar" :class="{ collapsed, open: mobileOpen }" :aria-label="t('nav.mainNavigation')">
    <div class="sidebar-brand">
      <span class="sidebar-logo" aria-hidden="true">{{ initial }}</span>
      <div class="sidebar-brand-text">
        <span class="sidebar-title">{{ t('nav.companyName') }}</span>
        <span class="sidebar-subtitle">{{ t('nav.subtitle') }}</span>
      </div>
      <button type="button" class="sidebar-close" :aria-label="t('nav.closeMenu')" @click="closeDrawer">
        <NavIcon name="close" />
      </button>
    </div>

    <nav class="sidebar-nav">
      <div v-for="section in navSections" :key="section.labelKey" class="sidebar-section">
        <div class="sidebar-section-label">{{ t(section.labelKey) }}</div>
        <router-link
          v-for="item in section.items"
          :key="item.to"
          :to="item.to"
          class="sidebar-link"
          :class="{ active: isActive(item.to) }"
          :aria-current="isActive(item.to) ? 'page' : undefined"
          :title="t(item.labelKey)"
        >
          <NavIcon :name="item.icon" />
          <span class="sidebar-link-text">{{ t(item.labelKey) }}</span>
        </router-link>
      </div>
    </nav>

    <div class="sidebar-footer">
      <slot name="footer" />
      <div class="sidebar-actions">
        <button type="button" class="sidebar-action" :title="themeLabel" :aria-label="themeLabel" @click="toggleTheme">
          <NavIcon :name="theme === 'dark' ? 'sun' : 'moon'" />
          <span class="sidebar-link-text">{{ themeLabel }}</span>
        </button>
        <button
          type="button"
          class="sidebar-action sidebar-collapse"
          :aria-expanded="String(!collapsed)"
          :title="collapseLabel"
          :aria-label="collapseLabel"
          @click="toggleCollapsed"
        >
          <NavIcon :name="collapsed ? 'chevronRight' : 'chevronLeft'" />
          <span class="sidebar-link-text">{{ collapseLabel }}</span>
        </button>
      </div>
    </div>
  </aside>
</template>

<script>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from '../composables/useI18n'
import { useShell } from '../composables/useShell'
import { navSections } from '../navigation'
import NavIcon from './NavIcon'

export default {
  name: 'AppSidebar',
  components: { NavIcon },
  setup() {
    const route = useRoute()
    const { t } = useI18n()
    const { collapsed, mobileOpen, theme, toggleCollapsed, toggleTheme, closeDrawer } = useShell()

    // Prefix match keeps a parent link highlighted on nested routes; '/' must match exactly.
    const isActive = (to) => route.path === to || (to !== '/' && route.path.startsWith(to + '/'))

    const initial = computed(() => (t('nav.companyName') || '?').trim().charAt(0).toUpperCase())
    const themeLabel = computed(() => (theme.value === 'dark' ? t('nav.lightMode') : t('nav.darkMode')))
    const collapseLabel = computed(() => (collapsed.value ? t('nav.expandSidebar') : t('nav.collapseSidebar')))

    return { t, navSections, collapsed, mobileOpen, theme, toggleCollapsed, toggleTheme, closeDrawer, isActive, initial, themeLabel, collapseLabel }
  }
}
</script>
```

New i18n keys used here (`nav.sections.*`, `nav.mainNavigation`, `nav.closeMenu`, `nav.lightMode`, `nav.darkMode`, `nav.expandSidebar`, `nav.collapseSidebar`) must be added to every locale file.

The logo is a letter tile because inventing a logo is outside scope; if the project has a logo asset, use it instead.

## App.vue layout

Keep the existing `<script>` (tasks, modals, event handlers) intact. Change only the template skeleton and the styles. Import `AppSidebar`, `useShell`, `NavIcon`.

```vue
<div class="app-shell" :class="{ collapsed }">
  <AppSidebar>
    <template #footer>
      <LanguageSwitcher />
      <ProfileMenu @show-profile-details="showProfileDetails = true" @show-tasks="showTasks = true" />
    </template>
  </AppSidebar>
  <div v-if="mobileOpen" class="drawer-overlay" @click="closeDrawer"></div>

  <div class="app-column">
    <header class="mobile-bar">
      <button type="button" class="icon-button" :aria-label="t('nav.openMenu')" @click="openDrawer"><NavIcon name="menu" /></button>
      <span class="mobile-bar-title">{{ t('nav.companyName') }}</span>
    </header>
    <FilterBar />
    <main class="app-content"><router-view /></main>
  </div>

  <!-- existing modals unchanged -->
</div>
```

In `setup()`: `const { collapsed, mobileOpen, openDrawer, closeDrawer } = useShell()`, a `watch(() => route.path, closeDrawer)` so navigating closes the drawer, and an Escape handler (`keydown` listener added in `onMounted`, removed in `onBeforeUnmount`) that closes it. Return them all.

## Shell CSS

Goes in App.vue's global style block (or the project's global stylesheet). Remove the old `.top-nav`, `.nav-container`, `.nav-tabs`, `.logo` rules; leaving dead CSS behind misleads the next person.

```css
.app-shell {
  --sidebar-current: var(--sidebar-width);
  display: grid;
  grid-template-columns: var(--sidebar-current) minmax(0, 1fr);
  min-height: 100vh;
  min-height: 100dvh;
}
.app-shell.collapsed { --sidebar-current: var(--sidebar-width-collapsed); }

.app-column { --sticky-offset: 0px; min-width: 0; display: flex; flex-direction: column; }
.app-content { flex: 1; width: 100%; max-width: var(--content-max-width); margin: 0 auto; padding: var(--space-6) var(--space-8); }

.sidebar {
  position: sticky; top: 0; height: 100vh; height: 100dvh;
  display: flex; flex-direction: column;
  background: var(--sidebar-bg); border-right: 1px solid var(--sidebar-border);
  z-index: var(--z-sidebar);
}
.sidebar-brand { display: flex; align-items: center; gap: var(--space-3); padding: var(--space-5) var(--space-4); min-height: var(--toolbar-height); }
.sidebar-logo { flex: none; width: 2rem; height: 2rem; border-radius: var(--radius-md); background: var(--primary); color: var(--on-primary); display: grid; place-items: center; font-weight: 700; }
.sidebar-brand-text { display: flex; flex-direction: column; min-width: 0; }
.sidebar-title { font-weight: 700; color: var(--text-strong); font-size: var(--text-base); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.sidebar-subtitle { font-size: var(--text-xs); color: var(--text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.sidebar-close { display: none; margin-left: auto; }

.sidebar-nav { flex: 1; overflow-y: auto; padding: var(--space-2) var(--space-3); }
.sidebar-section + .sidebar-section { margin-top: var(--space-5); }
.sidebar-section-label { padding: 0 var(--space-3); margin-bottom: var(--space-2); font-size: var(--text-xs); font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; color: var(--text-faint); }

.sidebar-link, .sidebar-action {
  display: flex; align-items: center; gap: var(--space-3); width: 100%;
  padding: var(--space-2) var(--space-3); border: 0; border-radius: var(--radius-md);
  background: transparent; color: var(--sidebar-link); font: inherit; font-size: var(--text-sm); font-weight: 500;
  text-decoration: none; cursor: pointer; transition: background var(--transition), color var(--transition);
}
.sidebar-link + .sidebar-link { margin-top: 2px; }
.sidebar-link:hover, .sidebar-action:hover { background: var(--sidebar-link-hover-bg); color: var(--text-strong); }
.sidebar-link.active { background: var(--sidebar-link-active-bg); color: var(--sidebar-link-active-text); font-weight: 600; }
.sidebar-link svg, .sidebar-action svg { flex: none; }
.sidebar-link-text { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* Footer widgets (language switcher, profile menu) may open dropdowns, so it must not clip. */
.sidebar-footer { padding: var(--space-3); border-top: 1px solid var(--sidebar-border); display: flex; flex-direction: column; gap: var(--space-2); overflow: visible; }
.sidebar-actions { display: flex; flex-direction: column; gap: 2px; }

/* Collapsed rail: icons only. Titles/aria-labels on the controls keep it usable. */
.sidebar.collapsed .sidebar-brand-text,
.sidebar.collapsed .sidebar-section-label,
.sidebar.collapsed .sidebar-link-text { display: none; }
.sidebar.collapsed .sidebar-link, .sidebar.collapsed .sidebar-action { justify-content: center; padding: var(--space-3); }
.sidebar.collapsed .sidebar-brand { justify-content: center; padding-left: 0; padding-right: 0; }

.mobile-bar, .drawer-overlay { display: none; }
.icon-button { display: inline-grid; place-items: center; width: 2.25rem; height: 2.25rem; border: 0; border-radius: var(--radius-md); background: transparent; color: var(--text-secondary); cursor: pointer; }
.icon-button:hover { background: var(--surface-hover); }

@media (prefers-reduced-motion: no-preference) {
  .app-shell { transition: grid-template-columns var(--transition); }
  .sidebar { transition: transform 200ms ease; }
}

/* Below this width the sidebar is an off-canvas drawer. The collapsed state is ignored here. */
@media (max-width: 1023px) {
  .app-shell, .app-shell.collapsed { --sidebar-current: 0px; grid-template-columns: minmax(0, 1fr); }
  .sidebar, .sidebar.collapsed { position: fixed; inset: 0 auto 0 0; width: min(var(--sidebar-width), 86vw); transform: translateX(-100%); z-index: var(--z-drawer); box-shadow: var(--shadow-lg); }
  .sidebar.open { transform: translateX(0); }
  .sidebar.collapsed .sidebar-brand-text, .sidebar.collapsed .sidebar-section-label, .sidebar.collapsed .sidebar-link-text { display: initial; }
  .sidebar.collapsed .sidebar-link, .sidebar.collapsed .sidebar-action { justify-content: flex-start; padding: var(--space-2) var(--space-3); }
  .sidebar-close { display: inline-grid; }
  .sidebar-collapse { display: none; }
  .drawer-overlay { display: block; position: fixed; inset: 0; background: rgba(15, 23, 42, 0.5); z-index: var(--z-drawer-overlay); }
  .app-column { --sticky-offset: var(--toolbar-height); }
  .mobile-bar { display: flex; align-items: center; gap: var(--space-3); position: sticky; top: 0; z-index: var(--z-sticky); height: var(--toolbar-height); padding: 0 var(--space-4); background: var(--surface); border-bottom: 1px solid var(--border); }
  .mobile-bar-title { font-weight: 700; color: var(--text-strong); }
  .app-content { padding: var(--space-4); }
}
```

The `.sidebar.collapsed` overrides inside the media query exist because a drawer that is "collapsed" would show only icons with no way to expand it; on small screens the drawer is always full.

Sticky toolbars under the old header (a filter bar with `top: 70px`) become `top: var(--sticky-offset, 0px)` and `z-index: var(--z-sticky)`. That one variable makes them correct on both desktop (0) and mobile (below the mobile bar).

## Checklist

- Every route has a sidebar entry; every new i18n key exists in every locale.
- Existing modals use `z-index: var(--z-modal)` (or a value above `--z-drawer`) and cover the sidebar.
- Language/profile dropdowns in the footer open in a direction that stays on screen, in expanded and collapsed modes.
- Tab through the sidebar: focus ring visible, Enter activates, Escape closes the drawer.
- Resize across 1023px: no horizontal page scroll, no overlap of toolbar and content.
- Both themes: text/background contrast is readable on cards, tables, badges and the sidebar.
