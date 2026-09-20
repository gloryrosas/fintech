import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
import plotly.express as px
import io
from datetime import datetime

# Configuración de la página de Streamlit
st.set_page_config(
    page_title="Sabertec AI: Auditoría Fintech",
    page_icon="🛡️",
    layout="wide"
)

# Estilo CSS para alinear el título principal centrado, en letra grande y que entre en una sola línea
st.markdown("""
    <style>
    .titulo-principal {
        font-size: 26px;
        font-weight: bold;
        text-align: center;
        width: 100%;
        margin-bottom: 30px;
    }
    </style>
    <div class="titulo-principal">DICTAMEN EJECUTIVO DE AUDITORÍA Y PREVENCIÓN DE FRAUDE</div>
""", unsafe_allow_html=True)

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
    value="Audita 500 transacciones con un umbral de alerta de 75. Si encuentras operaciones críticas, procede a congelar preventivamente la primera detectada y preséntame el dictamen ejecutivo estructurado.",
    height=130
)

run_agent = st.sidebar.button("🚀 Ejecutar Auditoría Inteligente")

# Inicializamos el estado en la sesión si no existe
if "df_500" not in st.session_state:
    st.session_state.df_500 = None
if "response_text" not in st.session_state:
    st.session_state.response_text = None
if "fecha_actual" not in st.session_state:
    st.session_state.fecha_actual = None

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
                        "Eres un sistema experto en auditoría fintech y prevención de fraude. "
                        "Analiza los objetivos del usuario, decide qué herramientas invocar y procesa las observaciones. "
                        "IMPORTANTE: Redacta únicamente el cuerpo del dictamen (comenzando directamente por '1. Resumen Ejecutivo'). "
                        "NO incluyas títulos principales, subtítulos repetidos, ni fechas de emisión en tu texto, ya que la interfaz se encarga de mostrarlos de forma independiente."
                    ),
                    temperature=0.2
                )

                # Iniciar la conversación con el modelo actualizado y compatible
                chat = client.chats.create(model="gemini-3.6-flash", config=config)
                response = chat.send_message(prompt_usuario)

                st.session_state.response_text = response.text
                
                # Generar la fecha actual formateada en español
                meses = {
                    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
                    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
                }
                ahora = datetime.now()
                st.session_state.fecha_actual = f"{ahora.day} de {meses[ahora.month]} de {ahora.year}"

                import random
                random.seed(42)
                
                ids = [f"TX-{str(i).zfill(5)}" for i in range(90000, 90500)]
                canales = ["Checkout Web", "POS Físico", "Banca por Internet", "App Móvil"]
                estados_posibles = ["APROBADO", "REVISION_KYC", "CRITICO_FRAUDE"]
                pesos_estados = [0.75, 0.22, 0.03]

                lista_transacciones = []
                for i in range(500):
                    est = random.choices(estados_posibles, weights=pesos_estados)[0]
                    lista_transacciones.append({
                        "ID Transacción": ids[i],
                        "Canal": random.choice(canales),
                        "Monto (USD)": round(random.uniform(50.0, 9000.0), 2),
                        "Score de Riesgo": round(random.uniform(10.0, 95.0), 1) if est != "CRITICO_FRAUDE" else round(random.uniform(76.0, 99.9), 1),
                        "Estado de Diagnóstico": est
                    })

                df_500 = pd.DataFrame(lista_transacciones)
                df_500.loc[df_500["Estado de Diagnóstico"] == "CRITICO_FRAUDE", "ID Transacción"].iloc[0] = "TX-CRIT-001"
                
                st.session_state.df_500 = df_500

            except Exception as e:
                error_str = str(e)
                if "503" in error_str or "UNAVAILABLE" in error_str:
                    st.warning("⚠️ El servicio de IA está experimentando alta demanda en este momento (Error 503). Por favor, espera unos segundos y vuelve a hacer clic en 'Ejecutar Auditoría Inteligente'.")
                else:
                    st.error(f"Error durante la ejecución del agente: {e}")

# Renderizado de la interfaz si ya existen datos en memoria (session_state)
if st.session_state.df_500 is not None:
    # Subtítulo alineado a la izquierda según solicitud
    st.markdown("### Dictamen del Agente")
    
    st.markdown(f"""
    - **Agente Auditor:** IA Experta en Auditoría Fintech y Riesgo Operativo
    - **Estado de Auditoría:** Completado con Éxito
    - **Fecha de Emisión:** {st.session_state.fecha_actual}
    - **Alcance:** Monitoreo y Análisis de Riesgo transaccional
    """)

    st.markdown(st.session_state.response_text)

    st.markdown("---")
    st.markdown("### Resumen y Distribución General de Transacciones (N=500)")

    conteo_estados = st.session_state.df_500["Estado de Diagnóstico"].value_counts().reset_index()
    conteo_estados.columns = ["Estado de Diagnóstico", "Cantidad"]

    col_tabla, col_grafico = st.columns([1.2, 0.8])

    with col_tabla:
        st.subheader("📋 Consolidado por Estado")
        st.dataframe(conteo_estados, use_container_width=True)

    with col_grafico:
        st.subheader("Distribución de Transacciones Auditadas")
        fig = px.pie(
            conteo_estados, 
            names='Estado de Diagnóstico', 
            values='Cantidad', 
            hole=0.4, 
            color='Estado de Diagnóstico',
            color_discrete_map={
                "APROBADO": "#27ae60",         # Verde
                "REVISION_KYC": "#f39c12",     # Amarillo corporativo (KYC)
                "CRITICO_FRAUDE": "#e74c3c"    # Rojo de alerta crítica
            }
        )
        fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=300)
        st.plotly_chart(fig, use_container_width=True)

    # --- SECCIÓN DE DESCARGA DE EXCELS SIN REINICIAR ---
    st.markdown("---")
    st.markdown("### 📥 Exportación de Reportes para el Equipo Operativo")
    st.markdown("Descarga los registros detallados de los casos que requieren atención inmediata:")

    df_kyc = st.session_state.df_500[st.session_state.df_500["Estado de Diagnóstico"] == "REVISION_KYC"]
    df_critico = st.session_state.df_500[st.session_state.df_500["Estado de Diagnóstico"] == "CRITICO_FRAUDE"]

    def convertir_a_excel(df):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Transacciones')
        processed_data = output.getvalue()
        return processed_data

    col_excel1, col_excel2 = st.columns(2)

    with col_excel1:
        excel_kyc_data = convertir_a_excel(df_kyc)
        st.download_button(
            label="📥 Descargar Excel: Revisiones KYC (Amarillo)",
            data=excel_kyc_data,
            file_name="transacciones_revision_kyc.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    with col_excel2:
        excel_critico_data = convertir_a_excel(df_critico)
        st.download_button(
            label="📥 Descargar Excel: Críticos por Fraude (Rojo)",
            data=excel_critico_data,
            file_name="transacciones_criticas_fraude.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
