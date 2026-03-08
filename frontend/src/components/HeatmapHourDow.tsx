import type { PivotData } from '../types/api'

interface Props {
  data: PivotData
}

function getColor(value: number, max: number): string {
  if (max <= 0) return 'rgb(255, 255, 255)'
  const t = value / max
  const r = Math.round(255 - t * 200)
  const g = Math.round(255 - t * 150)
  const b = Math.round(255 - t * 50)
  return `rgb(${r},${g},${b})`
}

export function HeatmapHourDow({ data }: Props) {
  const { rows, columns, data: values } = data
  const max = values.length
    ? Math.max(...values.flat().map(Number))
    : 0

  if (!rows?.length || !columns?.length) {
    return (
      <div className="chart-card">
        <h2>Purchase behavior by hour & day of week</h2>
        <p className="loading">No heatmap data</p>
      </div>
    )
  }

  return (
    <div className="chart-card">
      <h2>Purchase behavior by hour & day of week</h2>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ borderCollapse: 'collapse', width: '100%', fontSize: 12 }}>
          <thead>
            <tr>
              <th style={{ padding: 6, textAlign: 'left' }}>Hour</th>
              {columns.map((c) => (
                <th key={c} style={{ padding: 6 }}>
                  {c}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr key={row}>
                <td style={{ padding: 4, fontWeight: 500 }}>{row}</td>
                {(values[i] || []).map((v, j) => (
                  <td
                    key={j}
                    style={{
                      padding: 4,
                      backgroundColor: getColor(Number(v), max),
                      minWidth: 28,
                      textAlign: 'center',
                    }}
                    title={`${row} ${columns[j]}: ${v}`}
                  >
                    {Number(v) > 0 ? v : ''}
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
