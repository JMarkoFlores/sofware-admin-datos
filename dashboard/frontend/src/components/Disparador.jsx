import React, { useState, useEffect, useRef } from "react";
import axios from "axios";

function Disparador() {
  // ===================== ESTADOS DISPARADOR MENSAJE =====================
  const [isRunning, setIsRunning] = useState(false);
  const [status, setStatus] = useState({});
  const [loading, setLoading] = useState(false);
  const [phoneNumber, setPhoneNumber] = useState("51900685850");
  const [error, setError] = useState("");
  const [isEditing, setIsEditing] = useState(false);
  const inputRef = useRef(null);

  // ===================== ESTADOS DISPARADOR BACKUP =====================
  const [backupRunning, setBackupRunning] = useState(false);
  const [backupStatus, setBackupStatus] = useState({});
  const [backupLoading, setBackupLoading] = useState(false);
  const [backupPhone, setBackupPhone] = useState("51900685850");
  const [backupError, setBackupError] = useState("");
  const [isEditingBackup, setIsEditingBackup] = useState(false);
  const backupInputRef = useRef(null);

  // ===================== ESTADOS REPORTES AUTOMÁTICOS =====================
  const [reportsRunning, setReportsRunning] = useState(false);
  const [reportsStatus, setReportsStatus] = useState({});
  const [reportsLoading, setReportsLoading] = useState(false);
  const [reportsPhone, setReportsPhone] = useState("51900685850");
  const [reportsError, setReportsError] = useState("");
  const [isEditingReports, setIsEditingReports] = useState(false);
  const reportsInputRef = useRef(null);

  // Configuración de horarios y habilitación
  const [dailyEnabled, setDailyEnabled] = useState(true);
  const [dailyHour, setDailyHour] = useState(8);
  const [dailyMinute, setDailyMinute] = useState(0);
  const [weeklyEnabled, setWeeklyEnabled] = useState(true);
  const [weeklyDay, setWeeklyDay] = useState("MON");
  const [weeklyHour, setWeeklyHour] = useState(9);
  const [weeklyMinute, setWeeklyMinute] = useState(0);
  const [monthlyEnabled, setMonthlyEnabled] = useState(true);
  const [monthlyDay, setMonthlyDay] = useState(1);
  const [monthlyHour, setMonthlyHour] = useState(10);
  const [monthlyMinute, setMonthlyMinute] = useState(0);

  const handleToggleReport = async (type, enabled) => {
    try {
      const res = await axios.post('/api/reports/toggle', { type, enabled });
      if (res.data.success) {
        if (type === 'daily') setDailyEnabled(enabled);
        if (type === 'weekly') setWeeklyEnabled(enabled);
        if (type === 'monthly') setMonthlyEnabled(enabled);
        fetchReportsStatus(false);
      }
    } catch (e) {
      console.error('Error toggling report:', e);
    }
  };

  // ===================== CARGA INICIAL =====================
  useEffect(() => {
    fetchStatus(true);
    fetchBackupStatus(true);
    fetchReportsStatus(true);
  }, []);

  // ===================== POLLING MENSAJE =====================
  useEffect(() => {
    if (!isRunning) return;
    const interval = setInterval(() => fetchStatus(false), 5000);
    return () => clearInterval(interval);
  }, [isRunning]);

  // ===================== POLLING BACKUP =====================
  useEffect(() => {
    if (!backupRunning) return;
    const interval = setInterval(() => fetchBackupStatus(false), 5000);
    return () => clearInterval(interval);
  }, [backupRunning]);

  // ===================== POLLING REPORTES =====================
  useEffect(() => {
    if (!reportsRunning) return;
    const interval = setInterval(() => fetchReportsStatus(false), 5000);
    return () => clearInterval(interval);
  }, [reportsRunning]);

  // ===================== HELPERS =====================
  const validateInput = (number) => {
    const cleaned = number.replace(/\s/g, "").replace(/\+/g, "");
    if (!cleaned) return "Ingresa un número de teléfono";
    if (!/^\d+$/.test(cleaned)) return "Solo se permiten números";
    if (cleaned.length < 10)
      return `Número muy corto (${cleaned.length} dígitos). Mínimo 10.`;
    if (cleaned.length > 13)
      return `Número muy largo (${cleaned.length} dígitos). Máximo 13.`;
    return "";
  };

  // ===================== MENSAJE - FETCH =====================
  const fetchStatus = async (updatePhone = false) => {
    try {
      const res = await axios.get("/api/status");
      setStatus(res.data);
      setIsRunning(res.data.is_running);
      if (updatePhone && !isEditing && res.data.destination) {
        setPhoneNumber(res.data.destination);
      }
    } catch (e) {
      console.log("Error fetching status:", e);
    }
  };

  // ===================== MENSAJE - START / STOP =====================
  const handleStart = async () => {
    setError("");
    const validationError = validateInput(phoneNumber);
    if (validationError) {
      setError(validationError);
      return;
    }
    setLoading(true);
    try {
      const res = await axios.post("/api/start", {
        number: phoneNumber.trim(),
      });
      if (res.data.success) {
        setIsRunning(true);
        setStatus((prev) => ({ ...prev, destination: phoneNumber.trim() }));
      } else {
        setError(res.data.message);
      }
    } catch (e) {
      const errorMsg = e.response?.data?.message || e.message;
      setError("Error al iniciar: " + errorMsg);
    }
    setLoading(false);
  };

  const handleStop = async () => {
    setLoading(true);
    try {
      const res = await axios.get("/api/stop");
      if (res.data.success) {
        setIsRunning(false);
        fetchStatus(true);
      }
    } catch (e) {
      setError("Error al detener: " + e.message);
    }
    setLoading(false);
  };

  // ===================== MENSAJE - INPUT HANDLERS =====================
  const handleInputChange = (e) => {
    setIsEditing(true);
    setPhoneNumber(e.target.value);
    setError("");
    clearTimeout(window.editTimeout);
    window.editTimeout = setTimeout(() => {
      setIsEditing(false);
    }, 2000);
  };

  const handleInputBlur = () => setIsEditing(false);
  const handleInputFocus = () => setIsEditing(true);

  // ===================== BACKUP - FETCH =====================
  const fetchBackupStatus = async (updatePhone = false) => {
    try {
      const res = await axios.get("/api/backup/status");
      setBackupStatus(res.data);
      setBackupRunning(res.data.is_running);
      if (updatePhone && !isEditingBackup && res.data.destination) {
        setBackupPhone(res.data.destination);
      }
    } catch (e) {
      console.log("Error fetching backup status:", e);
    }
  };

  // ===================== BACKUP - START / STOP =====================
  const handleBackupStart = async () => {
    setBackupError("");
    const validationError = validateInput(backupPhone);
    if (validationError) {
      setBackupError(validationError);
      return;
    }
    setBackupLoading(true);
    try {
      const res = await axios.post("/api/backup/start", {
        number: backupPhone.trim(),
      });
      if (res.data.success) {
        setBackupRunning(true);
        setBackupStatus((prev) => ({
          ...prev,
          destination: backupPhone.trim(),
        }));
      } else {
        setBackupError(res.data.message);
      }
    } catch (e) {
      const errorMsg = e.response?.data?.message || e.message;
      setBackupError("Error al iniciar: " + errorMsg);
    }
    setBackupLoading(false);
  };

  const handleBackupStop = async () => {
    setBackupLoading(true);
    try {
      const res = await axios.get("/api/backup/stop");
      if (res.data.success) {
        setBackupRunning(false);
        fetchBackupStatus(true);
      }
    } catch (e) {
      setBackupError("Error al detener: " + e.message);
    }
    setBackupLoading(false);
  };

  // ===================== BACKUP - INPUT HANDLERS =====================
  const handleBackupInputChange = (e) => {
    setIsEditingBackup(true);
    setBackupPhone(e.target.value);
    setBackupError("");
    clearTimeout(window.backupEditTimeout);
    window.backupEditTimeout = setTimeout(() => {
      setIsEditingBackup(false);
    }, 2000);
  };

  const handleBackupInputBlur = () => setIsEditingBackup(false);
  const handleBackupInputFocus = () => setIsEditingBackup(true);

  // ===================== REPORTES - FETCH =====================
  const fetchReportsStatus = async (updatePhone = false) => {
    try {
      const res = await axios.get("/api/reports/status");
      setReportsStatus(res.data);
      setReportsRunning(res.data.is_running);
      if (updatePhone && !isEditingReports && res.data.destination) {
        setReportsPhone(res.data.destination);
      }
      // Actualizar flags de habilitación desde el backend
      if (res.data.daily_enabled !== undefined) setDailyEnabled(res.data.daily_enabled);
      if (res.data.weekly_enabled !== undefined) setWeeklyEnabled(res.data.weekly_enabled);
      if (res.data.monthly_enabled !== undefined) setMonthlyEnabled(res.data.monthly_enabled);
    } catch (e) {
      console.log("Error fetching reports status:", e);
    }
  };

  // ===================== REPORTES - START / STOP =====================
  const handleReportsStart = async () => {
    setReportsError("");
    const validationError = validateInput(reportsPhone);
    if (validationError) {
      setReportsError(validationError);
      return;
    }
    setReportsLoading(true);
    try {
      const res = await axios.post("/api/reports/start", {
        number: reportsPhone.trim(),
        daily_enabled: dailyEnabled,
        weekly_enabled: weeklyEnabled,
        monthly_enabled: monthlyEnabled,
        daily_hour: dailyHour,
        daily_minute: dailyMinute,
        weekly_day: weeklyDay,
        weekly_hour: weeklyHour,
        weekly_minute: weeklyMinute,
        monthly_day: monthlyDay,
        monthly_hour: monthlyHour,
        monthly_minute: monthlyMinute,
      });
      if (res.data.success) {
        setReportsRunning(true);
        setReportsStatus(res.data);
      } else {
        setReportsError(res.data.message);
      }
    } catch (e) {
      const errorMsg = e.response?.data?.message || e.message;
      setReportsError("Error al iniciar: " + errorMsg);
    }
    setReportsLoading(false);
  };

  const handleReportsStop = async () => {
    setReportsLoading(true);
    try {
      const res = await axios.get("/api/reports/stop");
      if (res.data.success) {
        setReportsRunning(false);
        fetchReportsStatus(true);
      }
    } catch (e) {
      setReportsError("Error al detener: " + e.message);
    }
    setReportsLoading(false);
  };

  // ===================== REPORTES - INPUT HANDLERS =====================
  const handleReportsInputChange = (e) => {
    setIsEditingReports(true);
    setReportsPhone(e.target.value);
    setReportsError("");
    clearTimeout(window.reportsEditTimeout);
    window.reportsEditTimeout = setTimeout(() => {
      setIsEditingReports(false);
    }, 2000);
  };

  const handleReportsInputBlur = () => setIsEditingReports(false);
  const handleReportsInputFocus = () => setIsEditingReports(true);

  // ===================== RENDER =====================
  return (
    <div className="disparador-container">
      {/* ========== DISPARADOR DE MENSAJE ========== */}
      <div className="card">
        <div className="card-header">
          <h2>Disparador de Mensaje</h2>
          <div className={`status-badge ${isRunning ? "active" : "inactive"}`}>
            {isRunning ? "En ejecucion" : "Detenido"}
          </div>
        </div>

        <div className="card-body">
          <div className="info-grid">
            <div className="info-item">
              <label>Destino:</label>
              {isRunning ? (
                <span className="value">{phoneNumber}</span>
              ) : (
                <>
                  <input
                    ref={inputRef}
                    type="text"
                    className={`phone-input ${error ? "error" : ""}`}
                    value={phoneNumber}
                    onChange={handleInputChange}
                    onBlur={handleInputBlur}
                    onFocus={handleInputFocus}
                    placeholder="519XXXXXXXX"
                    disabled={isRunning}
                    autoComplete="off"
                  />
                  <span className="input-hint">
                    Ej: 51952310138 (11 dígitos)
                  </span>
                </>
              )}
            </div>
            <div className="info-item">
              <label>Intervalo:</label>
              <span className="value">Cada 1 minuto</span>
            </div>
            <div className="info-item">
              <label>Ultimo envio:</label>
              <span className="value">{status.last_sent || "Nunca"}</span>
            </div>
          </div>

          {error && (
            <div className="error-message">
              <strong>Error:</strong> {error}
            </div>
          )}

          <div className="action-area">
            {isRunning ? (
              <button
                className="btn btn-danger"
                onClick={handleStop}
                disabled={loading}
              >
                {loading ? "Deteniendo..." : "Detener"}
              </button>
            ) : (
              <button
                className="btn btn-primary"
                onClick={handleStart}
                disabled={loading}
              >
                {loading ? "Iniciando..." : "Iniciar"}
              </button>
            )}
          </div>

          {status.last_message && (
            <div className="last-message">
              <label>Ultimo mensaje:</label>
              <p>{status.last_message}</p>
            </div>
          )}
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>Informacion del envio</h3>
        </div>
        <div className="card-body">
          <p className="description">
            Al iniciar, se enviara un mensaje de WhatsApp inmediatamente y luego
            cada 1 minuto con la cantidad de tablas y sus nombres de la base de
            datos <strong>Bibliouni</strong>.
          </p>
          <ul className="feature-list">
            <li>Numero de destino editable</li>
            <li>Consulta automatica de tablas</li>
            <li>Envio via Evolution API</li>
            <li>Intervalo de 1 minuto</li>
          </ul>
        </div>
      </div>

      {/* ========== DISPARADOR DE BACKUP ========== */}
      <div className="card">
        <div className="card-header">
          <h2>Disparador de Backup</h2>
          <div
            className={`status-badge ${
              backupRunning ? "active" : "inactive"
            }`}
          >
            {backupRunning ? "En ejecucion" : "Detenido"}
          </div>
        </div>

        <div className="card-body">
          <div className="info-grid">
            <div className="info-item">
              <label>Destino:</label>
              {backupRunning ? (
                <span className="value">{backupPhone}</span>
              ) : (
                <>
                  <input
                    ref={backupInputRef}
                    type="text"
                    className={`phone-input ${backupError ? "error" : ""}`}
                    value={backupPhone}
                    onChange={handleBackupInputChange}
                    onBlur={handleBackupInputBlur}
                    onFocus={handleBackupInputFocus}
                    placeholder="519XXXXXXXX"
                    disabled={backupRunning}
                    autoComplete="off"
                  />
                  <span className="input-hint">
                    Ej: 51952310138 (11 dígitos)
                  </span>
                </>
              )}
            </div>
            <div className="info-item">
              <label>Proxima verif.:</label>
              <span className="value">
                {backupRunning
                  ? backupStatus.next_run
                    ? `${backupStatus.check_time} (${backupStatus.timezone})`
                    : "Calculando..."
                  : "--"}
              </span>
            </div>
            <div className="info-item">
              <label>Ultima verif.:</label>
              <span className="value">
                {backupStatus.last_check
                  ? `${backupStatus.last_check} — ${
                      backupStatus.last_result === "exito"
                        ? "Éxito"
                        : backupStatus.last_result === "alerta"
                        ? "Alerta enviada"
                        : "Nunca"
                    }`
                  : "Nunca"}
              </span>
            </div>
          </div>

          {backupError && (
            <div className="error-message">
              <strong>Error:</strong> {backupError}
            </div>
          )}

          <div className="action-area">
            {backupRunning ? (
              <button
                className="btn btn-danger"
                onClick={handleBackupStop}
                disabled={backupLoading}
              >
                {backupLoading ? "Deteniendo..." : "Detener Monitoreo"}
              </button>
            ) : (
              <button
                className="btn btn-primary"
                onClick={handleBackupStart}
                disabled={backupLoading}
              >
                {backupLoading ? "Iniciando..." : "Iniciar Monitoreo"}
              </button>
            )}
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>Informacion del monitoreo</h3>
        </div>
        <div className="card-body">
          <p className="description">
            El sistema verifica automáticamente a las{" "}
            <strong>7:00 AM (America/Lima)</strong> si existe un backup de la
            base de datos <strong>Bibliouni</strong> realizado durante el día.
          </p>
          <ul className="feature-list">
            <li>Verificación diaria a las 7:00 AM</li>
            <li>Alerta por WhatsApp si falta backup</li>
            <li>Responda "RESUELVE BACKUP" para ejecutar</li>
            <li>Webhook configurado automaticamente</li>
          </ul>
        </div>
      </div>

      {/* ========== REPORTES AUTOMÁTICOS ========== */}
      <div className="card">
        <div className="card-header">
          <h2>📊 Reportes Automáticos</h2>
          <div
            className={`status-badge ${
              reportsRunning ? "active" : "inactive"
            }`}
          >
            {reportsRunning ? "En ejecucion" : "Detenido"}
          </div>
        </div>

        <div className="card-body">
          <div className="info-grid">
            <div className="info-item">
              <label>Destino:</label>
              {reportsRunning ? (
                <span className="value">{reportsPhone}</span>
              ) : (
                <>
                  <input
                    ref={reportsInputRef}
                    type="text"
                    className={`phone-input ${reportsError ? "error" : ""}`}
                    value={reportsPhone}
                    onChange={handleReportsInputChange}
                    onBlur={handleReportsInputBlur}
                    onFocus={handleReportsInputFocus}
                    placeholder="519XXXXXXXX"
                    disabled={reportsRunning}
                    autoComplete="off"
                  />
                  <span className="input-hint">
                    Ej: 51952310138 (11 dígitos)
                  </span>
                </>
              )}
            </div>
            <div className="info-item">
              <label>Proximo diario:</label>
              <span className="value">
                {reportsStatus.daily?.next_run
                  ? new Date(reportsStatus.daily.next_run).toLocaleString()
                  : "--"}
              </span>
            </div>
            <div className="info-item">
              <label>Proximo semanal:</label>
              <span className="value">
                {reportsStatus.weekly?.next_run
                  ? new Date(reportsStatus.weekly.next_run).toLocaleString()
                  : "--"}
              </span>
            </div>
            <div className="info-item">
              <label>Proximo mensual:</label>
              <span className="value">
                {reportsStatus.monthly?.next_run
                  ? new Date(reportsStatus.monthly.next_run).toLocaleString()
                  : "--"}
              </span>
            </div>
          </div>

          {/* CONFIGURACIÓN DE HORARIOS */}
          <div className="schedules-config">
              <h4>⚙️ Configuración de Horarios</h4>
              
              {/* DIARIO */}
              <div className="schedule-config-item">
                <div style={{display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px'}}>
                  <label className="toggle-switch">
                    <input 
                      type="checkbox" 
                      id="daily-enabled" 
                      checked={dailyEnabled} 
                      onChange={(e) => {
                        if (reportsRunning) {
                          handleToggleReport('daily', e.target.checked);
                        } else {
                          setDailyEnabled(e.target.checked);
                        }
                      }}
                    />
                    <span className="slider"></span>
                  </label>
                  <label htmlFor="daily-enabled" style={{fontWeight: 'bold', margin: 0, cursor: 'pointer'}}>📅 Reporte Diario</label>
                </div>
                <div className="time-inputs" style={{opacity: dailyEnabled ? 1 : 0.5}}>
                  <div className="time-input-group">
                    <label>Hora:</label>
                    <input
                      type="number"
                      min="0"
                      max="23"
                      value={dailyHour}
                      onChange={(e) => setDailyHour(parseInt(e.target.value) || 0)}
                      disabled={reportsRunning || !dailyEnabled}
                    />
                  </div>
                  <div className="time-input-group">
                    <label>Minuto:</label>
                    <input
                      type="number"
                      min="0"
                      max="59"
                      value={dailyMinute}
                      onChange={(e) => setDailyMinute(parseInt(e.target.value) || 0)}
                      disabled={reportsRunning || !dailyEnabled}
                    />
                  </div>
                  <div className="time-preview">
                    {String(dailyHour).padStart(2, "0")}:{String(dailyMinute).padStart(2, "0")}
                  </div>
                </div>
              </div>

              {/* SEMANAL */}
              <div className="schedule-config-item">
                <div style={{display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px'}}>
                  <label className="toggle-switch">
                    <input 
                      type="checkbox" 
                      id="weekly-enabled" 
                      checked={weeklyEnabled} 
                      onChange={(e) => {
                        if (reportsRunning) {
                          handleToggleReport('weekly', e.target.checked);
                        } else {
                          setWeeklyEnabled(e.target.checked);
                        }
                      }}
                    />
                    <span className="slider"></span>
                  </label>
                  <label htmlFor="weekly-enabled" style={{fontWeight: 'bold', margin: 0, cursor: 'pointer'}}>📆 Reporte Semanal</label>
                </div>
                <div className="time-inputs" style={{opacity: weeklyEnabled ? 1 : 0.5}}>
                  <div className="time-input-group">
                    <label>Día:</label>
                    <select value={weeklyDay} onChange={(e) => setWeeklyDay(e.target.value)} disabled={reportsRunning || !weeklyEnabled}>
                      <option value="MON">Lunes</option>
                      <option value="TUE">Martes</option>
                      <option value="WED">Miércoles</option>
                      <option value="THU">Jueves</option>
                      <option value="FRI">Viernes</option>
                      <option value="SAT">Sábado</option>
                      <option value="SUN">Domingo</option>
                    </select>
                  </div>
                  <div className="time-input-group">
                    <label>Hora:</label>
                    <input
                      type="number"
                      min="0"
                      max="23"
                      value={weeklyHour}
                      onChange={(e) => setWeeklyHour(parseInt(e.target.value) || 0)}
                      disabled={reportsRunning || !weeklyEnabled}
                    />
                  </div>
                  <div className="time-input-group">
                    <label>Minuto:</label>
                    <input
                      type="number"
                      min="0"
                      max="59"
                      value={weeklyMinute}
                      onChange={(e) => setWeeklyMinute(parseInt(e.target.value) || 0)}
                      disabled={reportsRunning || !weeklyEnabled}
                    />
                  </div>
                  <div className="time-preview">
                    {weeklyDay} {String(weeklyHour).padStart(2, "0")}:{String(weeklyMinute).padStart(2, "0")}
                  </div>
                </div>
              </div>

              {/* MENSUAL */}
              <div className="schedule-config-item">
                <div style={{display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px'}}>
                  <label className="toggle-switch">
                    <input 
                      type="checkbox" 
                      id="monthly-enabled" 
                      checked={monthlyEnabled} 
                      onChange={(e) => {
                        if (reportsRunning) {
                          handleToggleReport('monthly', e.target.checked);
                        } else {
                          setMonthlyEnabled(e.target.checked);
                        }
                      }}
                    />
                    <span className="slider"></span>
                  </label>
                  <label htmlFor="monthly-enabled" style={{fontWeight: 'bold', margin: 0, cursor: 'pointer'}}>🗓️ Reporte Mensual</label>
                </div>
                <div className="time-inputs" style={{opacity: monthlyEnabled ? 1 : 0.5}}>
                  <div className="time-input-group">
                    <label>Día del mes:</label>
                    <input
                      type="number"
                      min="1"
                      max="31"
                      value={monthlyDay}
                      onChange={(e) => setMonthlyDay(parseInt(e.target.value) || 1)}
                      disabled={reportsRunning || !monthlyEnabled}
                    />
                  </div>
                  <div className="time-input-group">
                    <label>Hora:</label>
                    <input
                      type="number"
                      min="0"
                      max="23"
                      value={monthlyHour}
                      onChange={(e) => setMonthlyHour(parseInt(e.target.value) || 0)}
                      disabled={reportsRunning || !monthlyEnabled}
                    />
                  </div>
                  <div className="time-input-group">
                    <label>Minuto:</label>
                    <input
                      type="number"
                      min="0"
                      max="59"
                      value={monthlyMinute}
                      onChange={(e) => setMonthlyMinute(parseInt(e.target.value) || 0)}
                      disabled={reportsRunning || !monthlyEnabled}
                    />
                  </div>
                  <div className="time-preview">
                    Día {monthlyDay} {String(monthlyHour).padStart(2, "0")}:{String(monthlyMinute).padStart(2, "0")}
                  </div>
                </div>
              </div>
            </div>

          <div className="schedule-info">
            <div className="schedule-box">
              <strong>
                📅 Reportes Diarios{" "}
                <span style={{fontSize: '0.8em', color: reportsStatus.daily_enabled ? 'green' : 'red'}}>
                  [{reportsStatus.daily_enabled ? "HABILITADO" : "DESHABILITADO"}]
                </span>
              </strong>
              <p>
                Hora: {reportsStatus.daily?.time || "--"} ({reportsStatus.timezone})
              </p>
              <p>
                Tipos:{" "}
                {Array.isArray(reportsStatus.daily?.types)
                  ? reportsStatus.daily.types.join(", ")
                  : "--"}
              </p>
            </div>
            <div className="schedule-box">
              <strong>
                📆 Reportes Semanales{" "}
                <span style={{fontSize: '0.8em', color: reportsStatus.weekly_enabled ? 'green' : 'red'}}>
                  [{reportsStatus.weekly_enabled ? "HABILITADO" : "DESHABILITADO"}]
                </span>
              </strong>
              <p>
                Día: {reportsStatus.weekly?.day || "--"} a las{" "}
                {reportsStatus.weekly?.time || "--"}
              </p>
              <p>
                Tipos:{" "}
                {Array.isArray(reportsStatus.weekly?.types)
                  ? reportsStatus.weekly.types.join(", ")
                  : "--"}
              </p>
            </div>
            <div className="schedule-box">
              <strong>
                🗓️ Reportes Mensuales{" "}
                <span style={{fontSize: '0.8em', color: reportsStatus.monthly_enabled ? 'green' : 'red'}}>
                  [{reportsStatus.monthly_enabled ? "HABILITADO" : "DESHABILITADO"}]
                </span>
              </strong>
              <p>
                Día: {reportsStatus.monthly?.day || "--"} a las{" "}
                {reportsStatus.monthly?.time || "--"}
              </p>
              <p>
                Tipos:{" "}
                {Array.isArray(reportsStatus.monthly?.types)
                  ? reportsStatus.monthly.types.join(", ")
                  : "--"}
              </p>
            </div>
          </div>

          {reportsError && (
            <div className="error-message">
              <strong>Error:</strong> {reportsError}
            </div>
          )}

          <div className="action-area">
            {reportsRunning ? (
              <button
                className="btn btn-danger"
                onClick={handleReportsStop}
                disabled={reportsLoading}
              >
                {reportsLoading ? "Deteniendo..." : "Detener"}
              </button>
            ) : (
              <button
                className="btn btn-primary"
                onClick={handleReportsStart}
                disabled={reportsLoading}
              >
                {reportsLoading ? "Iniciando..." : "Iniciar Reportes"}
              </button>
            )}
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>Reportes Interactivos</h3>
        </div>
        <div className="card-body">
          <p className="description">
            Después de activar los reportes, los usuarios pueden enviar mensajes por
            WhatsApp para solicitar reportes bajo demanda de forma interactiva.
          </p>
          <div className="interactive-info">
            <strong>🎯 Flujo interactivo:</strong>
            <ol>
              <li>Usuario envía cualquier mensaje a la conversación</li>
              <li>Sistema muestra menú de tipos de reportes disponibles</li>
              <li>Usuario selecciona (1-5) el reporte que desea</li>
              <li>Sistema genera y envía el reporte en tiempo real</li>
              <li>Se ofrece opción de generar otro reporte o cancelar</li>
            </ol>
          </div>
          <ul className="feature-list">
            <li>✅ Estadísticas Generales</li>
            <li>✅ Libros Más Prestados</li>
            <li>✅ Multas Pendientes</li>
            <li>✅ Préstamos Vencidos</li>
            <li>✅ Libros Dañados (últimos 30 días)</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default Disparador;
