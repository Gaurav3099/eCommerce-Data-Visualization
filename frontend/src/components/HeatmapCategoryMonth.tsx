import type { PivotData } from '../types/api'

interface Props {
  data: PivotData
}

function getColor(value: number, max: number): string {
  if (max <= 0) return 'rgb(240, 248, 255)'
  const t = value / max
  const r = Math.round(240 - t * 200)
  const g = Math.round(248 - t * 200)
  const b = 255
  return `rgb(${r},${g},${b})`
}

export function HeatmapCategoryMonth({ data }: Props) {
  const { rows, columns, data: values } = data
  const max = values.length ? Math.max(...values.flat().map(Number)) : 0

  if (!rows?.length || !columns?.length) {
    return (
      <div className="chart-card">
        <h2>Revenue by category & month</h2>
        <p className="loading">No heatmap data</p>
      </div>
    )
  }

  return (
    <div className="chart-card">
      <h2>Revenue by category & month</h2>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ borderCollapse: 'collapse', width: '100%', fontSize: 11 }}>
          <thead>
            <tr>
              <th style={{ padding: 6, textAlign: 'left', maxWidth: 120 }}>Category</th>
              {columns.map((c) => (
                <th key={c} style={{ padding: 6, minWidth: 60 }}>
                  {c}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr key={row}>
                <td style={{ padding: 4, fontWeight: 500 }} title={row}>
                  {row.length > 25 ? row.slice(0, 25) + '…' : row}
                </td>
                {(values[i] || []).map((v, j) => (
                  <td
                    key={j}
                    style={{
                      padding: 4,
                      backgroundColor: getColor(Number(v), max),
                      textAlign: 'right',
                    }}
                    title={`${row} ${columns[j]}: $${Number(v).toLocaleString()}`}
                  >
                    {Number(v) > 0 ? `$${Number(v).toLocaleString()}` : ''}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
