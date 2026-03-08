import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import type { CustomerSegment } from '../types/api'

interface Props {
  data: CustomerSegment[]
}

export function CustomerSegments({ data }: Props) {
  if (!data?.length) {
    return (
      <div className="chart-card">
        <h2>Customer segmentation</h2>
        <p className="loading">No segment data</p>
      </div>
    )
  }

  return (
    <div className="chart-card">
      <h2>Customer segmentation</h2>
      <ResponsiveContainer width="100%" height={360}>
        <BarChart data={data} margin={{ top: 8, right: 24, left: 8, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
          <XAxis dataKey="segment" tick={{ fontSize: 12 }} />
          <YAxis yAxisId="left" tick={{ fontSize: 12 }} />
          <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 12 }} tickFormatter={(v) => `$${v}`} />
          <Tooltip
            formatter={(value: number, name: string) =>
              [name === 'Revenue' ? `$${Number(value).toLocaleString()}` : value, name]
            }
          />
          <Legend />
          <Bar yAxisId="left" dataKey="users" fill="#1473e6" name="Users" radius={[4, 4, 0, 0]} />
          <Bar yAxisId="right" dataKey="revenue" fill="#0d5bb7" name="Revenue" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
