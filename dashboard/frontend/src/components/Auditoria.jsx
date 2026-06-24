import React, { useEffect, useState } from 'react'
import axios from 'axios'

function Auditoria() {
  const [registros, setRegistros] = useState([])
  const [filtros, setFiltros] = useState({ modulo: '', usuario: '' })

  const fetchAuditoria = () => {
    const params = {}
    if (filtros.modulo) params.modulo = filtros.modulo
    if (filtros.usuario) params.usuario = filtros.usuario
    axios.get('/api/auditoria', { params })
      .then(res => setRegistros(res.data))
      .catch(err => console.error(err))
  }

  useEffect(() => {
    fetchAuditoria()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <div className="auditoria-container">
      <div className="card">
        <div className="card-header">
          <h3>Historial de Auditoría</h3>
          <div className="filters">
            <input placeholder="Módulo" value={filtros.modulo} onChange={e => setFiltros({ ...filtros, modulo: e.target.value })} />
            <input placeholder="Usuario" value={filtros.usuario} onChange={e => setFiltros({ ...filtros, usuario: e.target.value })} />
            <button className="btn btn-primary" onClick={fetchAuditoria}>Filtrar</button>
          </div>
        </div>
        <div className="card-body">
          <table className="data-table">
            <thead>
              <tr><th>ID</th><th>Operación</th><th>Módulo</th><th>Descripción</th><th>Usuario</th><th>Resultado</th><th>Fecha</th></tr>
            </thead>
            <tbody>
              {registros.map(r => (
                <tr key={r.id}>
                  <td>{r.id}</td>
                  <td>{r.tipo_operacion}</td>
                  <td>{r.modulo}</td>
                  <td>{r.descripcion}</td>
                  <td>{r.usuario}</td>
                  <td>{r.resultado}</td>
                  <td>{r.fecha_hora}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default Auditoria
