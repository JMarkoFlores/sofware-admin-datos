import React, { useEffect, useState } from 'react'
import axios from 'axios'

function Reportes() {
  const [data, setData] = useState({})

  useEffect(() => {
    Promise.all([
      axios.get('/api/reportes/prestamos-activos'),
      axios.get('/api/reportes/multas-pendientes'),
      axios.get('/api/reportes/libros-mas-prestados'),
      axios.get('/api/reportes/lectores-con-multas'),
    ]).then(([prestamos, multas, libros, lectores]) => {
      setData({
        prestamos: prestamos.data,
        multas: multas.data,
        libros: libros.data,
        lectores: lectores.data,
      })
    }).catch(err => console.error(err))
  }, [])

  return (
    <div className="reportes-container">
      <div className="card">
        <div className="card-header"><h3>Préstamos Activos</h3></div>
        <div className="card-body">
          <p>Total: <strong>{data.prestamos?.total_prestamos_activos ?? '-'}</strong></p>
        </div>
      </div>
      <div className="card">
        <div className="card-header"><h3>Multas Pendientes</h3></div>
        <div className="card-body">
          <p>Total: <strong>{data.multas?.total_multas_pendientes ?? '-'}</strong></p>
          <p>Monto total: S/ <strong>{data.multas?.monto_total ?? '-'}</strong></p>
        </div>
      </div>
      <div className="card">
        <div className="card-header"><h3>Libros Más Prestados</h3></div>
        <div className="card-body">
          <table className="data-table">
            <thead><tr><th>Libro</th><th>Préstamos</th></tr></thead>
            <tbody>
              {data.libros?.map((l, i) => (
                <tr key={i}><td>{l.titulo}</td><td>{l.total}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      <div className="card">
        <div className="card-header"><h3>Lectores con Multas</h3></div>
        <div className="card-body">
          <table className="data-table">
            <thead><tr><th>Lector</th><th>Multas</th></tr></thead>
            <tbody>
              {data.lectores?.map((l, i) => (
                <tr key={i}><td>{l.lector}</td><td>{l.multas}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default Reportes
