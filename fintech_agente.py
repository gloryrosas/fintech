import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
import plotly.express as px

# Configuración de la página de Streamlit
st.set_page_config(
    page_title="Sabertec AI: Agente Autónomo Fintech",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Sabertec AI: Agente Autónomo con Function Calling (Gemini)")
st.markdown("Demostración del Bucle de Control: Percibir ➔ Decidir (LLM) ➔ Actuar (Tools) ➔ Observar")

# Verificamos si la librería genai está disponible
HAS_GENAI = True

# Definición de Herramientas (Tools / Functions)
def auditar_transacciones_fintech(limite: int = 500, umbral_alerta: int = 75) -> dict:
    """Simula la auditoría de un lote de transacciones financieras y retorna métricas clave."""
    return {
        "total_auditadas": limite,
        "umbral_aplicado": umbral_alerta,
        "alertas_detectadas": 12,
        "estado": "Completado con éxito"
    }

def congelar_cuenta_riesgo(tx_id: str) -> dict:
    """Congela preventivamente una cuenta asociada a una transacción de alto riesgo."""
    return {
        "transaccion_afectada": tx_id,
        "estado": "CONGELADA_PREVENTIVAMENTE",
        "mensaje": "Se ha bloqueado la operación de forma exitosa."
    }

# Configuración en Sidebar
st.sidebar.header("⚙️ Configuración del Agente")
prompt_usuario = st.sidebar.text_area(
    "💬 Objetivo del Agente:",
    value="Audita 500 transacciones con un umbral de alerta de 75. Si encuentras operaciones críticas, procede a congelar preventivamente la primera detectada y preséntame el dictamen en una tabla detallada junto con un gráfico de distribución.",
    height=130
)

run_agent = st.sidebar.button("🚀 Iniciar Bucle Autónomo")

if run_agent:
    if not HAS_GENAI:
        st.error("⚠️ La librería `google-genai` no está instalada o configurada correctamente.")
    else:
        with st.spinner("🤖 El agente está procesando el bucle de razonamiento y llamadas a herramientas..."):
            try:
                # Inicializar cliente de Google GenAI usando el secreto de Streamlit
                client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

                # Configuración del motor con las funciones inyectadas como herramientas
                config = types.GenerateContentConfig(
                    tools=[auditar_transacciones_fintech, congelar_cuenta_riesgo],
                    system_instruction=(
                        "Eres Pulso, un agente de IA experto en auditoría fintech y prevención de fraude. "
                        "Analiza los objetivos del usuario, decide qué herramientas invocar, procesa las observaciones "
                        "y redacta un dictamen ejecutivo estructurado."
                    ),
                    temperature=0.2
                )

                # Iniciar la conversación con el modelo actualizado y compatible
                chat = client.chats.create(model="gemini-3.6-flash", config=config)
                response = chat.send_message(prompt_usuario)

                # Mostramos la respuesta generada por el agente
                st.markdown("### 📋 Dictamen del Agente")
                st.markdown(response.text)

                # Simulación de un DataFrame representativo para la tabla y el gráfico de torta
                data_ejemplo = {
                    "ID Transacción": ["TX-90000", "TX-90001", "TX-90002", "TX-90003", "TX-90004"],
                    "Canal": ["Checkout Web", "POS Físico", "Banca por Internet", "App Móvil", "Banca por Internet"],
                    "Monto (USD)": [3192.97, 8081.81, 6225.97, 5094.62, 1338.82],
                    "Score de Riesgo": [70.6, 55.4, 34.1, 81.5, 69.4],
                    "Estado de Diagnóstico": ["REVISION_KYC", "REVISION_KYC", "APROBADO", "CRITICO_FRAUDE", "REVISION_KYC"]
                }
                df = pd.DataFrame(data_ejemplo)

                st.markdown("---")
                st.markdown("### 2. Detalle de Muestra Representativa y Gráfico de Distribución")
                
                # Dividimos el espacio en 2 columnas: izquierda para la tabla, derecha para el gráfico de torta/dona
                col_tabla, col_grafico = st.columns([1.2, 0.8])

                with col_tabla:
                    st.subheader("📋 Tabla de Transacciones")
                    st.dataframe(df, use_container_width=True)

                with col_grafico:
                    st.subheader("📊 Distribución por Canal")
                    fig = px.pie(
                        df, 
                        names='Canal', 
                        values='Monto (USD)', 
                        hole=0.4, # Estilo dona moderno
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300)
                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"Error durante la ejecución del agente: {e}")
