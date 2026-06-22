import React from 'react'

function Sidebar({ activeModule, setActiveModule }) {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'productos', label: 'Productos' },
    { id: 'documentos', label: 'Documentos' },
    { id: 'disparador', label: 'Disparador' },
    { id: 'reportes', label: 'Reportes' },
    { id: 'mantenimiento', label: 'Mantenimiento' },
    { id: 'configuracion', label: 'Configuracion' },
  ]

  return (
    <aside className="sidebar">
      <div className="brand">
        <h2>TENEBROSA</h2>
        <span>Tenebrosa System</span>
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
