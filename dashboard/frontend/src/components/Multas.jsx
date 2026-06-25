import React, { useEffect, useState } from 'react'
import axios from 'axios'
import {
  FiAlertCircle, FiCheckCircle, FiDollarSign, FiTrash2,
  FiPlus, FiX, FiSearch, FiFilter, FiUser, FiFileText,
  FiClock, FiTrendingUp
} from 'react-icons/fi'

function Multas() {
  const [items, setItems] = useState([])
  const [lectores, setLectores] = useState([])
  const [prestamos, setPrestamos] = useState([])
  const [form, setForm] = useState({ lector_id: '', prestamo_id: '', monto: '', motivo: '', pagada: false })
  const [showForm, setShowForm] = useState(false)
  const [search, setSearch] = useState('')
  const [filterPagada, setFilterPagada] = useState('all')
  const [loading, setLoading] = useState(true)
  const [confirmDelete, setConfirmDelete] = useState(null)
  const [confirmPagar, setConfirmPagar] = useState(null)

  const fetchItems = () => {
    setLoading(true)
    axios.get('/api/multas').then(res => { setItems(res.data); setLoading(false) })
  }

  useEffect(() => {
    fetchItems()
    axios.get('/api/lectores').then(res => setLectores(res.data))
    axios.get('/api/prestamos').then(res => setPrestamos(res.data))
  }, [])

  const handleSubmit = (e) => {
    e.preventDefault()
    axios.post('/api/multas', {
      ...form,
      lector_id: Number(form.lector_id),
      prestamo_id: Number(form.prestamo_id) || null,
      monto: Number(form.monto)
    }).then(() => {
      fetchItems()
      setForm({ lector_id: '', prestamo_id: '', monto: '', motivo: '', pagada: false })
      setShowForm(false)
    })
  }

  const handlePagar = (id) => {
    axios.put(`/api/multas/${id}/pagar`).then(() => { fetchItems(); setConfirmPagar(null) })
  }

  const handleDelete = (id) => {
    axios.delete(`/api/multas/${id}`).then(() => { fetchItems(); setConfirmDelete(null) })
  }

  const filtered = items.filter(item => {
    const nombre = item.lector ? `${item.lector.nombres} ${item.lector.apellidos}`.toLowerCase() : ''
    const motivo = (item.motivo || '').toLowerCase()
    const matchSearch = nombre.includes(search.toLowerCase()) || motivo.includes(search.toLowerCase())
    const matchFilter = filterPagada === 'all'
      ? true
      : filterPagada === 'pagada' ? item.pagada : !item.pagada
    return matchSearch && matchFilter
  })

  const totalPendiente = items.filter(i => !i.pagada).reduce((acc, i) => acc + Number(i.monto), 0)
  const totalPagado = items.filter(i => i.pagada).reduce((acc, i) => acc + Number(i.monto), 0)
  const pendientesCount = items.filter(i => !i.pagada).length

  return (
    <div className="m-page">

      {/* ── Header ── */}
      <div className="m-header">
        <div className="m-header-left">
          <div className="m-header-icon multas-icon">
            <FiAlertCircle size={22} />
          </div>
          <div>
            <h1 className="m-title">Gestión de Multas</h1>
            <p className="m-subtitle">Control de penalidades y cobros de la biblioteca</p>
          </div>
        </div>
        <button className="m-btn-primary" onClick={() => setShowForm(v => !v)}>
          {showForm ? <><FiX size={16} /> Cerrar</> : <><FiPlus size={16} /> Nueva Multa</>}
        </button>
      </div>

      {/* ── KPI Cards ── */}
      <div className="m-kpi-grid">
        <div className="m-kpi-card kpi-red">
          <div className="m-kpi-icon"><FiAlertCircle size={20} /></div>
          <div>
            <div className="m-kpi-value">{pendientesCount}</div>
            <div className="m-kpi-label">Multas Pendientes</div>
          </div>
        </div>
        <div className="m-kpi-card kpi-amber">
          <div className="m-kpi-icon"><FiDollarSign size={20} /></div>
          <div>
            <div className="m-kpi-value">S/ {totalPendiente.toFixed(2)}</div>
            <div className="m-kpi-label">Monto por Cobrar</div>
          </div>
        </div>
        <div className="m-kpi-card kpi-green">
          <div className="m-kpi-icon"><FiCheckCircle size={20} /></div>
          <div>
            <div className="m-kpi-value">{items.filter(i => i.pagada).length}</div>
            <div className="m-kpi-label">Multas Pagadas</div>
          </div>
        </div>
        <div className="m-kpi-card kpi-blue">
          <div className="m-kpi-icon"><FiTrendingUp size={20} /></div>
          <div>
            <div className="m-kpi-value">S/ {totalPagado.toFixed(2)}</div>
            <div className="m-kpi-label">Total Recaudado</div>
          </div>
        </div>
      </div>

      {/* ── Form Panel ── */}
      {showForm && (
        <div className="m-form-panel">
          <div className="m-form-panel-header">
            <h3><FiPlus size={16} /> Registrar Nueva Multa</h3>
          </div>
          <form onSubmit={handleSubmit} className="m-form-grid">
            <div className="m-form-group">
              <label><FiUser size={13} /> Lector</label>
              <select value={form.lector_id} onChange={e => setForm({ ...form, lector_id: e.target.value })} required>
                <option value="">Seleccionar lector...</option>
                {lectores.map(l => <option key={l.id} value={l.id}>{l.nombres} {l.apellidos}</option>)}
              </select>
            </div>
            <div className="m-form-group">
              <label><FiFileText size={13} /> Préstamo asociado</label>
              <select value={form.prestamo_id} onChange={e => setForm({ ...form, prestamo_id: e.target.value })}>
                <option value="">Sin préstamo (opcional)</option>
                {prestamos.map(p => <option key={p.id} value={p.id}>#{p.id} – {p.libro?.titulo} / {p.lector?.nombres}</option>)}
              </select>
            </div>
            <div className="m-form-group">
              <label><FiDollarSign size={13} /> Monto (S/)</label>
              <input type="number" step="0.01" min="0" placeholder="0.00" value={form.monto}
                onChange={e => setForm({ ...form, monto: e.target.value })} required />
            </div>
            <div className="m-form-group">
              <label><FiFileText size={13} /> Motivo</label>
              <input placeholder="Ej: Devolución tardía" value={form.motivo}
                onChange={e => setForm({ ...form, motivo: e.target.value })} />
            </div>
            <div className="m-form-actions">
              <button type="submit" className="m-btn-primary">Registrar Multa</button>
              <button type="button" className="m-btn-ghost" onClick={() => setShowForm(false)}>Cancelar</button>
            </div>
          </form>
        </div>
      )}

      {/* ── Filters ── */}
      <div className="m-toolbar">
        <div className="m-search">
          <FiSearch size={15} className="m-search-icon" />
          <input placeholder="Buscar por lector o motivo..." value={search}
            onChange={e => setSearch(e.target.value)} />
        </div>
        <div className="m-filter-tabs">
          <FiFilter size={14} style={{ color: '#64748b' }} />
          {[['all', 'Todas'], ['pendiente', 'Pendientes'], ['pagada', 'Pagadas']].map(([val, label]) => (
            <button key={val} className={`m-filter-tab ${filterPagada === val ? 'active' : ''}`}
              onClick={() => setFilterPagada(val)}>{label}</button>
          ))}
        </div>
        <span className="m-count">{filtered.length} resultado{filtered.length !== 1 ? 's' : ''}</span>
      </div>

      {/* ── Table ── */}
      <div className="m-table-card">
        {loading ? (
          <div className="m-loading"><div className="m-spinner" /><span>Cargando multas...</span></div>
        ) : filtered.length === 0 ? (
          <div className="m-empty">
            <FiAlertCircle size={40} />
            <h3>No hay multas</h3>
            <p>No se encontraron registros con los filtros aplicados</p>
          </div>
        ) : (
          <table className="m-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Lector</th>
                <th>Monto</th>
                <th>Motivo</th>
                <th>Estado</th>
                <th>Fecha</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(item => (
                <tr key={item.id} className={item.pagada ? 'row-paid' : 'row-pending'}>
                  <td className="m-id">#{item.id}</td>
                  <td>
                    <div className="m-user-cell">
                      <div className="m-avatar">{item.lector ? item.lector.nombres[0] : '?'}</div>
                      <span>{item.lector ? `${item.lector.nombres} ${item.lector.apellidos}` : '—'}</span>
                    </div>
                  </td>
                  <td><span className="m-monto">S/ {Number(item.monto).toFixed(2)}</span></td>
                  <td className="m-motivo">{item.motivo || <span className="m-null">Sin motivo</span>}</td>
                  <td>
                    {item.pagada
                      ? <span className="m-badge m-badge-paid"><FiCheckCircle size={11} /> Pagada</span>
                      : <span className="m-badge m-badge-pending"><FiClock size={11} /> Pendiente</span>}
                  </td>
                  <td className="m-date">{item.created_at ? new Date(item.created_at).toLocaleDateString('es-PE') : '—'}</td>
                  <td>
                    <div className="m-actions">
                      {!item.pagada && (
                        <button className="m-action-btn pay" title="Marcar como pagada"
                          onClick={() => setConfirmPagar(item)}>
                          <FiDollarSign size={15} />
                        </button>
                      )}
                      <button className="m-action-btn del" title="Eliminar"
                        onClick={() => setConfirmDelete(item)}>
                        <FiTrash2 size={15} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* ── Confirm Pagar Modal ── */}
      {confirmPagar && (
        <div className="m-modal-overlay" onClick={() => setConfirmPagar(null)}>
          <div className="m-modal" onClick={e => e.stopPropagation()}>
            <div className="m-modal-icon pay"><FiDollarSign size={28} /></div>
            <h3>Confirmar pago</h3>
            <p>¿Marcar como pagada la multa de <strong>{confirmPagar.lector?.nombres}</strong> por <strong>S/ {Number(confirmPagar.monto).toFixed(2)}</strong>?</p>
            <div className="m-modal-actions">
              <button className="m-btn-primary" onClick={() => handlePagar(confirmPagar.id)}>Sí, marcar pagada</button>
              <button className="m-btn-ghost" onClick={() => setConfirmPagar(null)}>Cancelar</button>
            </div>
          </div>
        </div>
      )}

      {/* ── Confirm Delete Modal ── */}
      {confirmDelete && (
        <div className="m-modal-overlay" onClick={() => setConfirmDelete(null)}>
          <div className="m-modal" onClick={e => e.stopPropagation()}>
            <div className="m-modal-icon del"><FiTrash2 size={28} /></div>
            <h3>Eliminar multa</h3>
            <p>¿Eliminar la multa de <strong>{confirmDelete.lector?.nombres}</strong>? Esta acción no se puede deshacer.</p>
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

export default Multas
