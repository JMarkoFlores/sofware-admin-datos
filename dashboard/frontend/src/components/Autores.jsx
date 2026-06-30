import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { FiUsers, FiPlus, FiX, FiEdit2, FiTrash2, FiSearch, FiFilter, FiGlobe, FiCalendar, FiFileText } from 'react-icons/fi'

function Autores() {
  const [items, setItems] = useState([])
  const [form, setForm] = useState({ nombre: '', apellido: '', nacionalidad: '', fecha_nacimiento: '', biografia: '' })
  const [showForm, setShowForm] = useState(false)
  const [editing, setEditing] = useState(null)
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [confirmDelete, setConfirmDelete] = useState(null)

  const fetchItems = () => {
    setLoading(true)
    axios.get('/api/autores').then(res => { setItems(res.data); setLoading(false) })
  }

  useEffect(() => { fetchItems() }, [])

  const handleSubmit = (e) => {
    e.preventDefault()
    const req = editing
      ? axios.put(`/api/autores/${editing}`, form)
      : axios.post('/api/autores', form)
    req.then(() => { 
      fetchItems()
      setForm({ nombre: '', apellido: '', nacionalidad: '', fecha_nacimiento: '', biografia: '' })
      setEditing(null)
      setShowForm(false)
    })
  }

  const handleEdit = (item) => {
    setEditing(item.id)
    setForm({
      nombre: item.nombre,
      apellido: item.apellido,
      nacionalidad: item.nacionalidad || '',
      fecha_nacimiento: item.fecha_nacimiento ? item.fecha_nacimiento.split('T')[0] : '',
      biografia: item.biografia || '',
    })
    setShowForm(true)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleCancel = () => {
    setEditing(null)
    setShowForm(false)
    setForm({ nombre: '', apellido: '', nacionalidad: '', fecha_nacimiento: '', biografia: '' })
  }

  const handleDelete = (id) => {
    axios.delete(`/api/autores/${id}`).then(() => { fetchItems(); setConfirmDelete(null) })
  }

  const filtered = items.filter(item => {
    return item.nombre.toLowerCase().includes(search.toLowerCase()) 
      || item.apellido.toLowerCase().includes(search.toLowerCase())
      || (item.nacionalidad && item.nacionalidad.toLowerCase().includes(search.toLowerCase()))
  })

  const totalAutores = items.length
  const conNacionalidad = items.filter(i => i.nacionalidad).length

  return (
    <div className="m-page">
      <div className="m-header">
        <div className="m-header-left">
          <div className="m-header-icon" style={{ background: 'linear-gradient(135deg, #7c3aed, #a78bfa)' }}>
            <FiUsers size={22} />
          </div>
          <div>
            <h1 className="m-title">Gestión de Autores</h1>
            <p className="m-subtitle">Registro de autores del catálogo</p>
          </div>
        </div>
        <button className="m-btn-primary" onClick={() => setShowForm(v => !v)}>
          {showForm ? <><FiX size={16} /> Cerrar</> : <><FiPlus size={16} /> Nuevo Autor</>}
        </button>
      </div>

      <div className="m-kpi-grid">
        <div className="m-kpi-card kpi-indigo">
          <div className="m-kpi-icon"><FiUsers size={20} /></div>
          <div>
            <div className="m-kpi-value">{totalAutores}</div>
            <div className="m-kpi-label">Autores Registrados</div>
          </div>
        </div>
        <div className="m-kpi-card kpi-green">
          <div className="m-kpi-icon"><FiGlobe size={20} /></div>
          <div>
            <div className="m-kpi-value">{conNacionalidad}</div>
            <div className="m-kpi-label">Con Nacionalidad</div>
          </div>
        </div>
      </div>

      {showForm && (
        <div className="m-form-panel">
          <div className="m-form-panel-header">
            <h3>{editing ? <><FiEdit2 size={16} /> Editar Autor</> : <><FiPlus size={16} /> Nuevo Autor</>}</h3>
          </div>
          <form onSubmit={handleSubmit} className="m-form-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))' }}>
            <div className="m-form-group">
              <label><FiUsers size={13} /> Nombre *</label>
              <input placeholder="Ingrese el nombre" value={form.nombre} onChange={e => setForm({ ...form, nombre: e.target.value })} required />
            </div>
            <div className="m-form-group">
              <label><FiUsers size={13} /> Apellido *</label>
              <input placeholder="Ingrese el apellido" value={form.apellido} onChange={e => setForm({ ...form, apellido: e.target.value })} required />
            </div>
            <div className="m-form-group">
              <label><FiGlobe size={13} /> Nacionalidad</label>
              <input placeholder="País de origen" value={form.nacionalidad} onChange={e => setForm({ ...form, nacionalidad: e.target.value })} />
            </div>
            <div className="m-form-group">
              <label><FiCalendar size={13} /> Fecha de Nacimiento</label>
              <input type="date" value={form.fecha_nacimiento} onChange={e => setForm({ ...form, fecha_nacimiento: e.target.value })} />
            </div>
            <div className="m-form-group" style={{ gridColumn: '1 / -1' }}>
              <label><FiFileText size={13} /> Biografía</label>
              <textarea placeholder="Breve biografía del autor" value={form.biografia} onChange={e => setForm({ ...form, biografia: e.target.value })} rows={3} />
            </div>
            <div className="m-form-actions" style={{ gridColumn: '1 / -1' }}>
              <button type="submit" className="m-btn-primary">
                {editing ? 'Actualizar Autor' : 'Guardar Autor'}
              </button>
              <button type="button" className="m-btn-ghost" onClick={handleCancel}>Cancelar</button>
            </div>
          </form>
        </div>
      )}

      <div className="m-toolbar">
        <div className="m-search">
          <FiSearch size={15} className="m-search-icon" />
          <input placeholder="Buscar por nombre o nacionalidad..." value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <span className="m-count">{filtered.length} autor{filtered.length !== 1 ? 'es' : ''}</span>
      </div>

      <div className="m-table-card">
        {loading ? (
          <div className="m-loading"><div className="m-spinner" /><span>Cargando autores...</span></div>
        ) : filtered.length === 0 ? (
          <div className="m-empty">
            <FiUsers size={40} />
            <h3>No hay autores registrados</h3>
            <p>Comienza agregando el primer autor</p>
          </div>
        ) : (
          <table className="m-table">
            <thead>
              <tr>
                <th>Nombre Completo</th>
                <th>Nacionalidad</th>
                <th>Fecha de Nacimiento</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(item => (
                <tr key={item.id}>
                  <td>
                    <div className="m-user-cell">
                      <div className="m-avatar" style={{ background: 'linear-gradient(135deg, #7c3aed, #a78bfa)' }}>
                        {item.nombre[0].toUpperCase()}
                      </div>
                      <div>
                        <div style={{ fontWeight: '600', color: '#1e293b' }}>{item.nombre} {item.apellido}</div>
                      </div>
                    </div>
                  </td>
                  <td>{item.nacionalidad || <span className="m-null">Sin datos</span>}</td>
                  <td className="m-date">
                    {item.fecha_nacimiento ? new Date(item.fecha_nacimiento).toLocaleDateString('es-PE') : '-'}
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
            <h3>Eliminar Autor</h3>
            <p>¿Estás seguro de eliminar a <strong>{confirmDelete.nombre} {confirmDelete.apellido}</strong>?</p>
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

export default Autores
