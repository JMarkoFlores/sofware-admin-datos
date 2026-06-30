import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { FiFilter, FiPlus, FiX, FiEdit2, FiTrash2, FiSearch, FiFileText } from 'react-icons/fi'

function Categorias() {
  const [items, setItems] = useState([])
  const [form, setForm] = useState({ nombre: '', descripcion: '' })
  const [showForm, setShowForm] = useState(false)
  const [editing, setEditing] = useState(null)
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [confirmDelete, setConfirmDelete] = useState(null)

  const fetchItems = () => {
    setLoading(true)
    axios.get('/api/categorias').then(res => { setItems(res.data); setLoading(false) })
  }

  useEffect(() => { fetchItems() }, [])

  const handleSubmit = (e) => {
    e.preventDefault()
    const req = editing ? axios.put(`/api/categorias/${editing}`, form) : axios.post('/api/categorias', form)
    req.then(() => { 
      fetchItems()
      setForm({ nombre: '', descripcion: '' })
      setEditing(null)
      setShowForm(false)
    })
  }

  const handleEdit = (item) => {
    setEditing(item.id)
    setForm({ nombre: item.nombre, descripcion: item.descripcion || '' })
    setShowForm(true)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleCancel = () => {
    setEditing(null)
    setShowForm(false)
    setForm({ nombre: '', descripcion: '' })
  }

  const handleDelete = (id) => {
    axios.delete(`/api/categorias/${id}`).then(() => { fetchItems(); setConfirmDelete(null) })
  }

  const filtered = items.filter(item => {
    return item.nombre.toLowerCase().includes(search.toLowerCase()) 
      || (item.descripcion && item.descripcion.toLowerCase().includes(search.toLowerCase()))
  })

  return (
    <div className="m-page">
      <div className="m-header">
        <div className="m-header-left">
          <div className="m-header-icon" style={{ background: 'linear-gradient(135deg, #059669, #34d399)' }}>
            <FiFilter size={22} />
          </div>
          <div>
            <h1 className="m-title">Gestión de Categorías</h1>
            <p className="m-subtitle">Clasificación del catálogo de libros</p>
          </div>
        </div>
        <button className="m-btn-primary" onClick={() => setShowForm(v => !v)}>
          {showForm ? <><FiX size={16} /> Cerrar</> : <><FiPlus size={16} /> Nueva Categoría</>}
        </button>
      </div>

      <div className="m-kpi-grid">
        <div className="m-kpi-card kpi-green">
          <div className="m-kpi-icon"><FiFilter size={20} /></div>
          <div>
            <div className="m-kpi-value">{items.length}</div>
            <div className="m-kpi-label">Categorías Registradas</div>
          </div>
        </div>
      </div>

      {showForm && (
        <div className="m-form-panel">
          <div className="m-form-panel-header">
            <h3>{editing ? <><FiEdit2 size={16} /> Editar Categoría</> : <><FiPlus size={16} /> Nueva Categoría</>}</h3>
          </div>
          <form onSubmit={handleSubmit} className="m-form-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))' }}>
            <div className="m-form-group" style={{ gridColumn: '1 / -1' }}>
              <label><FiFilter size={13} /> Nombre de la Categoría *</label>
              <input placeholder="Ingrese el nombre" value={form.nombre} onChange={e => setForm({ ...form, nombre: e.target.value })} required />
            </div>
            <div className="m-form-group" style={{ gridColumn: '1 / -1' }}>
              <label><FiFileText size={13} /> Descripción</label>
              <textarea placeholder="Descripción de la categoría" value={form.descripcion} onChange={e => setForm({ ...form, descripcion: e.target.value })} rows={3} />
            </div>
            <div className="m-form-actions" style={{ gridColumn: '1 / -1' }}>
              <button type="submit" className="m-btn-primary">
                {editing ? 'Actualizar Categoría' : 'Guardar Categoría'}
              </button>
              <button type="button" className="m-btn-ghost" onClick={handleCancel}>Cancelar</button>
            </div>
          </form>
        </div>
      )}

      <div className="m-toolbar">
        <div className="m-search">
          <FiSearch size={15} className="m-search-icon" />
          <input placeholder="Buscar categoría..." value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <span className="m-count">{filtered.length} categoría{filtered.length !== 1 ? 's' : ''}</span>
      </div>

      <div className="m-table-card">
        {loading ? (
          <div className="m-loading"><div className="m-spinner" /><span>Cargando categorías...</span></div>
        ) : filtered.length === 0 ? (
          <div className="m-empty">
            <FiFilter size={40} />
            <h3>No hay categorías registradas</h3>
            <p>Comienza agregando la primera categoría</p>
          </div>
        ) : (
          <table className="m-table">
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Descripción</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(item => (
                <tr key={item.id}>
                  <td>
                    <span style={{ fontWeight: '600', color: '#1e293b' }}>{item.nombre}</span>
                  </td>
                  <td>{item.descripcion || <span className="m-null">Sin descripción</span>}</td>
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
            <h3>Eliminar Categoría</h3>
            <p>¿Estás seguro de eliminar la categoría <strong>{confirmDelete.nombre}</strong>?</p>
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

export default Categorias
