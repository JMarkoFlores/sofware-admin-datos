import React, { useEffect, useState } from 'react'
import axios from 'axios'

function Prestamos() {
  const [items, setItems] = useState([])
  const [lectores, setLectores] = useState([])
  const [libros, setLibros] = useState([])
  const [form, setForm] = useState({ lector_id: '', libro_id: '', fecha_devolucion_esperada: '', observaciones: '' })

  const fetchItems = () => axios.get('/api/prestamos').then(res => setItems(res.data))
  useEffect(() => {
    fetchItems()
    axios.get('/api/lectores').then(res => setLectores(res.data))
    axios.get('/api/libros').then(res => setLibros(res.data))
  }, [])

  const handleSubmit = (e) => {
    e.preventDefault()
    axios.post('/api/prestamos', { ...form, lector_id: Number(form.lector_id), libro_id: Number(form.libro_id) })
      .then(() => { fetchItems(); setForm({ lector_id: '', libro_id: '', fecha_devolucion_esperada: '', observaciones: '' }) })
  }

  const handleDevolver = (id) => {
    if (confirm('¿Marcar como devuelto?')) axios.put(`/api/prestamos/${id}/devolver`).then(fetchItems)
  }
  const handleDelete = (id) => { if (confirm('¿Eliminar préstamo?')) axios.delete(`/api/prestamos/${id}`).then(fetchItems) }

  return (
    <div className="crud-container">
      <div className="card">
        <div className="card-header"><h3>Nuevo Préstamo</h3></div>
        <div className="card-body">
          <form onSubmit={handleSubmit} className="crud-form">
            <div className="form-group">
              <label>Lector</label>
              <select value={form.lector_id} onChange={e => setForm({ ...form, lector_id: e.target.value })} required>
                <option value="">Seleccionar lector</option>
                {lectores.map(l => <option key={l.id} value={l.id}>{l.nombres} {l.apellidos}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Libro</label>
              <select value={form.libro_id} onChange={e => setForm({ ...form, libro_id: e.target.value })} required>
                <option value="">Seleccionar libro</option>
                {libros.map(b => <option key={b.id} value={b.id}>{b.titulo}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Fecha devolución esperada</label>
              <input type="date" value={form.fecha_devolucion_esperada} onChange={e => setForm({ ...form, fecha_devolucion_esperada: e.target.value })} required />
            </div>
            <div className="form-group">
              <label>Observaciones</label>
              <textarea placeholder="Ingrese observaciones" value={form.observaciones} onChange={e => setForm({ ...form, observaciones: e.target.value })} rows={2} />
            </div>
            <div className="form-actions">
              <button type="submit" className="btn btn-primary">Registrar Préstamo</button>
            </div>
          </form>
        </div>
      </div>
      <div className="card">
        <div className="card-header"><h3>Lista de Préstamos</h3></div>
        <div className="card-body">
          <table className="data-table">
            <thead><tr><th>Lector</th><th>Libro</th><th>Fecha préstamo</th><th>Devolución esperada</th><th>Estado</th><th>Acciones</th></tr></thead>
            <tbody>
              {items.map(item => (
                <tr key={item.id}>
                  <td>{item.lector ? `${item.lector.nombres} ${item.lector.apellidos}` : '-'}</td>
                  <td>{item.libro?.titulo || '-'}</td>
                  <td>{item.fecha_prestamo?.split('T')[0]}</td>
                  <td>{item.fecha_devolucion_esperada?.split('T')[0]}</td>
                  <td><span className={`badge ${item.estado}`}>{item.estado}</span></td>
                  <td>
                    {item.estado === 'activo' && <button className="btn-icon edit" onClick={() => handleDevolver(item.id)}>↩</button>}
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

export default Prestamos
