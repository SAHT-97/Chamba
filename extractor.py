import pdfplumber
import re
import ppm

def es_libro_mayor(texto_pagina):
    if not texto_pagina: return False
    texto = texto_pagina.upper()
    palabras_clave = ["LIBRO MAYOR", "DEBE", "HABER", "SALDO", "CUENTA", "ANALISIS", "FICHA"]
    coincidencias = sum(1 for p in palabras_clave if p in texto)
    return coincidencias >= 2

def limpiar_monto_individual(texto_monto):
    try:
        if not texto_monto: return 0
        val_str = str(texto_monto).strip()
        val_str = val_str.replace('.', '').replace(',', '.').split('.')[0]
        val_str = re.sub(r'[^\d-]', '', val_str)
        if not val_str: return 0
        return int(val_str)
    except: return 0

# --- ESTRATEGIA PARA CONTALIVE / GENÉRICO ---
def extraer_datos_mayor(archivo):
    datos_archivo = []
    with pdfplumber.open(archivo) as pdf:
        for pagina in pdf.pages:
            tablas = pagina.extract_tables()
            for tabla in tablas:
                if not tabla: continue
                for fila in tabla:
                    fila_str = [str(c) if c else "" for c in fila]
                    if len(fila_str) < 5: continue
                    col_fecha, col_glosa, col_debe = fila_str[0], fila_str[3], fila_str[4]
                    fechas_encontradas = re.findall(r'\d{2}-\d{2}-\d{4}', col_fecha)
                    if not fechas_encontradas: continue
                    montos_raw = col_debe.split('\n')
                    glosas_raw = col_glosa.split('\n')
                    montos_limpios = [m for m in montos_raw if m.strip() != ""]
                    glosas_limpias = [g.strip() for g in glosas_raw if g.strip() != ""]
                    for i, fecha in enumerate(fechas_encontradas):
                        monto_txt = montos_limpios[i] if i < len(montos_limpios) else "0"
                        monto_val = limpiar_monto_individual(monto_txt)
                        if monto_val == 0: continue
                        detalle_txt = glosas_limpias[i] if i < len(glosas_limpias) else ""
                        
                        # LIMPIEZA ADICIONAL POR SI ACASO
                        detalle_txt = re.sub(r'^[A-Z]\s+\d+\s*', '', detalle_txt).strip()

                        mes_pago_inicial = ppm.calcular_mes_pago_inicial(fecha)
                        factor_inicial = None
                        if "-12-" in fecha:
                            factor_inicial = 0.0
                        else:
                            try:
                                from datetime import datetime
                                dt = datetime.strptime(fecha, "%d-%m-%Y")
                                if dt.day == 1 and dt.month == 1:
                                    mes_pago_inicial = "Sin Asignar"
                                    factor_inicial = None
                                else:
                                    factor_inicial = ppm.recalcular_factor_desde_texto(mes_pago_inicial)
                            except: pass
                        
                        datos_archivo.append({
                            "Seleccionar": True,
                            "FECHA": fecha,
                            "PPM": monto_val,
                            "DETALLE": detalle_txt,
                            "MES DE PAGO": mes_pago_inicial,
                            "FACTOR": factor_inicial,
                            "AJUSTE": 0,
                            "PPM ACTUALIZADO": 0
                        })
    return datos_archivo

# --- ESTRATEGIA PARA ICONTADOR ---
def extraer_datos_icontador(archivo):
    datos_archivo = []
    with pdfplumber.open(archivo) as pdf:
        for pagina in pdf.pages:
            settings = {
                "vertical_strategy": "text",
                "horizontal_strategy": "text",
                "snap_tolerance": 4,
            }
            tablas = pagina.extract_tables(table_settings=settings)
            for tabla in tablas:
                if not tabla: continue
                for fila in tabla:
                    fila_str = [str(c).strip() if c else "" for c in fila]
                    if len(fila_str) < 3: continue
                    
                    texto_inicio = " ".join(fila_str[:2])
                    fechas_encontradas = re.findall(r'\d{2}-\d{2}-\d{4}', texto_inicio)
                    if not fechas_encontradas: continue
                    fecha_valida = fechas_encontradas[0]
                    
                    try:
                        col_debe = fila_str[-3]
                        idx_debe = len(fila_str) - 3
                        
                        if idx_debe > 1:
                            col_glosa = " ".join(fila_str[1:idx_debe])
                        else:
                            col_glosa = fila_str[1]
                        
                        col_glosa = re.sub(r'^[A-Z]\s+\d+\s*', '', col_glosa).strip()

                    except IndexError:
                        continue 
                    
                    monto_val = limpiar_monto_individual(col_debe)
                    if monto_val == 0: continue
                    
                    mes_pago_inicial = ppm.calcular_mes_pago_inicial(fecha_valida)
                    factor_inicial = None
                    
                    if "-12-" in fecha_valida:
                        factor_inicial = 0.0
                    else:
                        try:
                            from datetime import datetime
                            dt = datetime.strptime(fecha_valida, "%d-%m-%Y")
                            if dt.day == 1 and dt.month == 1 and "APERTURA" in col_glosa.upper(): 
                                mes_pago_inicial = "Sin Asignar"
                                factor_inicial = None
                            else:
                                factor_inicial = ppm.recalcular_factor_desde_texto(mes_pago_inicial)
                        except: pass
                    
                    datos_archivo.append({
                        "Seleccionar": True,
                        "FECHA": fecha_valida,
                        "PPM": monto_val,
                        "DETALLE": col_glosa.replace('\n', ' '),
                        "MES DE PAGO": mes_pago_inicial,
                        "FACTOR": factor_inicial,
                        "AJUSTE": 0,
                        "PPM ACTUALIZADO": 0
                    })
    return datos_archivo