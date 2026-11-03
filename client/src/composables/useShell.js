import { ref, watch } from 'vue'

// Storage can throw (private windows, blocked storage), so every access is guarded.
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
    // The UI still works without storage; it just will not remember the choice.
  }
}

const prefersDark = window.matchMedia('(prefers-color-scheme: dark)')

// Module-level refs share shell state across components without a store.
const collapsed = ref(read('sidebar-collapsed', 'false') === 'true')
const mobileOpen = ref(false)
const theme = ref(
  document.documentElement.dataset.theme || (prefersDark.matches ? 'dark' : 'light')
)

watch(collapsed, (value) => write('sidebar-collapsed', String(value)))

// Tablet = 640px-1023px (must match the CSS breakpoints). JS only needs it to pick what the
// footer toggle does and to reset the overlay; layout itself is pure CSS media queries.
const tabletQuery = window.matchMedia('(min-width: 640px) and (max-width: 1023px)')
const isTablet = ref(tabletQuery.matches)

// Fires when crossing either edge of the tablet range, i.e. every tier change. Closing here
// avoids an overlay left open with no matching sidebar, or a stuck drawer after a resize.
tabletQuery.addEventListener('change', (event) => {
  isTablet.value = event.matches
  mobileOpen.value = false
})

// Without an explicit choice the CSS follows the OS, so keep the toggle icon in step with it.
prefersDark.addEventListener('change', (event) => {
  if (!document.documentElement.dataset.theme) {
    theme.value = event.matches ? 'dark' : 'light'
  }
})

export function useShell() {
  const toggleTheme = () => {
    const next = theme.value === 'dark' ? 'light' : 'dark'
    theme.value = next
    document.documentElement.dataset.theme = next
    // Only an explicit toggle is persisted; an unset theme keeps following the OS.
    write('theme', next)
  }

  return {
    collapsed,
    mobileOpen,
    isTablet,
    theme,
    toggleCollapsed: () => { collapsed.value = !collapsed.value },
    // On tablet the rail is fixed, so the toggle opens the temporary overlay and leaves the
    // persisted desktop `collapsed` preference untouched.
    toggleSidebar: () => {
      if (isTablet.value) mobileOpen.value = !mobileOpen.value
      else collapsed.value = !collapsed.value
    },
    openDrawer: () => { mobileOpen.value = true },
    closeDrawer: () => { mobileOpen.value = false },
    toggleTheme
  }
}
