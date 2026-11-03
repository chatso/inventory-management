<template>
  <aside class="sidebar" :class="{ collapsed, open: mobileOpen, tablet: isTablet }" :aria-label="t('nav.mainNavigation')">
    <div class="sidebar-brand">
      <span class="sidebar-logo" aria-hidden="true">{{ initial }}</span>
      <div class="sidebar-brand-text">
        <span class="sidebar-title">{{ t('nav.companyName') }}</span>
        <span class="sidebar-subtitle">{{ t('nav.subtitle') }}</span>
      </div>
      <button
        type="button"
        class="icon-button sidebar-close"
        :aria-label="t('nav.closeMenu')"
        @click="closeDrawer"
      >
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
          @click="closeDrawer"
          :title="t(item.labelKey)"
          :aria-label="t(item.labelKey)"
        >
          <NavIcon :name="item.icon" />
          <span class="sidebar-link-text">{{ t(item.labelKey) }}</span>
        </router-link>
      </div>
    </nav>

    <div class="sidebar-footer">
      <div class="sidebar-actions">
        <button
          type="button"
          class="sidebar-action"
          :title="themeLabel"
          :aria-label="themeLabel"
          @click="toggleTheme"
        >
          <NavIcon :name="theme === 'dark' ? 'sun' : 'moon'" />
          <span class="sidebar-link-text">{{ themeLabel }}</span>
        </button>
        <button
          type="button"
          class="sidebar-action sidebar-collapse"
          :aria-expanded="String(sidebarExpanded)"
          :title="collapseLabel"
          :aria-label="collapseLabel"
          @click="toggleSidebar"
        >
          <NavIcon :name="sidebarExpanded ? 'chevronLeft' : 'chevronRight'" />
          <span class="sidebar-link-text">{{ collapseLabel }}</span>
        </button>
      </div>
      <slot name="footer" />
    </div>
  </aside>
</template>

<script>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from '../composables/useI18n'
import { useShell } from '../composables/useShell'
import NavIcon from './NavIcon'

// Every route in main.js must appear here. Label keys are the existing nav i18n keys.
const navSections = [
  {
    labelKey: 'nav.sections.overview',
    items: [{ to: '/', labelKey: 'nav.overview', icon: 'dashboard' }]
  },
  {
    labelKey: 'nav.sections.operations',
    items: [
      { to: '/inventory', labelKey: 'nav.inventory', icon: 'box' },
      { to: '/orders', labelKey: 'nav.orders', icon: 'list' },
      { to: '/restocking', labelKey: 'nav.restocking', icon: 'restock' },
      { to: '/demand', labelKey: 'nav.demandForecast', icon: 'trend' }
    ]
  },
  {
    labelKey: 'nav.sections.financeInsights',
    items: [
      { to: '/spending', labelKey: 'nav.finance', icon: 'wallet' },
      { to: '/reports', labelKey: 'nav.reports', icon: 'file' }
    ]
  }
]

export default {
  name: 'AppSidebar',
  components: { NavIcon },
  setup() {
    const route = useRoute()
    const { t } = useI18n()
    const { collapsed, mobileOpen, isTablet, theme, toggleSidebar, toggleTheme, closeDrawer } = useShell()

    // Same exact-path rule the old top nav used.
    const isActive = (to) => route.path === to

    const initial = computed(() => (t('nav.companyName') || '?').trim().charAt(0).toUpperCase())
    const themeLabel = computed(() => (theme.value === 'dark' ? t('nav.lightMode') : t('nav.darkMode')))
    // Tablet expansion is the transient overlay; desktop expansion is the persisted preference.
    const sidebarExpanded = computed(() => (isTablet.value ? mobileOpen.value : !collapsed.value))
    const collapseLabel = computed(() =>
      sidebarExpanded.value ? t('nav.collapseSidebar') : t('nav.expandSidebar')
    )

    return {
      t,
      navSections,
      collapsed,
      mobileOpen,
      isTablet,
      theme,
      sidebarExpanded,
      toggleSidebar,
      toggleTheme,
      closeDrawer,
      isActive,
      initial,
      themeLabel,
      collapseLabel
    }
  }
}
</script>

<!-- Unscoped on purpose: the footer slot hosts other components (language switcher, profile
     menu) whose inner elements this block must be able to restyle. Everything is under .sidebar. -->
<style>
.sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  height: 100dvh;
  display: flex;
  flex-direction: column;
  background: var(--sidebar-bg);
  border-right: 1px solid var(--sidebar-border);
  z-index: var(--z-sidebar);
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-4);
  min-height: var(--toolbar-height);
}

.sidebar-logo {
  flex: none;
  width: 2rem;
  height: 2rem;
  border-radius: var(--radius-md);
  background: var(--primary);
  color: var(--on-primary);
  display: grid;
  place-items: center;
  font-weight: 700;
}

.sidebar-brand-text {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.sidebar-title {
  font-weight: 700;
  color: var(--text-strong);
  font-size: var(--text-base);
  letter-spacing: -0.01em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-subtitle {
  font-size: var(--text-xs);
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* .sidebar prefix: .icon-button is defined later and would otherwise win with display: inline-grid. */
.sidebar .sidebar-close {
  display: none;
  margin-left: auto;
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-2) var(--space-3);
}

.sidebar-section + .sidebar-section {
  margin-top: var(--space-5);
}

.sidebar-section-label {
  padding: 0 var(--space-3);
  margin-bottom: var(--space-2);
  font-size: var(--text-xs);
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--text-faint);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-link,
.sidebar-action {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  width: 100%;
  padding: var(--space-2) var(--space-3);
  border: 0;
  border-radius: var(--radius-md);
  background: transparent;
  color: var(--sidebar-link);
  font: inherit;
  font-size: var(--text-sm);
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  transition: background-color var(--transition), color var(--transition);
}

.sidebar-link + .sidebar-link {
  margin-top: 2px;
}

.sidebar-link:hover,
.sidebar-action:hover {
  background: var(--sidebar-link-hover-bg);
  color: var(--text-strong);
}

.sidebar-link.active {
  background: var(--sidebar-link-active-bg);
  color: var(--sidebar-link-active-text);
  font-weight: 600;
}

.sidebar-link:focus-visible,
.sidebar-action:focus-visible {
  outline-offset: -2px;
}

.sidebar-link svg,
.sidebar-action svg {
  flex: none;
}

.sidebar-link-text {
  min-width: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Footer widgets (language switcher, profile menu) open dropdowns, so it must never clip. */
.sidebar-footer {
  padding: var(--space-3);
  border-top: 1px solid var(--sidebar-border);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  overflow: visible;
}

.sidebar-actions {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

/* Footer widgets keep their own components; only their size is adapted to the sidebar. */
.sidebar .sidebar-footer .language-switcher,
.sidebar .sidebar-footer .profile-menu {
  width: 100%;
}

.sidebar .sidebar-footer .language-button,
.sidebar .sidebar-footer .profile-button {
  width: 100%;
  min-width: 0;
}

.sidebar .sidebar-footer .language-label,
.sidebar .sidebar-footer .profile-name {
  flex: 1;
  min-width: 0;
  text-align: left;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Collapsed icon rail. Desktop only: below 1024px the drawer is always full width. */
@media (min-width: 1024px) {
  .sidebar.collapsed .sidebar-brand-text,
  .sidebar.collapsed .sidebar-section-label,
  .sidebar.collapsed .sidebar-link-text,
  .sidebar.collapsed .sidebar-footer .language-label,
  .sidebar.collapsed .sidebar-footer .profile-name,
  .sidebar.collapsed .sidebar-footer .chevron {
    display: none;
  }

  .sidebar.collapsed .sidebar-link,
  .sidebar.collapsed .sidebar-action {
    justify-content: center;
    padding: var(--space-3);
  }

  .sidebar.collapsed .sidebar-brand {
    justify-content: center;
    padding-left: 0;
    padding-right: 0;
  }

  /* Hairline stands in for the hidden section labels. */
  .sidebar.collapsed .sidebar-section + .sidebar-section {
    margin-top: var(--space-3);
    padding-top: var(--space-3);
    border-top: 1px solid var(--sidebar-border);
  }

  .sidebar.collapsed .sidebar-footer .language-button,
  .sidebar.collapsed .sidebar-footer .profile-button {
    justify-content: center;
    padding: var(--space-2);
  }
}

/* Shared with the mobile top bar in App.vue. */
.icon-button {
  display: inline-grid;
  place-items: center;
  width: 2.25rem;
  height: 2.25rem;
  border: 0;
  border-radius: var(--radius-md);
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  transition: background-color var(--transition), color var(--transition);
}

.icon-button:hover {
  background: var(--surface-hover);
  color: var(--text-strong);
}

@media (prefers-reduced-motion: no-preference) and (max-width: 639px) {
  /* visibility is delayed on close so the drawer finishes sliding out before it is hidden. */
  .sidebar {
    transition: transform 200ms ease, visibility 0s linear 200ms;
  }

  .sidebar.open {
    transition: transform 200ms ease, visibility 0s;
  }
}

/* Tablet: always an icon rail docked in the grid. Same rail look as the desktop collapsed state,
   but keyed on :not(.open) so the persisted `collapsed` flag is irrelevant here. */
@media (min-width: 640px) and (max-width: 1023px) {
  .sidebar:not(.open) .sidebar-brand-text,
  .sidebar:not(.open) .sidebar-section-label,
  .sidebar:not(.open) .sidebar-link-text,
  .sidebar:not(.open) .sidebar-footer .language-label,
  .sidebar:not(.open) .sidebar-footer .profile-name,
  .sidebar:not(.open) .sidebar-footer .chevron {
    display: none;
  }

  .sidebar:not(.open) .sidebar-link,
  .sidebar:not(.open) .sidebar-action {
    justify-content: center;
    padding: var(--space-3);
  }

  .sidebar:not(.open) .sidebar-brand {
    justify-content: center;
    padding-left: 0;
    padding-right: 0;
  }

  .sidebar:not(.open) .sidebar-section + .sidebar-section {
    margin-top: var(--space-3);
    padding-top: var(--space-3);
    border-top: 1px solid var(--sidebar-border);
  }

  .sidebar:not(.open) .sidebar-footer .language-button,
  .sidebar:not(.open) .sidebar-footer .profile-button {
    justify-content: center;
    padding: var(--space-2);
  }

  /* Open = overlay: the sidebar stays in its sticky rail cell (so the grid and content do not
     shift) and simply grows wider, painting above the drawer overlay. */
  .sidebar.open {
    width: var(--sidebar-width);
    z-index: var(--z-drawer);
    box-shadow: var(--shadow-lg);
  }

  /* The footer toggle is the close control here. */
  .sidebar .sidebar-close {
    display: none;
  }
}

@media (min-width: 640px) and (max-width: 1023px) and (prefers-reduced-motion: no-preference) {
  .sidebar {
    transition: width 200ms ease;
  }
}

/* Phone: off-canvas drawer; the collapsed state is ignored. */
@media (max-width: 639px) {
  .sidebar,
  .sidebar.collapsed {
    position: fixed;
    inset: 0 auto 0 0;
    width: min(var(--sidebar-width), 86vw);
    transform: translateX(-100%);
    z-index: var(--z-drawer);
    box-shadow: var(--shadow-lg);
  }

  .sidebar.open {
    transform: translateX(0);
  }

  .sidebar .sidebar-close {
    display: inline-grid;
  }

  .sidebar .sidebar-collapse {
    display: none;
  }

  /* Keep a closed drawer out of the tab order and the accessibility tree. */
  .sidebar:not(.open) {
    visibility: hidden;
  }
}
</style>
