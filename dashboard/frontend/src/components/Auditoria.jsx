import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { FiActivity, FiSearch, FiFilter, FiUser, FiCalendar, FiPlus, FiEdit2, FiTrash2 } from 'react-icons/fi'

function Auditoria() {
  const [items, setItems] = useState([])
  const [search, setSearch] = useState('')
  const [filterModulo, setFilterModulo] = useState('all')
  const [loading, setLoading] = useState(true)

  const fetchItems = () => {
    setLoading(true)
    const params = {}
    if (filterModulo && filterModulo !== 'all') params.modulo = filterModulo
    axios.get('/api/auditoria', { params }).then(res => { setItems(res.data); setLoading(false) })
  }

  useEffect(() => { fetchItems() }, [filterModulo])

  const filtered = items.filter(item => {
    const matchSearch = item.descripcion.toLowerCase().includes(search.toLowerCase()) ||
                       item.usuario.toLowerCase().includes(search.toLowerCase()) ||
                       item.modulo.toLowerCase().includes(search.toLowerCase())
    return matchSearch
  })

  const modulos = [...new Set(items.map(i => i.modulo))]

  return (
    <div className="m-page">
      <div className="m-header">
        <div className="m-header-left">
          <div className="m-header-icon" style={{ background: 'linear-gradient(135deg, #3b82f6, #60a5fa)' }}>
            <FiActivity size={22} />
          </div>
          <div>
            <h1 className="m-title">Historial de Auditoría</h1>
            <p className="m-subtitle">Registro de todas las operaciones del sistema</p>
          </div>
        </div>
      </div>

      <div className="m-kpi-grid">
        <div className="m-kpi-card kpi-blue">
          <div className="m-kpi-icon"><FiActivity size={20} /></div>
          <div>
            <div className="m-kpi-value">{items.length}</div>
            <div className="m-kpi-label">Total Registros</div>
          </div>
        </div>
      </div>

      <div className="m-toolbar">
        <div className="m-search">
          <FiSearch size={15} className="m-search-icon" />
          <input placeholder="Buscar en auditoría..." value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <div className="m-filter-tabs">
          <FiFilter size={14} style={{ color: '#64748b' }} />
          <button key="all" className={`m-filter-tab ${filterModulo === 'all' ? 'active' : ''}`} onClick={() => setFilterModulo('all')}>Todos</button>
          {modulos.map(m => (
            <button key={m} className={`m-filter-tab ${filterModulo === m ? 'active' : ''}`} onClick={() => setFilterModulo(m)}>{m}</button>
          ))}
        </div>
        <span className="m-count">{filtered.length} registro{filtered.length !== 1 ? 's' : ''}</span>
      </div>

      <div className="m-table-card">
        {loading ? (
          <div className="m-loading"><div className="m-spinner" /><span>Cargando auditoría...</span></div>
        ) : filtered.length === 0 ? (
          <div className="m-empty">
            <FiActivity size={40} />
            <h3>No hay registros de auditoría</h3>
            <p>Los registros aparecerán aquí cuando se realicen operaciones</p>
          </div>
        ) : (
          <table className="m-table">
            <thead>
              <tr>
                <th>Operación</th>
                <th>Usuario</th>
                <th>Módulo</th>
                <th>Fecha y Hora</th>
                <th>Resultado</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(item => (
                <tr key={item.id}>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      {item.tipo_operacion === 'CREATE' && <FiPlus size={14} style={{ color: '#059669' }} />}
                      {item.tipo_operacion === 'UPDATE' && <FiEdit2 size={14} style={{ color: '#2563eb' }} />}
                      {item.tipo_operacion === 'DELETE' && <FiTrash2 size={14} style={{ color: '#dc2626' }} />}
                      <span style={{ fontWeight: '600', color: '#1e293b' }}>{item.tipo_operacion}</span>
                    </div>
                    <div style={{ fontSize: '12px', color: '#64748b', marginTop: '2px' }}>{item.descripcion}</div>
                  </td>
                  <td>
                    <div className="m-user-cell">
                      <div className="m-avatar" style={{ background: 'linear-gradient(135deg, #7c3aed, #a78bfa)' }}>
                        {item.usuario[0]?.toUpperCase() || 'U'}
                      </div>
                      <span>{item.usuario}</span>
                    </div>
                  </td>
                  <td><span className="m-badge" style={{ background: '#f1f5f9', color: '#475569' }}>{item.modulo}</span></td>
                  <td className="m-date">{item.fecha_hora ? new Date(item.fecha_hora).toLocaleString('es-PE') : '-'}</td>
                  <td>
                    {item.resultado === 'Éxito' ? (
                      <span className="m-badge m-badge-paid"><FiActivity size={11} /> Éxito</span>
                    ) : (
                      <span className="m-badge m-badge-pending"><FiActivity size={11} /> {item.resultado}</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

export default Auditoria
