import React, { useEffect, useState } from 'react'
import axios from 'axios'

function Libros() {
  const [items, setItems] = useState([])
  const [autores, setAutores] = useState([])
  const [categorias, setCategorias] = useState([])
  const [form, setForm] = useState({ titulo: '', isbn: '', anio_publicacion: '', editorial: '', ejemplares_total: 1, ejemplares_disponibles: 1, autor_id: '', categoria_id: '' })
  const [editing, setEditing] = useState(null)

  const fetchItems = () => axios.get('/api/libros').then(res => setItems(res.data))
  useEffect(() => {
    fetchItems()
    axios.get('/api/autores').then(res => setAutores(res.data))
    axios.get('/api/categorias').then(res => setCategorias(res.data))
  }, [])

  const handleSubmit = (e) => {
    e.preventDefault()
    const payload = { ...form, anio_publicacion: Number(form.anio_publicacion) || null, ejemplares_total: Number(form.ejemplares_total), ejemplares_disponibles: Number(form.ejemplares_disponibles), autor_id: Number(form.autor_id) || null, categoria_id: Number(form.categoria_id) || null }
    const req = editing ? axios.put(`/api/libros/${editing}`, payload) : axios.post('/api/libros', payload)
    req.then(() => { fetchItems(); setForm({ titulo: '', isbn: '', anio_publicacion: '', editorial: '', ejemplares_total: 1, ejemplares_disponibles: 1, autor_id: '', categoria_id: '' }); setEditing(null) })
  }

  const handleEdit = (item) => {
    setEditing(item.id)
    setForm({
      titulo: item.titulo, isbn: item.isbn || '', anio_publicacion: item.anio_publicacion || '',
      editorial: item.editorial || '', ejemplares_total: item.ejemplares_total,
      ejemplares_disponibles: item.ejemplares_disponibles, autor_id: item.autor_id || '', categoria_id: item.categoria_id || ''
    })
  }
  const handleDelete = (id) => { if (confirm('¿Eliminar libro?')) axios.delete(`/api/libros/${id}`).then(fetchItems) }

  return (
    <div className="crud-container">
      <div className="card">
        <div className="card-header"><h3>{editing ? 'Editar Libro' : 'Nuevo Libro'}</h3></div>
        <div className="card-body">
          <form onSubmit={handleSubmit} className="crud-form">
            <div className="form-group">
              <label>Título</label>
              <input placeholder="Ingrese el título" value={form.titulo} onChange={e => setForm({ ...form, titulo: e.target.value })} required />
            </div>
            <div className="form-group">
              <label>ISBN</label>
              <input placeholder="Ingrese el ISBN" value={form.isbn} onChange={e => setForm({ ...form, isbn: e.target.value })} />
            </div>
            <div className="form-group">
              <label>Año publicación</label>
              <input type="number" placeholder="Ingrese el año" value={form.anio_publicacion} onChange={e => setForm({ ...form, anio_publicacion: e.target.value })} />
            </div>
            <div className="form-group">
              <label>Editorial</label>
              <input placeholder="Ingrese la editorial" value={form.editorial} onChange={e => setForm({ ...form, editorial: e.target.value })} />
            </div>
            <div className="form-group">
              <label>Ejemplares total</label>
              <input type="number" placeholder="Total de ejemplares" value={form.ejemplares_total} onChange={e => setForm({ ...form, ejemplares_total: e.target.value })} required />
            </div>
            <div className="form-group">
              <label>Ejemplares disponibles</label>
              <input type="number" placeholder="Disponibles" value={form.ejemplares_disponibles} onChange={e => setForm({ ...form, ejemplares_disponibles: e.target.value })} required />
            </div>
            <div className="form-group">
              <label>Autor</label>
              <select value={form.autor_id} onChange={e => setForm({ ...form, autor_id: e.target.value })}>
                <option value="">Seleccionar autor</option>
                {autores.map(a => <option key={a.id} value={a.id}>{a.nombre} {a.apellido}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Categoría</label>
              <select value={form.categoria_id} onChange={e => setForm({ ...form, categoria_id: e.target.value })}>
                <option value="">Seleccionar categoría</option>
                {categorias.map(c => <option key={c.id} value={c.id}>{c.nombre}</option>)}
              </select>
            </div>
            <div className="form-actions">
              <button type="submit" className="btn btn-primary">{editing ? 'Actualizar' : 'Guardar'}</button>
              {editing && <button type="button" className="btn btn-secondary" onClick={() => { setEditing(null); setForm({ titulo: '', isbn: '', anio_publicacion: '', editorial: '', ejemplares_total: 1, ejemplares_disponibles: 1, autor_id: '', categoria_id: '' }) }}>Cancelar</button>}
            </div>
          </form>
        </div>
      </div>
      <div className="card">
        <div className="card-header"><h3>Lista de Libros</h3></div>
        <div className="card-body">
          <table className="data-table">
            <thead><tr><th>Título</th><th>ISBN</th><th>Autor</th><th>Categoría</th><th>Disponibles</th><th>Acciones</th></tr></thead>
            <tbody>
              {items.map(item => (
                <tr key={item.id}>
                  <td>{item.titulo}</td>
                  <td>{item.isbn}</td>
                  <td>{item.autor ? `${item.autor.nombre} ${item.autor.apellido}` : '-'}</td>
                  <td>{item.categoria?.nombre || '-'}</td>
                  <td>{item.ejemplares_disponibles}/{item.ejemplares_total}</td>
                  <td>
                    <button className="btn-icon edit" onClick={() => handleEdit(item)}>✎</button>
                    <button className="btn-icon delete" onClick={() => handleDelete(item.id)}>🗑</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default Libros
