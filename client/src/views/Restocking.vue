<template>
  <div class="restocking">
    <div class="page-header">
      <h2>{{ t('restocking.title') }}</h2>
      <p>{{ t('restocking.description') }}</p>
    </div>

    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="eligibleItems.length === 0" class="card empty-state">
      <p class="empty-title">{{ t('restocking.noForecasts') }}</p>
      <p class="empty-hint">{{ t('restocking.noForecastsHint') }}</p>
    </div>
    <div v-else>
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.budget') }}</h3>
        </div>
        <div class="budget-value">{{ formatMoney(budget, 0) }}</div>
        <input
          v-model.number="budget"
          class="budget-slider"
          type="range"
          min="0"
          :max="maxBudget"
          :step="BUDGET_STEP"
          :disabled="submitting"
          :aria-label="t('restocking.budget')"
        />
        <div class="budget-range">
          <span>{{ formatMoney(0, 0) }}</span>
          <span>{{ formatMoney(maxBudget, 0) }}</span>
        </div>
        <p class="budget-hint">{{ t('restocking.budgetHint') }}</p>
      </div>

      <div class="summary-grid">
        <div class="stat-card">
          <div class="stat-label">{{ t('restocking.totalSpend') }}</div>
          <div class="stat-value">{{ formatMoney(totalSpend) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">{{ t('restocking.remainingBudget') }}</div>
          <div class="stat-value">{{ formatMoney(remainingBudget) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">{{ t('restocking.itemsToOrder') }}</div>
          <div class="stat-value">{{ recommendedItems.length }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">{{ t('restocking.orderLeadTime') }}</div>
          <div class="stat-value">{{ orderLeadTimeDays === null ? '-' : t('restocking.days', { count: orderLeadTimeDays }) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">{{ t('restocking.expectedDelivery') }}</div>
          <div class="stat-value stat-value-date">{{ expectedDeliveryDate ? formatDate(expectedDeliveryDate) : '-' }}</div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.recommendedItems') }} ({{ recommendedItems.length }})</h3>
          <button
            type="button"
            class="place-order-btn"
            :disabled="recommendedItems.length === 0 || submitting"
            @click="placeOrder"
          >
            {{ submitting ? t('restocking.placingOrder') : t('restocking.placeOrder') }}
          </button>
        </div>

        <div v-if="orderError" class="error" role="alert">{{ orderError }}</div>

        <div v-if="orderResult" class="success-banner" role="status">
          <div class="success-title">{{ t('restocking.orderPlaced') }}</div>
          <div class="success-details">
            <span>{{ t('orders.table.orderNumber') }}: <strong>{{ orderResult.order_number }}</strong></span>
            <span>{{ t('orders.table.totalValue') }}: <strong>{{ formatMoney(orderResult.total_value) }}</strong></span>
            <span>{{ t('restocking.orderLeadTime') }}: <strong>{{ t('restocking.days', { count: orderResult.lead_time_days }) }}</strong></span>
            <span>{{ t('restocking.expectedDelivery') }}: <strong>{{ formatDate(orderResult.expected_delivery) }}</strong></span>
          </div>
          <router-link to="/orders" class="success-link">{{ t('restocking.viewInOrders') }}</router-link>
        </div>

        <div v-if="recommendedItems.length === 0" class="empty-state">
          <p class="empty-title">{{ t('restocking.budgetTooLow') }}</p>
          <p class="empty-hint">{{ t('restocking.budgetTooLowHint') }}</p>
        </div>
        <div v-else class="table-container">
          <table>
            <thead>
              <tr>
                <th>{{ t('demand.table.sku') }}</th>
                <th>{{ t('demand.table.itemName') }}</th>
                <th>{{ t('restocking.table.supplier') }}</th>
                <th>{{ t('demand.table.change') }}</th>
                <th>{{ t('restocking.table.quantity') }}</th>
                <th>{{ t('restocking.table.unitCost') }}</th>
                <th>{{ t('restocking.table.lineCost') }}</th>
                <th>{{ t('restocking.table.leadTime') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in recommendedItems" :key="item.item_sku">
                <td><strong>{{ item.item_sku }}</strong></td>
                <td>{{ translateProductName(item.item_name) }}</td>
                <td>{{ item.supplier_name }}</td>
                <td>
                  <span :style="{ color: getChangeColor(item) }">{{ getChangePercent(item) }}</span>
                </td>
                <td>{{ item.quantity }}</td>
                <td>{{ formatMoney(item.unit_cost) }}</td>
                <td><strong>{{ formatMoney(item.lineCost) }}</strong></td>
                <td>{{ item.lead_time_days }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-if="skippedItems.length > 0" class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.notAffordable') }} ({{ skippedItems.length }})</h3>
        </div>
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>{{ t('demand.table.sku') }}</th>
                <th>{{ t('demand.table.itemName') }}</th>
                <th>{{ t('restocking.table.lineCost') }}</th>
                <th>{{ t('orders.table.status') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in skippedItems" :key="item.item_sku">
                <td><strong>{{ item.item_sku }}</strong></td>
                <td>{{ translateProductName(item.item_name) }}</td>
                <td>{{ formatMoney(item.lineCost) }}</td>
                <td><span class="badge danger">{{ t('restocking.overBudget') }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <p v-if="excludedCount > 0" class="excluded-note">
        {{ t('restocking.excludedDecreasing', { count: excludedCount }) }}
      </p>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue'
import { api } from '../api'
import { useI18n } from '../composables/useI18n'

const BUDGET_STEP = 100

// Work in integer cents to avoid floating point drift when summing line costs
const toCents = (amount) => Math.round(amount * 100)

export default {
  name: 'Restocking',
  setup() {
    const { t, currentLocale, currentCurrency, translateProductName } = useI18n()

    // Same convention as Orders/Inventory: symbol only, no conversion
    const currencySymbol = computed(() => {
      return currentCurrency.value === 'JPY' ? '¥' : '$'
    })

    const loading = ref(true)
    const error = ref(null)
    const forecasts = ref([])
    const budget = ref(0)

    const submitting = ref(false)
    const orderError = ref(null)
    const orderResult = ref(null)

    const isValidForecast = (f) => {
      return Number.isFinite(f.forecasted_demand) &&
        f.forecasted_demand > 0 &&
        Number.isFinite(f.unit_cost) &&
        f.unit_cost >= 0
    }

    // Decreasing items are never recommended
    const eligibleItems = computed(() => {
      return forecasts.value.filter(f => f.trend !== 'decreasing' && isValidForecast(f))
    })

    const excludedCount = computed(() => {
      return forecasts.value.filter(f => f.trend === 'decreasing').length
    })

    // Growth ratio used for ranking; zero current demand ranks first
    const getGrowth = (f) => {
      if (!(f.current_demand > 0)) return Infinity
      return (f.forecasted_demand - f.current_demand) / f.current_demand
    }

    const rankedItems = computed(() => {
      return eligibleItems.value
        .map(f => ({
          ...f,
          quantity: Math.round(f.forecasted_demand),
          lineCost: Math.round(f.forecasted_demand) * f.unit_cost,
          growth: getGrowth(f)
        }))
        .sort((a, b) => {
          if (a.growth !== b.growth) return b.growth - a.growth
          return a.item_sku.localeCompare(b.item_sku)
        })
    })

    // Cost of ordering every eligible item, rounded up to the slider step
    const maxBudget = computed(() => {
      const totalCents = rankedItems.value.reduce((sum, item) => sum + toCents(item.lineCost), 0)
      return Math.max(BUDGET_STEP, Math.ceil(totalCents / 100 / BUDGET_STEP) * BUDGET_STEP)
    })

    // Greedy fill: take an item if it fits the remaining budget, otherwise skip and keep going
    const recommendation = computed(() => {
      let remainingCents = toCents(Number(budget.value) || 0)
      const recommended = []
      const skipped = []

      for (const item of rankedItems.value) {
        const costCents = toCents(item.lineCost)
        if (costCents <= remainingCents) {
          recommended.push(item)
          remainingCents -= costCents
        } else {
          skipped.push(item)
        }
      }

      return { recommended, skipped }
    })

    const recommendedItems = computed(() => recommendation.value.recommended)
    const skippedItems = computed(() => recommendation.value.skipped)

    const totalSpend = computed(() => {
      return recommendedItems.value.reduce((sum, item) => sum + toCents(item.lineCost), 0) / 100
    })

    const remainingBudget = computed(() => {
      return (toCents(Number(budget.value) || 0) - toCents(totalSpend.value)) / 100
    })

    const orderLeadTimeDays = computed(() => {
      if (recommendedItems.value.length === 0) return null
      return Math.max(...recommendedItems.value.map(item => Number(item.lead_time_days) || 0))
    })

    const expectedDeliveryDate = computed(() => {
      if (orderLeadTimeDays.value === null) return null
      const date = new Date()
      date.setDate(date.getDate() + orderLeadTimeDays.value)
      return date
    })

    const formatMoney = (value, decimals = 2) => {
      const amount = Number(value)
      if (!Number.isFinite(amount)) return '-'
      return `${currencySymbol.value}${amount.toLocaleString(undefined, {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
      })}`
    }

    const formatDate = (value) => {
      const date = value instanceof Date ? value : new Date(value)
      if (isNaN(date.getTime())) return '-'
      const locale = currentLocale.value === 'ja' ? 'ja-JP' : 'en-US'
      return date.toLocaleDateString(locale, {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    // Sign/color convention matches Demand.vue
    const getChangePercent = (item) => {
      if (!(item.current_demand > 0)) return '-'
      const change = ((item.forecasted_demand - item.current_demand) / item.current_demand * 100).toFixed(1)
      return (change > 0 ? `+${change}` : change) + '%'
    }

    const getChangeColor = (item) => {
      if (!(item.current_demand > 0)) return '#64748b'
      const change = item.forecasted_demand - item.current_demand
      const changePercent = Math.abs((change / item.current_demand) * 100)

      if (changePercent <= 2) return '#3b82f6'
      if (change > 0) return '#10b981'
      if (change < 0) return '#ef4444'
      return '#3b82f6'
    }

    const loadForecasts = async () => {
      try {
        loading.value = true
        error.value = null
        forecasts.value = await api.getDemandForecasts()
        // Default the slider to roughly half of the maximum budget
        budget.value = Math.round(maxBudget.value / 2 / BUDGET_STEP) * BUDGET_STEP
      } catch (err) {
        error.value = 'Failed to load demand forecasts: ' + err.message
      } finally {
        loading.value = false
      }
    }

    // A previous confirmation or error no longer applies once the budget changes
    watch(budget, () => {
      if (!submitting.value) {
        orderError.value = null
        orderResult.value = null
      }
    })

    const placeOrder = async () => {
      if (submitting.value || recommendedItems.value.length === 0) return

      submitting.value = true
      orderError.value = null
      orderResult.value = null

      // Prices are looked up by the server; only SKU and quantity are sent
      const payload = {
        budget: Number(budget.value),
        items: recommendedItems.value.map(item => ({
          sku: item.item_sku,
          quantity: item.quantity
        }))
      }

      try {
        orderResult.value = await api.createRestockingOrder(payload)
      } catch (err) {
        orderError.value = err.response?.data?.detail || err.message
      } finally {
        submitting.value = false
      }
    }

    onMounted(loadForecasts)

    return {
      t,
      BUDGET_STEP,
      loading,
      error,
      budget,
      maxBudget,
      eligibleItems,
      excludedCount,
      recommendedItems,
      skippedItems,
      totalSpend,
      remainingBudget,
      orderLeadTimeDays,
      expectedDeliveryDate,
      submitting,
      orderError,
      orderResult,
      formatMoney,
      formatDate,
      getChangePercent,
      getChangeColor,
      translateProductName,
      placeOrder
    }
  }
}
</script>

<style scoped>
.budget-value {
  font-size: 2.25rem;
  font-weight: 700;
  color: var(--text-strong);
  letter-spacing: -0.025em;
  margin-bottom: 0.75rem;
}

.budget-slider {
  width: 100%;
  accent-color: var(--text-strong);
  cursor: pointer;
}

.budget-slider:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.budget-range {
  display: flex;
  justify-content: space-between;
  font-size: 0.813rem;
  color: var(--text-muted);
  margin-top: 0.25rem;
}

.budget-hint {
  margin-top: 0.75rem;
  font-size: 0.813rem;
  color: var(--text-muted);
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.25rem;
  margin-bottom: 1.25rem;
}

.stat-value-date {
  font-size: 1.5rem;
  line-height: 2.7rem;
}

.place-order-btn {
  /* Inverted pair: dark fill with light text in light mode, light fill with dark text in dark mode. */
  background: var(--text-strong);
  color: var(--surface);
  border: none;
  border-radius: 8px;
  padding: 0.5rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.place-order-btn:hover:not(:disabled) {
  background: var(--text);
}

.place-order-btn:disabled {
  background: var(--border-strong);
  color: var(--text-muted);
  cursor: not-allowed;
}

.success-banner {
  background: var(--success-subtle);
  border: 1px solid var(--success-soft);
  color: var(--success-soft-text);
  padding: 1rem;
  border-radius: 8px;
  margin: 0 0 1rem;
  font-size: 0.938rem;
}

.success-title {
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.success-details {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 1.5rem;
  margin-bottom: 0.75rem;
}

.success-link {
  color: var(--success-soft-text);
  font-weight: 600;
  text-decoration: underline;
}

.empty-state {
  text-align: center;
  padding: 2rem 1rem;
}

.empty-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-strong);
}

.empty-hint {
  margin-top: 0.25rem;
  font-size: 0.875rem;
  color: var(--text-muted);
}

.excluded-note {
  font-size: 0.813rem;
  color: var(--text-muted);
  margin-bottom: 1.25rem;
}
</style>
