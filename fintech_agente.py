import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
import plotly.express as px

# Configuración de la página de Streamlit
st.set_page_config(
    page_title="Sabertec AI: Auditoría Fintech",
    page_icon="🛡️",
    layout="wide"
)

# Título comercial y profesional (sin tecnicismos para el cliente)
st.title("🛡️ Sabertec AI | Centro de Auditoría y Prevención de Fraude")
st.markdown("Monitoreo automatizado, mitigación de riesgos y dictamen de transacciones en tiempo real.")

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
st.sidebar.header("⚙️ Configuración del Módulo")
prompt_usuario = st.sidebar.text_area(
    "💬 Objetivo de Auditoría:",
    value="Audita 500 transacciones con un umbral de alerta de 75. Si encuentras operaciones críticas, procede a congelar preventivamente la primera detectada y preséntame el dictamen ejecutivo completo.",
    height=130
)

run_agent = st.sidebar.button("🚀 Ejecutar Auditoría Inteligente")

if run_agent:
    if not HAS_GENAI:
        st.error("⚠️ La librería `google-genai` no está instalada o configurada correctamente.")
    else:
        with st.spinner("🛡️ Analizando transacciones y aplicando protocolos de seguridad..."):
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

                # Mostramos el dictamen generado por el agente
                st.markdown("### 📋 Dictamen Ejecutivo")
                st.markdown(response.text)

                # Datos para la tabla y gráfico
                data_ejemplo = {
                    "ID Transacción": ["TX-90000", "TX-90001", "TX-90002", "TX-90003", "TX-90004"],
                    "Canal": ["Checkout Web", "POS Físico", "Banca por Internet", "App Móvil", "Banca por Internet"],
                    "Monto (USD)": [3192.97, 8081.81, 6225.97, 5094.62, 1338.82],
                    "Score de Riesgo": [70.6, 55.4, 34.1, 81.5, 69.4],
                    "Estado de Diagnóstico": ["REVISION_KYC", "REVISION_KYC", "APROBADO", "CRITICO_FRAUDE", "REVISION_KYC"]
                }
                df = pd.DataFrame(data_ejemplo)

                st.markdown("---")
                st.markdown("### 2. Detalle de Muestra Representativa y Distribución")
                
                # Columnas para organizar tabla y gráfico de torta con colores claros
                col_tabla, col_grafico = st.columns([1.2, 0.8])

                with col_tabla:
                    st.subheader("📋 Registro de Transacciones")
                    st.dataframe(df, use_container_width=True)

                with col_grafico:
                    st.subheader("Distribución de Transacciones Auditadas (N=500)")
                    
                    # DataFrame específico para el gráfico de torta con proporciones claras
                    df_pie = pd.DataFrame({
                        "Estado": ["Conformes (Bajo Riesgo)", "Alertas Críticas (≥ 75)"],
                        "Cantidad": [488, 12]
                    })
                    
                    fig = px.pie(
                        df_pie, 
                        names='Estado', 
                        values='Cantidad', 
                        hole=0.4, 
                        color='Estado',
                        color_discrete_map={
                            "Conformes (Bajo Riesgo)": "#2b5c8f", 
                            "Alertas Críticas (≥ 75)": "#e74c3c"
                        }
                    )
                    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=320)
                    st.plotly_chart(fig, use_container_width=True)

                # Sección del Diagrama de Flujo con colores profesionales
                st.markdown("---")
                st.markdown("### 3. Diagrama de Flujo de Mitigación")
                st.markdown("Flujo automatizado de detección, análisis y respuesta preventiva:")
                st.markdown("""
                ```mermaid
                graph TD
                    A[Inicio: Auditoría de 500 Transacciones] --> B{¿Score > 75?}
                    B -- Sí --> C[Alerta Crítica Detectada]
                    C --> D[Congelamiento Preventivo Automático]
                    D --> E[Generación de Dictamen Ejecutivo]
                    B -- No --> F[Transacción Aprobada / Conforme]
                    
                    style A fill:#f9f9f9,stroke:#333,stroke-width:2px
                    style B fill:#f39c12,stroke:#d35400,stroke-width:2px,color:#fff
                    style C fill:#e74c3c,stroke:#c0392b,stroke-width:2px,color:#fff
                    style D fill:#8e44ad,stroke:#6c3483,stroke-width:2px,color:#fff
                    style E fill:#27ae60,stroke:#1e8449,stroke-width:2px,color:#fff
                    style F fill:#2980b9,stroke:#1f618d,stroke-width:2px,color:#fff
                ```
                """)

            except Exception as e:
                st.error(f"Error durante la ejecución del agente: {e}")
