import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { FiBook, FiPlus, FiX, FiTrash2, FiSearch, FiFilter, FiCalendar, FiUser, FiCheckCircle, FiXCircle } from 'react-icons/fi'

function Devoluciones() {
  const [items, setItems] = useState([])
  const [prestamos, setPrestamos] = useState([])
  const [form, setForm] = useState({ prestamo_id: '', estado_libro: 'bueno', observaciones: '' })
  const [showForm, setShowForm] = useState(false)
  const [search, setSearch] = useState('')
  const [filterEstado, setFilterEstado] = useState('all')
  const [loading, setLoading] = useState(true)
  const [confirmDelete, setConfirmDelete] = useState(null)

  const fetchItems = () => {
    setLoading(true)
    axios.get('/api/devoluciones').then(res => { setItems(res.data); setLoading(false) })
  }

  useEffect(() => {
    fetchItems()
    axios.get('/api/prestamos').then(res => setPrestamos(res.data.filter(p => p.estado === 'activo' || p.estado === 'vencido')))
  }, [])

  const handleSubmit = (e) => {
    e.preventDefault()
    axios.post('/api/devoluciones', { ...form, prestamo_id: Number(form.prestamo_id) })
      .then(() => { 
        fetchItems()
        setForm({ prestamo_id: '', estado_libro: 'bueno', observaciones: '' })
        setShowForm(false)
      })
  }

  const handleDelete = (id) => {
    axios.delete(`/api/devoluciones/${id}`).then(() => { fetchItems(); setConfirmDelete(null) })
  }

  const filtered = items.filter(item => {
    const lector = item.prestamo?.lector ? `${item.prestamo.lector.nombres} ${item.prestamo.lector.apellidos}`.toLowerCase() : ''
    const libro = item.prestamo?.libro ? item.prestamo.libro.titulo.toLowerCase() : ''
    const matchSearch = lector.includes(search.toLowerCase()) || libro.includes(search.toLowerCase())
    const matchEstado = filterEstado === 'all' ? true : item.estado_libro === filterEstado
    return matchSearch && matchEstado
  })

  const totalDevoluciones = items.length
  const devolucionesBuenas = items.filter(i => i.estado_libro === 'bueno').length
  const devolucionesDaniadas = items.filter(i => i.estado_libro === 'dañado' || i.estado_libro === 'perdido').length

  return (
    <div className="m-page">
      <div className="m-header">
        <div className="m-header-left">
          <div className="m-header-icon" style={{ background: 'linear-gradient(135deg, #059669, #34d399)' }}>
            <FiCheckCircle size={22} />
          </div>
          <div>
            <h1 className="m-title">Gestión de Devoluciones</h1>
            <p className="m-subtitle">Registro de devoluciones de libros</p>
          </div>
        </div>
        <button className="m-btn-primary" onClick={() => setShowForm(v => !v)}>
          {showForm ? <><FiX size={16} /> Cerrar</> : <><FiPlus size={16} /> Nueva Devolución</>}
        </button>
      </div>

      <div className="m-kpi-grid">
        <div className="m-kpi-card kpi-green">
          <div className="m-kpi-icon"><FiCheckCircle size={20} /></div>
          <div>
            <div className="m-kpi-value">{totalDevoluciones}</div>
            <div className="m-kpi-label">Total Devoluciones</div>
          </div>
        </div>
        <div className="m-kpi-card kpi-amber">
          <div className="m-kpi-icon"><FiBook size={20} /></div>
          <div>
            <div className="m-kpi-value">{devolucionesBuenas}</div>
            <div className="m-kpi-label">En Buen Estado</div>
          </div>
        </div>
        <div className="m-kpi-card kpi-red">
          <div className="m-kpi-icon"><FiXCircle size={20} /></div>
          <div>
            <div className="m-kpi-value">{devolucionesDaniadas}</div>
            <div className="m-kpi-label">Dañados/Perdidos</div>
          </div>
        </div>
      </div>

      {showForm && (
        <div className="m-form-panel">
          <div className="m-form-panel-header">
            <h3><FiPlus size={16} /> Nueva Devolución</h3>
          </div>
          <form onSubmit={handleSubmit} className="m-form-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))' }}>
            <div className="m-form-group">
              <label><FiBook size={13} /> Préstamo *</label>
              <select value={form.prestamo_id} onChange={e => setForm({ ...form, prestamo_id: e.target.value })} required>
                <option value="">Seleccionar préstamo...</option>
                {prestamos.map(p => <option key={p.id} value={p.id}>{p.libro?.titulo} - {p.lector?.nombres} {p.lector?.apellidos}</option>)}
              </select>
            </div>
            <div className="m-form-group">
              <label><FiCheckCircle size={13} /> Estado Libro</label>
              <select value={form.estado_libro} onChange={e => setForm({ ...form, estado_libro: e.target.value })}>
                <option value="bueno">Bueno</option>
                <option value="dañado">Dañado</option>
                <option value="perdido">Perdido</option>
              </select>
            </div>
            <div className="m-form-group" style={{ gridColumn: '1 / -1' }}>
              <label><FiBook size={13} /> Observaciones</label>
              <textarea placeholder="Observaciones de la devolución" value={form.observaciones} onChange={e => setForm({ ...form, observaciones: e.target.value })} rows={2} />
            </div>
            <div className="m-form-actions" style={{ gridColumn: '1 / -1' }}>
              <button type="submit" className="m-btn-primary">Registrar Devolución</button>
              <button type="button" className="m-btn-ghost" onClick={() => { setShowForm(false); setForm({ prestamo_id: '', estado_libro: 'bueno', observaciones: '' }) }}>Cancelar</button>
            </div>
          </form>
        </div>
      )}

      <div className="m-toolbar">
        <div className="m-search">
          <FiSearch size={15} className="m-search-icon" />
          <input placeholder="Buscar por lector o libro..." value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <div className="m-filter-tabs">
          <FiFilter size={14} style={{ color: '#64748b' }} />
          {[['all', 'Todos'], ['bueno', 'Bueno'], ['dañado', 'Dañado'], ['perdido', 'Perdido']].map(([val, label]) => (
            <button key={val} className={`m-filter-tab ${filterEstado === val ? 'active' : ''}`} onClick={() => setFilterEstado(val)}>{label}</button>
          ))}
        </div>
        <span className="m-count">{filtered.length} devolución{filtered.length !== 1 ? 'es' : ''}</span>
      </div>

      <div className="m-table-card">
        {loading ? (
          <div className="m-loading"><div className="m-spinner" /><span>Cargando devoluciones...</span></div>
        ) : filtered.length === 0 ? (
          <div className="m-empty">
            <FiCheckCircle size={40} />
            <h3>No hay devoluciones registradas</h3>
            <p>Comienza registrando la primera devolución</p>
          </div>
        ) : (
          <table className="m-table">
            <thead>
              <tr>
                <th>Devolución</th>
                <th>Fecha Devolución</th>
                <th>Estado Libro</th>
                <th>Observaciones</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(item => (
                <tr key={item.id} className={item.estado_libro === 'bueno' ? 'row-paid' : item.estado_libro === 'perdido' ? 'row-pending' : ''}>
                  <td>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                      <div style={{ fontWeight: '600', color: '#1e293b' }}>{item.prestamo?.libro?.titulo || 'Sin libro'}</div>
                      <div style={{ fontSize: '12px', color: '#94a3b8', display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <FiUser size={10} /> {item.prestamo?.lector?.nombres} {item.prestamo?.lector?.apellidos}
                      </div>
                    </div>
                  </td>
                  <td className="m-date">{item.fecha_devolucion ? new Date(item.fecha_devolucion).toLocaleDateString('es-PE') : '-'}</td>
                  <td>
                    {item.estado_libro === 'bueno' && <span className="m-badge m-badge-paid"><FiCheckCircle size={11} /> Bueno</span>}
                    {item.estado_libro === 'dañado' && <span className="m-badge" style={{ background: '#fef3c7', color: '#d97706' }}><FiBook size={11} /> Dañado</span>}
                    {item.estado_libro === 'perdido' && <span className="m-badge m-badge-pending"><FiXCircle size={11} /> Perdido</span>}
                  </td>
                  <td>{item.observaciones || <span className="m-null">Sin observaciones</span>}</td>
                  <td>
                    <div className="m-actions">
                      <button className="m-action-btn del" title="Eliminar" onClick={() => setConfirmDelete(item)}><FiTrash2 size={15} /></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {confirmDelete && (
        <div className="m-modal-overlay" onClick={() => setConfirmDelete(null)}>
          <div className="m-modal" onClick={e => e.stopPropagation()}>
            <div className="m-modal-icon del"><FiTrash2 size={28} /></div>
            <h3>Eliminar Devolución</h3>
            <p>¿Estás seguro de eliminar la devolución de <strong>{confirmDelete.prestamo?.libro?.titulo}</strong>?</p>
            <div className="m-modal-actions">
              <button className="m-btn-danger" onClick={() => handleDelete(confirmDelete.id)}>Sí, eliminar</button>
              <button className="m-btn-ghost" onClick={() => setConfirmDelete(null)}>Cancelar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Devoluciones
