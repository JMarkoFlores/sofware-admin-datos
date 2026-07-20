import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import {
  FiMessageSquare,
  FiDatabase,
  FiPlay,
  FiSquare,
  FiRefreshCw,
  FiClock,
  FiCheckCircle,
  FiAlertCircle,
  FiPhone,
  FiSettings,
  FiActivity,
  FiCalendar,
  FiList,
} from "react-icons/fi";

function Disparador() {
  const [isRunning, setIsRunning] = useState(false);
  const [status, setStatus] = useState({});
  const [loading, setLoading] = useState(false);
  const [phoneNumber, setPhoneNumber] = useState("51900685850");
  const [error, setError] = useState("");
  const [isEditing, setIsEditing] = useState(false);
  const inputRef = useRef(null);

  const [backupRunning, setBackupRunning] = useState(false);
  const [backupStatus, setBackupStatus] = useState({});
  const [backupLoading, setBackupLoading] = useState(false);
  const [backupPhone, setBackupPhone] = useState("51900685850");
  const [backupError, setBackupError] = useState("");
  const [isEditingBackup, setIsEditingBackup] = useState(false);
  const [backupHour, setBackupHour] = useState(7);
  const [backupMinute, setBackupMinute] = useState(0);
  const backupInputRef = useRef(null);

  const [fillFactor, setFillFactor] = useState(80);
  const [fillFactorLoading, setFillFactorLoading] = useState(false);
  const [fillFactorResult, setFillFactorResult] = useState(null);
  const [fillFactorError, setFillFactorError] = useState("");
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
      const res = await axios.post("/api/reports/toggle", { type, enabled });
      if (res.data.success) {
        if (type === "daily") setDailyEnabled(enabled);
        if (type === "weekly") setWeeklyEnabled(enabled);
        if (type === "monthly") setMonthlyEnabled(enabled);
        fetchReportsStatus(false);
      }
    } catch (e) {
      console.error("Error toggling report:", e);
    }
  };

  // ===================== CARGA INICIAL =====================
  useEffect(() => {
    fetchStatus(true);
    fetchBackupStatus(true);
    fetchReportsStatus(true);
  }, []);

  const [fragRunning, setFragRunning] = useState(false);
  const [fragStatus, setFragStatus] = useState({});
  const [fragLoading, setFragLoading] = useState(false);
  const [fragUmbral, setFragUmbral] = useState(30);
  const [fragError, setFragError] = useState("");
  const [fragTestResult, setFragTestResult] = useState(null);
  const [fragTestLoading, setFragTestLoading] = useState(false);

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
  const [loginSecurityRunning, setLoginSecurityRunning] = useState(false);
  const [loginSecurityStatus, setLoginSecurityStatus] = useState({});
  const [loginSecurityLoading, setLoginSecurityLoading] = useState(false);
  const [loginSecurityPhone, setLoginSecurityPhone] = useState("51900685850");
  const [loginSecurityError, setLoginSecurityError] = useState("");
  const [isEditingLoginSecurity, setIsEditingLoginSecurity] = useState(false);
  const loginSecurityInputRef = useRef(null);

  const fetchStatus = async (updatePhone = false) => {
    try {
      const res = await axios.get("/api/status");
      setStatus(res.data);
      setIsRunning(res.data.is_running);
      if (updatePhone && !isEditing && res.data.destination)
        setPhoneNumber(res.data.destination);
    } catch (e) {
      console.log("Error fetching status:", e);
    }
  };

  const fetchBackupStatus = async (updatePhone = false) => {
    try {
      const res = await axios.get("/api/backup/status");
      setBackupStatus(res.data);
      setBackupRunning(res.data.is_running);
      if (updatePhone && !isEditingBackup && res.data.destination)
        setBackupPhone(res.data.destination);
      if (res.data.check_time) {
        const [h, m] = res.data.check_time.split(":").map(Number);
        if (!isNaN(h)) setBackupHour(h);
        if (!isNaN(m)) setBackupMinute(m);
      }
    } catch (e) {
      console.log("Error fetching backup status:", e);
    }
  };

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

  const fetchLoginSecurityStatus = async (updatePhone = false) => {
    try {
      const res = await axios.get("/api/login-security/status");
      setLoginSecurityStatus(res.data);
      setLoginSecurityRunning(res.data.is_running);
      if (updatePhone && !isEditingLoginSecurity && res.data.destination)
        setLoginSecurityPhone(res.data.destination);
    } catch (e) {
      console.log("Error fetching login security status:", e);
    }
  };

  useEffect(() => {
    fetchStatus(true);
    fetchBackupStatus(true);
    fetchFragStatus(true);
    fetchLoginSecurityStatus(true);
  }, []);

  useEffect(() => {
    fetchStatus(true);
    fetchBackupStatus(true);
    fetchFragStatus(true);
  }, []);

  useEffect(() => {
    let interval;
    if (isRunning) interval = setInterval(() => fetchStatus(false), 5000);
    return () => clearInterval(interval);
  }, [isRunning]);

  useEffect(() => {
    let interval;
    if (backupRunning)
      interval = setInterval(() => fetchBackupStatus(false), 5000);
    return () => clearInterval(interval);
  }, [backupRunning]);

  useEffect(() => {
    if (!fragRunning) return;
    const interval = setInterval(() => fetchFragStatus(false), 10000);
    return () => clearInterval(interval);
  }, [fragRunning]);

  useEffect(() => {
    if (!loginSecurityRunning) return;
    const interval = setInterval(() => fetchLoginSecurityStatus(false), 10000);
    return () => clearInterval(interval);
  }, [loginSecurityRunning]);

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
        setStatus((prev) => ({
          ...prev,
          destination: phoneNumber.trim(),
          last_sent: res.data.last_sent || prev.last_sent,
          last_message: res.data.last_message || prev.last_message,
        }));
      } else setError(res.data.message);
    } catch (e) {
      setError("Error al iniciar: " + (e.response?.data?.message || e.message));
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

  const handleInputChange = (e) => {
    setIsEditing(true);
    setPhoneNumber(e.target.value);
    setError("");
    clearTimeout(window.editTimeout);
    window.editTimeout = setTimeout(() => setIsEditing(false), 2000);
  };
  const handleInputBlur = () => setIsEditing(false);
  const handleInputFocus = () => setIsEditing(true);

  const handleBackupStart = async () => {
    setBackupError("");
    const validationError = validateInput(backupPhone);
    if (validationError) {
      setBackupError(validationError);
      return;
    }
    setBackupLoading(true);
    try {
      const hour = parseInt(backupHour, 10);
      const minute = parseInt(backupMinute, 10);
      const res = await axios.post("/api/backup/start", {
        number: backupPhone.trim(),
        hour: isNaN(hour) ? 7 : hour,
        minute: isNaN(minute) ? 0 : minute,
      });
      if (res.data.success) {
        setBackupRunning(true);
        setBackupStatus((prev) => ({
          ...prev,
          destination: backupPhone.trim(),
          check_time: res.data.check_time,
          timezone: res.data.timezone,
        }));
      } else setBackupError(res.data.message);
    } catch (e) {
      setBackupError(
        "Error al iniciar: " + (e.response?.data?.message || e.message),
      );
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

  const handleBackupInputChange = (e) => {
    setIsEditingBackup(true);
    setBackupPhone(e.target.value);
    setBackupError("");
    clearTimeout(window.backupEditTimeout);
    window.backupEditTimeout = setTimeout(
      () => setIsEditingBackup(false),
      2000,
    );
  };
  const handleBackupInputBlur = () => setIsEditingBackup(false);
  const handleBackupInputFocus = () => setIsEditingBackup(true);

  const handleBackupHourChange = (e) => {
    let val = parseInt(e.target.value, 10);
    if (isNaN(val)) val = "";
    if (val !== "" && val < 0) val = 0;
    if (val !== "" && val > 23) val = 23;
    setBackupHour(val);
    setBackupError("");
  };

  const handleBackupMinuteChange = (e) => {
    let val = parseInt(e.target.value, 10);
    if (isNaN(val)) val = "";
    if (val !== "" && val < 0) val = 0;
    if (val !== "" && val > 59) val = 59;
    setBackupMinute(val);
    setBackupError("");
  };

  const handleFillFactor = async () => {
    setFillFactorError("");
    setFillFactorResult(null);

    const val = parseInt(fillFactor, 10);
    if (isNaN(val) || val < 1 || val > 100) {
      setFillFactorError(
        "El factor de llenado debe ser un número entre 1 y 100.",
      );
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
      setFragError(
        "Error al iniciar: " + (e.response?.data?.message || e.message),
      );
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
      setFragError(
        "Error al verificar: " + (e.response?.data?.message || e.message),
      );
    }
    setFragTestLoading(false);
  };

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
      if (res.data.daily_enabled !== undefined)
        setDailyEnabled(res.data.daily_enabled);
      if (res.data.weekly_enabled !== undefined)
        setWeeklyEnabled(res.data.weekly_enabled);
      if (res.data.monthly_enabled !== undefined)
        setMonthlyEnabled(res.data.monthly_enabled);
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
  const handleLoginSecurityStart = async () => {
    setLoginSecurityError("");
    const validationError = validateInput(loginSecurityPhone);
    if (validationError) {
      setLoginSecurityError(validationError);
      return;
    }
    setLoginSecurityLoading(true);
    try {
      const res = await axios.post("/api/login-security/start", {
        number: loginSecurityPhone.trim(),
      });
      if (res.data.success) {
        setLoginSecurityRunning(true);
        setLoginSecurityStatus((prev) => ({
          ...prev,
          destination: loginSecurityPhone.trim(),
        }));
      } else setLoginSecurityError(res.data.message);
    } catch (e) {
      setLoginSecurityError(
        "Error al iniciar: " + (e.response?.data?.message || e.message),
      );
    }
    setLoginSecurityLoading(false);
  };

  const handleLoginSecurityStop = async () => {
    setLoginSecurityLoading(true);
    try {
      const res = await axios.get("/api/login-security/stop");
      if (res.data.success) {
        setLoginSecurityRunning(false);
        fetchLoginSecurityStatus(true);
      }
    } catch (e) {
      setLoginSecurityError("Error al detener: " + e.message);
    }
    setLoginSecurityLoading(false);
  };

  const handleLoginSecurityInputChange = (e) => {
    setIsEditingLoginSecurity(true);
    setLoginSecurityPhone(e.target.value);
    setLoginSecurityError("");
    clearTimeout(window.loginSecurityEditTimeout);
    window.loginSecurityEditTimeout = setTimeout(
      () => setIsEditingLoginSecurity(false),
      2000,
    );
  };
  const handleLoginSecurityInputBlur = () => setIsEditingLoginSecurity(false);
  const handleLoginSecurityInputFocus = () => setIsEditingLoginSecurity(true);

  return (
    <div className="m-page">
      <div className="m-header">
        <div className="m-header-left">
          <div
            className="m-header-icon"
            style={{ background: "linear-gradient(135deg, #ef4444, #f87171)" }}
          >
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
          <div className="m-kpi-icon">
            <FiMessageSquare size={20} />
          </div>
          <div>
            <div className="m-kpi-value">
              {isRunning ? "Activo" : "Detenido"}
            </div>
            <div className="m-kpi-label">Estado Mensajes</div>
          </div>
        </div>
        <div className="m-kpi-card kpi-blue">
          <div className="m-kpi-icon">
            <FiDatabase size={20} />
          </div>
          <div>
            <div className="m-kpi-value">
              {backupRunning ? "Activo" : "Detenido"}
            </div>
            <div className="m-kpi-label">Estado Backup</div>
          </div>
        </div>
        <div className="m-kpi-card kpi-green">
          <div className="m-kpi-icon">
            <FiActivity size={20} />
          </div>
          <div>
            <div className="m-kpi-value">
              {fragRunning ? "Activo" : "Detenido"}
            </div>
            <div className="m-kpi-label">Fragmentación</div>
          </div>
        </div>
        <div
          className="m-kpi-card"
          style={{ background: "linear-gradient(135deg, #f59e0b, #fbbf24)" }}
        >
          <div className="m-kpi-icon">
            <FiAlertCircle size={20} />
          </div>
          <div>
            <div className="m-kpi-value">
              {loginSecurityRunning ? "Activo" : "Detenido"}
            </div>
            <div className="m-kpi-label">Seguridad Login</div>
          </div>
        </div>
      </div>

      {/* Fila 1: Info Envío - Disparador Mensajes */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "20px",
          marginBottom: "20px",
        }}
      >
        <div className="m-table-card">
          <div
            style={{
              padding: "16px 20px",
              borderBottom: "1px solid #e2e8f0",
              display: "flex",
              alignItems: "center",
              gap: "10px",
            }}
          >
            <FiMessageSquare size={18} style={{ color: "#ef4444" }} />
            <h3 style={{ margin: 0, fontSize: "16px", color: "#1e293b" }}>
              Información del Envío
            </h3>
          </div>
          <div style={{ padding: "20px" }}>
            <p
              style={{
                margin: "0 0 8px 0",
                color: "#475569",
                fontSize: "14px",
              }}
            >
              Al iniciar, se enviará un mensaje de WhatsApp inmediatamente y
              luego cada 1 minuto con la cantidad de tablas y sus nombres de la
              base de datos <strong>Bibliouni</strong>.
            </p>
            <ul
              style={{
                margin: 0,
                paddingLeft: "20px",
                color: "#64748b",
                fontSize: "13px",
              }}
            >
              <li style={{ marginBottom: "4px" }}>
                Número de destino editable
              </li>
              <li style={{ marginBottom: "4px" }}>
                Consulta automática de tablas
              </li>
              <li style={{ marginBottom: "4px" }}>Envío por Evolution API</li>
              <li>Intervalo de 1 minuto</li>
            </ul>
          </div>
        </div>

        <div className="m-table-card">
          <div
            style={{
              padding: "16px 20px",
              borderBottom: "1px solid #e2e8f0",
              display: "flex",
              alignItems: "center",
              gap: "10px",
            }}
          >
            <FiMessageSquare size={18} style={{ color: "#ef4444" }} />
            <h3 style={{ margin: 0, fontSize: "16px", color: "#1e293b" }}>
              Disparador de Mensajes
            </h3>
            <span
              className={`m-badge ${isRunning ? "m-badge-paid" : "m-badge-pending"}`}
              style={{ marginLeft: "auto" }}
            >
              {isRunning ? (
                <FiCheckCircle size={11} />
              ) : (
                <FiAlertCircle size={11} />
              )}
              {isRunning ? " En ejecución" : " Detenido"}
            </span>
          </div>
          <div style={{ padding: "20px" }}>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
                gap: "16px",
                marginBottom: "16px",
              }}
            >
              <div className="m-form-group" style={{ margin: 0 }}>
                <label>
                  <FiPhone size={13} /> Número de Destino
                </label>
                {isRunning ? (
                  <span
                    style={{
                      display: "block",
                      padding: "10px 14px",
                      background: "#f1f5f9",
                      borderRadius: "8px",
                      color: "#475569",
                      fontWeight: "500",
                    }}
                  >
                    {phoneNumber}
                  </span>
                ) : (
                  <div
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      gap: "4px",
                    }}
                  >
                    <input
                      ref={inputRef}
                      type="text"
                      value={phoneNumber}
                      onChange={handleInputChange}
                      onBlur={handleInputBlur}
                      onFocus={handleInputFocus}
                      placeholder="519XXXXXXXX"
                      style={{
                        padding: "10px 14px",
                        fontSize: "14px",
                        borderRadius: "8px",
                        border: error
                          ? "1px solid #ef4444"
                          : "1px solid #e2e8f0",
                        outline: "none",
                        transition: "border-color 0.2s",
                      }}
                    />
                    <span style={{ fontSize: "12px", color: "#94a3b8" }}>
                      Ej: 51952310138 (11 dígitos)
                    </span>
                  </div>
                )}
              </div>

              <div className="m-form-group" style={{ margin: 0 }}>
                <label>
                  <FiClock size={13} /> Próxima Verificación
                </label>
                <span
                  style={{
                    display: "block",
                    padding: "10px 14px",
                    background: "#f1f5f9",
                    borderRadius: "8px",
                    color: "#475569",
                    fontWeight: "500",
                  }}
                >
                  {status.last_sent || "Nunca"}
                </span>
              </div>
            </div>

            {error && (
              <div
                style={{
                  padding: "12px 16px",
                  background: "#fef2f2",
                  border: "1px solid #fee2e2",
                  borderRadius: "8px",
                  color: "#dc2626",
                  marginBottom: "16px",
                }}
              >
                <strong>Error:</strong> {error}
              </div>
            )}

            <div
              className="m-form-actions"
              style={{ justifyContent: "flex-start", marginBottom: "16px" }}
            >
              {isRunning ? (
                <button
                  className="m-btn-danger"
                  onClick={handleStop}
                  disabled={loading}
                >
                  {loading ? (
                    <FiRefreshCw
                      size={14}
                      style={{ animation: "spin 1s linear infinite" }}
                    />
                  ) : (
                    <FiSquare size={14} />
                  )}
                  {loading ? " Deteniendo..." : " Detener"}
                </button>
              ) : (
                <button
                  className="m-btn-primary"
                  onClick={handleStart}
                  disabled={loading}
                >
                  {loading ? (
                    <FiRefreshCw
                      size={14}
                      style={{ animation: "spin 1s linear infinite" }}
                    />
                  ) : (
                    <FiPlay size={14} />
                  )}
                  {loading ? " Iniciando..." : " Iniciar"}
                </button>
              )}
            </div>

            {status.last_message && (
              <div
                style={{
                  padding: "12px 16px",
                  background: "#f1f5f9",
                  borderRadius: "8px",
                }}
              >
                <label
                  style={{
                    fontSize: "12px",
                    fontWeight: "600",
                    color: "#64748b",
                    textTransform: "uppercase",
                    letterSpacing: "0.5px",
                    display: "block",
                    marginBottom: "4px",
                  }}
                >
                  <FiMessageSquare size={10} /> Último Mensaje
                </label>
                <p style={{ margin: 0, color: "#1e293b", fontSize: "14px" }}>
                  {status.last_message}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Fila 2: Info Backup - Disparador Backup */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "20px",
          marginBottom: "20px",
        }}
      >
        <div className="m-table-card">
          <div
            style={{
              padding: "16px 20px",
              borderBottom: "1px solid #e2e8f0",
              display: "flex",
              alignItems: "center",
              gap: "10px",
            }}
          >
            <FiDatabase size={18} style={{ color: "#3b82f6" }} />
            <h3 style={{ margin: 0, fontSize: "16px", color: "#1e293b" }}>
              Información del Monitoreo
            </h3>
          </div>
          <div style={{ padding: "20px" }}>
            <p
              style={{
                margin: "0 0 8px 0",
                color: "#475569",
                fontSize: "14px",
              }}
            >
              El sistema verifica automáticamente a las{" "}
              <strong>
                {String(backupHour).padStart(2, "0")}:
                {String(backupMinute).padStart(2, "0")} (
                {backupStatus.timezone || "America/Lima"})
              </strong>{" "}
              si existe un backup de la base de datos <strong>Bibliouni</strong>{" "}
              realizado durante el día.
            </p>
            <ul
              style={{
                margin: 0,
                paddingLeft: "20px",
                color: "#64748b",
                fontSize: "13px",
              }}
            >
              <li style={{ marginBottom: "4px" }}>
                Verificación diaria a las {String(backupHour).padStart(2, "0")}:
                {String(backupMinute).padStart(2, "0")}
              </li>
              <li style={{ marginBottom: "4px" }}>
                Alerta por WhatsApp si falta backup
              </li>
              <li style={{ marginBottom: "4px" }}>
                Responde "RESUELVE BACKUP" para ejecutar
              </li>
              <li>Webhook configurado automáticamente</li>
            </ul>
          </div>
        </div>

        <div className="m-table-card">
          <div
            style={{
              padding: "16px 20px",
              borderBottom: "1px solid #e2e8f0",
              display: "flex",
              alignItems: "center",
              gap: "10px",
            }}
          >
            <FiDatabase size={18} style={{ color: "#3b82f6" }} />
            <h3 style={{ margin: 0, fontSize: "16px", color: "#1e293b" }}>
              Disparador de Backup
            </h3>
            <span
              className={`m-badge ${backupRunning ? "m-badge-paid" : "m-badge-pending"}`}
              style={{ marginLeft: "auto" }}
            >
              {backupRunning ? (
                <FiCheckCircle size={11} />
              ) : (
                <FiAlertCircle size={11} />
              )}
              {backupRunning ? " En ejecución" : " Detenido"}
            </span>
          </div>
          <div style={{ padding: "20px" }}>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
                gap: "16px",
                marginBottom: "16px",
              }}
            >
              <div className="m-form-group" style={{ margin: 0 }}>
                <label>
                  <FiPhone size={13} /> Número de Destino
                </label>
                {backupRunning ? (
                  <span
                    style={{
                      display: "block",
                      padding: "10px 14px",
                      background: "#f1f5f9",
                      borderRadius: "8px",
                      color: "#475569",
                      fontWeight: "500",
                    }}
                  >
                    {backupPhone}
                  </span>
                ) : (
                  <div
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      gap: "4px",
                    }}
                  >
                    <input
                      ref={backupInputRef}
                      type="text"
                      value={backupPhone}
                      onChange={handleBackupInputChange}
                      onBlur={handleBackupInputBlur}
                      onFocus={handleBackupInputFocus}
                      placeholder="519XXXXXXXX"
                      style={{
                        padding: "10px 14px",
                        fontSize: "14px",
                        borderRadius: "8px",
                        border: backupError
                          ? "1px solid #ef4444"
                          : "1px solid #e2e8f0",
                        outline: "none",
                        transition: "border-color 0.2s",
                      }}
                    />
                    <span style={{ fontSize: "12px", color: "#94a3b8" }}>
                      Ej: 51952310138 (11 dígitos)
                    </span>
                  </div>
                )}
              </div>

              <div className="m-form-group" style={{ margin: 0 }}>
                <label>
                  <FiClock size={13} /> Horario de Verificación
                </label>
                {backupRunning ? (
                  <span
                    style={{
                      display: "block",
                      padding: "10px 14px",
                      background: "#f1f5f9",
                      borderRadius: "8px",
                      color: "#475569",
                      fontWeight: "500",
                    }}
                  >
                    {backupStatus.check_time || "07:00"}
                  </span>
                ) : (
                  <div
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      gap: "8px",
                    }}
                  >
                    <div style={{ display: "flex", gap: "8px" }}>
                      <div style={{ flex: 1 }}>
                        <label
                          style={{
                            display: "block",
                            fontSize: "11px",
                            color: "#94a3b8",
                            marginBottom: "4px",
                            textTransform: "uppercase",
                          }}
                        >
                          Hora
                        </label>
                        <input
                          type="number"
                          min={0}
                          max={23}
                          value={backupHour}
                          onChange={handleBackupHourChange}
                          placeholder="7"
                          style={{
                            width: "100%",
                            padding: "10px 14px",
                            fontSize: "14px",
                            borderRadius: "8px",
                            border: "1px solid #e2e8f0",
                            outline: "none",
                            transition: "border-color 0.2s",
                          }}
                        />
                      </div>
                      <div style={{ flex: 1 }}>
                        <label
                          style={{
                            display: "block",
                            fontSize: "11px",
                            color: "#94a3b8",
                            marginBottom: "4px",
                            textTransform: "uppercase",
                          }}
                        >
                          Minuto
                        </label>
                        <input
                          type="number"
                          min={0}
                          max={59}
                          value={backupMinute}
                          onChange={handleBackupMinuteChange}
                          placeholder="0"
                          style={{
                            width: "100%",
                            padding: "10px 14px",
                            fontSize: "14px",
                            borderRadius: "8px",
                            border: "1px solid #e2e8f0",
                            outline: "none",
                            transition: "border-color 0.2s",
                          }}
                        />
                      </div>
                      <div
                        style={{
                          display: "flex",
                          alignItems: "flex-end",
                          paddingBottom: "10px",
                          color: "#64748b",
                          fontWeight: "500",
                          fontSize: "14px",
                        }}
                      >
                        {String(backupHour).padStart(2, "0")}:
                        {String(backupMinute).padStart(2, "0")}
                      </div>
                    </div>
                    <span style={{ fontSize: "12px", color: "#94a3b8" }}>
                      Hora local ({backupStatus.timezone || "America/Lima"})
                    </span>
                  </div>
                )}
              </div>

              <div className="m-form-group" style={{ margin: 0 }}>
                <label>
                  <FiClock size={13} /> Próxima Verificación
                </label>
                <span
                  style={{
                    display: "block",
                    padding: "10px 14px",
                    background: "#f1f5f9",
                    borderRadius: "8px",
                    color: "#475569",
                    fontWeight: "500",
                  }}
                >
                  {backupRunning
                    ? backupStatus.check_time
                      ? `${backupStatus.check_time} (${backupStatus.timezone})`
                      : "Calculando..."
                    : "-"}
                </span>
              </div>

              <div className="m-form-group" style={{ margin: 0 }}>
                <label>
                  <FiCheckCircle size={13} /> Última Verificación
                </label>
                <span
                  style={{
                    display: "block",
                    padding: "10px 14px",
                    background: "#f1f5f9",
                    borderRadius: "8px",
                    color: "#475569",
                    fontWeight: "500",
                  }}
                >
                  {backupStatus.last_check
                    ? `${backupStatus.last_check} — ${backupStatus.last_result === "exito" ? "Éxito" : backupStatus.last_result === "alerta" ? "Alerta enviada" : "Nunca"}`
                    : "Nunca"}
                </span>
              </div>
            </div>

            {backupError && (
              <div
                style={{
                  padding: "12px 16px",
                  background: "#fef2f2",
                  border: "1px solid #fee2e2",
                  borderRadius: "8px",
                  color: "#dc2626",
                  marginBottom: "16px",
                }}
              >
                <strong>Error:</strong> {backupError}
              </div>
            )}

            {/* Lógica para el boton que está en backup  */}
            <div
              className="m-form-actions"
              style={{ justifyContent: "flex-start", marginBottom: "16px" }}
            >
              {backupRunning ? (
                <button
                  className="m-btn-danger"
                  onClick={handleBackupStop}
                  disabled={backupLoading}
                >
                  {backupLoading ? (
                    <FiRefreshCw
                      size={14}
                      style={{ animation: "spin 1s linear infinite" }}
                    />
                  ) : (
                    <FiSquare size={14} />
                  )}
                  {backupLoading ? " Deteniendo..." : " Detener Monitoreo"}
                </button>
              ) : (
                <button
                  className="m-btn-primary"
                  onClick={handleBackupStart}
                  disabled={backupLoading}
                >
                  {backupLoading ? (
                    <FiRefreshCw
                      size={14}
                      style={{ animation: "spin 1s linear infinite" }}
                    />
                  ) : (
                    <FiPlay size={14} />
                  )}
                  {backupLoading ? " Iniciando..." : " Iniciar Monitoreo"}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Fila 3: Info Factor Llenado - Factor Llenado */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "20px",
          marginBottom: "20px",
        }}
      >
        <div className="m-table-card">
          <div
            style={{
              padding: "16px 20px",
              borderBottom: "1px solid #e2e8f0",
              display: "flex",
              alignItems: "center",
              gap: "10px",
            }}
          >
            <FiSettings size={18} style={{ color: "#8b5cf6" }} />
            <h3 style={{ margin: 0, fontSize: "16px", color: "#1e293b" }}>
              ¿Qué es el Factor de Llenado?
            </h3>
          </div>
          <div style={{ padding: "20px" }}>
            <p
              style={{
                margin: "0 0 8px 0",
                color: "#475569",
                fontSize: "14px",
              }}
            >
              El <strong>factor de llenado</strong> define qué porcentaje de
              cada página de índice se llena con datos al reconstruir. Dejar
              espacio libre reduce los <em>page splits</em> y mejora el
              rendimiento en tablas con muchas escrituras.
            </p>
            <ul
              style={{
                margin: 0,
                paddingLeft: "20px",
                color: "#64748b",
                fontSize: "13px",
              }}
            >
              <li style={{ marginBottom: "4px" }}>
                <strong>100%</strong> — Para tablas de solo lectura (máximo
                rendimiento de lectura)
              </li>
              <li style={{ marginBottom: "4px" }}>
                <strong>80-90%</strong> — Recomendado para tablas con
                operaciones mixtas (lectura + escritura)
              </li>
              <li style={{ marginBottom: "4px" }}>
                <strong>60-70%</strong> — Para tablas con muchas inserciones
                aleatorias
              </li>
            </ul>
            <p
              style={{
                margin: "12px 0 0 0",
                color: "#475569",
                fontSize: "14px",
              }}
            >
              También puede ejecutarse enviando por WhatsApp: <br />
              <code
                style={{
                  background: "rgba(139,92,246,0.07)",
                  padding: "4px 10px",
                  borderRadius: "6px",
                  fontFamily: "monospace",
                  fontSize: "0.95em",
                  color: "#8b5cf6",
                }}
              >
                FACTOR LLENADO 80
              </code>
            </p>
          </div>
        </div>

        <div className="m-table-card">
          <div
            style={{
              padding: "16px 20px",
              borderBottom: "1px solid #e2e8f0",
              display: "flex",
              alignItems: "center",
              gap: "10px",
            }}
          >
            <FiSettings size={18} style={{ color: "#8b5cf6" }} />
            <h3 style={{ margin: 0, fontSize: "16px", color: "#1e293b" }}>
              Factor de Llenado de Índices
            </h3>
          </div>
          <div style={{ padding: "20px" }}>
            <p
              style={{
                margin: "0 0 16px 0",
                color: "#475569",
                fontSize: "14px",
              }}
            >
              Reconstruye todos los índices de <strong>Bibliouni</strong> con el
              factor de llenado especificado.
            </p>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
                gap: "16px",
                marginBottom: "16px",
              }}
            >
              <div className="m-form-group" style={{ margin: 0 }}>
                <label>
                  <FiSettings size={13} /> Factor de llenado (%)
                </label>
                <input
                  type="number"
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
                  style={{
                    padding: "10px 14px",
                    fontSize: "14px",
                    borderRadius: "8px",
                    border: fillFactorError
                      ? "1px solid #ef4444"
                      : "1px solid #e2e8f0",
                    outline: "none",
                    transition: "border-color 0.2s",
                    width: "100%",
                  }}
                />
                <span style={{ fontSize: "12px", color: "#94a3b8" }}>
                  Número entre 1 y 100 (recomendado: 80)
                </span>
              </div>
            </div>

            {fillFactorError && (
              <div
                style={{
                  padding: "12px 16px",
                  background: "#fef2f2",
                  border: "1px solid #fee2e2",
                  borderRadius: "8px",
                  color: "#dc2626",
                  marginBottom: "16px",
                }}
              >
                <strong>Error:</strong> {fillFactorError}
              </div>
            )}

            {fillFactorResult && (
              <div
                style={{
                  padding: "12px 16px",
                  borderLeft: `3px solid ${fillFactorResult.success ? "#22c55e" : "#ef4444"}`,
                  background: fillFactorResult.success
                    ? "rgba(34,197,94,0.07)"
                    : "rgba(239,68,68,0.07)",
                  borderRadius: "8px",
                  marginBottom: "16px",
                }}
              >
                <label
                  style={{
                    fontSize: "12px",
                    fontWeight: "600",
                    textTransform: "uppercase",
                    letterSpacing: "0.5px",
                    display: "block",
                    marginBottom: "4px",
                  }}
                >
                  {fillFactorResult.success
                    ? "✅ Rebuild completado"
                    : "❌ Error en rebuild"}
                </label>
                <p style={{ margin: 0, color: "#1e293b", fontSize: "14px" }}>
                  {fillFactorResult.result?.mensaje || "Operación finalizada."}
                </p>
                {fillFactorResult.result?.tablas_procesadas !== undefined && (
                  <p
                    style={{
                      margin: "8px 0 0 0",
                      color: "#475569",
                      fontSize: "13px",
                    }}
                  >
                    Tablas procesadas:{" "}
                    <strong>{fillFactorResult.result.tablas_procesadas}</strong>
                  </p>
                )}
                {fillFactorResult.result?.tablas_con_error?.length > 0 && (
                  <p
                    style={{
                      margin: "8px 0 0 0",
                      color: "#f59e0b",
                      fontSize: "13px",
                    }}
                  >
                    ⚠️ Tablas con error:{" "}
                    {fillFactorResult.result.tablas_con_error
                      .map((e) => e.tabla)
                      .join(", ")}
                  </p>
                )}
              </div>
            )}

            <div
              className="m-form-actions"
              style={{ justifyContent: "flex-start" }}
            >
              <button
                className="m-btn-primary"
                onClick={handleFillFactor}
                disabled={fillFactorLoading}
              >
                {fillFactorLoading ? (
                  <FiRefreshCw
                    size={14}
                    style={{ animation: "spin 1s linear infinite" }}
                  />
                ) : (
                  <FiPlay size={14} />
                )}
                {fillFactorLoading
                  ? " Ejecutando rebuild..."
                  : ` Ejecutar con Fill Factor ${fillFactor}%`}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Fila 4: Info Fragmentación - Monitoreo Fragmentación */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "20px",
          marginBottom: "20px",
        }}
      >
        <div className="m-table-card">
          <div
            style={{
              padding: "16px 20px",
              borderBottom: "1px solid #e2e8f0",
              display: "flex",
              alignItems: "center",
              gap: "10px",
            }}
          >
            <FiActivity size={18} style={{ color: "#10b981" }} />
            <h3 style={{ margin: 0, fontSize: "16px", color: "#1e293b" }}>
              ¿Cómo funciona el Monitoreo?
            </h3>
          </div>
          <div style={{ padding: "20px" }}>
            <p
              style={{
                margin: "0 0 8px 0",
                color: "#475569",
                fontSize: "14px",
              }}
            >
              El sistema verifica cada <strong>1 hora</strong> el nivel de
              fragmentación de los índices en <strong>Bibliouni</strong>. Si
              algún índice supera el umbral configurado, envía una alerta por
              WhatsApp con el detalle y el comando sugerido.
            </p>
            <ul
              style={{
                margin: 0,
                paddingLeft: "20px",
                color: "#64748b",
                fontSize: "13px",
              }}
            >
              <li style={{ marginBottom: "4px" }}>
                Verificación automática cada 1 hora
              </li>
              <li style={{ marginBottom: "4px" }}>
                Alerta por WhatsApp si hay fragmentación alta
              </li>
              <li style={{ marginBottom: "4px" }}>
                Muestra qué tablas e índices están afectados
              </li>
              <li style={{ marginBottom: "4px" }}>
                Responde "FACTOR LLENADO 80" para optimizar
              </li>
              <li>Botón "Verificar Ahora" para comprobar al instante</li>
            </ul>
          </div>
        </div>

        <div className="m-table-card">
          <div
            style={{
              padding: "16px 20px",
              borderBottom: "1px solid #e2e8f0",
              display: "flex",
              alignItems: "center",
              gap: "10px",
            }}
          >
            <FiActivity size={18} style={{ color: "#10b981" }} />
            <h3 style={{ margin: 0, fontSize: "16px", color: "#1e293b" }}>
              Monitoreo de Fragmentación
            </h3>
            <span
              className={`m-badge ${fragRunning ? "m-badge-paid" : "m-badge-pending"}`}
              style={{ marginLeft: "auto" }}
            >
              {fragRunning ? (
                <FiCheckCircle size={11} />
              ) : (
                <FiAlertCircle size={11} />
              )}
              {fragRunning ? " En ejecución" : " Detenido"}
            </span>
          </div>
          <div style={{ padding: "20px" }}>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
                gap: "16px",
                marginBottom: "16px",
              }}
            >
              <div className="m-form-group" style={{ margin: 0 }}>
                <label>
                  <FiAlertCircle size={13} /> Umbral de alerta (%)
                </label>
                {fragRunning ? (
                  <span
                    style={{
                      display: "block",
                      padding: "10px 14px",
                      background: "#f1f5f9",
                      borderRadius: "8px",
                      color: "#475569",
                      fontWeight: "500",
                    }}
                  >
                    {fragUmbral}%
                  </span>
                ) : (
                  <div
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      gap: "4px",
                    }}
                  >
                    <input
                      type="number"
                      value={fragUmbral}
                      onChange={(e) => {
                        setFragUmbral(e.target.value);
                        setFragError("");
                      }}
                      min="1"
                      max="100"
                      placeholder="30"
                      disabled={fragRunning}
                      style={{
                        padding: "10px 14px",
                        fontSize: "14px",
                        borderRadius: "8px",
                        border: fragError
                          ? "1px solid #ef4444"
                          : "1px solid #e2e8f0",
                        outline: "none",
                        transition: "border-color 0.2s",
                        width: "100%",
                      }}
                    />
                    <span style={{ fontSize: "12px", color: "#94a3b8" }}>
                      Si un índice supera este %, se envía alerta
                    </span>
                  </div>
                )}
              </div>

              <div className="m-form-group" style={{ margin: 0 }}>
                <label>
                  <FiClock size={13} /> Próxima Verificación
                </label>
                <span
                  style={{
                    display: "block",
                    padding: "10px 14px",
                    background: "#f1f5f9",
                    borderRadius: "8px",
                    color: "#475569",
                    fontWeight: "500",
                  }}
                >
                  {fragRunning
                    ? `Cada ${fragStatus.interval_minutes || 60} min`
                    : "-"}
                </span>
              </div>

              <div className="m-form-group" style={{ margin: 0 }}>
                <label>
                  <FiCheckCircle size={13} /> Última Verificación
                </label>
                <span
                  style={{
                    display: "block",
                    padding: "10px 14px",
                    background: "#f1f5f9",
                    borderRadius: "8px",
                    color: "#475569",
                    fontWeight: "500",
                  }}
                >
                  {fragStatus.last_check
                    ? `${fragStatus.last_check} — ${fragStatus.last_result?.hay_alerta ? `⚠️ ${fragStatus.last_result.tablas_fragmentadas?.length || 0} índices fragmentados` : "✅ Todo OK"}`
                    : "Nunca"}
                </span>
              </div>
            </div>

            {fragError && (
              <div
                style={{
                  padding: "12px 16px",
                  background: "#fef2f2",
                  border: "1px solid #fee2e2",
                  borderRadius: "8px",
                  color: "#dc2626",
                  marginBottom: "16px",
                }}
              >
                <strong>Error:</strong> {fragError}
              </div>
            )}

            <div
              className="m-form-actions"
              style={{
                justifyContent: "flex-start",
                gap: "10px",
                flexWrap: "wrap",
              }}
            >
              {fragRunning ? (
                <button
                  className="m-btn-danger"
                  onClick={handleFragStop}
                  disabled={fragLoading}
                >
                  {fragLoading ? (
                    <FiRefreshCw
                      size={14}
                      style={{ animation: "spin 1s linear infinite" }}
                    />
                  ) : (
                    <FiSquare size={14} />
                  )}
                  {fragLoading ? " Deteniendo..." : " Detener Monitoreo"}
                </button>
              ) : (
                <button
                  className="m-btn-primary"
                  onClick={handleFragStart}
                  disabled={fragLoading}
                >
                  {fragLoading ? (
                    <FiRefreshCw
                      size={14}
                      style={{ animation: "spin 1s linear infinite" }}
                    />
                  ) : (
                    <FiPlay size={14} />
                  )}
                  {fragLoading ? " Iniciando..." : " Iniciar Monitoreo"}
                </button>
              )}
              <button
                onClick={handleFragTest}
                disabled={fragTestLoading}
                style={{
                  padding: "10px 18px",
                  borderRadius: "8px",
                  border: "1px solid #e2e8f0",
                  background: "white",
                  color: "#475569",
                  fontSize: "14px",
                  fontWeight: "500",
                  cursor: "pointer",
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "8px",
                  transition: "all 0.2s",
                }}
                onMouseEnter={(e) =>
                  (e.currentTarget.style.background = "#f8fafc")
                }
                onMouseLeave={(e) =>
                  (e.currentTarget.style.background = "white")
                }
              >
                {fragTestLoading ? (
                  <FiRefreshCw
                    size={14}
                    style={{ animation: "spin 1s linear infinite" }}
                  />
                ) : (
                  <FiActivity size={14} />
                )}
                {fragTestLoading ? " Verificando..." : " Verificar Ahora"}
              </button>
            </div>

            {fragTestResult && (
              <div
                style={{
                  marginTop: "16px",
                  padding: "16px",
                  borderLeft: `3px solid ${fragTestResult.hay_alerta ? "#f59e0b" : "#22c55e"}`,
                  background: fragTestResult.hay_alerta
                    ? "rgba(245,158,11,0.07)"
                    : "rgba(34,197,94,0.07)",
                  borderRadius: "8px",
                }}
              >
                <label
                  style={{
                    fontSize: "12px",
                    fontWeight: "600",
                    textTransform: "uppercase",
                    letterSpacing: "0.5px",
                    display: "block",
                    marginBottom: "8px",
                  }}
                >
                  {fragTestResult.hay_alerta
                    ? `⚠️ ${fragTestResult.tablas_fragmentadas.length} índices superan el ${fragTestResult.umbral}%`
                    : `✅ Todos los índices por debajo del ${fragTestResult.umbral}%`}
                </label>
                <p
                  style={{
                    margin: "0 0 12px 0",
                    color: "#475569",
                    fontSize: "14px",
                  }}
                >
                  {fragTestResult.mensaje}
                </p>

                {fragTestResult.tablas_fragmentadas?.length > 0 && (
                  <div style={{ overflowX: "auto" }}>
                    <table
                      style={{
                        width: "100%",
                        borderCollapse: "collapse",
                        fontSize: "0.9em",
                        background: "white",
                        borderRadius: "8px",
                        overflow: "hidden",
                      }}
                    >
                      <thead style={{ background: "#f1f5f9" }}>
                        <tr>
                          <th
                            style={{
                              textAlign: "left",
                              padding: "10px 12px",
                              fontWeight: "600",
                              color: "#475569",
                            }}
                          >
                            Tabla
                          </th>
                          <th
                            style={{
                              textAlign: "left",
                              padding: "10px 12px",
                              fontWeight: "600",
                              color: "#475569",
                            }}
                          >
                            Índice
                          </th>
                          <th
                            style={{
                              textAlign: "right",
                              padding: "10px 12px",
                              fontWeight: "600",
                              color: "#475569",
                            }}
                          >
                            Fragmentación
                          </th>
                          <th
                            style={{
                              textAlign: "right",
                              padding: "10px 12px",
                              fontWeight: "600",
                              color: "#475569",
                            }}
                          >
                            Páginas
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {fragTestResult.tablas_fragmentadas.map((item, idx) => (
                          <tr
                            key={idx}
                            style={{ borderBottom: "1px solid #e2e8f0" }}
                          >
                            <td
                              style={{ padding: "10px 12px", color: "#1e293b" }}
                            >
                              {item.tabla}
                            </td>
                            <td
                              style={{ padding: "10px 12px", color: "#1e293b" }}
                            >
                              {item.indice}
                            </td>
                            <td
                              style={{
                                padding: "10px 12px",
                                textAlign: "right",
                                color:
                                  item.fragmentacion >= 50
                                    ? "#ef4444"
                                    : "#f59e0b",
                                fontWeight: "500",
                              }}
                            >
                              {item.fragmentacion.toFixed(1)}%
                            </td>
                            <td
                              style={{
                                padding: "10px 12px",
                                textAlign: "right",
                                color: "#475569",
                              }}
                            >
                              {item.paginas}
                            </td>
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
      </div>

      {/* ========== REPORTES AUTOMÁTICOS ========== */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "20px",
          marginBottom: "20px",
        }}
      >
        {/* Izquierda: Información */}
        <div className="m-table-card">
          <div
            style={{
              padding: "16px 20px",
              borderBottom: "1px solid #e2e8f0",
              display: "flex",
              alignItems: "center",
              gap: "10px",
            }}
          >
            <FiCalendar size={18} style={{ color: "#8b5cf6" }} />
            <h3 style={{ margin: 0, fontSize: "16px", color: "#1e293b" }}>
              Reportes Automáticos
            </h3>
          </div>
          <div style={{ padding: "20px" }}>
            <p
              style={{
                margin: "0 0 12px 0",
                color: "#475569",
                fontSize: "14px",
              }}
            >
              Programa el envío automático de reportes bibliotecarios por
              WhatsApp según la periodicidad que configures. El sistema enviará
              un menú interactivo al número destino en los horarios programados.
            </p>
            <ul
              style={{
                margin: "0 0 16px 0",
                paddingLeft: "20px",
                color: "#64748b",
                fontSize: "13px",
              }}
            >
              <li style={{ marginBottom: "4px" }}>
                Reporte diario a la hora configurada
              </li>
              <li style={{ marginBottom: "4px" }}>
                Reporte semanal el día y hora configurados
              </li>
              <li style={{ marginBottom: "4px" }}>
                Reporte mensual el día y hora configurados
              </li>
              <li style={{ marginBottom: "4px" }}>
                Envío automático por WhatsApp mediante Evolution API
              </li>
              <li style={{ marginBottom: "4px" }}>Zona horaria America/Lima</li>
            </ul>

            <div
              style={{
                background: "#f8fafc",
                borderRadius: "8px",
                padding: "14px",
                marginBottom: "14px",
              }}
            >
              <strong
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "6px",
                  marginBottom: "8px",
                  color: "#1e293b",
                  fontSize: "13px",
                }}
              >
                <FiMessageSquare size={14} style={{ color: "#8b5cf6" }} />
                Reportes Interactivos
              </strong>
              <p
                style={{
                  margin: 0,
                  color: "#64748b",
                  fontSize: "12px",
                  lineHeight: "1.5",
                }}
              >
                También puedes solicitar reportes bajo demanda respondiendo al
                menú de WhatsApp. El sistema genera y envía el PDF en tiempo
                real.
              </p>
            </div>

            <div
              style={{
                background: "#f8fafc",
                borderRadius: "8px",
                padding: "14px",
              }}
            >
              <strong
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "6px",
                  marginBottom: "8px",
                  color: "#1e293b",
                  fontSize: "13px",
                }}
              >
                <FiList size={14} style={{ color: "#8b5cf6" }} />
                Reportes Disponibles
              </strong>
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr",
                  gap: "6px",
                }}
              >
                {[
                  { num: "1", icon: "📊", name: "Estadísticas" },
                  { num: "2", icon: "📚", name: "Libros Prestados" },
                  { num: "3", icon: "💰", name: "Multas" },
                  { num: "4", icon: "⏰", name: "Préstamos Vencidos" },
                  { num: "5", icon: "📕", name: "Libros Dañados" },
                ].map((item) => (
                  <div
                    key={item.num}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "6px",
                      fontSize: "12px",
                      color: "#64748b",
                    }}
                  >
                    <span
                      style={{
                        display: "inline-flex",
                        alignItems: "center",
                        justifyContent: "center",
                        width: "18px",
                        height: "18px",
                        background: "#e0e7ff",
                        color: "#4338ca",
                        borderRadius: "4px",
                        fontSize: "10px",
                        fontWeight: "700",
                      }}
                    >
                      {item.num}
                    </span>
                    <span>
                      {item.icon} {item.name}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Derecha: Configuración */}
        <div className="m-table-card">
          <div
            style={{
              padding: "16px 20px",
              borderBottom: "1px solid #e2e8f0",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <FiSettings size={18} style={{ color: "#8b5cf6" }} />
              <h3 style={{ margin: 0, fontSize: "16px", color: "#1e293b" }}>
                Configuración de Reportes
              </h3>
            </div>
            <span
              className={`m-badge ${reportsRunning ? "m-badge-paid" : "m-badge-pending"}`}
            >
              {reportsRunning ? (
                <FiCheckCircle size={11} />
              ) : (
                <FiAlertCircle size={11} />
              )}
              {reportsRunning ? " En ejecución" : " Detenido"}
            </span>
          </div>
          <div style={{ padding: "20px" }}>
            {/* Destino */}
            <div className="m-form-group" style={{ marginBottom: "16px" }}>
              <label>
                <FiPhone size={13} /> Número de Destino
              </label>
              {reportsRunning ? (
                <span
                  style={{
                    display: "block",
                    padding: "10px 14px",
                    background: "#f1f5f9",
                    borderRadius: "8px",
                    color: "#475569",
                    fontWeight: "500",
                  }}
                >
                  {reportsPhone}
                </span>
              ) : (
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "4px",
                  }}
                >
                  <input
                    ref={reportsInputRef}
                    type="text"
                    value={reportsPhone}
                    onChange={handleReportsInputChange}
                    onBlur={handleReportsInputBlur}
                    onFocus={handleReportsInputFocus}
                    placeholder="519XXXXXXXX"
                    disabled={reportsRunning}
                    autoComplete="off"
                    style={{
                      padding: "10px 14px",
                      fontSize: "14px",
                      borderRadius: "8px",
                      border: reportsError
                        ? "1px solid #ef4444"
                        : "1px solid #e2e8f0",
                      outline: "none",
                    }}
                  />
                  <span style={{ fontSize: "12px", color: "#94a3b8" }}>
                    Ej: 51952310138 (11 dígitos)
                  </span>
                </div>
              )}
            </div>

            {/* Configuración de horarios */}
            <div
              style={{
                background: "#f8fafc",
                borderRadius: "8px",
                padding: "16px",
                marginBottom: "16px",
              }}
            >
              <h4
                style={{
                  margin: "0 0 12px 0",
                  fontSize: "14px",
                  color: "#1e293b",
                }}
              >
                ⚙️ Configuración de Horarios
              </h4>

              {/* DIARIO */}
              <div
                style={{
                  padding: "12px",
                  background: "white",
                  borderRadius: "8px",
                  marginBottom: "10px",
                  opacity: dailyEnabled ? 1 : 0.6,
                }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                    marginBottom: "8px",
                  }}
                >
                  <label className="toggle-switch">
                    <input
                      type="checkbox"
                      id="daily-enabled"
                      checked={dailyEnabled}
                      onChange={(e) => {
                        if (reportsRunning) {
                          handleToggleReport("daily", e.target.checked);
                        } else {
                          setDailyEnabled(e.target.checked);
                        }
                      }}
                    />
                    <span className="slider"></span>
                  </label>
                  <label
                    htmlFor="daily-enabled"
                    style={{
                      fontWeight: "600",
                      margin: 0,
                      cursor: "pointer",
                      fontSize: "14px",
                    }}
                  >
                    📅 Reporte Diario
                  </label>
                </div>
                <div
                  className="time-inputs"
                  style={{ display: "flex", gap: "10px", alignItems: "end" }}
                >
                  <div className="time-input-group">
                    <label style={{ fontSize: "12px", color: "#64748b" }}>
                      Hora
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="23"
                      value={dailyHour}
                      onChange={(e) =>
                        setDailyHour(parseInt(e.target.value) || 0)
                      }
                      disabled={reportsRunning || !dailyEnabled}
                      style={{
                        padding: "6px 10px",
                        borderRadius: "6px",
                        border: "1px solid #e2e8f0",
                        width: "60px",
                      }}
                    />
                  </div>
                  <div className="time-input-group">
                    <label style={{ fontSize: "12px", color: "#64748b" }}>
                      Minuto
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="59"
                      value={dailyMinute}
                      onChange={(e) =>
                        setDailyMinute(parseInt(e.target.value) || 0)
                      }
                      disabled={reportsRunning || !dailyEnabled}
                      style={{
                        padding: "6px 10px",
                        borderRadius: "6px",
                        border: "1px solid #e2e8f0",
                        width: "60px",
                      }}
                    />
                  </div>
                  <div
                    style={{
                      padding: "6px 12px",
                      background: "#e0e7ff",
                      color: "#4338ca",
                      borderRadius: "6px",
                      fontWeight: "600",
                      fontSize: "13px",
                    }}
                  >
                    {String(dailyHour).padStart(2, "0")}:
                    {String(dailyMinute).padStart(2, "0")}
                  </div>
                </div>
              </div>

              {/* SEMANAL */}
              <div
                style={{
                  padding: "12px",
                  background: "white",
                  borderRadius: "8px",
                  marginBottom: "10px",
                  opacity: weeklyEnabled ? 1 : 0.6,
                }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                    marginBottom: "8px",
                  }}
                >
                  <label className="toggle-switch">
                    <input
                      type="checkbox"
                      id="weekly-enabled"
                      checked={weeklyEnabled}
                      onChange={(e) => {
                        if (reportsRunning) {
                          handleToggleReport("weekly", e.target.checked);
                        } else {
                          setWeeklyEnabled(e.target.checked);
                        }
                      }}
                    />
                    <span className="slider"></span>
                  </label>
                  <label
                    htmlFor="weekly-enabled"
                    style={{
                      fontWeight: "600",
                      margin: 0,
                      cursor: "pointer",
                      fontSize: "14px",
                    }}
                  >
                    📆 Reporte Semanal
                  </label>
                </div>
                <div
                  className="time-inputs"
                  style={{ display: "flex", gap: "10px", alignItems: "end" }}
                >
                  <div className="time-input-group">
                    <label style={{ fontSize: "12px", color: "#64748b" }}>
                      Día
                    </label>
                    <select
                      value={weeklyDay}
                      onChange={(e) => setWeeklyDay(e.target.value)}
                      disabled={reportsRunning || !weeklyEnabled}
                      style={{
                        padding: "6px 10px",
                        borderRadius: "6px",
                        border: "1px solid #e2e8f0",
                      }}
                    >
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
                    <label style={{ fontSize: "12px", color: "#64748b" }}>
                      Hora
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="23"
                      value={weeklyHour}
                      onChange={(e) =>
                        setWeeklyHour(parseInt(e.target.value) || 0)
                      }
                      disabled={reportsRunning || !weeklyEnabled}
                      style={{
                        padding: "6px 10px",
                        borderRadius: "6px",
                        border: "1px solid #e2e8f0",
                        width: "60px",
                      }}
                    />
                  </div>
                  <div className="time-input-group">
                    <label style={{ fontSize: "12px", color: "#64748b" }}>
                      Minuto
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="59"
                      value={weeklyMinute}
                      onChange={(e) =>
                        setWeeklyMinute(parseInt(e.target.value) || 0)
                      }
                      disabled={reportsRunning || !weeklyEnabled}
                      style={{
                        padding: "6px 10px",
                        borderRadius: "6px",
                        border: "1px solid #e2e8f0",
                        width: "60px",
                      }}
                    />
                  </div>
                  <div
                    style={{
                      padding: "6px 12px",
                      background: "#e0e7ff",
                      color: "#4338ca",
                      borderRadius: "6px",
                      fontWeight: "600",
                      fontSize: "13px",
                    }}
                  >
                    {weeklyDay} {String(weeklyHour).padStart(2, "0")}:
                    {String(weeklyMinute).padStart(2, "0")}
                  </div>
                </div>
              </div>

              {/* MENSUAL */}
              <div
                style={{
                  padding: "12px",
                  background: "white",
                  borderRadius: "8px",
                  opacity: monthlyEnabled ? 1 : 0.6,
                }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                    marginBottom: "8px",
                  }}
                >
                  <label className="toggle-switch">
                    <input
                      type="checkbox"
                      id="monthly-enabled"
                      checked={monthlyEnabled}
                      onChange={(e) => {
                        if (reportsRunning) {
                          handleToggleReport("monthly", e.target.checked);
                        } else {
                          setMonthlyEnabled(e.target.checked);
                        }
                      }}
                    />
                    <span className="slider"></span>
                  </label>
                  <label
                    htmlFor="monthly-enabled"
                    style={{
                      fontWeight: "600",
                      margin: 0,
                      cursor: "pointer",
                      fontSize: "14px",
                    }}
                  >
                    🗓️ Reporte Mensual
                  </label>
                </div>
                <div
                  className="time-inputs"
                  style={{ display: "flex", gap: "10px", alignItems: "end" }}
                >
                  <div className="time-input-group">
                    <label style={{ fontSize: "12px", color: "#64748b" }}>
                      Día
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="31"
                      value={monthlyDay}
                      onChange={(e) =>
                        setMonthlyDay(parseInt(e.target.value) || 1)
                      }
                      disabled={reportsRunning || !monthlyEnabled}
                      style={{
                        padding: "6px 10px",
                        borderRadius: "6px",
                        border: "1px solid #e2e8f0",
                        width: "60px",
                      }}
                    />
                  </div>
                  <div className="time-input-group">
                    <label style={{ fontSize: "12px", color: "#64748b" }}>
                      Hora
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="23"
                      value={monthlyHour}
                      onChange={(e) =>
                        setMonthlyHour(parseInt(e.target.value) || 0)
                      }
                      disabled={reportsRunning || !monthlyEnabled}
                      style={{
                        padding: "6px 10px",
                        borderRadius: "6px",
                        border: "1px solid #e2e8f0",
                        width: "60px",
                      }}
                    />
                  </div>
                  <div className="time-input-group">
                    <label style={{ fontSize: "12px", color: "#64748b" }}>
                      Minuto
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="59"
                      value={monthlyMinute}
                      onChange={(e) =>
                        setMonthlyMinute(parseInt(e.target.value) || 0)
                      }
                      disabled={reportsRunning || !monthlyEnabled}
                      style={{
                        padding: "6px 10px",
                        borderRadius: "6px",
                        border: "1px solid #e2e8f0",
                        width: "60px",
                      }}
                    />
                  </div>
                  <div
                    style={{
                      padding: "6px 12px",
                      background: "#e0e7ff",
                      color: "#4338ca",
                      borderRadius: "6px",
                      fontWeight: "600",
                      fontSize: "13px",
                    }}
                  >
                    Día {monthlyDay} {String(monthlyHour).padStart(2, "0")}:
                    {String(monthlyMinute).padStart(2, "0")}
                  </div>
                </div>
              </div>
            </div>

            {/* Resumen */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(3, 1fr)",
                gap: "10px",
                marginBottom: "16px",
              }}
            >
              <div
                style={{
                  padding: "12px",
                  background: "#eff6ff",
                  borderRadius: "8px",
                  border: "1px solid #dbeafe",
                }}
              >
                <div
                  style={{
                    fontSize: "12px",
                    color: "#1d4ed8",
                    fontWeight: "600",
                    marginBottom: "4px",
                  }}
                >
                  📅 Diario
                </div>
                <div style={{ fontSize: "12px", color: "#475569" }}>
                  {reportsStatus.daily?.time || "--"}
                </div>
                <div style={{ fontSize: "11px", color: "#64748b" }}>
                  {reportsStatus.daily_enabled ? "Habilitado" : "Deshabilitado"}
                </div>
              </div>
              <div
                style={{
                  padding: "12px",
                  background: "#eff6ff",
                  borderRadius: "8px",
                  border: "1px solid #dbeafe",
                }}
              >
                <div
                  style={{
                    fontSize: "12px",
                    color: "#1d4ed8",
                    fontWeight: "600",
                    marginBottom: "4px",
                  }}
                >
                  📆 Semanal
                </div>
                <div style={{ fontSize: "12px", color: "#475569" }}>
                  {reportsStatus.weekly?.day || "--"}{" "}
                  {reportsStatus.weekly?.time || ""}
                </div>
                <div style={{ fontSize: "11px", color: "#64748b" }}>
                  {reportsStatus.weekly_enabled
                    ? "Habilitado"
                    : "Deshabilitado"}
                </div>
              </div>
              <div
                style={{
                  padding: "12px",
                  background: "#eff6ff",
                  borderRadius: "8px",
                  border: "1px solid #dbeafe",
                }}
              >
                <div
                  style={{
                    fontSize: "12px",
                    color: "#1d4ed8",
                    fontWeight: "600",
                    marginBottom: "4px",
                  }}
                >
                  🗓️ Mensual
                </div>
                <div style={{ fontSize: "12px", color: "#475569" }}>
                  Día {reportsStatus.monthly?.day || "--"}{" "}
                  {reportsStatus.monthly?.time || ""}
                </div>
                <div style={{ fontSize: "11px", color: "#64748b" }}>
                  {reportsStatus.monthly_enabled
                    ? "Habilitado"
                    : "Deshabilitado"}
                </div>
              </div>
            </div>

            {reportsError && (
              <div
                style={{
                  padding: "12px 16px",
                  background: "#fef2f2",
                  border: "1px solid #fee2e2",
                  borderRadius: "8px",
                  color: "#dc2626",
                  marginBottom: "16px",
                }}
              >
                <strong>Error:</strong> {reportsError}
              </div>
            )}

            <div
              className="m-form-actions"
              style={{ justifyContent: "flex-start" }}
            >
              {reportsRunning ? (
                <button
                  className="m-btn-danger"
                  onClick={handleReportsStop}
                  disabled={reportsLoading}
                >
                  {reportsLoading ? (
                    <FiRefreshCw
                      size={14}
                      style={{ animation: "spin 1s linear infinite" }}
                    />
                  ) : (
                    <FiSquare size={14} />
                  )}
                  {reportsLoading ? " Deteniendo..." : " Detener"}
                </button>
              ) : (
                <button
                  className="m-btn-primary"
                  onClick={handleReportsStart}
                  disabled={reportsLoading}
                >
                  {reportsLoading ? (
                    <FiRefreshCw
                      size={14}
                      style={{ animation: "spin 1s linear infinite" }}
                    />
                  ) : (
                    <FiPlay size={14} />
                  )}
                  {reportsLoading ? " Iniciando..." : " Iniciar Reportes"}
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Fila 5: Info Seguridad Login - Disparador Seguridad Login */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: "20px",
            marginBottom: "20px",
          }}
        >
          <div className="m-table-card">
            <div
              style={{
                padding: "16px 20px",
                borderBottom: "1px solid #e2e8f0",
                display: "flex",
                alignItems: "center",
                gap: "10px",
              }}
            >
              <FiAlertCircle size={18} style={{ color: "#f59e0b" }} />
              <h3 style={{ margin: 0, fontSize: "16px", color: "#1e293b" }}>
                Información Seguridad Login
              </h3>
            </div>
            <div style={{ padding: "20px" }}>
              <p
                style={{
                  margin: "0 0 8px 0",
                  color: "#475569",
                  fontSize: "14px",
                }}
              >
                Monitorea intentos fallidos de inicio de sesión en SQL Server.
                Cuando un usuario falla más de 2 veces, envía una alerta por
                WhatsApp y espera tu confirmación para bloquear la cuenta.
              </p>
              <ul
                style={{
                  margin: 0,
                  paddingLeft: "20px",
                  color: "#64748b",
                  fontSize: "13px",
                }}
              >
                <li style={{ marginBottom: "4px" }}>
                  Verificación automática cada 5 minutos
                </li>
                <li style={{ marginBottom: "4px" }}>
                  Alerta por WhatsApp cuando un usuario falla más de 2 veces
                </li>
                <li style={{ marginBottom: "4px" }}>
                  Responde{" "}
                  <code
                    style={{
                      background: "rgba(245,158,11,0.1)",
                      padding: "2px 6px",
                      borderRadius: "4px",
                    }}
                  >
                    BLOQUEA
                  </code>{" "}
                  para deshabilitar la cuenta
                </li>
                <li>
                  No bloquea automáticamente, requiere confirmación humana
                </li>
              </ul>
            </div>
          </div>

          <div className="m-table-card">
            <div
              style={{
                padding: "16px 20px",
                borderBottom: "1px solid #e2e8f0",
                display: "flex",
                alignItems: "center",
                gap: "10px",
              }}
            >
              <FiAlertCircle size={18} style={{ color: "#f59e0b" }} />
              <h3 style={{ margin: 0, fontSize: "16px", color: "#1e293b" }}>
                Monitoreo Seguridad Login
              </h3>
              <span
                className={`m-badge ${loginSecurityRunning ? "m-badge-paid" : "m-badge-pending"}`}
                style={{ marginLeft: "auto" }}
              >
                {loginSecurityRunning ? (
                  <FiCheckCircle size={11} />
                ) : (
                  <FiAlertCircle size={11} />
                )}
                {loginSecurityRunning ? " En ejecución" : " Detenido"}
              </span>
            </div>
            <div style={{ padding: "20px" }}>
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
                  gap: "16px",
                  marginBottom: "16px",
                }}
              >
                <div className="m-form-group" style={{ margin: 0 }}>
                  <label>
                    <FiPhone size={13} /> Número de Destino
                  </label>
                  {loginSecurityRunning ? (
                    <span
                      style={{
                        display: "block",
                        padding: "10px 14px",
                        background: "#f1f5f9",
                        borderRadius: "8px",
                        color: "#475569",
                        fontWeight: "500",
                      }}
                    >
                      {loginSecurityPhone}
                    </span>
                  ) : (
                    <div
                      style={{
                        display: "flex",
                        flexDirection: "column",
                        gap: "4px",
                      }}
                    >
                      <input
                        ref={loginSecurityInputRef}
                        type="text"
                        value={loginSecurityPhone}
                        onChange={handleLoginSecurityInputChange}
                        onBlur={handleLoginSecurityInputBlur}
                        onFocus={handleLoginSecurityInputFocus}
                        placeholder="519XXXXXXXX"
                        style={{
                          padding: "10px 14px",
                          fontSize: "14px",
                          borderRadius: "8px",
                          border: loginSecurityError
                            ? "1px solid #ef4444"
                            : "1px solid #e2e8f0",
                          outline: "none",
                          transition: "border-color 0.2s",
                        }}
                      />
                      <span style={{ fontSize: "12px", color: "#94a3b8" }}>
                        Ej: 51952310138 (11 dígitos)
                      </span>
                    </div>
                  )}
                </div>

                <div className="m-form-group" style={{ margin: 0 }}>
                  <label>
                    <FiClock size={13} /> Última Alerta Emitida
                  </label>
                  <span
                    style={{
                      display: "block",
                      padding: "10px 14px",
                      background: "#f1f5f9",
                      borderRadius: "8px",
                      color: "#475569",
                      fontWeight: "500",
                    }}
                  >
                    {loginSecurityStatus.last_alert?.timestamp ||
                      loginSecurityStatus.last_check ||
                      "Nunca"}
                  </span>
                </div>
              </div>

              {loginSecurityError && (
                <div
                  style={{
                    padding: "12px 16px",
                    background: "#fef2f2",
                    border: "1px solid #fee2e2",
                    borderRadius: "8px",
                    color: "#dc2626",
                    marginBottom: "16px",
                  }}
                >
                  <strong>Error:</strong> {loginSecurityError}
                </div>
              )}

              <div
                className="m-form-actions"
                style={{ justifyContent: "flex-start" }}
              >
                {loginSecurityRunning ? (
                  <button
                    className="m-btn-danger"
                    onClick={handleLoginSecurityStop}
                    disabled={loginSecurityLoading}
                  >
                    {loginSecurityLoading ? (
                      <FiRefreshCw
                        size={14}
                        style={{ animation: "spin 1s linear infinite" }}
                      />
                    ) : (
                      <FiSquare size={14} />
                    )}
                    {loginSecurityLoading
                      ? " Deteniendo..."
                      : " Detener Monitoreo"}
                  </button>
                ) : (
                  <button
                    className="m-btn-primary"
                    onClick={handleLoginSecurityStart}
                    disabled={loginSecurityLoading}
                  >
                    {loginSecurityLoading ? (
                      <FiRefreshCw
                        size={14}
                        style={{ animation: "spin 1s linear infinite" }}
                      />
                    ) : (
                      <FiPlay size={14} />
                    )}
                    {loginSecurityLoading
                      ? " Iniciando..."
                      : " Iniciar Monitoreo"}
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Disparador;
