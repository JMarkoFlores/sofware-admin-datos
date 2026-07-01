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

  // ===================== ESTADOS MONITOREO FRAGMENTACIÓN =====================
  const [fragRunning, setFragRunning] = useState(false);
  const [fragStatus, setFragStatus] = useState({});
  const [fragLoading, setFragLoading] = useState(false);
  const [fragUmbral, setFragUmbral] = useState(30);
  const [fragError, setFragError] = useState("");
  const [fragTestResult, setFragTestResult] = useState(null);
  const [fragTestLoading, setFragTestLoading] = useState(false);

  // ===================== CARGA INICIAL =====================
  useEffect(() => {
    fetchStatus(true);
    fetchBackupStatus(true);
    fetchFragStatus(true);
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

  // ===================== POLLING FRAGMENTACIÓN =====================
  useEffect(() => {
    if (!fragRunning) return;
    const interval = setInterval(() => fetchFragStatus(false), 10000);
    return () => clearInterval(interval);
  }, [fragRunning]);

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

  // ===================== FRAGMENTACIÓN - FETCH =====================
  const fetchFragStatus = async (initial = false) => {
    try {
      const res = await axios.get("/api/fragmentacion/status");
      setFragStatus(res.data);
      setFragRunning(res.data.is_running);
      if (initial && res.data.umbral) {
        setFragUmbral(res.data.umbral);
      }
    } catch (e) {
      console.log("Error fetching frag status:", e);
    }
  };

  // ===================== FRAGMENTACIÓN - START / STOP =====================
  const handleFragStart = async () => {
    setFragError("");
    const val = parseInt(fragUmbral, 10);
    if (isNaN(val) || val < 1 || val > 100) {
      setFragError("El umbral debe ser un número entre 1 y 100.");
      return;
    }
    setFragLoading(true);
    try {
      const res = await axios.post("/api/fragmentacion/start", { umbral: val });
      if (res.data.success) {
        setFragRunning(true);
        fetchFragStatus(false);
      } else {
        setFragError(res.data.message);
      }
    } catch (e) {
      setFragError("Error al iniciar: " + (e.response?.data?.message || e.message));
    }
    setFragLoading(false);
  };

  const handleFragStop = async () => {
    setFragLoading(true);
    try {
      const res = await axios.get("/api/fragmentacion/stop");
      if (res.data.success) {
        setFragRunning(false);
        fetchFragStatus(true);
      }
    } catch (e) {
      setFragError("Error al detener: " + e.message);
    }
    setFragLoading(false);
  };

  // ===================== FRAGMENTACIÓN - TEST MANUAL =====================
  const handleFragTest = async () => {
    setFragError("");
    setFragTestResult(null);
    const val = parseInt(fragUmbral, 10);
    if (isNaN(val) || val < 1 || val > 100) {
      setFragError("El umbral debe ser un número entre 1 y 100.");
      return;
    }
    setFragTestLoading(true);
    try {
      const res = await axios.get(`/api/fragmentacion/test?umbral=${val}`);
      setFragTestResult(res.data.result);
    } catch (e) {
      setFragError("Error al verificar: " + (e.response?.data?.message || e.message));
    }
    setFragTestLoading(false);
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

      {/* ========== MONITOREO DE FRAGMENTACIÓN ========== */}
      <div className="card">
        <div className="card-header">
          <h2>Monitoreo de Fragmentación</h2>
          <div className={`status-badge ${fragRunning ? "active" : "inactive"}`}>
            {fragRunning ? "En ejecución" : "Detenido"}
          </div>
        </div>
        <div className="card-body">
          <p className="description">
            Verifica diariamente el nivel de fragmentación de los índices de{" "}
            <strong>Bibliouni</strong>. Si algún índice supera el umbral
            configurado, envía una alerta por WhatsApp para que decidas si
            ejecutar el factor de llenado.
          </p>

          <div className="info-grid">
            <div className="info-item">
              <label>Umbral de alerta (%):</label>
              {fragRunning ? (
                <span className="value">{fragUmbral}%</span>
              ) : (
                <>
                  <input
                    type="number"
                    className={`phone-input ${fragError ? "error" : ""}`}
                    value={fragUmbral}
                    onChange={(e) => {
                      setFragUmbral(e.target.value);
                      setFragError("");
                    }}
                    min="1"
                    max="100"
                    placeholder="30"
                    disabled={fragRunning}
                  />
                  <span className="input-hint">
                    Si un índice supera este %, se envía alerta (recomendado: 30)
                  </span>
                </>
              )}
            </div>
            <div className="info-item">
              <label>Próxima verif.:</label>
              <span className="value">
                {fragRunning
                  ? `Cada ${fragStatus.interval_minutes || 60} min`
                  : "--"}
              </span>
            </div>
            <div className="info-item">
              <label>Última verif.:</label>
              <span className="value">
                {fragStatus.last_check
                  ? `${fragStatus.last_check} — ${
                      fragStatus.last_result?.hay_alerta
                        ? `⚠️ ${fragStatus.last_result.tablas_fragmentadas?.length || 0} índices fragmentados`
                        : "✅ Todo OK"
                    }`
                  : "Nunca"}
              </span>
            </div>
          </div>

          {fragError && (
            <div className="error-message">
              <strong>Error:</strong> {fragError}
            </div>
          )}

          <div className="action-area" style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
            {fragRunning ? (
              <button
                className="btn btn-danger"
                onClick={handleFragStop}
                disabled={fragLoading}
              >
                {fragLoading ? "Deteniendo..." : "Detener Monitoreo"}
              </button>
            ) : (
              <button
                className="btn btn-primary"
                onClick={handleFragStart}
                disabled={fragLoading}
              >
                {fragLoading ? "Iniciando..." : "Iniciar Monitoreo"}
              </button>
            )}
            <button
              className="btn btn-primary"
              onClick={handleFragTest}
              disabled={fragTestLoading}
              style={{ background: "rgba(255,255,255,0.08)", border: "1px solid rgba(255,255,255,0.15)" }}
            >
              {fragTestLoading ? "Verificando..." : "Verificar Ahora"}
            </button>
          </div>

          {fragTestResult && (
            <div
              className="last-message"
              style={{
                marginTop: "15px",
                borderLeft: `3px solid ${
                  fragTestResult.hay_alerta ? "#f59e0b" : "#22c55e"
                }`,
                background: fragTestResult.hay_alerta
                  ? "rgba(245,158,11,0.07)"
                  : "rgba(34,197,94,0.07)",
              }}
            >
              <label>
                {fragTestResult.hay_alerta
                  ? `⚠️ ${fragTestResult.tablas_fragmentadas.length} índices superan el ${fragTestResult.umbral}%`
                  : `✅ Todos los índices por debajo del ${fragTestResult.umbral}%`}
              </label>
              <p>{fragTestResult.mensaje}</p>
              {fragTestResult.tablas_fragmentadas?.length > 0 && (
                <div style={{ marginTop: "8px" }}>
                  <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.9em" }}>
                    <thead>
                      <tr style={{ borderBottom: "1px solid rgba(255,255,255,0.1)" }}>
                        <th style={{ textAlign: "left", padding: "6px 8px" }}>Tabla</th>
                        <th style={{ textAlign: "left", padding: "6px 8px" }}>Índice</th>
                        <th style={{ textAlign: "right", padding: "6px 8px" }}>Fragmentación</th>
                        <th style={{ textAlign: "right", padding: "6px 8px" }}>Páginas</th>
                      </tr>
                    </thead>
                    <tbody>
                      {fragTestResult.tablas_fragmentadas.map((item, idx) => (
                        <tr key={idx} style={{ borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
                          <td style={{ padding: "5px 8px" }}>{item.tabla}</td>
                          <td style={{ padding: "5px 8px" }}>{item.indice}</td>
                          <td style={{ padding: "5px 8px", textAlign: "right", color: item.fragmentacion >= 50 ? "#ef4444" : "#f59e0b" }}>
                            {item.fragmentacion.toFixed(1)}%
                          </td>
                          <td style={{ padding: "5px 8px", textAlign: "right" }}>{item.paginas}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>¿Cómo funciona el monitoreo?</h3>
        </div>
        <div className="card-body">
          <p className="description">
            El sistema verifica cada <strong>1 hora</strong> el
            nivel de fragmentación de los índices en <strong>Bibliouni</strong>.
            Si algún índice supera el umbral configurado, envía una alerta por
            WhatsApp con el detalle y el comando sugerido.
          </p>
          <ul className="feature-list">
            <li>Verificación automática cada 1 hora</li>
            <li>Alerta por WhatsApp si hay fragmentación alta</li>
            <li>Muestra qué tablas e índices están afectados</li>
            <li>Responda "FACTOR LLENADO 80" para optimizar</li>
            <li>Botón "Verificar Ahora" para comprobar al instante</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default Disparador;
