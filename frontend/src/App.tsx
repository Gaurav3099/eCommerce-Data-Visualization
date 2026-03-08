import { useState, useEffect, useCallback } from 'react'
import { fetchData, fetchCategories } from './api/client'
import type { ApiData } from './types/api'
import { RevenueTrends } from './components/RevenueTrends'
import { ConversionFunnel } from './components/ConversionFunnel'
import { CustomerSegments } from './components/CustomerSegments'
import { TopCategories } from './components/TopCategories'
import { HeatmapHourDow } from './components/HeatmapHourDow'
import { HeatmapCategoryMonth } from './components/HeatmapCategoryMonth'
import { CohortRetention } from './components/CohortRetention'

type TabId = 'revenue' | 'funnel' | 'segments' | 'categories' | 'heatmaps' | 'cohort'

const TABS: { id: TabId; label: string }[] = [
  { id: 'revenue', label: 'Revenue trends' },
  { id: 'funnel', label: 'Conversion funnel' },
  { id: 'segments', label: 'Customer segmentation' },
  { id: 'categories', label: 'Top categories' },
  { id: 'heatmaps', label: 'Purchase heatmaps' },
  { id: 'cohort', label: 'Cohort retention' },
]

export default function App() {
  const [data, setData] = useState<ApiData | null>(null)
  const [categories, setCategories] = useState<string[]>([])
  const [selectedCategories, setSelectedCategories] = useState<string[]>([])
  const [tab, setTab] = useState<TabId>('revenue')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadCategories = useCallback(async () => {
    try {
      const list = await fetchCategories()
      setCategories(list)
    } catch {
      setCategories([])
    }
  }, [])

  const loadData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await fetchData({
        nrows: 100_000,
        categories: selectedCategories.length ? selectedCategories : undefined,
      })
      setData(result)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load data')
      setData(null)
    } finally {
      setLoading(false)
    }
  }, [selectedCategories])

  useEffect(() => {
    loadCategories()
  }, [loadCategories])

  useEffect(() => {
    loadData()
  }, [loadData])

  const handleCategoryChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = e.target.value
    if (!val) {
      setSelectedCategories([])
      return
    }
    const selected = Array.from(e.target.selectedOptions, (o) => o.value)
    setSelectedCategories(selected)
  }

  return (
    <div className="app">
      <header className="header">
        <h1>E-commerce Analytics</h1>
        <div className="filters">
          <label htmlFor="cat-filter">Category filter</label>
          <select
            id="cat-filter"
            multiple
            value={selectedCategories}
            onChange={handleCategoryChange}
            size={Math.min(6, Math.max(2, categories.length || 1))}
          >
            {categories.map((c) => (
              <option key={c} value={c}>
                {c.length > 45 ? c.slice(0, 45) + '…' : c}
              </option>
            ))}
          </select>
          <button type="button" onClick={loadData} style={{ padding: '0.4rem 0.8rem', borderRadius: 6, border: 'none', cursor: 'pointer', background: 'rgba(255,255,255,0.2)' }}>
            Refresh
          </button>
        </div>
      </header>

      <main className="content">
        <div className="tabs">
          {TABS.map(({ id, label }) => (
            <button
              key={id}
              type="button"
              className={tab === id ? 'active' : ''}
              onClick={() => setTab(id)}
            >
              {label}
            </button>
          ))}
        </div>

        {loading && <div className="loading">Loading data…</div>}
        {error && <div className="error">{error}</div>}
        {!loading && !error && data && (
          <>
            {tab === 'revenue' && <RevenueTrends data={data.revenue_by_month} />}
            {tab === 'funnel' && <ConversionFunnel data={data.conversion_funnel} />}
            {tab === 'segments' && <CustomerSegments data={data.customer_segments} />}
            {tab === 'categories' && <TopCategories data={data.top_categories_revenue} />}
            {tab === 'heatmaps' && (
              <div className="heatmaps-grid">
                <HeatmapHourDow data={data.heatmap_hour_dow} />
                <HeatmapCategoryMonth data={data.heatmap_category_month} />
              </div>
            )}
            {tab === 'cohort' && <CohortRetention data={data.cohort_retention} />}
          </>
        )}
      </main>
    </div>
  )
}
