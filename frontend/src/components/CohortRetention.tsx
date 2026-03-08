import type { PivotData } from '../types/api'

interface Props {
  data: PivotData
}

function retentionColor(rate: number): string {
  if (rate <= 0) return 'rgb(255, 255, 255)'
  const g = Math.round(rate * 255)
  const r = Math.round((1 - rate) * 200)
  return `rgb(${r},${g},100)`
}

export function CohortRetention({ data }: Props) {
  const { rows, columns, data: values } = data

  if (!rows?.length || !columns?.length) {
    return (
      <div className="chart-card">
        <h2>Cohort retention</h2>
        <p className="loading">No cohort data</p>
      </div>
    )
  }

  return (
    <div className="chart-card">
      <h2>Cohort retention (by first purchase month)</h2>
      <p style={{ margin: '0 0 1rem', fontSize: 14, color: '#666' }}>
        Share of users from each cohort who made a purchase in that month.
      </p>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ borderCollapse: 'collapse', width: '100%', fontSize: 12 }}>
          <thead>
            <tr>
              <th style={{ padding: 6, textAlign: 'left' }}>Cohort</th>
              {columns.map((c) => (
                <th key={c} style={{ padding: 6 }}>
                  Month {c}
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
                      padding: 6,
                      backgroundColor: retentionColor(Number(v)),
                      textAlign: 'center',
                      minWidth: 56,
                    }}
                    title={`${row}, month ${columns[j]}: ${(Number(v) * 100).toFixed(0)}%`}
                  >
                    {Number(v) > 0 ? `${(Number(v) * 100).toFixed(0)}%` : '—'}
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
