import React, { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import { FiMessageSquare, FiDatabase, FiPlay, FiSquare, FiRefreshCw, FiClock, FiCheckCircle, FiAlertCircle, FiPhone } from 'react-icons/fi'

function Disparador() {
  const [isRunning, setIsRunning] = useState(false)
  const [status, setStatus] = useState({})
  const [loading, setLoading] = useState(false)
  const [phoneNumber, setPhoneNumber] = useState('')
  const [error, setError] = useState('')
  const [isEditing, setIsEditing] = useState(false)
  const inputRef = useRef(null)

  const [backupRunning, setBackupRunning] = useState(false)
  const [backupStatus, setBackupStatus] = useState({})
  const [backupLoading, setBackupLoading] = useState(false)
  const [backupPhone, setBackupPhone] = useState('')
  const [backupError, setBackupError] = useState('')
  const [isEditingBackup, setIsEditingBackup] = useState(false)
  const backupInputRef = useRef(null)

  const fetchStatus = async (updatePhone = false) => {
    try {
      const res = await axios.get('/api/status')
      setStatus(res.data)
      setIsRunning(res.data.is_running)
      if (updatePhone && !isEditing && res.data.destination) setPhoneNumber(res.data.destination)
    } catch (e) { console.log('Error fetching status:', e) }
  }

  const fetchBackupStatus = async (updatePhone = false) => {
    try {
      const res = await axios.get('/api/backup/status')
      setBackupStatus(res.data)
      setBackupRunning(res.data.is_running)
      if (updatePhone && !isEditingBackup && res.data.destination) setBackupPhone(res.data.destination)
    } catch (e) { console.log('Error fetching backup status:', e) }
  }

  useEffect(() => { fetchStatus(true); fetchBackupStatus(true) }, [])

  useEffect(() => {
    let interval
    if (isRunning) interval = setInterval(() => fetchStatus(false), 5000)
    return () => clearInterval(interval)
  }, [isRunning])

  useEffect(() => {
    let interval
    if (backupRunning) interval = setInterval(() => fetchBackupStatus(false), 5000)
    return () => clearInterval(interval)
  }, [backupRunning])

  const validateInput = (number) => {
    const cleaned = number.replace(/\s/g, '').replace(/\+/g, '')
    if (!cleaned) return 'Ingresa un número de teléfono'
    if (!/^\d+$/.test(cleaned)) return 'Solo se permiten números'
    if (cleaned.length < 10) return `Número muy corto (${cleaned.length} dígitos). Mínimo 10.`
    if (cleaned.length > 13) return `Número muy largo (${cleaned.length} dígitos). Máximo 13.`
    return ''
  }

  const handleStart = async () => {
    setError('')
    const validationError = validateInput(phoneNumber)
    if (validationError) { setError(validationError); return }
    setLoading(true)
    try {
      const res = await axios.post('/api/start', { number: phoneNumber.trim() })
      if (res.data.success) setIsRunning(true)
      else setError(res.data.message)
    } catch (e) {
      setError('Error al iniciar: ' + (e.response?.data?.message || e.message))
    }
    setLoading(false)
  }

  const handleStop = async () => {
    setLoading(true)
    try {
      const res = await axios.get('/api/stop')
      if (res.data.success) { setIsRunning(false); fetchStatus(true) }
    } catch (e) { setError('Error al detener: ' + e.message) }
    setLoading(false)
  }

  const handleInputChange = (e) => { setIsEditing(true); setPhoneNumber(e.target.value); setError(''); clearTimeout(window.editTimeout); window.editTimeout = setTimeout(() => setIsEditing(false), 2000) }
  const handleInputBlur = () => setIsEditing(false)
  const handleInputFocus = () => setIsEditing(true)

  const handleBackupStart = async () => {
    setBackupError('')
    const validationError = validateInput(backupPhone)
    if (validationError) { setBackupError(validationError); return }
    setBackupLoading(true)
    try {
      const res = await axios.post('/api/backup/start', { number: backupPhone.trim() })
      if (res.data.success) setBackupRunning(true)
      else setBackupError(res.data.message)
    } catch (e) {
      setBackupError('Error al iniciar: ' + (e.response?.data?.message || e.message))
    }
    setBackupLoading(false)
  }

  const handleBackupStop = async () => {
    setBackupLoading(true)
    try {
      const res = await axios.get('/api/backup/stop')
      if (res.data.success) { setBackupRunning(false); fetchBackupStatus(true) }
    } catch (e) { setBackupError('Error al detener: ' + e.message) }
    setBackupLoading(false)
  }

  const handleBackupInputChange = (e) => { setIsEditingBackup(true); setBackupPhone(e.target.value); setBackupError(''); clearTimeout(window.backupEditTimeout); window.backupEditTimeout = setTimeout(() => setIsEditingBackup(false), 2000) }
  const handleBackupInputBlur = () => setIsEditingBackup(false)
  const handleBackupInputFocus = () => setIsEditingBackup(true)

  return (
    <div className="m-page">
      <div className="m-header">
        <div className="m-header-left">
          <div className="m-header-icon" style={{ background: 'linear-gradient(135deg, #ef4444, #f87171)' }}>
            <FiMessageSquare size={22} />
          </div>
          <div>
            <h1 className="m-title">Disparador de Notificaciones</h1>
            <p className="m-subtitle">Monitoreo y alertas de WhatsApp</p>
          </div>
        </div>
      </div>

      <div className="m-kpi-grid">
        <div className="m-kpi-card kpi-red">
          <div className="m-kpi-icon"><FiMessageSquare size={20} /></div>
          <div>
            <div className="m-kpi-value">{isRunning ? 'Activo' : 'Detenido'}</div>
            <div className="m-kpi-label">Estado Mensajes</div>
          </div>
        </div>
        <div className="m-kpi-card kpi-blue">
          <div className="m-kpi-icon"><FiDatabase size={20} /></div>
          <div>
            <div className="m-kpi-value">{backupRunning ? 'Activo' : 'Detenido'}</div>
            <div className="m-kpi-label">Estado Backup</div>
          </div>
        </div>
      </div>

      <div className="m-table-card">
        <div style={{ padding: '16px 20px', borderBottom: '1px solid #e2e8f0', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <FiMessageSquare size={18} style={{ color: '#ef4444' }} />
          <h3 style={{ margin: 0, fontSize: '16px', color: '#1e293b' }}>Disparador de Mensajes</h3>
          <span className={`m-badge ${isRunning ? 'm-badge-paid' : 'm-badge-pending'}`} style={{ marginLeft: 'auto' }}>
            {isRunning ? <FiCheckCircle size={11} /> : <FiAlertCircle size={11} />}
            {isRunning ? ' En ejecución' : ' Detenido'}
          </span>
        </div>

        <div style={{ padding: '20px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px', marginBottom: '16px' }}>
            <div className="m-form-group" style={{ margin: 0 }}>
              <label><FiPhone size={13} /> Número de Destino</label>
              {isRunning ? (
                <span style={{ display: 'block', padding: '10px 14px', background: '#f1f5f9', borderRadius: '8px', color: '#475569', fontWeight: '500' }}>{phoneNumber}</span>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  <input
                    ref={inputRef}
                    type="text"
                    value={phoneNumber}
                    onChange={handleInputChange}
                    onBlur={handleInputBlur}
                    onFocus={handleInputFocus}
                    placeholder="519XXXXXXXX"
                    style={{
                      padding: '10px 14px',
                      fontSize: '14px',
                      borderRadius: '8px',
                      border: error ? '1px solid #ef4444' : '1px solid #e2e8f0',
                      outline: 'none',
                      transition: 'border-color 0.2s'
                    }}
                  />
                  <span style={{ fontSize: '12px', color: '#94a3b8' }}>Ej: 51952310138 (11 dígitos)</span>
                </div>
              )}
            </div>

            <div className="m-form-group" style={{ margin: 0 }}>
              <label><FiClock size={13} /> Último Envío</label>
              <span style={{ display: 'block', padding: '10px 14px', background: '#f1f5f9', borderRadius: '8px', color: '#475569', fontWeight: '500' }}>{status.last_sent || 'Nunca'}</span>
            </div>
          </div>

          {error && (
            <div style={{ padding: '12px 16px', background: '#fef2f2', border: '1px solid #fee2e2', borderRadius: '8px', color: '#dc2626', marginBottom: '16px' }}>
              <strong>Error:</strong> {error}
            </div>
          )}

          <div className="m-form-actions" style={{ justifyContent: 'flex-start', marginBottom: '16px' }}>
            {isRunning ? (
              <button className="m-btn-danger" onClick={handleStop} disabled={loading}>
                {loading ? <FiRefreshCw size={14} style={{ animation: 'spin 1s linear infinite' }} /> : <FiSquare size={14} />}
                {loading ? ' Deteniendo...' : ' Detener'}
              </button>
            ) : (
              <button className="m-btn-primary" onClick={handleStart} disabled={loading}>
                {loading ? <FiRefreshCw size={14} style={{ animation: 'spin 1s linear infinite' }} /> : <FiPlay size={14} />}
                {loading ? ' Iniciando...' : ' Iniciar'}
              </button>
            )}
          </div>

          {status.last_message && (
            <div style={{ padding: '12px 16px', background: '#f1f5f9', borderRadius: '8px' }}>
              <label style={{ fontSize: '12px', fontWeight: '600', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px', display: 'block', marginBottom: '4px' }}><FiMessageSquare size={10} /> Último Mensaje</label>
              <p style={{ margin: 0, color: '#1e293b', fontSize: '14px' }}>{status.last_message}</p>
            </div>
          )}
        </div>
      </div>

      <div className="m-table-card" style={{ marginTop: '20px' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid #e2e8f0', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <FiDatabase size={18} style={{ color: '#3b82f6' }} />
          <h3 style={{ margin: 0, fontSize: '16px', color: '#1e293b' }}>Disparador de Backup</h3>
          <span className={`m-badge ${backupRunning ? 'm-badge-paid' : 'm-badge-pending'}`} style={{ marginLeft: 'auto' }}>
            {backupRunning ? <FiCheckCircle size={11} /> : <FiAlertCircle size={11} />}
            {backupRunning ? ' En ejecución' : ' Detenido'}
          </span>
        </div>

        <div style={{ padding: '20px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px', marginBottom: '16px' }}>
            <div className="m-form-group" style={{ margin: 0 }}>
              <label><FiPhone size={13} /> Número de Destino</label>
              {backupRunning ? (
                <span style={{ display: 'block', padding: '10px 14px', background: '#f1f5f9', borderRadius: '8px', color: '#475569', fontWeight: '500' }}>{backupPhone}</span>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  <input
                    ref={backupInputRef}
                    type="text"
                    value={backupPhone}
                    onChange={handleBackupInputChange}
                    onBlur={handleBackupInputBlur}
                    onFocus={handleBackupInputFocus}
                    placeholder="519XXXXXXXX"
                    style={{
                      padding: '10px 14px',
                      fontSize: '14px',
                      borderRadius: '8px',
                      border: backupError ? '1px solid #ef4444' : '1px solid #e2e8f0',
                      outline: 'none',
                      transition: 'border-color 0.2s'
                    }}
                  />
                  <span style={{ fontSize: '12px', color: '#94a3b8' }}>Ej: 51952310138 (11 dígitos)</span>
                </div>
              )}
            </div>

            <div className="m-form-group" style={{ margin: 0 }}>
              <label><FiClock size={13} /> Próxima Verificación</label>
              <span style={{ display: 'block', padding: '10px 14px', background: '#f1f5f9', borderRadius: '8px', color: '#475569', fontWeight: '500' }}>
                {backupRunning ? (backupStatus.check_time ? `${backupStatus.check_time} (${backupStatus.timezone})` : 'Calculando...') : '-'}
              </span>
            </div>

            <div className="m-form-group" style={{ margin: 0 }}>
              <label><FiCheckCircle size={13} /> Última Verificación</label>
              <span style={{ display: 'block', padding: '10px 14px', background: '#f1f5f9', borderRadius: '8px', color: '#475569', fontWeight: '500' }}>
                {backupStatus.last_check ? `${backupStatus.last_check} — ${backupStatus.last_result === 'Éxito' ? 'Éxito' : backupStatus.last_result === 'alerta' ? 'Alerta enviada' : 'Nunca'}` : 'Nunca'}
              </span>
            </div>
          </div>

          {backupError && (
            <div style={{ padding: '12px 16px', background: '#fef2f2', border: '1px solid #fee2e2', borderRadius: '8px', color: '#dc2626', marginBottom: '16px' }}>
              <strong>Error:</strong> {backupError}
            </div>
          )}

          <div className="m-form-actions" style={{ justifyContent: 'flex-start', marginBottom: '16px' }}>
            {backupRunning ? (
              <button className="m-btn-danger" onClick={handleBackupStop} disabled={backupLoading}>
                {backupLoading ? <FiRefreshCw size={14} style={{ animation: 'spin 1s linear infinite' }} /> : <FiSquare size={14} />}
                {backupLoading ? ' Deteniendo...' : ' Detener Monitoreo'}
              </button>
            ) : (
              <button className="m-btn-primary" onClick={handleBackupStart} disabled={backupLoading}>
                {backupLoading ? <FiRefreshCw size={14} style={{ animation: 'spin 1s linear infinite' }} /> : <FiPlay size={14} />}
                {backupLoading ? ' Iniciando...' : ' Iniciar Monitoreo'}
              </button>
            )}
          </div>

          <div style={{ padding: '12px 16px', background: '#f8fafc', borderRadius: '8px' }}>
            <p style={{ margin: '0 0 8px 0', color: '#475569', fontSize: '14px' }}>El sistema verifica automáticamente a las <strong>7:00 AM (America/Lima)</strong> si existe un backup de la base de datos <strong>Bibliouni</strong> realizado durante el día.</p>
            <ul style={{ margin: 0, paddingLeft: '20px', color: '#64748b', fontSize: '13px' }}>
              <li style={{ marginBottom: '4px' }}>Verificación diaria a las 7:00 AM</li>
              <li style={{ marginBottom: '4px' }}>Alerta por WhatsApp si falta backup</li>
              <li style={{ marginBottom: '4px' }}>Responde "RESUELVE BACKUP" para ejecutar</li>
              <li>Webhook configurado automáticamente</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Disparador
