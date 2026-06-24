import React, { useState, useEffect, useRef } from "react";
import axios from "axios";

function Disparador() {
  const [isRunning, setIsRunning] = useState(false);
  const [status, setStatus] = useState({});
  const [loading, setLoading] = useState(false);
  const [phoneNumber, setPhoneNumber] = useState("51952310138");
  const [error, setError] = useState("");
  const [isEditing, setIsEditing] = useState(false);
  const inputRef = useRef(null);

  // Cargar estado inicial solo al montar
  useEffect(() => {
    fetchStatus(true);
  }, []);

  // Refrescar estado periódicamente SOLO si está corriendo
  useEffect(() => {
    if (!isRunning) return;
    const interval = setInterval(() => fetchStatus(false), 5000);
    return () => clearInterval(interval);
  }, [isRunning]);

  const fetchStatus = async (updatePhone = false) => {
    try {
      const res = await axios.get("/api/status");
      setStatus(res.data);
      setIsRunning(res.data.is_running);
      
      // Solo actualizar el número si se solicita explícitamente (montaje inicial)
      // y el usuario no está editando
      if (updatePhone && !isEditing && res.data.destination) {
        setPhoneNumber(res.data.destination);
      }
    } catch (e) {
      console.log("Error fetching status:", e);
    }
  };

  const validateInput = (number) => {
    const cleaned = number.replace(/\s/g, '').replace(/\+/g, '');
    if (!cleaned) return "Ingresa un número de teléfono";
    if (!/^\d+$/.test(cleaned)) return "Solo se permiten números";
    if (cleaned.length < 10) return `Número muy corto (${cleaned.length} dígitos). Mínimo 10.`;
    if (cleaned.length > 13) return `Número muy largo (${cleaned.length} dígitos). Máximo 13.`;
    return "";
  };

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
        number: phoneNumber.trim()
      });
      if (res.data.success) {
        setIsRunning(true);
        setStatus(prev => ({...prev, destination: phoneNumber.trim()}));
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

  const handleInputChange = (e) => {
    setIsEditing(true);
    setPhoneNumber(e.target.value);
    setError("");
    
    // Después de 2 segundos sin escribir, marcar que ya no está editando
    clearTimeout(window.editTimeout);
    window.editTimeout = setTimeout(() => {
      setIsEditing(false);
    }, 2000);
  };

  const handleInputBlur = () => {
    setIsEditing(false);
  };

  const handleInputFocus = () => {
    setIsEditing(true);
  };

  return (
    <div className="disparador-container">
      <div className="card">
        <div className="card-header">
          <h2>Disparador de WhatsApp</h2>
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
                    className={`phone-input ${error ? 'error' : ''}`}
                    value={phoneNumber}
                    onChange={handleInputChange}
                    onBlur={handleInputBlur}
                    onFocus={handleInputFocus}
                    placeholder="519XXXXXXXX"
                    disabled={isRunning}
                    autoComplete="off"
                  />
                  <span className="input-hint">Ej: 51952310138 (11 dígitos)</span>
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
    </div>
  );
}

export default Disparador;
