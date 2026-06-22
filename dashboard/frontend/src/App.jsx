import React, { useState } from 'react'
import Sidebar from './components/Sidebar'
import Disparador from './components/Disparador'
import Banco from './components/Banco'

function App() {
  const [activeModule, setActiveModule] = useState('disparador')

  return (
    <div className="app">
      <Sidebar activeModule={activeModule} setActiveModule={setActiveModule} />
      <main className="main-content">
        <header className="top-bar">
          <div className="breadcrumb">
            <span className="panel-title">Panel administrativo</span>
            <h1>{activeModule === 'disparador' ? 'Disparador / WhatsApp' : 'Banco'}</h1>
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
              <div className="avatar">TJ</div>
              <span>Admin</span>
            </div>
          </div>
        </header>

        <div className="content-area">
          {activeModule === 'disparador' && <Disparador />}
          {activeModule === 'banco' && <Banco />}
        </div>
      </main>
    </div>
  )
}

export default App
