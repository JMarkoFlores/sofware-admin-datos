import React, { useEffect, useState } from 'react'
import axios from 'axios'

function Categorias() {
  const [items, setItems] = useState([])
  const [form, setForm] = useState({ nombre: '', descripcion: '' })
  const [editing, setEditing] = useState(null)

  const fetchItems = () => axios.get('/api/categorias').then(res => setItems(res.data))
  useEffect(() => { fetchItems() }, [])

  const handleSubmit = (e) => {
    e.preventDefault()
    const req = editing ? axios.put(`/api/categorias/${editing}`, form) : axios.post('/api/categorias', form)
    req.then(() => { fetchItems(); setForm({ nombre: '', descripcion: '' }); setEditing(null) })
  }

  const handleEdit = (item) => { setEditing(item.id); setForm({ nombre: item.nombre, descripcion: item.descripcion || '' }) }
  const handleDelete = (id) => { if (confirm('¿Eliminar categoría?')) axios.delete(`/api/categorias/${id}`).then(fetchItems) }

  return (
    <div className="crud-container">
      <div className="card">
        <div className="card-header"><h3>{editing ? 'Editar Categoría' : 'Nueva Categoría'}</h3></div>
        <div className="card-body">
          <form onSubmit={handleSubmit} className="crud-form">
            <div className="form-group">
              <label>Nombre</label>
              <input placeholder="Ingrese el nombre" value={form.nombre} onChange={e => setForm({ ...form, nombre: e.target.value })} required />
            </div>
            <div className="form-group">
              <label>Descripción</label>
              <textarea placeholder="Ingrese la descripción" value={form.descripcion} onChange={e => setForm({ ...form, descripcion: e.target.value })} rows={3} />
            </div>
            <div className="form-actions">
              <button type="submit" className="btn btn-primary">{editing ? 'Actualizar' : 'Guardar'}</button>
              {editing && <button type="button" className="btn btn-secondary" onClick={() => { setEditing(null); setForm({ nombre: '', descripcion: '' }) }}>Cancelar</button>}
            </div>
          </form>
        </div>
      </div>
      <div className="card">
        <div className="card-header"><h3>Lista de Categorías</h3></div>
        <div className="card-body">
          <table className="data-table">
            <thead><tr><th>Nombre</th><th>Descripción</th><th>Acciones</th></tr></thead>
            <tbody>
              {items.map(item => (
                <tr key={item.id}>
                  <td>{item.nombre}</td>
                  <td>{item.descripcion}</td>
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

export default Categorias
