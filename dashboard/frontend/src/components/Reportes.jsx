import React, { useEffect, useState } from 'react'
import axios from 'axios'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend, LineChart, Line, Area, AreaChart
} from 'recharts'
import {
  FiBarChart2, FiTrendingUp, FiAlertCircle, FiBook,
  FiUsers, FiDollarSign, FiRefreshCw, FiClock, FiCheckCircle
} from 'react-icons/fi'

const COLORS = ['#6366f1', '#f59e0b', '#10b981', '#ef4444', '#3b82f6', '#8b5cf6']

const CustomTooltip = ({ active, payload, label, prefix = '' }) => {
  if (active && payload && payload.length) {
    return (
      <div className="r-tooltip">
        {label && <p className="r-tooltip-label">{label}</p>}
        {payload.map((p, i) => (
          <p key={i} style={{ color: p.color || p.fill }}>
            {p.name}: <strong>{prefix}{p.value}</strong>
          </p>
        ))}
      </div>
    )
  }
  return null
}

const CustomPieLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }) => {
  const RADIAN = Math.PI / 180
  const radius = innerRadius + (outerRadius - innerRadius) * 0.5
  const x = cx + radius * Math.cos(-midAngle * RADIAN)
  const y = cy + radius * Math.sin(-midAngle * RADIAN)
  if (percent < 0.05) return null
  return (
    <text x={x} y={y} fill="white" textAnchor="middle" dominantBaseline="central" fontSize={13} fontWeight={600}>
      {`${(percent * 100).toFixed(0)}%`}
    </text>
  )
}

function Reportes() {
  const [data, setData] = useState({})
  const [loading, setLoading] = useState(true)
  const [lastUpdate, setLastUpdate] = useState(null)
  const [refreshing, setRefreshing] = useState(false)

  const fetchAll = () => {
    setRefreshing(true)
    Promise.all([
      axios.get('/api/reportes/prestamos-activos'),
      axios.get('/api/reportes/multas-pendientes'),
      axios.get('/api/reportes/libros-mas-prestados'),
      axios.get('/api/reportes/lectores-con-multas'),
    ]).then(([prestamos, multas, libros, lectores]) => {
      setData({
        prestamos: prestamos.data,
        multas: multas.data,
        libros: libros.data,
        lectores: lectores.data,
      })
      setLastUpdate(new Date())
      setLoading(false)
      setRefreshing(false)
    }).catch(() => { setLoading(false); setRefreshing(false) })
  }

  useEffect(() => { fetchAll() }, [])

  // Pie data: estado de multas
  const multasPieData = [
    { name: 'Pendientes', value: data.multas?.total_multas_pendientes || 0 },
    { name: 'Recaudado (S/)', value: Math.round(data.multas?.monto_total || 0) },
  ].filter(d => d.value > 0)

  // Bar data: libros más prestados
  const librosBar = (data.libros || []).map(l => ({
    titulo: l.titulo.length > 20 ? l.titulo.substring(0, 18) + '…' : l.titulo,
    tituloFull: l.titulo,
    prestamos: l.total
  }))

  // Bar data: lectores con multas
  const lectoresBar = (data.lectores || []).map(l => ({
    nombre: l.lector.split(' ')[0],
    nombreFull: l.lector,
    multas: l.multas
  }))

  if (loading) {
    return (
      <div className="m-page">
        <div className="m-loading" style={{ height: '60vh' }}>
          <div className="m-spinner" />
          <span>Cargando reportes...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="m-page">

      {/* ── Header ── */}
      <div className="m-header">
        <div className="m-header-left">
          <div className="m-header-icon reportes-icon">
            <FiBarChart2 size={22} />
          </div>
          <div>
            <h1 className="m-title">Reportes y Estadísticas</h1>
            <p className="m-subtitle">
              {lastUpdate && (
                <><FiClock size={12} style={{ marginRight: 4 }} />
                Actualizado {lastUpdate.toLocaleTimeString('es-PE')}</>
              )}
            </p>
          </div>
        </div>
        <button className={`m-btn-ghost ${refreshing ? 'spinning' : ''}`} onClick={fetchAll} disabled={refreshing}>
          <FiRefreshCw size={15} />
          {refreshing ? 'Actualizando...' : 'Actualizar'}
        </button>
      </div>

      {/* ── KPI Cards ── */}
      <div className="m-kpi-grid r-kpi-grid">
        <div className="m-kpi-card kpi-indigo">
          <div className="m-kpi-icon"><FiBook size={20} /></div>
          <div>
            <div className="m-kpi-value">{data.prestamos?.total_prestamos_activos ?? '—'}</div>
            <div className="m-kpi-label">Préstamos Activos</div>
          </div>
        </div>
        <div className="m-kpi-card kpi-red">
          <div className="m-kpi-icon"><FiAlertCircle size={20} /></div>
          <div>
            <div className="m-kpi-value">{data.multas?.total_multas_pendientes ?? '—'}</div>
            <div className="m-kpi-label">Multas Pendientes</div>
          </div>
        </div>
        <div className="m-kpi-card kpi-amber">
          <div className="m-kpi-icon"><FiDollarSign size={20} /></div>
          <div>
            <div className="m-kpi-value">S/ {Number(data.multas?.monto_total || 0).toFixed(2)}</div>
            <div className="m-kpi-label">Monto por Cobrar</div>
          </div>
        </div>
        <div className="m-kpi-card kpi-green">
          <div className="m-kpi-icon"><FiUsers size={20} /></div>
          <div>
            <div className="m-kpi-value">{data.lectores?.length ?? '—'}</div>
            <div className="m-kpi-label">Lectores con Multas</div>
          </div>
        </div>
      </div>

      {/* ── Charts Grid ── */}
      <div className="r-charts-grid">

        {/* ── Chart 1: Libros más prestados (Bar) ── */}
        <div className="r-chart-card r-span-2">
          <div className="r-chart-header">
            <div className="r-chart-title">
              <FiBook size={16} className="r-chart-icon indigo" />
              Top 5 Libros Más Prestados
            </div>
            <span className="r-chart-badge">{librosBar.length} libros</span>
          </div>
          {librosBar.length === 0 ? (
            <div className="r-empty-chart">
              <FiBook size={32} />
              <p>Sin datos de préstamos</p>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={librosBar} margin={{ top: 10, right: 20, left: 0, bottom: 60 }}>
                <defs>
                  <linearGradient id="barGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.9} />
                    <stop offset="95%" stopColor="#818cf8" stopOpacity={0.7} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                <XAxis dataKey="titulo" tick={{ fill: '#64748b', fontSize: 12 }}
                  angle={-35} textAnchor="end" interval={0} />
                <YAxis tick={{ fill: '#64748b', fontSize: 12 }} allowDecimals={false} />
                <Tooltip content={<CustomTooltip />}
                  formatter={(val, name, props) => [val, props.payload.tituloFull]} />
                <Bar dataKey="prestamos" fill="url(#barGrad)" radius={[6, 6, 0, 0]} maxBarSize={60}
                  label={{ position: 'top', fill: '#6366f1', fontSize: 13, fontWeight: 700 }} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* ── Chart 2: Estado de multas (Pie) ── */}
        <div className="r-chart-card">
          <div className="r-chart-header">
            <div className="r-chart-title">
              <FiDollarSign size={16} className="r-chart-icon amber" />
              Estado de Multas
            </div>
          </div>
          {multasPieData.length === 0 ? (
            <div className="r-empty-chart">
              <FiCheckCircle size={32} style={{ color: '#10b981' }} />
              <p>Sin multas registradas</p>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie data={multasPieData} cx="50%" cy="50%" outerRadius={90}
                  dataKey="value" labelLine={false} label={<CustomPieLabel />}>
                  {multasPieData.map((_, i) => (
                    <Cell key={i} fill={['#ef4444', '#f59e0b'][i]} />
                  ))}
                </Pie>
                <Tooltip formatter={(val, name) => name === 'Recaudado (S/)' ? [`S/ ${val}`, name] : [val, name]} />
                <Legend iconType="circle" iconSize={10}
                  formatter={(val) => <span style={{ fontSize: 13, color: '#475569' }}>{val}</span>} />
              </PieChart>
            </ResponsiveContainer>
          )}
          <div className="r-pie-stats">
            <div className="r-pie-stat">
              <span className="r-dot" style={{ background: '#ef4444' }} />
              <span>{data.multas?.total_multas_pendientes || 0} pendientes</span>
            </div>
            <div className="r-pie-stat">
              <span className="r-dot" style={{ background: '#f59e0b' }} />
              <span>S/ {Number(data.multas?.monto_total || 0).toFixed(2)} por cobrar</span>
            </div>
          </div>
        </div>

        {/* ── Chart 3: Lectores con más multas (Bar horizontal) ── */}
        <div className="r-chart-card r-span-2">
          <div className="r-chart-header">
            <div className="r-chart-title">
              <FiUsers size={16} className="r-chart-icon red" />
              Lectores con Multas Pendientes
            </div>
            <span className="r-chart-badge">{lectoresBar.length} lectores</span>
          </div>
          {lectoresBar.length === 0 ? (
            <div className="r-empty-chart">
              <FiCheckCircle size={32} style={{ color: '#10b981' }} />
              <p>¡Sin lectores con multas pendientes!</p>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={lectoresBar} layout="vertical"
                margin={{ top: 10, right: 40, left: 20, bottom: 10 }}>
                <defs>
                  <linearGradient id="redGrad" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.85} />
                    <stop offset="95%" stopColor="#f87171" stopOpacity={0.7} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" horizontal={false} />
                <XAxis type="number" tick={{ fill: '#64748b', fontSize: 12 }} allowDecimals={false} />
                <YAxis dataKey="nombre" type="category" tick={{ fill: '#64748b', fontSize: 13 }} width={80} />
                <Tooltip content={<CustomTooltip />}
                  formatter={(val, name, props) => [val, props.payload.nombreFull]} />
                <Bar dataKey="multas" fill="url(#redGrad)" radius={[0, 6, 6, 0]} maxBarSize={32}
                  label={{ position: 'right', fill: '#ef4444', fontSize: 13, fontWeight: 700 }} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* ── Chart 4: Resumen general (Area fake timeline para visual) ── */}
        <div className="r-chart-card">
          <div className="r-chart-header">
            <div className="r-chart-title">
              <FiTrendingUp size={16} className="r-chart-icon green" />
              Resumen General
            </div>
          </div>
          <div className="r-summary-grid">
            <div className="r-summary-item">
              <div className="r-summary-icon" style={{ background: 'linear-gradient(135deg,#6366f1,#818cf8)' }}>
                <FiBook size={18} />
              </div>
              <div>
                <div className="r-summary-value">{data.prestamos?.total_prestamos_activos ?? 0}</div>
                <div className="r-summary-label">Préstamos en curso</div>
              </div>
            </div>
            <div className="r-summary-item">
              <div className="r-summary-icon" style={{ background: 'linear-gradient(135deg,#ef4444,#f87171)' }}>
                <FiAlertCircle size={18} />
              </div>
              <div>
                <div className="r-summary-value">{data.multas?.total_multas_pendientes ?? 0}</div>
                <div className="r-summary-label">Multas sin pagar</div>
              </div>
            </div>
            <div className="r-summary-item">
              <div className="r-summary-icon" style={{ background: 'linear-gradient(135deg,#f59e0b,#fbbf24)' }}>
                <FiDollarSign size={18} />
              </div>
              <div>
                <div className="r-summary-value">S/ {Number(data.multas?.monto_total || 0).toFixed(0)}</div>
                <div className="r-summary-label">Deuda total</div>
              </div>
            </div>
            <div className="r-summary-item">
              <div className="r-summary-icon" style={{ background: 'linear-gradient(135deg,#10b981,#34d399)' }}>
                <FiUsers size={18} />
              </div>
              <div>
                <div className="r-summary-value">{data.libros?.length ?? 0}</div>
                <div className="r-summary-label">Libros con préstamos</div>
              </div>
            </div>
          </div>

          {/* Mini area chart decorativo */}
          <div style={{ marginTop: 16 }}>
            <ResponsiveContainer width="100%" height={100}>
              <AreaChart data={[
                { v: 4 }, { v: 7 }, { v: 5 }, { v: data.prestamos?.total_prestamos_activos || 8 },
                { v: 6 }, { v: 9 }, { v: data.lectores?.length || 5 }
              ]} margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
                <defs>
                  <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0.02} />
                  </linearGradient>
                </defs>
                <Area type="monotone" dataKey="v" stroke="#10b981" strokeWidth={2}
                  fill="url(#areaGrad)" dot={false} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>
    </div>
  )
}

export default Reportes
