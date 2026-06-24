import React, { useEffect, useState } from 'react'
import axios from 'axios'

function Lectores() {
  const [items, setItems] = useState([])
  const [form, setForm] = useState({ codigo_estudiante: '', nombres: '', apellidos: '', email: '', telefono: '', carrera: '', facultad: '', activo: true })
  const [editing, setEditing] = useState(null)

  const fetchItems = () => axios.get('/api/lectores').then(res => setItems(res.data))
  useEffect(() => { fetchItems() }, [])

  const handleSubmit = (e) => {
    e.preventDefault()
    const req = editing ? axios.put(`/api/lectores/${editing}`, form) : axios.post('/api/lectores', form)
    req.then(() => { fetchItems(); setForm({ codigo_estudiante: '', nombres: '', apellidos: '', email: '', telefono: '', carrera: '', facultad: '', activo: true }); setEditing(null) })
  }

  const handleEdit = (item) => {
    setEditing(item.id)
    setForm({ codigo_estudiante: item.codigo_estudiante, nombres: item.nombres, apellidos: item.apellidos, email: item.email || '', telefono: item.telefono || '', carrera: item.carrera || '', facultad: item.facultad || '', activo: item.activo })
  }
  const handleDelete = (id) => { if (confirm('¿Eliminar lector?')) axios.delete(`/api/lectores/${id}`).then(fetchItems) }

  return (
    <div className="crud-container">
      <div className="card">
        <div className="card-header"><h3>{editing ? 'Editar Lector' : 'Nuevo Lector'}</h3></div>
        <div className="card-body">
          <form onSubmit={handleSubmit} className="crud-form">
            <div className="form-group">
              <label>Código estudiante</label>
              <input placeholder="Ingrese el código" value={form.codigo_estudiante} onChange={e => setForm({ ...form, codigo_estudiante: e.target.value })} required />
            </div>
            <div className="form-group">
              <label>Nombres</label>
              <input placeholder="Ingrese los nombres" value={form.nombres} onChange={e => setForm({ ...form, nombres: e.target.value })} required />
            </div>
            <div className="form-group">
              <label>Apellidos</label>
              <input placeholder="Ingrese los apellidos" value={form.apellidos} onChange={e => setForm({ ...form, apellidos: e.target.value })} required />
            </div>
            <div className="form-group">
              <label>Email</label>
              <input placeholder="Ingrese el email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} />
            </div>
            <div className="form-group">
              <label>Teléfono</label>
              <input placeholder="Ingrese el teléfono" value={form.telefono} onChange={e => setForm({ ...form, telefono: e.target.value })} />
            </div>
            <div className="form-group">
              <label>Carrera</label>
              <input placeholder="Ingrese la carrera" value={form.carrera} onChange={e => setForm({ ...form, carrera: e.target.value })} />
            </div>
            <div className="form-group">
              <label>Facultad</label>
              <input placeholder="Ingrese la facultad" value={form.facultad} onChange={e => setForm({ ...form, facultad: e.target.value })} />
            </div>
            <div className="form-group">
              <label>
                <input type="checkbox" checked={form.activo} onChange={e => setForm({ ...form, activo: e.target.checked })} /> Activo
              </label>
            </div>
            <div className="form-actions">
              <button type="submit" className="btn btn-primary">{editing ? 'Actualizar' : 'Guardar'}</button>
              {editing && <button type="button" className="btn btn-secondary" onClick={() => { setEditing(null); setForm({ codigo_estudiante: '', nombres: '', apellidos: '', email: '', telefono: '', carrera: '', facultad: '', activo: true }) }}>Cancelar</button>}
            </div>
          </form>
        </div>
      </div>
      <div className="card">
        <div className="card-header"><h3>Lista de Lectores</h3></div>
        <div className="card-body">
          <table className="data-table">
            <thead><tr><th>Código</th><th>Nombres</th><th>Apellidos</th><th>Carrera</th><th>Facultad</th><th>Activo</th><th>Acciones</th></tr></thead>
            <tbody>
              {items.map(item => (
                <tr key={item.id}>
                  <td>{item.codigo_estudiante}</td>
                  <td>{item.nombres}</td>
                  <td>{item.apellidos}</td>
                  <td>{item.carrera}</td>
                  <td>{item.facultad}</td>
                  <td>{item.activo ? 'Sí' : 'No'}</td>
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

export default Lectores
