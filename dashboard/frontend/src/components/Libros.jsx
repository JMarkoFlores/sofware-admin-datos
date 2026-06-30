import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { FiBook, FiPlus, FiX, FiEdit2, FiTrash2, FiSearch, FiFilter, FiCalendar, FiHash, FiCopy } from 'react-icons/fi'

function Libros() {
  const [items, setItems] = useState([])
  const [autores, setAutores] = useState([])
  const [categorias, setCategorias] = useState([])
  const [form, setForm] = useState({ titulo: '', isbn: '', anio_publicacion: '', editorial: '', ejemplares_total: 1, ejemplares_disponibles: 1, autor_id: '', categoria_id: '' })
  const [showForm, setShowForm] = useState(false)
  const [editing, setEditing] = useState(null)
  const [search, setSearch] = useState('')
  const [filterCategoria, setFilterCategoria] = useState('all')
  const [loading, setLoading] = useState(true)
  const [confirmDelete, setConfirmDelete] = useState(null)

  const fetchItems = () => {
    setLoading(true)
    axios.get('/api/libros').then(res => { setItems(res.data); setLoading(false) })
  }

  useEffect(() => {
    fetchItems()
    axios.get('/api/autores').then(res => setAutores(res.data))
    axios.get('/api/categorias').then(res => setCategorias(res.data))
  }, [])

  const handleSubmit = (e) => {
    e.preventDefault()
    const payload = { 
      ...form, 
      anio_publicacion: form.anio_publicacion ? Number(form.anio_publicacion) : null, 
      ejemplares_total: Number(form.ejemplares_total), 
      ejemplares_disponibles: Number(form.ejemplares_disponibles), 
      autor_id: form.autor_id ? Number(form.autor_id) : null, 
      categoria_id: form.categoria_id ? Number(form.categoria_id) : null 
    }
    
    const req = editing
      ? axios.put(`/api/libros/${editing}`, payload)
      : axios.post('/api/libros', payload)
      
    req.then(() => { 
      fetchItems()
      setForm({ titulo: '', isbn: '', anio_publicacion: '', editorial: '', ejemplares_total: 1, ejemplares_disponibles: 1, autor_id: '', categoria_id: '' })
      setEditing(null)
      setShowForm(false)
    })
  }

  const handleEdit = (item) => {
    setEditing(item.id)
    setForm({
      titulo: item.titulo,
      isbn: item.isbn || '',
      anio_publicacion: item.anio_publicacion || '',
      editorial: item.editorial || '',
      ejemplares_total: item.ejemplares_total,
      ejemplares_disponibles: item.ejemplares_disponibles,
      autor_id: item.autor_id || '',
      categoria_id: item.categoria_id || ''
    })
    setShowForm(true)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleCancel = () => {
    setEditing(null)
    setShowForm(false)
    setForm({ titulo: '', isbn: '', anio_publicacion: '', editorial: '', ejemplares_total: 1, ejemplares_disponibles: 1, autor_id: '', categoria_id: '' })
  }

  const handleDelete = (id) => {
    axios.delete(`/api/libros/${id}`).then(() => { fetchItems(); setConfirmDelete(null) })
  }

  const filtered = items.filter(item => {
    const matchSearch = item.titulo.toLowerCase().includes(search.toLowerCase()) 
      || (item.isbn && item.isbn.toLowerCase().includes(search.toLowerCase()))
      || (item.autor && `${item.autor.nombre} ${item.autor.apellido}`.toLowerCase().includes(search.toLowerCase()))
    
    const matchCategoria = filterCategoria === 'all' 
      ? true 
      : (item.categoria_id && item.categoria_id === Number(filterCategoria))
    
    return matchSearch && matchCategoria
  })

  const totalLibros = items.length
  const disponibles = items.reduce((acc, i) => acc + i.ejemplares_disponibles, 0)
  const totalEjemplares = items.reduce((acc, i) => acc + i.ejemplares_total, 0)

  return (
    <div className="m-page">
      <div className="m-header">
        <div className="m-header-left">
          <div className="m-header-icon" style={{ background: 'linear-gradient(135deg, #3b82f6, #60a5fa)' }}>
            <FiBook size={22} />
          </div>
          <div>
            <h1 className="m-title">Gestión de Libros</h1>
            <p className="m-subtitle">Catálogo completo de la biblioteca</p>
          </div>
        </div>
        <button className="m-btn-primary" onClick={() => setShowForm(v => !v)}>
          {showForm ? <><FiX size={16} /> Cerrar</> : <><FiPlus size={16} /> Nuevo Libro</>}
        </button>
      </div>

      <div className="m-kpi-grid">
        <div className="m-kpi-card kpi-blue">
          <div className="m-kpi-icon"><FiBook size={20} /></div>
          <div>
            <div className="m-kpi-value">{totalLibros}</div>
            <div className="m-kpi-label">Títulos Registrados</div>
          </div>
        </div>
        <div className="m-kpi-card kpi-green">
          <div className="m-kpi-icon"><FiCopy size={20} /></div>
          <div>
            <div className="m-kpi-value">{disponibles}</div>
            <div className="m-kpi-label">Ejemplares Disponibles</div>
          </div>
        </div>
        <div className="m-kpi-card kpi-indigo">
          <div className="m-kpi-icon"><FiBook size={20} /></div>
          <div>
            <div className="m-kpi-value">{totalEjemplares}</div>
            <div className="m-kpi-label">Total de Ejemplares</div>
          </div>
        </div>
      </div>

      {showForm && (
        <div className="m-form-panel">
          <div className="m-form-panel-header">
            <h3>{editing ? <><FiEdit2 size={16} /> Editar Libro</> : <><FiPlus size={16} /> Nuevo Libro</>}</h3>
          </div>
          <form onSubmit={handleSubmit} className="m-form-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))' }}>
            <div className="m-form-group" style={{ gridColumn: '1 / -1' }}>
              <label><FiBook size={13} /> Título del Libro *</label>
              <input placeholder="Ingrese el título completo" value={form.titulo} onChange={e => setForm({ ...form, titulo: e.target.value })} required />
            </div>
            <div className="m-form-group">
              <label><FiHash size={13} /> ISBN</label>
              <input placeholder="978-987-123456-7" value={form.isbn} onChange={e => setForm({ ...form, isbn: e.target.value })} />
            </div>
            <div className="m-form-group">
              <label><FiCalendar size={13} /> Año de Publicación</label>
              <input type="number" min="1000" max="2100" placeholder="2024" value={form.anio_publicacion} onChange={e => setForm({ ...form, anio_publicacion: e.target.value })} />
            </div>
            <div className="m-form-group">
              <label><FiBook size={13} /> Editorial</label>
              <input placeholder="Nombre de la editorial" value={form.editorial} onChange={e => setForm({ ...form, editorial: e.target.value })} />
            </div>
            <div className="m-form-group">
              <label><FiUsers size={13} /> Autor</label>
              <select value={form.autor_id} onChange={e => setForm({ ...form, autor_id: e.target.value })}>
                <option value="">Seleccionar autor...</option>
                {autores.map(a => <option key={a.id} value={a.id}>{a.nombre} {a.apellido}</option>)}
              </select>
            </div>
            <div className="m-form-group">
              <label><FiFilter size={13} /> Categoría</label>
              <select value={form.categoria_id} onChange={e => setForm({ ...form, categoria_id: e.target.value })}>
                <option value="">Seleccionar categoría...</option>
                {categorias.map(c => <option key={c.id} value={c.id}>{c.nombre}</option>)}
              </select>
            </div>
            <div className="m-form-group">
              <label><FiCopy size={13} /> Ejemplares Totales *</label>
              <input type="number" min="1" placeholder="Total de ejemplares" value={form.ejemplares_total} onChange={e => setForm({ ...form, ejemplares_total: e.target.value })} required />
            </div>
            <div className="m-form-group">
              <label><FiCopy size={13} /> Ejemplares Disponibles *</label>
              <input type="number" min="0" placeholder="Ejemplares disponibles" value={form.ejemplares_disponibles} onChange={e => setForm({ ...form, ejemplares_disponibles: e.target.value })} required />
            </div>
            <div className="m-form-actions" style={{ gridColumn: '1 / -1' }}>
              <button type="submit" className="m-btn-primary">
                {editing ? 'Actualizar Libro' : 'Guardar Libro'}
              </button>
              <button type="button" className="m-btn-ghost" onClick={handleCancel}>Cancelar</button>
            </div>
          </form>
        </div>
      )}

      <div className="m-toolbar">
        <div className="m-search">
          <FiSearch size={15} className="m-search-icon" />
          <input placeholder="Buscar por título, ISBN o autor..." value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <div className="m-filter-tabs">
          <FiFilter size={14} style={{ color: '#64748b' }} />
          <button key="all" className={`m-filter-tab ${filterCategoria === 'all' ? 'active' : ''}`} onClick={() => setFilterCategoria('all')}>Todos</button>
          {categorias.map(c => (
            <button key={c.id} className={`m-filter-tab ${filterCategoria === String(c.id) ? 'active' : ''}`} onClick={() => setFilterCategoria(String(c.id))}>{c.nombre}</button>
          ))}
        </div>
        <span className="m-count">{filtered.length} libro{filtered.length !== 1 ? 's' : ''}</span>
      </div>

      <div className="m-table-card">
        {loading ? (
          <div className="m-loading"><div className="m-spinner" /><span>Cargando libros...</span></div>
        ) : filtered.length === 0 ? (
          <div className="m-empty">
            <FiBook size={40} />
            <h3>No hay libros registrados</h3>
            <p>Comienza agregando el primer libro al catálogo</p>
          </div>
        ) : (
          <table className="m-table">
            <thead>
              <tr>
                <th>Título</th>
                <th>Autor</th>
                <th>Categoría</th>
                <th>Disponibles / Total</th>
                <th>Año</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(item => (
                <tr key={item.id}>
                  <td className="m-id" style={{ maxWidth: '300px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    <div style={{ fontWeight: '600', color: '#1e293b' }}>{item.titulo}</div>
                    {item.isbn && <div style={{ fontSize: '12px', color: '#94a3b8' }}>ISBN: {item.isbn}</div>}
                  </td>
                  <td>
                    <div className="m-user-cell">
                      <div className="m-avatar" style={{ background: 'linear-gradient(135deg, #3b82f6, #60a5fa)' }}>
                        {item.autor ? item.autor.nombre[0].toUpperCase() : '?'}
                      </div>
                      <span>{item.autor ? `${item.autor.nombre} ${item.autor.apellido}` : 'Sin autor'}</span>
                    </div>
                  </td>
                  <td>
                    {item.categoria ? (
                      <span className="m-badge" style={{ background: '#dbeafe', color: '#2563eb' }}>
                        {item.categoria.nombre}
                      </span>
                    ) : <span className="m-null">Sin categoría</span>}
                  </td>
                  <td>
                    <span style={{ fontWeight: '600', color: item.ejemplares_disponibles > 0 ? '#059669' : '#dc2626' }}>
                      {item.ejemplares_disponibles}
                    </span>
                    <span style={{ color: '#94a3b8' }}> / {item.ejemplares_total}</span>
                  </td>
                  <td className="m-date">{item.anio_publicacion || '-'}</td>
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
            <h3>Eliminar Libro</h3>
            <p>¿Estás seguro de eliminar el libro <strong>{confirmDelete.titulo}</strong>?</p>
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

export default Libros
