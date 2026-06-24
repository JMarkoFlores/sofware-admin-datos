import React, { useEffect, useState } from 'react'
import axios from 'axios'

function Dashboard() {
  const [stats, setStats] = useState(null)

  useEffect(() => {
    axios.get('/api/dashboard')
      .then(res => setStats(res.data))
      .catch(err => console.error(err))
  }, [])

  if (!stats) return <div className="loading">Cargando...</div>

  const cards = [
    { label: 'Total Libros', value: stats.total_libros, color: '#2563eb' },
    { label: 'Autores', value: stats.total_autores, color: '#7c3aed' },
    { label: 'Categorías', value: stats.total_categorias, color: '#059669' },
    { label: 'Lectores', value: stats.total_lectores, color: '#d97706' },
    { label: 'Préstamos Activos', value: stats.prestamos_activos, color: '#dc2626' },
    { label: 'Préstamos Vencidos', value: stats.prestamos_vencidos, color: '#991b1b' },
    { label: 'Multas Pendientes', value: stats.multas_pendientes, color: '#ea580c' },
    { label: 'Usuarios', value: stats.total_usuarios, color: '#4f46e5' },
  ]

  return (
    <div className="dashboard-container">
      <div className="dashboard-grid">
        {cards.map((card, i) => (
          <div key={i} className="stat-card" style={{ borderLeft: `4px solid ${card.color}` }}>
            <h3>{card.label}</h3>
            <span className="stat-value">{card.value}</span>
          </div>
        ))}
      </div>
      {stats.ultima_actividad && (
        <div className="card" style={{ marginTop: 24 }}>
          <div className="card-header"><h3>Última Actividad</h3></div>
          <div className="card-body">
            <p><strong>{stats.ultima_actividad.tipo_operacion}</strong> en <em>{stats.ultima_actividad.modulo}</em></p>
            <p>{stats.ultima_actividad.descripcion}</p>
            <small>{stats.ultima_actividad.fecha_hora}</small>
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard
