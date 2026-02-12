import streamlit as st
import pandas as pd
import io
import base64
from pathlib import Path
from decimal import Decimal
import pdfplumber 

# IMPORTACIÓN DE MÓDULOS PROPIOS
import extractor
import ppm

# ==========================================
# 1. CONFIGURACIÓN INICIAL Y CARGA DE RECURSOS
# ==========================================
# Nota: 'favicon.ico' debe estar en la misma carpeta que app.py
st.set_page_config(
    page_title="Calculadora PPM - Libro Mayor", 
    page_icon="favicon.ico", 
    layout="wide",
    initial_sidebar_state="expanded"
)

def cargar_css(file_name):
    try:
        with open(file_name, encoding='utf-8') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"⚠️ No se encontró el archivo {file_name}.")
    except Exception as e:
        st.error(f"Error al cargar CSS: {e}")

# ==========================================
# 2. FUNCIONES LÓGICAS
# ==========================================
def asegurar_tipos(df):
    """Normaliza los tipos de datos para asegurar cálculos correctos."""
    if df is None or df.empty:
        return df
    
    df = df.copy()
    
    if "Seleccionar" in df.columns:
        df["Seleccionar"] = df["Seleccionar"].fillna(True).astype(bool)
    
    for col in ["PPM", "AJUSTE", "PPM ACTUALIZADO"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
            
    if "FACTOR" in df.columns:
        df["FACTOR"] = pd.to_numeric(df["FACTOR"], errors='coerce')
        
    return df

# ==========================================
# 3. FUNCIÓN PRINCIPAL
# ==========================================
def main():
    cargar_css("style.css")

    # --- SIDEBAR (Con Logo Nuevo) ---
    with st.sidebar:
        # Intentamos cargar el logo lateral. Si no existe, no muestra error.
        try:
            st.image("Logo-B.png", use_container_width=True)
        except:
            st.markdown("## 📊 PPM Calculator")

        st.markdown("---")
        st.markdown("### 📂 Configuración")
        
        origen_datos = st.radio(
            "Formato del Software:",
            ["ContaLive", "IContador"], 
            help="Selecciona el software de origen."
        )
        
        st.write("") # Espacio
        st.markdown("### 📂 **Cargar el Mayor de la Cuenta PPM**")
        uploaded_files = st.file_uploader("Cargar Documentos", type="pdf", accept_multiple_files=True)
        st.write("") 
        boton_procesar = st.button("PROCESAR ARCHIVOS", use_container_width=True)

    # --- HERO SECTION (Título Principal) ---
    # Usamos el logo favicon también aquí si se desea, o un emoji
    st.markdown(f"""
        <div class="hero-card">
            <div class="hero-text">
                <h1>Cálculo PPM</h1>
                <p>Herramienta especializada para el cálculo de PPM y Reajustes desde Libro Mayor</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- ESTADO INICIAL ---
    if "df_mayor" not in st.session_state: 
        st.session_state.df_mayor = None

    # --- PROCESAMIENTO ---
    if uploaded_files and boton_procesar:
        lista_mayor = []
        bar_progreso = st.progress(0)
        
        with st.spinner("Analizando documentos..."):
            for i, archivo in enumerate(uploaded_files):
                try:
                    if origen_datos == "ContaLive":
                        with pdfplumber.open(archivo) as pdf:
                            texto_inicio = pdf.pages[0].extract_text() or ""
                        if extractor.es_libro_mayor(texto_inicio):
                            datos = extractor.extraer_datos_mayor(archivo)
                            lista_mayor.extend(datos)
                        else:
                            st.warning(f"Archivo {archivo.name}: Formato no válido para ContaLive.")

                    elif origen_datos == "IContador":
                        datos = extractor.extraer_datos_icontador(archivo)
                        if datos:
                            lista_mayor.extend(datos)
                        else:
                            st.warning(f"Archivo {archivo.name}: No se extrajeron datos IContador.")
                        
                except Exception as e:
                    st.error(f"Error {archivo.name}: {str(e)}")
                
                bar_progreso.progress((i + 1) / len(uploaded_files))
            
            bar_progreso.empty()
            
            if lista_mayor:
                df_m = pd.DataFrame(lista_mayor)
                
                # Normalizar nombres
                if "Mes Periodo" in df_m.columns:
                    df_m = df_m.rename(columns={
                        "Mes Periodo": "FECHA", "Detalle": "DETALLE", 
                        "Monto Historico": "PPM", "Mes de pago": "MES DE PAGO",
                        "Factor": "FACTOR", "Actualizacion": "AJUSTE", 
                        "PPM ACTUALIZADO": "PPM ACTUALIZADO"
                    })

                cols_orden = ["Seleccionar", "FECHA", "DETALLE", "PPM", "MES DE PAGO", 
                              "FACTOR", "AJUSTE", "PPM ACTUALIZADO"]
                
                for col in cols_orden:
                    if col not in df_m.columns: df_m[col] = None
                
                df_m = df_m[cols_orden].reset_index(drop=True)
                st.session_state.df_mayor = asegurar_tipos(df_m)
            else:
                st.error("No se encontraron datos válidos.")

    # --- VISUALIZACIÓN ---
    if st.session_state.df_mayor is not None:
        opciones_meses = ppm.generar_opciones_mes_pago()
        
        num_filas = len(st.session_state.df_mayor)
        altura_dinamica = (num_filas + 1) * 35 + 3
        
        # 1. RENDERIZAR EDITOR (Sin format en montos para permitir comas)
        df_editado = st.data_editor(
            st.session_state.df_mayor,
            key="editor_mayor",
            height=altura_dinamica,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Seleccionar": st.column_config.CheckboxColumn("✅", width="small", default=True),
                "FECHA": st.column_config.TextColumn("Fecha", disabled=True),
                "DETALLE": st.column_config.TextColumn("Detalle", disabled=True),
                
                "PPM": st.column_config.NumberColumn("PPM ($)", step=1), 
                "MES DE PAGO": st.column_config.SelectboxColumn("Mes de Pago", options=opciones_meses),
                "FACTOR": st.column_config.NumberColumn("Factor", format="%.3f", disabled=True),
                "AJUSTE": st.column_config.NumberColumn("Ajuste ($)", disabled=True),
                "PPM ACTUALIZADO": st.column_config.NumberColumn("PPM Actualizado ($)", disabled=True)
            }
        )

        st.warning("⚠️ **IMPORTANTE:** Selecciona solo los Periodos de Enero a Diciembre del AT (Año Tributario).")
        
        # 2. CÁLCULOS
        cambios_detectados = False
        
        if not df_editado.empty:
            try:
                nuevo_factor = df_editado.apply(
                    lambda row: Decimal(0) if "-12-" in str(row["FECHA"]) 
                    else ppm.recalcular_factor_desde_texto(row["MES DE PAGO"]), 
                    axis=1
                ).astype(float)
                
                df_editado["FACTOR"] = nuevo_factor

                nuevo_ajuste = df_editado.apply(
                    lambda row: ppm.calcular_monto_actualizacion(
                        float(row["PPM"]), 
                        float(row["FACTOR"]) if pd.notnull(row["FACTOR"]) else 0.0
                    ), 
                    axis=1
                ).fillna(0).astype(int)
                
                df_editado["AJUSTE"] = nuevo_ajuste

                nuevo_total = (df_editado["PPM"] + df_editado["AJUSTE"]).fillna(0).astype(int)
                df_editado["PPM ACTUALIZADO"] = nuevo_total

                df_editado_seguro = asegurar_tipos(df_editado)
                
                if not df_editado_seguro.equals(st.session_state.df_mayor):
                    st.session_state.df_mayor = df_editado_seguro
                    cambios_detectados = True

            except Exception:
                pass

        # 3. TOTALES
        df_seleccionados = df_editado[df_editado["Seleccionar"] == True]
        
        total_historico = df_seleccionados["PPM"].sum()
        total_reajuste = df_seleccionados["AJUSTE"].sum()
        total_actualizado = df_seleccionados["PPM ACTUALIZADO"].sum()

        st.divider()
        col_t1, col_t2, col_t3 = st.columns(3)
        
        with col_t1: st.metric("TOTAL PPM (Histórico)", f"$ {total_historico:,.0f}")
        with col_t2: st.metric("TOTAL REAJUSTE", f"$ {total_reajuste:,.0f}")
        with col_t3: st.metric("TOTAL PPM ACTUALIZADO", f"$ {total_actualizado:,.0f}")

        # 4. EXPORTACIÓN
        buffer_m = io.BytesIO()
        with pd.ExcelWriter(buffer_m) as writer:
            df_export = df_editado.copy()
            fila_total = {col: "" for col in df_export.columns}
            fila_total["FECHA"] = "TOTALES (Seleccionados)"
            fila_total["PPM"] = total_historico
            fila_total["AJUSTE"] = total_reajuste
            fila_total["PPM ACTUALIZADO"] = total_actualizado
            df_export = pd.concat([df_export, pd.DataFrame([fila_total])], ignore_index=True)
            df_export.to_excel(writer, index=False)
        
        st.write("")
        st.download_button("📥 Descargar Excel Mayor", buffer_m.getvalue(), "Libro_Mayor_Final.xlsx", type="primary")

        if cambios_detectados:
            st.rerun()

    else:
        st.markdown("""
            <div style="background-color: white; padding: 40px; border-radius: 12px; border: 2px dashed #4b6cb7; text-align: center; margin-top: 2rem;">
                <h3 style="color: #64748B;">Esperando archivos...</h3>
                <p style="color: #94A3B8;">Selecciona el formato y sube tu Libro Mayor en PDF.</p>
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()