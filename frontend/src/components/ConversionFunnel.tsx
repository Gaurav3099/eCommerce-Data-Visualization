import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts'
import type { ConversionFunnelStage } from '../types/api'

const COLORS = ['#1473e6', '#0d5bb7', '#094089']

interface Props {
  data: ConversionFunnelStage[]
}

export function ConversionFunnel({ data }: Props) {
  if (!data?.length) {
    return (
      <div className="chart-card">
        <h2>Conversion funnel</h2>
        <p className="loading">No funnel data (event_type view/cart/purchase required)</p>
      </div>
    )
  }

  const chartData = [...data].reverse().map((d) => ({
    stage: d.stage.charAt(0).toUpperCase() + d.stage.slice(1),
    users: d.users,
    sessions: d.sessions,
  }))

  return (
    <div className="chart-card">
      <h2>Conversion funnel (users by stage)</h2>
      <ResponsiveContainer width="100%" height={360}>
        <BarChart data={chartData} layout="vertical" margin={{ top: 8, right: 24, left: 80, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#eee" horizontal={false} />
          <XAxis type="number" tick={{ fontSize: 12 }} />
          <YAxis type="category" dataKey="stage" width={70} tick={{ fontSize: 12 }} />
          <Tooltip
            formatter={(value: number, name: string) => [value.toLocaleString(), name]}
            labelFormatter={(l) => l}
          />
          <Bar dataKey="users" name="Users" radius={[0, 4, 4, 0]}>
            {chartData.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
