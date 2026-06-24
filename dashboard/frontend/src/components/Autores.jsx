import React, { useEffect, useState } from 'react'
import axios from 'axios'

function Autores() {
  const [items, setItems] = useState([])
  const [form, setForm] = useState({ nombre: '', apellido: '', nacionalidad: '', fecha_nacimiento: '', biografia: '' })
  const [editing, setEditing] = useState(null)

  const fetchItems = () => axios.get('/api/autores').then(res => setItems(res.data))

  useEffect(() => { fetchItems() }, [])

  const handleSubmit = (e) => {
    e.preventDefault()
    const payload = { ...form }
    const req = editing
      ? axios.put(`/api/autores/${editing}`, payload)
      : axios.post('/api/autores', payload)
    req.then(() => { fetchItems(); setForm({ nombre: '', apellido: '', nacionalidad: '', fecha_nacimiento: '', biografia: '' }); setEditing(null) })
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
  }

  const handleDelete = (id) => {
    if (confirm('¿Eliminar autor?')) axios.delete(`/api/autores/${id}`).then(fetchItems)
  }

  return (
    <div className="crud-container">
      <div className="card">
        <div className="card-header"><h3>{editing ? 'Editar Autor' : 'Nuevo Autor'}</h3></div>
        <div className="card-body">
          <form onSubmit={handleSubmit} className="crud-form">
            <div className="form-group">
              <label>Nombre</label>
              <input placeholder="Ingrese el nombre" value={form.nombre} onChange={e => setForm({ ...form, nombre: e.target.value })} required />
            </div>
            <div className="form-group">
              <label>Apellido</label>
              <input placeholder="Ingrese el apellido" value={form.apellido} onChange={e => setForm({ ...form, apellido: e.target.value })} required />
            </div>
            <div className="form-group">
              <label>Nacionalidad</label>
              <input placeholder="Ingrese la nacionalidad" value={form.nacionalidad} onChange={e => setForm({ ...form, nacionalidad: e.target.value })} />
            </div>
            <div className="form-group">
              <label>Fecha de nacimiento</label>
              <input type="date" placeholder="Fecha de nacimiento" value={form.fecha_nacimiento} onChange={e => setForm({ ...form, fecha_nacimiento: e.target.value })} />
            </div>
            <div className="form-group">
              <label>Biografía</label>
              <textarea placeholder="Ingrese la biografía" value={form.biografia} onChange={e => setForm({ ...form, biografia: e.target.value })} rows={3} />
            </div>
            <div className="form-actions">
              <button type="submit" className="btn btn-primary">{editing ? 'Actualizar' : 'Guardar'}</button>
              {editing && <button type="button" className="btn btn-secondary" onClick={() => { setEditing(null); setForm({ nombre: '', apellido: '', nacionalidad: '', fecha_nacimiento: '', biografia: '' }) }}>Cancelar</button>}
            </div>
          </form>
        </div>
      </div>
      <div className="card">
        <div className="card-header"><h3>Lista de Autores</h3></div>
        <div className="card-body">
          <table className="data-table">
            <thead><tr><th>Nombre</th><th>Apellido</th><th>Nacionalidad</th><th>Acciones</th></tr></thead>
            <tbody>
              {items.map(item => (
                <tr key={item.id}>
                  <td>{item.nombre}</td>
                  <td>{item.apellido}</td>
                  <td>{item.nacionalidad}</td>
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

export default Autores
