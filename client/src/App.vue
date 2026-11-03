<template>
  <div class="app">
    <div class="app-shell" :class="{ collapsed }">
      <AppSidebar>
        <template #footer>
          <LanguageSwitcher />
          <ProfileMenu
            @show-profile-details="showProfileDetails = true"
            @show-tasks="showTasks = true"
          />
        </template>
      </AppSidebar>
      <div v-if="mobileOpen" class="drawer-overlay" aria-hidden="true" @click="closeDrawer"></div>

      <div class="app-column">
        <header class="mobile-bar">
          <button
            type="button"
            class="icon-button"
            :aria-label="t('nav.openMenu')"
            @click="openDrawer"
          >
            <NavIcon name="menu" />
          </button>
          <span class="mobile-bar-title">{{ t('nav.companyName') }}</span>
        </header>
        <FilterBar />
        <main class="app-content">
          <router-view />
        </main>
      </div>
    </div>

    <ProfileDetailsModal
      :is-open="showProfileDetails"
      @close="showProfileDetails = false"
    />

    <TasksModal
      :is-open="showTasks"
      :tasks="tasks"
      @close="showTasks = false"
      @add-task="addTask"
      @delete-task="deleteTask"
      @toggle-task="toggleTask"
    />
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { api } from './api'
import { useAuth } from './composables/useAuth'
import { useI18n } from './composables/useI18n'
import { useShell } from './composables/useShell'
import AppSidebar from './components/AppSidebar.vue'
import NavIcon from './components/NavIcon'
import FilterBar from './components/FilterBar.vue'
import ProfileMenu from './components/ProfileMenu.vue'
import ProfileDetailsModal from './components/ProfileDetailsModal.vue'
import TasksModal from './components/TasksModal.vue'
import LanguageSwitcher from './components/LanguageSwitcher.vue'

export default {
  name: 'App',
  components: {
    AppSidebar,
    NavIcon,
    FilterBar,
    ProfileMenu,
    ProfileDetailsModal,
    TasksModal,
    LanguageSwitcher
  },
  setup() {
    const { currentUser } = useAuth()
    const { t } = useI18n()
    const route = useRoute()
    const { collapsed, mobileOpen, openDrawer, closeDrawer } = useShell()
    const showProfileDetails = ref(false)
    const showTasks = ref(false)
    const apiTasks = ref([])

    // Merge mock tasks from currentUser with API tasks
    const tasks = computed(() => {
      return [...currentUser.value.tasks, ...apiTasks.value]
    })

    const loadTasks = async () => {
      try {
        apiTasks.value = await api.getTasks()
      } catch (err) {
        console.error('Failed to load tasks:', err)
      }
    }

    const addTask = async (taskData) => {
      try {
        const newTask = await api.createTask(taskData)
        // Add new task to the beginning of the array
        apiTasks.value.unshift(newTask)
      } catch (err) {
        console.error('Failed to add task:', err)
      }
    }

    const deleteTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const isMockTask = currentUser.value.tasks.some(t => t.id === taskId)

        if (isMockTask) {
          // Remove from mock tasks
          const index = currentUser.value.tasks.findIndex(t => t.id === taskId)
          if (index !== -1) {
            currentUser.value.tasks.splice(index, 1)
          }
        } else {
          // Remove from API tasks
          await api.deleteTask(taskId)
          apiTasks.value = apiTasks.value.filter(t => t.id !== taskId)
        }
      } catch (err) {
        console.error('Failed to delete task:', err)
      }
    }

    const toggleTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const mockTask = currentUser.value.tasks.find(t => t.id === taskId)

        if (mockTask) {
          // Toggle mock task status
          mockTask.status = mockTask.status === 'pending' ? 'completed' : 'pending'
        } else {
          // Toggle API task
          const updatedTask = await api.toggleTask(taskId)
          const index = apiTasks.value.findIndex(t => t.id === taskId)
          if (index !== -1) {
            apiTasks.value[index] = updatedTask
          }
        }
      } catch (err) {
        console.error('Failed to toggle task:', err)
      }
    }

    // Navigating or pressing Escape closes the mobile drawer.
    watch(() => route.path, closeDrawer)

    const onKeydown = (event) => {
      if (event.key === 'Escape' && mobileOpen.value) closeDrawer()
    }

    onMounted(() => {
      loadTasks()
      window.addEventListener('keydown', onKeydown)
    })

    onBeforeUnmount(() => {
      window.removeEventListener('keydown', onKeydown)
    })

    return {
      t,
      collapsed,
      mobileOpen,
      openDrawer,
      closeDrawer,
      showProfileDetails,
      showTasks,
      tasks,
      addTask,
      deleteTask,
      toggleTask
    }
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-sans);
  background: var(--bg);
  color: var(--text);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Visible keyboard focus everywhere; outline follows each element's own border-radius. */
:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}

::placeholder {
  color: var(--text-faint);
}

/* Native controls follow the theme; scoped rules with more specificity still win. */
input,
select,
textarea {
  background-color: var(--surface);
  color: var(--text-strong);
}

/* ---------- Shell layout ---------- */

.app {
  min-height: 100vh;
  min-height: 100dvh;
}

.app-shell {
  --sidebar-current: var(--sidebar-width);
  display: grid;
  grid-template-columns: var(--sidebar-current) minmax(0, 1fr);
  min-height: 100vh;
  min-height: 100dvh;
}

.app-shell.collapsed {
  --sidebar-current: var(--sidebar-width-collapsed);
}

.app-shell > .sidebar {
  align-self: start;
}

/* --sticky-offset is the height of whatever sticks above the filter bar (0 on desktop). */
.app-column {
  --sticky-offset: 0px;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.app-content {
  flex: 1;
  width: 100%;
  max-width: var(--content-max-width);
  margin: 0 auto;
  padding: var(--space-6) var(--space-8);
}

.mobile-bar,
.drawer-overlay {
  display: none;
}

@media (prefers-reduced-motion: no-preference) {
  .app-shell {
    transition: grid-template-columns var(--transition);
  }
}

/* Tablet: the sidebar is a fixed icon rail; the persisted `collapsed` flag is ignored. */
@media (min-width: 640px) and (max-width: 1023px) {
  .app-shell,
  .app-shell.collapsed {
    --sidebar-current: var(--sidebar-width-collapsed);
  }

  .app-content {
    padding: var(--space-5) var(--space-6);
  }
}

/* Tablet overlay and phone drawer share the dimming layer. */
@media (max-width: 1023px) {
  .drawer-overlay {
    display: block;
    position: fixed;
    inset: 0;
    background: var(--overlay);
    z-index: var(--z-drawer-overlay);
  }
}

/* Phone: the sidebar is an off-canvas drawer opened from a top bar. */
@media (max-width: 639px) {
  .app-shell,
  .app-shell.collapsed {
    --sidebar-current: 0px;
    grid-template-columns: minmax(0, 1fr);
  }

  .app-column {
    --sticky-offset: var(--toolbar-height);
  }

  .mobile-bar {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    position: sticky;
    top: 0;
    z-index: var(--z-sticky);
    height: var(--toolbar-height);
    padding: 0 var(--space-4);
    background: var(--surface);
    border-bottom: 1px solid var(--border);
  }

  .mobile-bar-title {
    font-weight: 700;
    color: var(--text-strong);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .app-content {
    padding: var(--space-4);
  }
}

/* ---------- Shared components ---------- */

.page-header {
  margin-bottom: var(--space-6);
}

.page-header h2 {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--text-strong);
  margin-bottom: var(--space-1);
  letter-spacing: -0.02em;
}

.page-header p {
  color: var(--text-muted);
  font-size: var(--text-base);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--space-5);
  margin-bottom: var(--space-6);
}

.stat-card {
  background: var(--surface);
  padding: var(--space-5);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border);
  transition: border-color var(--transition);
}

.stat-card:hover {
  border-color: var(--border-strong);
}

.stat-label {
  color: var(--text-muted);
  font-size: var(--text-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: var(--space-2);
}

.stat-value {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--text-strong);
  letter-spacing: -0.02em;
  font-variant-numeric: tabular-nums;
}

.stat-card.warning .stat-value {
  color: var(--warning);
}

.stat-card.success .stat-value {
  color: var(--success);
}

.stat-card.danger .stat-value {
  color: var(--danger);
}

.stat-card.info .stat-value {
  color: var(--primary);
}

.card {
  background: var(--surface);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  border: 1px solid var(--border);
  margin-bottom: var(--space-5);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-4);
  margin-bottom: var(--space-4);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--border);
}

.card-title {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--text-strong);
  letter-spacing: -0.01em;
}

/* The content column is narrower than before, so wide tables scroll inside their card. */
.table-container {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: var(--surface-muted);
  border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
}

th {
  text-align: left;
  padding: var(--space-2) var(--space-3);
  font-weight: 600;
  color: var(--text-secondary);
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
}

td {
  padding: var(--space-2) var(--space-3);
  border-top: 1px solid var(--border);
  color: var(--text);
  font-size: var(--text-sm);
  font-variant-numeric: tabular-nums;
}

/* IDs and SKUs live in the first column; keep them on one line. */
td:first-child {
  white-space: nowrap;
}

tbody tr {
  transition: background-color var(--transition);
}

tbody tr:hover {
  background: var(--surface-hover);
}

.badge {
  display: inline-block;
  padding: 0.125rem var(--space-2);
  border-radius: 999px;
  font-size: var(--text-xs);
  font-weight: 600;
  line-height: 1.5;
  white-space: nowrap;
}

.badge.success,
.badge.increasing {
  background: var(--success-soft);
  color: var(--success-soft-text);
}

.badge.warning,
.badge.medium {
  background: var(--warning-soft);
  color: var(--warning-soft-text);
}

.badge.danger,
.badge.decreasing,
.badge.high {
  background: var(--danger-soft);
  color: var(--danger-soft-text);
}

.badge.info,
.badge.low {
  background: var(--primary-soft);
  color: var(--primary-soft-text);
}

.badge.stable {
  background: var(--accent-soft);
  color: var(--accent-soft-text);
}

.loading {
  text-align: center;
  padding: var(--space-10);
  color: var(--text-muted);
  font-size: var(--text-base);
}

.error {
  background: var(--danger-subtle);
  border: 1px solid var(--danger-soft);
  color: var(--danger-soft-text);
  padding: var(--space-4);
  border-radius: var(--radius-md);
  margin: var(--space-4) 0;
  font-size: var(--text-base);
}

/* Honor the OS setting: drop every transition and animation. */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    transition-duration: 0.01ms !important;
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
  }
}
</style>
