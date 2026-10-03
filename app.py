import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Gemelo Digital - Aula", layout="wide")

st.title("🏫 Gemelo Digital: Control Térmico de Aula")
st.write("Simulación del comportamiento térmico en función de los alumnos y la refrigeración.")

# --- BARRA LATERAL: PARÁMETROS DEL MODELO ---
st.sidebar.header("⚙️ Parámetros del Aula")

volumen_m3 = st.sidebar.number_input("Volumen del aula (m³)", value=150.0, step=10.0)
temp_ext = st.sidebar.slider("Temperatura Exterior (°C)", 15.0, 45.0, 32.0)
num_alumnos = st.sidebar.slider("Número de Alumnos", 0, 50, 25)

st.sidebar.header("❄️ Aire Acondicionado")
ac_activo = st.sidebar.checkbox("Encender Aire Acondicionado", value=True)
potencia_btu = st.sidebar.selectbox("Potencia del AC (BTU/h)", [9000, 12000, 18000, 24000, 36000], index=2)
temp_objetivo = st.sidebar.slider("Temperatura Objetivo del Termostato (°C)", 16.0, 26.0, 22.0)

# --- CONSTANTES FÍSICAS ---
DENSIDAD_AIRE = 1.2  # kg/m3
CALOR_ESPECIFICO_AIRE = 1005  # J/(kg*°C)
CALOR_POR_ALUMNO = 90  # Watts por persona
COEF_PERDIDA_PARED = 15  # W/°C (aislamiento térmico general del aula)

# Conversión BTU/h a Watts (1 BTU/h ≈ 0.293071 W)
potencia_ac_w = potencia_btu * 0.293071 if ac_activo else 0.0

# Masa total de aire
m_aire = volumen_m3 * DENSIDAD_AIRE
capacidad_calorifica_aula = m_aire * CALOR_ESPECIFICO_AIRE

# --- SIMULACIÓN (DIFERENCIAS FINITAS) ---
tiempo_total_min = 60
dt_seg = 1  # Paso de integración (1 segundo)
pasos = tiempo_total_min * 60

# Arreglos para almacenar datos
tiempo = np.linspace(0, tiempo_total_min, pasos)
temperaturas = np.zeros(pasos)

# Temperatura inicial del aula (igual a la exterior)
temp_actual = temp_ext

for i in range(pasos):
    temperaturas[i] = temp_actual
    
    # 1. Ganancia por personas
    q_personas = num_alumnos * CALOR_POR_ALUMNO
    
    # 2. Transferencia con exterior
    q_exterior = COEF_PERDIDA_PARED * (temp_ext - temp_actual)
    
    # 3. Control del aire acondicionado (Termostato encendido/apagado)
    if ac_activo and temp_actual > temp_objetivo:
        q_ac = -potencia_ac_w
    else:
        q_ac = 0
    
    # Flujo neto de calor (Watts = Joules / segundo)
    q_neto = q_personas + q_exterior + q_ac
    
    # Cambio de temperatura dt
    d_temp = (q_neto / capacidad_calorifica_aula) * dt_seg
    temp_actual += d_temp

# --- MÉTRICAS Y RESULTADOS ---
col1, col2, col3 = st.columns(3)
col1.metric("Temp. Inicial", f"{temp_ext:.1f} °C")
col2.metric("Temp. Final (60 min)", f"{temperaturas[-1]:.1f} °C")
col3.metric("Calor Humano Generado", f"{num_alumnos * CALOR_POR_ALUMNO} W")

# --- GRÁFICO ---
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(tiempo, temperaturas, color="#1f77b4", linewidth=2.5, label="Temp. Aula (°C)")
ax.axhline(temp_ext, color="red", linestyle="--", alpha=0.6, label="Temp. Exterior")

if ac_activo:
    ax.axhline(temp_objetivo, color="green", linestyle="--", alpha=0.6, label="Setpoint AC")

ax.set_title("Evolución de la Temperatura en el Tiempo")
ax.set_xlabel("Tiempo (Minutos)")
ax.set_ylabel("Temperatura (°C)")
ax.set_ylim(15, max(temp_ext + 2, max(temperaturas) + 1))
ax.grid(True, linestyle=":", alpha=0.6)
ax.legend()

st.pyplot(fig)