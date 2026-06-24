import React, { useEffect, useState } from 'react'
import axios from 'axios'

function Devoluciones() {
  const [items, setItems] = useState([])
  const [prestamos, setPrestamos] = useState([])
  const [form, setForm] = useState({ prestamo_id: '', estado_libro: 'bueno', observaciones: '' })

  const fetchItems = () => axios.get('/api/devoluciones').then(res => setItems(res.data))
  useEffect(() => {
    fetchItems()
    axios.get('/api/prestamos').then(res => setPrestamos(res.data.filter(p => p.estado === 'devuelto' || p.estado === 'vencido')))
  }, [])

  const handleSubmit = (e) => {
    e.preventDefault()
    axios.post('/api/devoluciones', { ...form, prestamo_id: Number(form.prestamo_id) })
      .then(() => { fetchItems(); setForm({ prestamo_id: '', estado_libro: 'bueno', observaciones: '' }) })
  }

  const handleDelete = (id) => { if (confirm('¿Eliminar devolución?')) axios.delete(`/api/devoluciones/${id}`).then(fetchItems) }

  return (
    <div className="crud-container">
      <div className="card">
        <div className="card-header"><h3>Nueva Devolución</h3></div>
        <div className="card-body">
          <form onSubmit={handleSubmit} className="crud-form">
            <div className="form-group">
              <label>Préstamo</label>
              <select value={form.prestamo_id} onChange={e => setForm({ ...form, prestamo_id: e.target.value })} required>
                <option value="">Seleccionar préstamo</option>
                {prestamos.map(p => <option key={p.id} value={p.id}>{p.libro?.titulo} - {p.lector?.nombres} {p.lector?.apellidos}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Estado libro</label>
              <select value={form.estado_libro} onChange={e => setForm({ ...form, estado_libro: e.target.value })}>
                <option value="bueno">Bueno</option>
                <option value="dañado">Dañado</option>
                <option value="perdido">Perdido</option>
              </select>
            </div>
            <div className="form-group">
              <label>Observaciones</label>
              <textarea placeholder="Ingrese observaciones" value={form.observaciones} onChange={e => setForm({ ...form, observaciones: e.target.value })} rows={2} />
            </div>
            <div className="form-actions">
              <button type="submit" className="btn btn-primary">Registrar Devolución</button>
            </div>
          </form>
        </div>
      </div>
      <div className="card">
        <div className="card-header"><h3>Lista de Devoluciones</h3></div>
        <div className="card-body">
          <table className="data-table">
            <thead><tr><th>Préstamo ID</th><th>Fecha</th><th>Estado libro</th><th>Observaciones</th><th>Acciones</th></tr></thead>
            <tbody>
              {items.map(item => (
                <tr key={item.id}>
                  <td>{item.prestamo_id}</td>
                  <td>{item.fecha_devolucion?.split('T')[0]}</td>
                  <td><span className={`badge ${item.estado_libro}`}>{item.estado_libro}</span></td>
                  <td>{item.observaciones}</td>
                  <td>
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

export default Devoluciones
