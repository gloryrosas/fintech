import streamlit as st
import pandas as pd
import numpy as np
import io

# Importación segura de la API oficial de Google GenAI
try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

st.set_page_config(
    page_title="Sabertec AI - Agente Autónomo Fintech",
    page_icon="🤖",
    layout="wide"
)

st.markdown("""
    <style>
    .main-title { font-size: 28px; font-weight: bold; color: #0F172A; }
    .sub-title { font-size: 16px; color: #475569; margin-bottom: 20px; }
    .agent-log { background-color: #0F172A; color: #38BDF8; padding: 15px; border-radius: 8px; font-family: monospace; font-size: 13px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">🤖 Sabertec AI: Agente Autónomo con Function Calling (Gemini)</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Demostración del Bucle de Control: Percibir ➔ Decidir (LLM) ➔ Actuar (Tools) ➔ Observar</p>', unsafe_allow_html=True)

# ==========================================
# 1. DEFINICIÓN DE HERRAMIENTAS (LAS MANOS)
# ==========================================
def auditar_transacciones_fintech(num_registros: int, umbral_alerta: int) -> dict:
    """
    Simula la consulta a la pasarela de pagos y base de datos para extraer transacciones y calcular riesgos.
    
    Args:
        num_registros: Cantidad de transacciones a auditar en el lote.
        umbral_alerta: Nivel de score a partir del cual se considera riesgo crítico de fraude.
    """
    np.random.seed(42)
    canales = ["App Móvil", "API Gateway", "POS Físico", "Checkout Web", "Banca por Internet"]
    
    df = pd.DataFrame({
        "Tx_ID": [f"TX-{90000 + i}" for i in range(num_registros)],
        "Monto_USD": np.round(np.random.uniform(15.0, 8500.0, num_registros), 2),
        "Score_Riesgo": np.round(np.random.uniform(5, 99, num_registros), 1),
        "Canal": np.random.choice(canales, num_registros),
    })
    
    df["Estatus"] = np.where(df["Score_Riesgo"] > umbral_alerta, "CRITICO_FRAUDE", 
                   np.where(df["Score_Riesgo"] > 45, "REVISION_KYC", "APROBADO"))
    
    criticos = df[df["Estatus"] == "CRITICO_FRAUDE"]
    
    return {
        "total_analizadas": int(num_registros),
        "operaciones_criticas": int(len(criticos)),
        "monto_total_en_riesgo": float(criticos["Monto_USD"].sum()),
        "detalle_muestra": df.head(5).to_dict(orient="records")
    }

def congelar_cuenta_riesgo(tx_id: str) -> dict:
    """
    Ejecuta una acción de escritura para bloquear preventivamente la cuenta asociada a una transacción fraudulenta.
    
    Args:
        tx_id: Identificador único de la transacción crítica a congelar.
    """
    # Acción simulada con efecto secundario de seguridad
    return {
        "estatus_accion": "EJECUTADA_CON_EXITO",
        "transaccion": tx_id,
        "mensaje": f"La cuenta y pasarela asociadas a {tx_id} han sido bloqueadas preventivamente."
    }

# Mapeador de funciones disponibles para el agente
herramientas_disponibles = {
    "auditar_transacciones_fintech": auditar_transacciones_fintech,
    "congelar_cuenta_riesgo": congelar_cuenta_riesgo
}

# Configuración en Sidebar
st.sidebar.header("⚙️ Configuración del Agente")
prompt_usuario = st.sidebar.text_area(
    "💬 Objetivo del Agente:",
    value="Audita 500 transacciones con un umbral de alerta de 75. Si encuentras operaciones críticas, procede a congelar preventivamente la primera detectada y preséntame el dictamen ejecutivo.",
    height=130
)

run_agent = st.sidebar.button("🚀 Iniciar Bucle Autónomo")

if run_agent:
    if not HAS_GENAI:
        st.error("⚠️ La librería `google-genai` no está instalada o configurada correctamente.")
    else:
        with st.spinner("🤖 El agente está procesando el bucle de razonamiento y llamadas a herramientas..."):
            try:
                # Inicializar cliente de Google GenAI (requiere GEMINI_API_KEY en variables de entorno)
               client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
                
                # Configuración del motor con las funciones inyectadas como herramientas
                config = types.GenerateContentConfig(
                   tools=[auditar_transacciones_fintech, congelar_cuenta_riesgo],
                   system_instruction=(
                        "Eres Pulso, un agente de IA experto en auditoría fintech y prevención de fraude. "
                        "Analiza los objetivos del usuario, decide qué herramientas invocar, procesa las observaciones "
                        "y redacta un dictamen ejecutivo estructurado en Markdown."
                    ),
                    temperature=0.2
                )
                
                # Iniciar la conversación con el objetivo del usuario
                chat = client.chats.create(model="gemini-2.5-flash", config=config)
                response = chat.send_message(prompt_usuario)
                
                log_logs = []
                
                # ==========================================
                # 2. BUCLE AUTÓNOMO (AGENTIC LOOP)
                # ==========================================
                # El agente evalúa si necesita llamar a funciones de forma iterativa
                while response.function_calls:
                    for function_call in response.function_calls:
                        nombre_fn = function_call.name
                        args_fn = function_call.args
                        
                        log_logs.append(f"🛠️ [DECISIÓN DEL LLM] Invocando herramienta: `{nombre_fn}` con argumentos: {args_fn}")
                        
                        # Ejecutar la función localmente (Las Manos)
                        if nombre_fn in herramientas_disponibles:
                            resultado_fn = herramientas_disponibles[nombre_fn](**args_fn)
                        else:
                            resultado_fn = {"error": "Herramienta no encontrada"}
                            
                        log_logs.append(f"👁️ [OBSERVACIÓN] Resultado obtenido: {resultado_fn}")
                        
                        # Devolver el resultado al modelo para que continúe el ciclo (Observar ➔ Decidir)
                        response = chat.send_message(
                            types.Part.from_function_response(
                                name=nombre_fn,
                                response={"result": resultado_fn}
                            )
                        )
                
                # Mostrar traza técnica del bucle
                st.markdown("### 🔍 Traza del Bucle Autónomo (Agentic Loop)")
                for log in log_logs:
                    st.markdown(f'<div class="agent-log">{log}</div>', unsafe_allow_html=True)
                    
                st.markdown("---")
                st.markdown("### 📋 Dictamen Final del Agente")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"❌ Error durante la ejecución del agente: {e}")
else:
    st.info("👉 Configura tu objetivo en la barra lateral y haz clic en **'Iniciar Bucle Autónomo'** para ver al agente operar de forma dinámica.")
