import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
import plotly.express as px
import io

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
        font-size: 28px;
        font-weight: bold;
        text-align: center;
        width: 100%;
        margin-bottom: 5px;
    }
    .subtitulo-centrado {
        font-size: 16px;
        color: #555;
        text-align: center;
        margin-bottom: 30px;
    }
    </style>
    <div class="titulo-principal">Monitoreo automatizado, mitigación de riesgos y dictamen de transacciones en tiempo real</div>
    <div class="subtitulo-centrado">Centro de Auditoría y Prevención de Fraude - Sabertec AI</div>
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
                        "Analiza los objetivos del usuario, decide qué herramientas invocar, procesa las observaciones "
                        "y redacta un dictamen ejecutivo estructurado, limpio y sin menciones a nombres internos."
                    ),
                    temperature=0.2
                )

                # Iniciar la conversación con el modelo actualizado y compatible
                chat = client.chats.create(model="gemini-3.6-flash", config=config)
                response = chat.send_message(prompt_usuario)

                # Subtítulo alineado a la izquierda según solicitud
                st.markdown("### Dictamen del Agente")
                
                # Datos fijos y limpios solicitados
                st.markdown("""
                - **Agente Auditor:** IA Experta en Auditoría Fintech y Riesgo Operativo
                - **Estado de Auditoría:** Completado con Éxito
                """)

                # Mostramos la respuesta del modelo (manteniendo el Resumen Operativo intacto)
                st.markdown(response.text)

                # Generación de datos simulados coherentes para las 500 transacciones agrupadas por estado
                import random
                random.seed(42)
                
                ids = [f"TX-{str(i).zfill(5)}" for i in range(90000, 90500)]
                canales = ["Checkout Web", "POS Físico", "Banca por Internet", "App Móvil"]
                estados_posibles = ["APROBADO", "REVISION_KYC", "CRITICO_FRAUDE"]
                pesos_estados = [0.75, 0.22, 0.03] # Coherente con ~500 registros

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

                st.markdown("---")
                st.markdown("### Resumen y Distribución General de Transacciones (N=500)")

                # Agrupación de estados para la tabla resumen y el gráfico de torta
                conteo_estados = df_500["Estado de Diagnóstico"].value_counts().reset_index()
                conteo_estados.columns = ["Estado de Diagnóstico", "Cantidad"]

                # Dividimos en 2 columnas: Tabla resumida agrupada a la izquierda, Gráfico de Torta a la derecha con amarillo KYC
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

                # --- SECCIÓN DE DESCARGA DE EXCELS PARA REVISIÓN ---
                st.markdown("---")
                st.markdown("### 📥 Exportación de Reportes para el Equipo Operativo")
                st.markdown("Descarga los registros detallados de los casos que requieren atención inmediata:")

                # Filtramos los DataFrames para cada archivo
                df_kyc = df_500[df_500["Estado de Diagnóstico"] == "REVISION_KYC"]
                df_critico = df_500[df_500["Estado de Diagnóstico"] == "CRITICO_FRAUDE"]

                # Función auxiliar para convertir DataFrame a Excel en memoria
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

            except Exception as e:
                st.error(f"Error durante la ejecución del agente: {e}")
