import React, { useState } from 'react'
import Sidebar from './components/Sidebar'
import Dashboard from './components/Dashboard'
import Libros from './components/Libros'
import Autores from './components/Autores'
import Categorias from './components/Categorias'
import Lectores from './components/Lectores'
import Prestamos from './components/Prestamos'
import Devoluciones from './components/Devoluciones'
import Multas from './components/Multas'
import UsuariosSistema from './components/UsuariosSistema'
import Reportes from './components/Reportes'
import Auditoria from './components/Auditoria'
import Disparador from './components/Disparador'

const moduleTitles = {
  dashboard: 'Dashboard',
  libros: 'Gestión de Libros',
  autores: 'Gestión de Autores',
  categorias: 'Gestión de Categorías',
  lectores: 'Gestión de Lectores',
  prestamos: 'Gestión de Préstamos',
  devoluciones: 'Gestión de Devoluciones',
  multas: 'Gestión de Multas',
  usuarios: 'Usuarios del Sistema',
  reportes: 'Reportes',
  auditoria: 'Auditoría',
  disparador: 'Disparador / WhatsApp',
}

function App() {
  const [activeModule, setActiveModule] = useState('dashboard')

  return (
    <div className="app">
      <Sidebar activeModule={activeModule} setActiveModule={setActiveModule} />
      <main className="main-content">
        <header className="top-bar">
          <div className="breadcrumb">
            <span className="panel-title">Panel administrativo</span>
            <h1>{moduleTitles[activeModule] || activeModule}</h1>
          </div>
          <div className="user-actions">
            <div className="search-box">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="11" cy="11" r="8"></circle>
                <path d="m21 21-4.35-4.35"></path>
              </svg>
              <input type="text" placeholder="Buscar" />
            </div>
            <button className="icon-btn">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"></path>
                <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"></path>
              </svg>
            </button>
            <div className="user-profile">
              <div className="avatar">AD</div>
              <span>Admin</span>
            </div>
          </div>
        </header>

        <div className="content-area">
          {activeModule === 'dashboard' && <Dashboard />}
          {activeModule === 'libros' && <Libros />}
          {activeModule === 'autores' && <Autores />}
          {activeModule === 'categorias' && <Categorias />}
          {activeModule === 'lectores' && <Lectores />}
          {activeModule === 'prestamos' && <Prestamos />}
          {activeModule === 'devoluciones' && <Devoluciones />}
          {activeModule === 'multas' && <Multas />}
          {activeModule === 'usuarios' && <UsuariosSistema />}
          {activeModule === 'reportes' && <Reportes />}
          {activeModule === 'auditoria' && <Auditoria />}
          {activeModule === 'disparador' && <Disparador />}
        </div>
      </main>
    </div>
  )
}

export default App
