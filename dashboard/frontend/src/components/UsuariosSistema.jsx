import React, { useEffect, useState } from 'react'
import axios from 'axios'
import {
  FiUsers, FiPlus, FiX, FiEdit2, FiTrash2, FiSearch,
  FiShield, FiUser, FiEye, FiEyeOff, FiCheck, FiAlertTriangle,
  FiLock, FiToggleLeft, FiToggleRight
} from 'react-icons/fi'

function UsuariosSistema() {
  const [items, setItems] = useState([])
  const [form, setForm] = useState({ username: '', password: '', nombre_completo: '', rol: 'bibliotecario', activo: true })
  const [editing, setEditing] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [showPass, setShowPass] = useState(false)
  const [search, setSearch] = useState('')
  const [filterRol, setFilterRol] = useState('all')
  const [loading, setLoading] = useState(true)
  const [confirmDelete, setConfirmDelete] = useState(null)
  const [saved, setSaved] = useState(false)

  const fetchItems = () => {
    setLoading(true)
    axios.get('/api/usuarios').then(res => { setItems(res.data); setLoading(false) })
  }

  useEffect(() => { fetchItems() }, [])

  const handleSubmit = (e) => {
    e.preventDefault()
    const payload = { ...form }
    if (!payload.password) delete payload.password
    const req = editing
      ? axios.put(`/api/usuarios/${editing}`, payload)
      : axios.post('/api/usuarios', payload)
    req.then(() => {
      fetchItems()
      setForm({ username: '', password: '', nombre_completo: '', rol: 'bibliotecario', activo: true })
      setEditing(null)
      setShowForm(false)
      setSaved(true)
      setTimeout(() => setSaved(false), 2500)
    })
  }

  const handleEdit = (item) => {
    setEditing(item.id)
    setForm({ username: item.username, password: '', nombre_completo: item.nombre_completo || '', rol: item.rol, activo: item.activo })
    setShowForm(true)
    setShowPass(false)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleCancel = () => {
    setEditing(null)
    setShowForm(false)
    setForm({ username: '', password: '', nombre_completo: '', rol: 'bibliotecario', activo: true })
  }

  const handleDelete = (id) => {
    axios.delete(`/api/usuarios/${id}`).then(() => { fetchItems(); setConfirmDelete(null) })
  }

  const filtered = items.filter(item => {
    const matchSearch = item.username?.toLowerCase().includes(search.toLowerCase())
      || item.nombre_completo?.toLowerCase().includes(search.toLowerCase())
    const matchRol = filterRol === 'all' ? true : item.rol === filterRol
    return matchSearch && matchRol
  })

  const admins = items.filter(i => i.rol === 'admin').length
  const biblio = items.filter(i => i.rol === 'bibliotecario').length
  const activos = items.filter(i => i.activo).length

  return (
    <div className="m-page">

      {/* ── Header ── */}
      <div className="m-header">
        <div className="m-header-left">
          <div className="m-header-icon usuarios-icon">
            <FiUsers size={22} />
          </div>
          <div>
            <h1 className="m-title">Usuarios del Sistema</h1>
            <p className="m-subtitle">Administración de accesos y roles</p>
          </div>
        </div>
        <div className="m-header-right">
          {saved && <span className="m-saved-badge"><FiCheck size={14} /> Guardado</span>}
          <button className="m-btn-primary" onClick={() => { setShowForm(v => !v); setEditing(null) }}>
            {showForm && !editing ? <><FiX size={16} /> Cerrar</> : <><FiPlus size={16} /> Nuevo Usuario</>}
          </button>
        </div>
      </div>

      {/* ── KPI Cards ── */}
      <div className="m-kpi-grid">
        <div className="m-kpi-card kpi-indigo">
          <div className="m-kpi-icon"><FiUsers size={20} /></div>
          <div>
            <div className="m-kpi-value">{items.length}</div>
            <div className="m-kpi-label">Total Usuarios</div>
          </div>
        </div>
        <div className="m-kpi-card kpi-red">
          <div className="m-kpi-icon"><FiShield size={20} /></div>
          <div>
            <div className="m-kpi-value">{admins}</div>
            <div className="m-kpi-label">Administradores</div>
          </div>
        </div>
        <div className="m-kpi-card kpi-blue">
          <div className="m-kpi-icon"><FiUser size={20} /></div>
          <div>
            <div className="m-kpi-value">{biblio}</div>
            <div className="m-kpi-label">Bibliotecarios</div>
          </div>
        </div>
        <div className="m-kpi-card kpi-green">
          <div className="m-kpi-icon"><FiCheck size={20} /></div>
          <div>
            <div className="m-kpi-value">{activos}</div>
            <div className="m-kpi-label">Activos</div>
          </div>
        </div>
      </div>

      {/* ── Form Panel ── */}
      {showForm && (
        <div className="m-form-panel">
          <div className="m-form-panel-header">
            <h3>{editing ? <><FiEdit2 size={16} /> Editar Usuario</> : <><FiPlus size={16} /> Nuevo Usuario</>}</h3>
            {editing && <span className="m-editing-badge">Editando: @{form.username}</span>}
          </div>
          <form onSubmit={handleSubmit} className="m-form-grid">
            <div className="m-form-group">
              <label><FiUser size={13} /> Username</label>
              <input placeholder="Ej: jmarko" value={form.username}
                onChange={e => setForm({ ...form, username: e.target.value })} required />
            </div>
            <div className="m-form-group">
              <label><FiLock size={13} /> {editing ? 'Nueva contraseña (opcional)' : 'Contraseña'}</label>
              <div className="m-pass-wrap">
                <input type={showPass ? 'text' : 'password'}
                  placeholder={editing ? 'Dejar vacío para no cambiar' : 'Contraseña segura'}
                  value={form.password}
                  onChange={e => setForm({ ...form, password: e.target.value })}
                  required={!editing} />
                <button type="button" className="m-pass-toggle" onClick={() => setShowPass(v => !v)}>
                  {showPass ? <FiEyeOff size={15} /> : <FiEye size={15} />}
                </button>
              </div>
            </div>
            <div className="m-form-group">
              <label><FiUser size={13} /> Nombre completo</label>
              <input placeholder="Ej: Jean Marco Flores" value={form.nombre_completo}
                onChange={e => setForm({ ...form, nombre_completo: e.target.value })} />
            </div>
            <div className="m-form-group">
              <label><FiShield size={13} /> Rol</label>
              <div className="m-rol-selector">
                {[['admin', 'Administrador', 'kpi-red'], ['bibliotecario', 'Bibliotecario', 'kpi-blue']].map(([val, label, cls]) => (
                  <button key={val} type="button"
                    className={`m-rol-btn ${form.rol === val ? 'active ' + cls : ''}`}
                    onClick={() => setForm({ ...form, rol: val })}>
                    {val === 'admin' ? <FiShield size={14} /> : <FiUser size={14} />}
                    {label}
                  </button>
                ))}
              </div>
            </div>
            <div className="m-form-group m-toggle-group">
              <label>Estado</label>
              <button type="button" className={`m-toggle ${form.activo ? 'on' : 'off'}`}
                onClick={() => setForm({ ...form, activo: !form.activo })}>
                {form.activo ? <FiToggleRight size={24} /> : <FiToggleLeft size={24} />}
                <span>{form.activo ? 'Activo' : 'Inactivo'}</span>
              </button>
            </div>
            <div className="m-form-actions">
              <button type="submit" className="m-btn-primary">
                {editing ? 'Actualizar Usuario' : 'Crear Usuario'}
              </button>
              <button type="button" className="m-btn-ghost" onClick={handleCancel}>Cancelar</button>
            </div>
          </form>
        </div>
      )}

      {/* ── Filters ── */}
      <div className="m-toolbar">
        <div className="m-search">
          <FiSearch size={15} className="m-search-icon" />
          <input placeholder="Buscar por usuario o nombre..." value={search}
            onChange={e => setSearch(e.target.value)} />
        </div>
        <div className="m-filter-tabs">
          {[['all', 'Todos'], ['admin', 'Admins'], ['bibliotecario', 'Bibliotecarios']].map(([val, label]) => (
            <button key={val} className={`m-filter-tab ${filterRol === val ? 'active' : ''}`}
              onClick={() => setFilterRol(val)}>{label}</button>
          ))}
        </div>
        <span className="m-count">{filtered.length} usuario{filtered.length !== 1 ? 's' : ''}</span>
      </div>

      {/* ── Table ── */}
      <div className="m-table-card">
        {loading ? (
          <div className="m-loading"><div className="m-spinner" /><span>Cargando usuarios...</span></div>
        ) : filtered.length === 0 ? (
          <div className="m-empty">
            <FiUsers size={40} />
            <h3>No hay usuarios</h3>
            <p>No se encontraron registros</p>
          </div>
        ) : (
          <table className="m-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Usuario</th>
                <th>Nombre Completo</th>
                <th>Rol</th>
                <th>Estado</th>
                <th>Último Acceso</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(item => (
                <tr key={item.id} className={!item.activo ? 'row-inactive' : ''}>
                  <td className="m-id">#{item.id}</td>
                  <td>
                    <div className="m-user-cell">
                      <div className={`m-avatar ${item.rol === 'admin' ? 'av-admin' : 'av-biblio'}`}>
                        {item.username ? item.username[0].toUpperCase() : '?'}
                      </div>
                      <div>
                        <div className="m-username">@{item.username}</div>
                      </div>
                    </div>
                  </td>
                  <td>{item.nombre_completo || <span className="m-null">Sin nombre</span>}</td>
                  <td>
                    {item.rol === 'admin'
                      ? <span className="m-badge m-badge-admin"><FiShield size={11} /> Admin</span>
                      : <span className="m-badge m-badge-biblio"><FiUser size={11} /> Bibliotecario</span>}
                  </td>
                  <td>
                    {item.activo
                      ? <span className="m-badge m-badge-paid"><FiCheck size={11} /> Activo</span>
                      : <span className="m-badge m-badge-inactive"><FiX size={11} /> Inactivo</span>}
                  </td>
                  <td className="m-date">
                    {item.ultimo_acceso ? new Date(item.ultimo_acceso).toLocaleString('es-PE') : <span className="m-null">Nunca</span>}
                  </td>
                  <td>
                    <div className="m-actions">
                      <button className="m-action-btn edit" title="Editar" onClick={() => handleEdit(item)}>
                        <FiEdit2 size={15} />
                      </button>
                      <button className="m-action-btn del" title="Eliminar" onClick={() => setConfirmDelete(item)}>
                        <FiTrash2 size={15} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* ── Confirm Delete Modal ── */}
      {confirmDelete && (
        <div className="m-modal-overlay" onClick={() => setConfirmDelete(null)}>
          <div className="m-modal" onClick={e => e.stopPropagation()}>
            <div className="m-modal-icon del"><FiAlertTriangle size={28} /></div>
            <h3>Eliminar usuario</h3>
            <p>¿Eliminar el usuario <strong>@{confirmDelete.username}</strong>? Esta acción es permanente.</p>
            <div className="m-modal-actions">
              <button className="m-btn-danger" onClick={() => handleDelete(confirmDelete.id)}>Sí, eliminar</button>
              <button className="m-btn-ghost" onClick={() => setConfirmDelete(null)}>Cancelar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default UsuariosSistema
