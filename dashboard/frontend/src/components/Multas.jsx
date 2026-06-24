import React, { useEffect, useState } from 'react'
import axios from 'axios'

function Multas() {
  const [items, setItems] = useState([])
  const [lectores, setLectores] = useState([])
  const [prestamos, setPrestamos] = useState([])
  const [form, setForm] = useState({ lector_id: '', prestamo_id: '', monto: '', motivo: '', pagada: false })

  const fetchItems = () => axios.get('/api/multas').then(res => setItems(res.data))
  useEffect(() => {
    fetchItems()
    axios.get('/api/lectores').then(res => setLectores(res.data))
    axios.get('/api/prestamos').then(res => setPrestamos(res.data))
  }, [])

  const handleSubmit = (e) => {
    e.preventDefault()
    axios.post('/api/multas', { ...form, lector_id: Number(form.lector_id), prestamo_id: Number(form.prestamo_id) || null, monto: Number(form.monto) })
      .then(() => { fetchItems(); setForm({ lector_id: '', prestamo_id: '', monto: '', motivo: '', pagada: false }) })
  }

  const handlePagar = (id) => { if (confirm('¿Marcar multa como pagada?')) axios.put(`/api/multas/${id}/pagar`).then(fetchItems) }
  const handleDelete = (id) => { if (confirm('¿Eliminar multa?')) axios.delete(`/api/multas/${id}`).then(fetchItems) }

  return (
    <div className="crud-container">
      <div className="card">
        <div className="card-header"><h3>Nueva Multa</h3></div>
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
              <label>Préstamo</label>
              <select value={form.prestamo_id} onChange={e => setForm({ ...form, prestamo_id: e.target.value })}>
                <option value="">Seleccionar préstamo (opcional)</option>
                {prestamos.map(p => <option key={p.id} value={p.id}>{p.libro?.titulo} - {p.lector?.nombres}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Monto</label>
              <input type="number" step="0.01" placeholder="Ingrese el monto" value={form.monto} onChange={e => setForm({ ...form, monto: e.target.value })} required />
            </div>
            <div className="form-group">
              <label>Motivo</label>
              <input placeholder="Ingrese el motivo" value={form.motivo} onChange={e => setForm({ ...form, motivo: e.target.value })} />
            </div>
            <div className="form-actions">
              <button type="submit" className="btn btn-primary">Registrar Multa</button>
            </div>
          </form>
        </div>
      </div>
      <div className="card">
        <div className="card-header"><h3>Lista de Multas</h3></div>
        <div className="card-body">
          <table className="data-table">
            <thead><tr><th>Lector</th><th>Monto</th><th>Motivo</th><th>Pagada</th><th>Acciones</th></tr></thead>
            <tbody>
              {items.map(item => (
                <tr key={item.id}>
                  <td>{item.lector ? `${item.lector.nombres} ${item.lector.apellidos}` : '-'}</td>
                  <td>S/ {item.monto}</td>
                  <td>{item.motivo}</td>
                  <td>{item.pagada ? 'Sí' : 'No'}</td>
                  <td>
                    {!item.pagada && <button className="btn-icon edit" onClick={() => handlePagar(item.id)}>$</button>}
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

export default Multas
