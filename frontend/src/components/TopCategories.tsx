import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import type { TopCategory } from '../types/api'

interface Props {
  data: TopCategory[]
}

export function TopCategories({ data }: Props) {
  if (!data?.length) {
    return (
      <div className="chart-card">
        <h2>Top categories by revenue</h2>
        <p className="loading">No category data</p>
      </div>
    )
  }

  const chartData = data.slice(0, 15).map((d) => ({
    ...d,
    label: d.category.length > 40 ? d.category.slice(0, 40) + '…' : d.category,
  }))

  return (
    <div className="chart-card">
      <h2>Top categories by revenue</h2>
      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={chartData} layout="vertical" margin={{ top: 8, right: 24, left: 8, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#eee" horizontal={false} />
          <XAxis type="number" tick={{ fontSize: 12 }} tickFormatter={(v) => `$${v}`} />
          <YAxis type="category" dataKey="label" width={180} tick={{ fontSize: 11 }} />
          <Tooltip
            formatter={(value: number) => [`$${Number(value).toLocaleString()}`, 'Revenue']}
            labelFormatter={(_, payload) => payload?.[0]?.payload?.category ?? _}
          />
          <Bar dataKey="revenue" fill="#1473e6" name="Revenue" radius={[0, 4, 4, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
