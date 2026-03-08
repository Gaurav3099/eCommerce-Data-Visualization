import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import type { RevenueByMonth } from '../types/api'

interface Props {
  data: RevenueByMonth[]
}

export function RevenueTrends({ data }: Props) {
  if (!data?.length) {
    return (
      <div className="chart-card">
        <h2>Revenue over time</h2>
        <p className="loading">No data</p>
      </div>
    )
  }

  return (
    <div className="chart-card">
      <h2>Revenue over time</h2>
      <ResponsiveContainer width="100%" height={360}>
        <LineChart data={data} margin={{ top: 8, right: 24, left: 8, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
          <XAxis dataKey="month" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} tickFormatter={(v) => `$${v}`} />
          <Tooltip formatter={(v: number) => [`$${Number(v).toLocaleString()}`, 'Revenue']} />
          <Line type="monotone" dataKey="revenue" stroke="#1473e6" strokeWidth={2} dot={{ r: 4 }} name="Revenue" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
