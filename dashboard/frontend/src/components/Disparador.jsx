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

  // ===================== ESTADOS FACTOR DE LLENADO =====================
  const [fillFactor, setFillFactor] = useState(80);
  const [fillFactorLoading, setFillFactorLoading] = useState(false);
  const [fillFactorResult, setFillFactorResult] = useState(null);
  const [fillFactorError, setFillFactorError] = useState("");

  // ===================== CARGA INICIAL =====================
  useEffect(() => {
    fetchStatus(true);
    fetchBackupStatus(true);
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

  // ===================== FILL FACTOR - HANDLER =====================
  const handleFillFactor = async () => {
    setFillFactorError("");
    setFillFactorResult(null);

    const val = parseInt(fillFactor, 10);
    if (isNaN(val) || val < 1 || val > 100) {
      setFillFactorError("El factor de llenado debe ser un número entre 1 y 100.");
      return;
    }

    setFillFactorLoading(true);
    try {
      const res = await axios.get(`/api/fill-factor/test?fill_factor=${val}`);
      setFillFactorResult(res.data);
    } catch (e) {
      const errorMsg = e.response?.data?.message || e.message;
      setFillFactorError("Error al ejecutar: " + errorMsg);
    }
    setFillFactorLoading(false);
  };

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

      {/* ========== FACTOR DE LLENADO ========== */}
      <div className="card">
        <div className="card-header">
          <h2>Factor de Llenado de Índices</h2>
          <div className="status-badge inactive">Manual</div>
        </div>
        <div className="card-body">
          <p className="description">
            Reconstruye todos los índices de <strong>Bibliouni</strong> con el
            factor de llenado (fill factor) especificado. También puede ejecutarse
            enviando el comando por WhatsApp al número configurado en el Disparador
            de Backup.
          </p>

          <div className="info-grid">
            <div className="info-item">
              <label>Factor de llenado (%):</label>
              <input
                type="number"
                className={`phone-input ${fillFactorError ? "error" : ""}`}
                value={fillFactor}
                onChange={(e) => {
                  setFillFactor(e.target.value);
                  setFillFactorError("");
                  setFillFactorResult(null);
                }}
                min="1"
                max="100"
                placeholder="80"
                disabled={fillFactorLoading}
              />
              <span className="input-hint">Número entre 1 y 100 (recomendado: 80)</span>
            </div>
          </div>

          {fillFactorError && (
            <div className="error-message">
              <strong>Error:</strong> {fillFactorError}
            </div>
          )}

          {fillFactorResult && (
            <div
              className="last-message"
              style={{
                borderLeft: `3px solid ${
                  fillFactorResult.success ? "#22c55e" : "#ef4444"
                }`,
                background: fillFactorResult.success
                  ? "rgba(34,197,94,0.07)"
                  : "rgba(239,68,68,0.07)",
              }}
            >
              <label>
                {fillFactorResult.success
                  ? "✅ Rebuild completado"
                  : "❌ Error en rebuild"}
              </label>
              <p>{fillFactorResult.result?.mensaje || "Operación finalizada."}</p>
              {fillFactorResult.result?.tablas_procesadas !== undefined && (
                <p>
                  Tablas procesadas:{" "}
                  <strong>{fillFactorResult.result.tablas_procesadas}</strong>
                </p>
              )}
              {fillFactorResult.result?.tablas_con_error?.length > 0 && (
                <p style={{ color: "#f59e0b" }}>
                  ⚠️ Tablas con error:{" "}
                  {fillFactorResult.result.tablas_con_error
                    .map((e) => e.tabla)
                    .join(", ")}
                </p>
              )}
            </div>
          )}

          <div className="action-area">
            <button
              className="btn btn-primary"
              onClick={handleFillFactor}
              disabled={fillFactorLoading}
            >
              {fillFactorLoading
                ? "Ejecutando rebuild..."
                : `Ejecutar con Fill Factor ${fillFactor}%`}
            </button>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>¿Qué es el Factor de Llenado?</h3>
        </div>
        <div className="card-body">
          <p className="description">
            El <strong>factor de llenado</strong> define qué porcentaje de cada
            página de índice se llena con datos al reconstruir. Dejar espacio
            libre reduce los <em>page splits</em> y mejora el rendimiento en
            tablas con muchas escrituras.
          </p>
          <ul className="feature-list">
            <li>
              <strong>100%</strong> — Para tablas de solo lectura (máximo
              rendimiento de lectura)
            </li>
            <li>
              <strong>80-90%</strong> — Recomendado para tablas con operaciones
              mixtas (lectura + escritura)
            </li>
            <li>
              <strong>60-70%</strong> — Para tablas con muchas inserciones
              aleatorias
            </li>
          </ul>
          <p className="description" style={{ marginTop: "10px" }}>
            También puede ejecutarse enviando por WhatsApp:
            <br />
            <code
              style={{
                background: "rgba(255,255,255,0.08)",
                padding: "4px 10px",
                borderRadius: "6px",
                fontFamily: "monospace",
                fontSize: "0.95em",
              }}
            >
              FACTOR LLENADO 80
            </code>
          </p>
        </div>
      </div>
    </div>
  );
}

export default Disparador;
