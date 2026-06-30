import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { FiBook, FiPlus, FiX, FiTrash2, FiSearch, FiFilter, FiCalendar, FiUser, FiCheckCircle, FiXCircle, FiArrowLeft } from 'react-icons/fi'

function Prestamos() {
  const [items, setItems] = useState([])
  const [lectores, setLectores] = useState([])
  const [libros, setLibros] = useState([])
  const [form, setForm] = useState({ lector_id: '', libro_id: '', fecha_devolucion_esperada: '', observaciones: '' })
  const [showForm, setShowForm] = useState(false)
  const [search, setSearch] = useState('')
  const [filterEstado, setFilterEstado] = useState('all')
  const [loading, setLoading] = useState(true)
  const [confirmDelete, setConfirmDelete] = useState(null)
  const [confirmDevolver, setConfirmDevolver] = useState(null)

  const fetchItems = () => {
    setLoading(true)
    axios.get('/api/prestamos').then(res => { setItems(res.data); setLoading(false) })
  }

  useEffect(() => {
    fetchItems()
    axios.get('/api/lectores').then(res => setLectores(res.data))
    axios.get('/api/libros').then(res => setLibros(res.data.filter(l => l.ejemplares_disponibles > 0)))
  }, [])

  const handleSubmit = (e) => {
    e.preventDefault()
    axios.post('/api/prestamos', { ...form, lector_id: Number(form.lector_id), libro_id: Number(form.libro_id) })
      .then(() => { 
        fetchItems()
        setForm({ lector_id: '', libro_id: '', fecha_devolucion_esperada: '', observaciones: '' })
        setShowForm(false)
      })
  }

  const handleDevolver = (id) => {
    axios.put(`/api/prestamos/${id}/devolver`).then(() => { fetchItems(); setConfirmDevolver(null) })
  }

  const handleDelete = (id) => {
    axios.delete(`/api/prestamos/${id}`).then(() => { fetchItems(); setConfirmDelete(null) })
  }

  const filtered = items.filter(item => {
    const lector = item.lector ? `${item.lector.nombres} ${item.lector.apellidos}`.toLowerCase() : ''
    const libro = item.libro ? item.libro.titulo.toLowerCase() : ''
    const matchSearch = lector.includes(search.toLowerCase()) || libro.includes(search.toLowerCase())
    const matchEstado = filterEstado === 'all' ? true : item.estado === filterEstado
    return matchSearch && matchEstado
  })

  const totalPrestamos = items.length
  const prestamosActivos = items.filter(i => i.estado === 'activo').length
  const prestamosVencidos = items.filter(i => i.estado === 'vencido').length

  return (
    <div className="m-page">
      <div className="m-header">
        <div className="m-header-left">
          <div className="m-header-icon" style={{ background: 'linear-gradient(135deg, #7c3aed, #a78bfa)' }}>
            <FiBook size={22} />
          </div>
          <div>
            <h1 className="m-title">Gestión de Préstamos</h1>
            <p className="m-subtitle">Control de préstamos de libros</p>
          </div>
        </div>
        <button className="m-btn-primary" onClick={() => setShowForm(v => !v)}>
          {showForm ? <><FiX size={16} /> Cerrar</> : <><FiPlus size={16} /> Nuevo Préstamo</>}
        </button>
      </div>

      <div className="m-kpi-grid">
        <div className="m-kpi-card kpi-indigo">
          <div className="m-kpi-icon"><FiBook size={20} /></div>
          <div>
            <div className="m-kpi-value">{totalPrestamos}</div>
            <div className="m-kpi-label">Total Préstamos</div>
          </div>
        </div>
        <div className="m-kpi-card kpi-amber">
          <div className="m-kpi-icon"><FiCalendar size={20} /></div>
          <div>
            <div className="m-kpi-value">{prestamosActivos}</div>
            <div className="m-kpi-label">Préstamos Activos</div>
          </div>
        </div>
        <div className="m-kpi-card kpi-red">
          <div className="m-kpi-icon"><FiXCircle size={20} /></div>
          <div>
            <div className="m-kpi-value">{prestamosVencidos}</div>
            <div className="m-kpi-label">Vencidos</div>
          </div>
        </div>
      </div>

      {showForm && (
        <div className="m-form-panel">
          <div className="m-form-panel-header">
            <h3><FiPlus size={16} /> Nuevo Préstamo</h3>
          </div>
          <form onSubmit={handleSubmit} className="m-form-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))' }}>
            <div className="m-form-group">
              <label><FiUser size={13} /> Lector *</label>
              <select value={form.lector_id} onChange={e => setForm({ ...form, lector_id: e.target.value })} required>
                <option value="">Seleccionar lector...</option>
                {lectores.map(l => <option key={l.id} value={l.id}>{l.nombres} {l.apellidos} ({l.codigo_estudiante})</option>)}
              </select>
            </div>
            <div className="m-form-group">
              <label><FiBook size={13} /> Libro *</label>
              <select value={form.libro_id} onChange={e => setForm({ ...form, libro_id: e.target.value })} required>
                <option value="">Seleccionar libro...</option>
                {libros.map(l => <option key={l.id} value={l.id}>{l.titulo} ({l.ejemplares_disponibles} disponibles)</option>)}
              </select>
            </div>
            <div className="m-form-group">
              <label><FiCalendar size={13} /> Fecha Devolución Esperada *</label>
              <input type="date" value={form.fecha_devolucion_esperada} onChange={e => setForm({ ...form, fecha_devolucion_esperada: e.target.value })} required />
            </div>
            <div className="m-form-group" style={{ gridColumn: '1 / -1' }}>
              <label><FiBook size={13} /> Observaciones</label>
              <textarea placeholder="Observaciones del préstamo" value={form.observaciones} onChange={e => setForm({ ...form, observaciones: e.target.value })} rows={2} />
            </div>
            <div className="m-form-actions" style={{ gridColumn: '1 / -1' }}>
              <button type="submit" className="m-btn-primary">Registrar Préstamo</button>
              <button type="button" className="m-btn-ghost" onClick={() => { setShowForm(false); setForm({ lector_id: '', libro_id: '', fecha_devolucion_esperada: '', observaciones: '' }) }}>Cancelar</button>
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
          {[['all', 'Todos'], ['activo', 'Activos'], ['devuelto', 'Devueltos'], ['vencido', 'Vencidos']].map(([val, label]) => (
            <button key={val} className={`m-filter-tab ${filterEstado === val ? 'active' : ''}`} onClick={() => setFilterEstado(val)}>{label}</button>
          ))}
        </div>
        <span className="m-count">{filtered.length} préstamo{filtered.length !== 1 ? 's' : ''}</span>
      </div>

      <div className="m-table-card">
        {loading ? (
          <div className="m-loading"><div className="m-spinner" /><span>Cargando préstamos...</span></div>
        ) : filtered.length === 0 ? (
          <div className="m-empty">
            <FiBook size={40} />
            <h3>No hay préstamos registrados</h3>
            <p>Comienza registrando el primer préstamo</p>
          </div>
        ) : (
          <table className="m-table">
            <thead>
              <tr>
                <th>Préstamo</th>
                <th>Fecha Préstamo</th>
                <th>Devolución Esperada</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(item => (
                <tr key={item.id} className={item.estado === 'vencido' ? 'row-pending' : item.estado === 'devuelto' ? 'row-paid' : ''}>
                  <td>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                      <div style={{ fontWeight: '600', color: '#1e293b' }}>{item.libro?.titulo || 'Sin libro'}</div>
                      <div style={{ fontSize: '12px', color: '#94a3b8', display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <FiUser size={10} /> {item.lector?.nombres} {item.lector?.apellidos}
                      </div>
                    </div>
                  </td>
                  <td className="m-date">{item.fecha_prestamo ? new Date(item.fecha_prestamo).toLocaleDateString('es-PE') : '-'}</td>
                  <td className="m-date">{item.fecha_devolucion_esperada ? new Date(item.fecha_devolucion_esperada).toLocaleDateString('es-PE') : '-'}</td>
                  <td>
                    {item.estado === 'activo' && <span className="m-badge" style={{ background: '#dbeafe', color: '#2563eb' }}><FiCalendar size={11} /> Activo</span>}
                    {item.estado === 'devuelto' && <span className="m-badge m-badge-paid"><FiCheckCircle size={11} /> Devuelto</span>}
                    {item.estado === 'vencido' && <span className="m-badge m-badge-pending"><FiXCircle size={11} /> Vencido</span>}
                  </td>
                  <td>
                    <div className="m-actions">
                      {item.estado === 'activo' && <button className="m-action-btn edit" title="Marcar devuelto" onClick={() => setConfirmDevolver(item)}><FiArrowLeft size={15} /></button>}
                      <button className="m-action-btn del" title="Eliminar" onClick={() => setConfirmDelete(item)}><FiTrash2 size={15} /></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {confirmDevolver && (
        <div className="m-modal-overlay" onClick={() => setConfirmDevolver(null)}>
          <div className="m-modal" onClick={e => e.stopPropagation()}>
            <div className="m-modal-icon" style={{ background: 'linear-gradient(135deg, #059669, #34d399)' }}><FiCheckCircle size={28} /></div>
            <h3>Marcar Préstamo Como Devuelto</h3>
            <p>¿Marcar como devuelto el préstamo de <strong>{confirmDevolver.libro?.titulo}</strong> a <strong>{confirmDevolver.lector?.nombres} {confirmDevolver.lector?.apellidos}</strong>?</p>
            <div className="m-modal-actions">
              <button className="m-btn-primary" onClick={() => handleDevolver(confirmDevolver.id)}>Sí, marcar devuelto</button>
              <button className="m-btn-ghost" onClick={() => setConfirmDevolver(null)}>Cancelar</button>
            </div>
          </div>
        </div>
      )}

      {confirmDelete && (
        <div className="m-modal-overlay" onClick={() => setConfirmDelete(null)}>
          <div className="m-modal" onClick={e => e.stopPropagation()}>
            <div className="m-modal-icon del"><FiTrash2 size={28} /></div>
            <h3>Eliminar Préstamo</h3>
            <p>¿Estás seguro de eliminar el préstamo de <strong>{confirmDelete.libro?.titulo}</strong>?</p>
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

export default Prestamos
