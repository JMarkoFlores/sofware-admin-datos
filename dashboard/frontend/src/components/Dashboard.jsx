import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { FiHome, FiBook, FiUsers, FiAlertCircle, FiCheckCircle, FiShield, FiActivity } from 'react-icons/fi'

function Dashboard() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    axios.get('/api/dashboard')
      .then(res => { setStats(res.data); setLoading(false) })
      .catch(err => { console.error(err); setLoading(false) })
  }, [])

  if (loading) {
    return (
      <div className="m-page">
        <div className="m-loading" style={{ height: '60vh' }}>
          <div className="m-spinner" />
          <span>Cargando dashboard...</span>
        </div>
      </div>
    )
  }

  const cards = [
    { label: 'Total Libros', value: stats?.total_libros || 0, color: 'kpi-blue', icon: FiBook },
    { label: 'Autores', value: stats?.total_autores || 0, color: 'kpi-indigo', icon: FiUsers },
    { label: 'Categorías', value: stats?.total_categorias || 0, color: 'kpi-green', icon: FiActivity },
    { label: 'Lectores', value: stats?.total_lectores || 0, color: 'kpi-amber', icon: FiUsers },
    { label: 'Préstamos Activos', value: stats?.prestamos_activos || 0, color: 'kpi-red', icon: FiBook },
    { label: 'Préstamos Vencidos', value: stats?.prestamos_vencidos || 0, color: 'kpi-red', icon: FiAlertCircle },
    { label: 'Multas Pendientes', value: stats?.multas_pendientes || 0, color: 'kpi-amber', icon: FiAlertCircle },
    { label: 'Usuarios del Sistema', value: stats?.total_usuarios || 0, color: 'kpi-indigo', icon: FiShield },
  ]

  return (
    <div className="m-page">
      <div className="m-header">
        <div className="m-header-left">
          <div className="m-header-icon" style={{ background: 'linear-gradient(135deg, #6366f1, #818cf8)' }}>
            <FiHome size={22} />
          </div>
          <div>
            <h1 className="m-title">Dashboard</h1>
            <p className="m-subtitle">Resumen general del sistema de biblioteca</p>
          </div>
        </div>
      </div>

      <div className="m-kpi-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))' }}>
        {cards.map((card, i) => (
          <div key={i} className={`m-kpi-card ${card.color}`}>
            <div className="m-kpi-icon">
              <card.icon size={20} />
            </div>
            <div>
              <div className="m-kpi-value">{card.value}</div>
              <div className="m-kpi-label">{card.label}</div>
            </div>
          </div>
        ))}
      </div>

      {stats?.ultima_actividad && (
        <div className="m-table-card" style={{ marginTop: '24px' }}>
          <div style={{ padding: '16px 20px', borderBottom: '1px solid #e2e8f0' }}>
            <h3 style={{ margin: 0, fontSize: '16px', color: '#1e293b', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <FiActivity size={18} style={{ color: '#6366f1' }} />
              Última Actividad del Sistema
            </h3>
          </div>
          <div style={{ padding: '20px' }}>
            <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
              <div style={{
                width: '48px',
                height: '48px',
                borderRadius: '12px',
                background: 'linear-gradient(135deg, #6366f1, #818cf8)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                flexShrink: 0
              }}>
                {stats.ultima_actividad.tipo_operacion === 'CREATE' && <FiBook size={20} />}
                {stats.ultima_actividad.tipo_operacion === 'UPDATE' && <FiCheckCircle size={20} />}
                {stats.ultima_actividad.tipo_operacion === 'DELETE' && <FiAlertCircle size={20} />}
                {!['CREATE', 'UPDATE', 'DELETE'].includes(stats.ultima_actividad.tipo_operacion) && <FiActivity size={20} />}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  <span style={{
                    fontSize: '12px',
                    fontWeight: '600',
                    padding: '2px 8px',
                    borderRadius: '9999px',
                    background: stats.ultima_actividad.tipo_operacion === 'CREATE' ? '#d1fae5' : stats.ultima_actividad.tipo_operacion === 'UPDATE' ? '#dbeafe' : '#fee2e2',
                    color: stats.ultima_actividad.tipo_operacion === 'CREATE' ? '#059669' : stats.ultima_actividad.tipo_operacion === 'UPDATE' ? '#2563eb' : '#dc2626'
                  }}>
                    {stats.ultima_actividad.tipo_operacion}
                  </span>
                  <span style={{ fontSize: '12px', color: '#64748b' }}>en</span>
                  <span style={{ fontSize: '14px', fontWeight: '600', color: '#1e293b' }}>{stats.ultima_actividad.modulo}</span>
                </div>
                <p style={{ margin: '4px 0', color: '#475569', fontSize: '14px' }}>{stats.ultima_actividad.descripcion}</p>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '8px' }}>
                  <span style={{ fontSize: '12px', color: '#64748b' }}>Realizado por</span>
                  <span style={{ fontSize: '12px', fontWeight: '600', color: '#1e293b', background: '#f1f5f9', padding: '2px 8px', borderRadius: '4px' }}>
                    {stats.ultima_actividad.usuario}
                  </span>
                  <span style={{ fontSize: '12px', color: '#94a3b8' }}>•</span>
                  <span style={{ fontSize: '12px', color: '#94a3b8' }}>
                    {new Date(stats.ultima_actividad.fecha_hora).toLocaleString('es-PE')}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard
