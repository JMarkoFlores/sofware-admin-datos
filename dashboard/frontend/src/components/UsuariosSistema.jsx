import React, { useEffect, useState } from 'react'
import axios from 'axios'

function UsuariosSistema() {
  const [items, setItems] = useState([])
  const [form, setForm] = useState({ username: '', password: '', nombre_completo: '', rol: 'bibliotecario', activo: true })
  const [editing, setEditing] = useState(null)

  const fetchItems = () => axios.get('/api/usuarios').then(res => setItems(res.data))
  useEffect(() => { fetchItems() }, [])

  const handleSubmit = (e) => {
    e.preventDefault()
    const payload = { ...form }
    if (!payload.password) delete payload.password
    const req = editing ? axios.put(`/api/usuarios/${editing}`, payload) : axios.post('/api/usuarios', payload)
    req.then(() => { fetchItems(); setForm({ username: '', password: '', nombre_completo: '', rol: 'bibliotecario', activo: true }); setEditing(null) })
  }

  const handleEdit = (item) => {
    setEditing(item.id)
    setForm({ username: item.username, password: '', nombre_completo: item.nombre_completo || '', rol: item.rol, activo: item.activo })
  }
  const handleDelete = (id) => { if (confirm('¿Eliminar usuario?')) axios.delete(`/api/usuarios/${id}`).then(fetchItems) }

  return (
    <div className="crud-container">
      <div className="card">
        <div className="card-header"><h3>{editing ? 'Editar Usuario' : 'Nuevo Usuario'}</h3></div>
        <div className="card-body">
          <form onSubmit={handleSubmit} className="crud-form">
            <div className="form-group">
              <label>Username</label>
              <input placeholder="Ingrese el username" value={form.username} onChange={e => setForm({ ...form, username: e.target.value })} required />
            </div>
            <div className="form-group">
              <label>Contraseña</label>
              <input type="password" placeholder={editing ? 'Nueva contraseña (opcional)' : 'Contraseña'} value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} required={!editing} />
            </div>
            <div className="form-group">
              <label>Nombre completo</label>
              <input placeholder="Ingrese el nombre completo" value={form.nombre_completo} onChange={e => setForm({ ...form, nombre_completo: e.target.value })} />
            </div>
            <div className="form-group">
              <label>Rol</label>
              <select value={form.rol} onChange={e => setForm({ ...form, rol: e.target.value })}>
                <option value="admin">Administrador</option>
                <option value="bibliotecario">Bibliotecario</option>
              </select>
            </div>
            <div className="form-group">
              <label>
                <input type="checkbox" checked={form.activo} onChange={e => setForm({ ...form, activo: e.target.checked })} /> Activo
              </label>
            </div>
            <div className="form-actions">
              <button type="submit" className="btn btn-primary">{editing ? 'Actualizar' : 'Guardar'}</button>
              {editing && <button type="button" className="btn btn-secondary" onClick={() => { setEditing(null); setForm({ username: '', password: '', nombre_completo: '', rol: 'bibliotecario', activo: true }) }}>Cancelar</button>}
            </div>
          </form>
        </div>
      </div>
      <div className="card">
        <div className="card-header"><h3>Lista de Usuarios</h3></div>
        <div className="card-body">
          <table className="data-table">
            <thead><tr><th>Username</th><th>Nombre</th><th>Rol</th><th>Activo</th><th>Acciones</th></tr></thead>
            <tbody>
              {items.map(item => (
                <tr key={item.id}>
                  <td>{item.username}</td>
                  <td>{item.nombre_completo}</td>
                  <td>{item.rol}</td>
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

export default UsuariosSistema
