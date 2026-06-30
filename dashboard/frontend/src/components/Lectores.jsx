import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { FiUser, FiPlus, FiX, FiEdit2, FiTrash2, FiSearch, FiMail, FiPhone, FiBookOpen, FiCheckCircle, FiXCircle } from 'react-icons/fi'

function Lectores() {
  const [items, setItems] = useState([])
  const [form, setForm] = useState({ codigo_estudiante: '', nombres: '', apellidos: '', email: '', telefono: '', carrera: '', facultad: '', activo: true })
  const [showForm, setShowForm] = useState(false)
  const [editing, setEditing] = useState(null)
  const [search, setSearch] = useState('')
  const [filterActivo, setFilterActivo] = useState('all')
  const [loading, setLoading] = useState(true)
  const [confirmDelete, setConfirmDelete] = useState(null)

  const fetchItems = () => {
    setLoading(true)
    axios.get('/api/lectores').then(res => { setItems(res.data); setLoading(false) })
  }

  useEffect(() => { fetchItems() }, [])

  const handleSubmit = (e) => {
    e.preventDefault()
    const req = editing ? axios.put(`/api/lectores/${editing}`, form) : axios.post('/api/lectores', form)
    req.then(() => { 
      fetchItems()
      setForm({ codigo_estudiante: '', nombres: '', apellidos: '', email: '', telefono: '', carrera: '', facultad: '', activo: true })
      setEditing(null)
      setShowForm(false)
    })
  }

  const handleEdit = (item) => {
    setEditing(item.id)
    setForm({ 
      codigo_estudiante: item.codigo_estudiante, 
      nombres: item.nombres, 
      apellidos: item.apellidos, 
      email: item.email || '', 
      telefono: item.telefono || '', 
      carrera: item.carrera || '', 
      facultad: item.facultad || '', 
      activo: item.activo 
    })
    setShowForm(true)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleCancel = () => {
    setEditing(null)
    setShowForm(false)
    setForm({ codigo_estudiante: '', nombres: '', apellidos: '', email: '', telefono: '', carrera: '', facultad: '', activo: true })
  }

  const handleDelete = (id) => {
    axios.delete(`/api/lectores/${id}`).then(() => { fetchItems(); setConfirmDelete(null) })
  }

  const filtered = items.filter(item => {
    const matchSearch = item.codigo_estudiante.toLowerCase().includes(search.toLowerCase()) 
      || item.nombres.toLowerCase().includes(search.toLowerCase())
      || item.apellidos.toLowerCase().includes(search.toLowerCase())
    const matchActivo = filterActivo === 'all' ? true : (filterActivo === 'activo' ? item.activo : !item.activo)
    return matchSearch && matchActivo
  })

  const totalLectores = items.length
  const lectoresActivos = items.filter(i => i.activo).length

  return (
    <div className="m-page">
      <div className="m-header">
        <div className="m-header-left">
          <div className="m-header-icon" style={{ background: 'linear-gradient(135deg, #d97706, #fbbf24)' }}>
            <FiUser size={22} />
          </div>
          <div>
            <h1 className="m-title">Gestión de Lectores</h1>
            <p className="m-subtitle">Registro de estudiantes y usuarios</p>
          </div>
        </div>
        <button className="m-btn-primary" onClick={() => setShowForm(v => !v)}>
          {showForm ? <><FiX size={16} /> Cerrar</> : <><FiPlus size={16} /> Nuevo Lector</>}
        </button>
      </div>

      <div className="m-kpi-grid">
        <div className="m-kpi-card kpi-amber">
          <div className="m-kpi-icon"><FiUser size={20} /></div>
          <div>
            <div className="m-kpi-value">{totalLectores}</div>
            <div className="m-kpi-label">Lectores Registrados</div>
          </div>
        </div>
        <div className="m-kpi-card kpi-green">
          <div className="m-kpi-icon"><FiCheckCircle size={20} /></div>
          <div>
            <div className="m-kpi-value">{lectoresActivos}</div>
            <div className="m-kpi-label">Activos</div>
          </div>
        </div>
      </div>

      {showForm && (
        <div className="m-form-panel">
          <div className="m-form-panel-header">
            <h3>{editing ? <><FiEdit2 size={16} /> Editar Lector</> : <><FiPlus size={16} /> Nuevo Lector</>}</h3>
          </div>
          <form onSubmit={handleSubmit} className="m-form-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))' }}>
            <div className="m-form-group">
              <label><FiBookOpen size={13} /> Código Estudiante *</label>
              <input placeholder="Ingrese el código" value={form.codigo_estudiante} onChange={e => setForm({ ...form, codigo_estudiante: e.target.value })} required />
            </div>
            <div className="m-form-group">
              <label><FiUser size={13} /> Nombres *</label>
              <input placeholder="Ingrese los nombres" value={form.nombres} onChange={e => setForm({ ...form, nombres: e.target.value })} required />
            </div>
            <div className="m-form-group">
              <label><FiUser size={13} /> Apellidos *</label>
              <input placeholder="Ingrese los apellidos" value={form.apellidos} onChange={e => setForm({ ...form, apellidos: e.target.value })} required />
            </div>
            <div className="m-form-group">
              <label><FiMail size={13} /> Email</label>
              <input type="email" placeholder="correo@ejemplo.com" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} />
            </div>
            <div className="m-form-group">
              <label><FiPhone size={13} /> Teléfono</label>
              <input placeholder="Número de teléfono" value={form.telefono} onChange={e => setForm({ ...form, telefono: e.target.value })} />
            </div>
            <div className="m-form-group">
              <label><FiBookOpen size={13} /> Carrera</label>
              <input placeholder="Carrera del estudiante" value={form.carrera} onChange={e => setForm({ ...form, carrera: e.target.value })} />
            </div>
            <div className="m-form-group">
              <label><FiBookOpen size={13} /> Facultad</label>
              <input placeholder="Facultad" value={form.facultad} onChange={e => setForm({ ...form, facultad: e.target.value })} />
            </div>
            <div className="m-form-group">
              <label><FiCheckCircle size={13} /> Estado</label>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', paddingTop: '8px' }}>
                <button type="button" onClick={() => setForm({ ...form, activo: true })} style={{
                  flex: 1,
                  padding: '10px 16px',
                  borderRadius: '8px',
                  border: '1px solid ' + (form.activo ? '#059669' : '#e2e8f0'),
                  background: form.activo ? '#d1fae5' : '#fff',
                  color: form.activo ? '#059669' : '#64748b',
                  fontWeight: '600',
                  cursor: 'pointer'
                }}><FiCheckCircle size={14} /> Activo</button>
                <button type="button" onClick={() => setForm({ ...form, activo: false })} style={{
                  flex: 1,
                  padding: '10px 16px',
                  borderRadius: '8px',
                  border: '1px solid ' + (!form.activo ? '#dc2626' : '#e2e8f0'),
                  background: !form.activo ? '#fee2e2' : '#fff',
                  color: !form.activo ? '#dc2626' : '#64748b',
                  fontWeight: '600',
                  cursor: 'pointer'
                }}><FiXCircle size={14} /> Inactivo</button>
              </div>
            </div>
            <div className="m-form-actions" style={{ gridColumn: '1 / -1' }}>
              <button type="submit" className="m-btn-primary">
                {editing ? 'Actualizar Lector' : 'Guardar Lector'}
              </button>
              <button type="button" className="m-btn-ghost" onClick={handleCancel}>Cancelar</button>
            </div>
          </form>
        </div>
      )}

      <div className="m-toolbar">
        <div className="m-search">
          <FiSearch size={15} className="m-search-icon" />
          <input placeholder="Buscar por código, nombres o apellidos..." value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <div className="m-filter-tabs">
          {[['all', 'Todos'], ['activo', 'Activos'], ['inactivo', 'Inactivos']].map(([val, label]) => (
            <button key={val} className={`m-filter-tab ${filterActivo === val ? 'active' : ''}`} onClick={() => setFilterActivo(val)}>{label}</button>
          ))}
        </div>
        <span className="m-count">{filtered.length} lector{filtered.length !== 1 ? 'es' : ''}</span>
      </div>

      <div className="m-table-card">
        {loading ? (
          <div className="m-loading"><div className="m-spinner" /><span>Cargando lectores...</span></div>
        ) : filtered.length === 0 ? (
          <div className="m-empty">
            <FiUser size={40} />
            <h3>No hay lectores registrados</h3>
            <p>Comienza agregando el primer lector</p>
          </div>
        ) : (
          <table className="m-table">
            <thead>
              <tr>
                <th>Lector</th>
                <th>Código</th>
                <th>Carrera</th>
                <th>Contacto</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(item => (
                <tr key={item.id} className={!item.activo ? 'row-inactive' : ''}>
                  <td>
                    <div className="m-user-cell">
                      <div className="m-avatar" style={{ background: 'linear-gradient(135deg, #d97706, #fbbf24)' }}>
                        {item.nombres[0].toUpperCase()}
                      </div>
                      <div>
                        <div style={{ fontWeight: '600', color: '#1e293b' }}>{item.nombres} {item.apellidos}</div>
                        <div style={{ fontSize: '12px', color: '#94a3b8' }}>{item.facultad || 'Sin facultad'}</div>
                      </div>
                    </div>
                  </td>
                  <td className="m-id">{item.codigo_estudiante}</td>
                  <td>{item.carrera || <span className="m-null">Sin carrera</span>}</td>
                  <td>
                    {item.email ? <div style={{ fontSize: '12px' }}><FiMail size={10} /> {item.email}</div> : ''}
                    {item.telefono ? <div style={{ fontSize: '12px', marginTop: '4px' }}><FiPhone size={10} /> {item.telefono}</div> : ''}
                    {!item.email && !item.telefono && <span className="m-null">Sin contacto</span>}
                  </td>
                  <td>
                    {item.activo
                      ? <span className="m-badge m-badge-paid"><FiCheckCircle size={11} /> Activo</span>
                      : <span className="m-badge m-badge-pending"><FiXCircle size={11} /> Inactivo</span>
                    }
                  </td>
                  <td>
                    <div className="m-actions">
                      <button className="m-action-btn edit" title="Editar" onClick={() => handleEdit(item)}>
                        <FiEdit2 size={15} />
                      </button>
                      <button className="m-action-btn del" title="Eliminar" onClick={() => setConfirmDelete(item)}>
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

      {confirmDelete && (
        <div className="m-modal-overlay" onClick={() => setConfirmDelete(null)}>
          <div className="m-modal" onClick={e => e.stopPropagation()}>
            <div className="m-modal-icon del"><FiTrash2 size={28} /></div>
            <h3>Eliminar Lector</h3>
            <p>¿Estás seguro de eliminar a <strong>{confirmDelete.nombres} {confirmDelete.apellidos}</strong>?</p>
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

export default Lectores
