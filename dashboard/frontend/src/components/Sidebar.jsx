import React from 'react'

function Sidebar({ activeModule, setActiveModule }) {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'libros', label: 'Libros' },
    { id: 'autores', label: 'Autores' },
    { id: 'categorias', label: 'Categorías' },
    { id: 'lectores', label: 'Lectores' },
    { id: 'prestamos', label: 'Préstamos' },
    { id: 'devoluciones', label: 'Devoluciones' },
    { id: 'multas', label: 'Multas' },
    { id: 'usuarios', label: 'Usuarios del Sistema' },
    { id: 'reportes', label: 'Reportes' },
    { id: 'auditoria', label: 'Auditoría' },
    { id: 'disparador', label: 'Disparador' },
  ]

  return (
    <aside className="sidebar">
      <div className="brand">
        <h2>BIBLIOUNI</h2>
        <span>Sistema de Biblioteca Universitaria</span>
      </div>
      <nav className="nav-menu">
        {menuItems.map(item => (
          <button
            key={item.id}
            className={`nav-item ${activeModule === item.id ? 'active' : ''}`}
            onClick={() => setActiveModule(item.id)}
          >
            <span className="nav-icon"></span>
            <span className="nav-label">{item.label}</span>
          </button>
        ))}
      </nav>
    </aside>
  )
}

export default Sidebar
