import React from 'react'
import { 
  FiHome, FiBook, FiUsers, FiFilter, FiUser, 
  FiCalendar, FiCheckCircle, FiAlertCircle, 
  FiShield, FiBarChart2, FiActivity, FiMessageSquare 
} from 'react-icons/fi'

function Sidebar({ activeModule, setActiveModule }) {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: FiHome },
    { id: 'libros', label: 'Libros', icon: FiBook },
    { id: 'autores', label: 'Autores', icon: FiUsers },
    { id: 'categorias', label: 'Categorías', icon: FiFilter },
    { id: 'lectores', label: 'Lectores', icon: FiUser },
    { id: 'prestamos', label: 'Préstamos', icon: FiCalendar },
    { id: 'devoluciones', label: 'Devoluciones', icon: FiCheckCircle },
    { id: 'multas', label: 'Multas', icon: FiAlertCircle },
    { id: 'usuarios', label: 'Usuarios del Sistema', icon: FiShield },
    { id: 'reportes', label: 'Reportes', icon: FiBarChart2 },
    { id: 'auditoria', label: 'Auditoría', icon: FiActivity },
    { id: 'disparador', label: 'Disparador', icon: FiMessageSquare },
  ]

  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-icon">
          <FiBook size={28} />
        </div>
        <div>
          <h2>BIBLIOUNI</h2>
          <span>Sistema de Biblioteca Universitaria</span>
        </div>
      </div>
      <nav className="nav-menu">
        {menuItems.map(item => (
          <button
            key={item.id}
            className={`nav-item ${activeModule === item.id ? 'active' : ''}`}
            onClick={() => setActiveModule(item.id)}
          >
            <item.icon className="nav-icon" size={18} />
            <span className="nav-label">{item.label}</span>
          </button>
        ))}
      </nav>
    </aside>
  )
}

export default Sidebar
