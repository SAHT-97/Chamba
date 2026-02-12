import pandas as pd
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

# ==========================================
# 1. BASE DE DATOS DE FACTORES
# ==========================================
_data_factores = [
    # AÑO 2025
    {"Mes": 1, "Anio": 2025, "Porcentaje": "3,6 %"},
    {"Mes": 2, "Anio": 2025, "Porcentaje": "2,6 %"},
    {"Mes": 3, "Anio": 2025, "Porcentaje": "2,2 %"},
    {"Mes": 4, "Anio": 2025, "Porcentaje": "1,6 %"},
    {"Mes": 5, "Anio": 2025, "Porcentaje": "1,4 %"},
    {"Mes": 6, "Anio": 2025, "Porcentaje": "1,2 %"},
    {"Mes": 7, "Anio": 2025, "Porcentaje": "1,7 %"},
    {"Mes": 8, "Anio": 2025, "Porcentaje": "0,8 %"},
    {"Mes": 9, "Anio": 2025, "Porcentaje": "0,7 %"},
    {"Mes": 10, "Anio": 2025, "Porcentaje": "0,3 %"},
    {"Mes": 11, "Anio": 2025, "Porcentaje": "0,3 %"},
    {"Mes": 12, "Anio": 2025, "Porcentaje": "0,0 %"},
    # AÑO 2024
    {"Mes": 1, "Anio": 2024, "Porcentaje": "4,7 %"},
    {"Mes": 2, "Anio": 2024, "Porcentaje": "4,0 %"},
    {"Mes": 3, "Anio": 2024, "Porcentaje": "3,4 %"},
    {"Mes": 4, "Anio": 2024, "Porcentaje": "3,0 %"},
    {"Mes": 5, "Anio": 2024, "Porcentaje": "2,5 %"},
    {"Mes": 6, "Anio": 2024, "Porcentaje": "2,2 %"},
    {"Mes": 7, "Anio": 2024, "Porcentaje": "2,3 %"},
    {"Mes": 8, "Anio": 2024, "Porcentaje": "1,6 %"},
    {"Mes": 9, "Anio": 2024, "Porcentaje": "1,3 %"},
    {"Mes": 10, "Anio": 2024, "Porcentaje": "1,2 %"},
    {"Mes": 11, "Anio": 2024, "Porcentaje": "0,3 %"},
    {"Mes": 12, "Anio": 2024, "Porcentaje": "0,0 %"},
    # AÑO 2023
    {"Mes": 1, "Anio": 2023, "Porcentaje": "4,5 %"},
    {"Mes": 2, "Anio": 2023, "Porcentaje": "3,7 %"},
    {"Mes": 3, "Anio": 2023, "Porcentaje": "3,7 %"},
    {"Mes": 4, "Anio": 2023, "Porcentaje": "2,6 %"},
    {"Mes": 5, "Anio": 2023, "Porcentaje": "2,3 %"},
    {"Mes": 6, "Anio": 2023, "Porcentaje": "2,2 %"},
    {"Mes": 7, "Anio": 2023, "Porcentaje": "2,3 %"},
    {"Mes": 8, "Anio": 2023, "Porcentaje": "2,0 %"},
    {"Mes": 9, "Anio": 2023, "Porcentaje": "1,9 %"},
    {"Mes": 10, "Anio": 2023, "Porcentaje": "1,2 %"},
    {"Mes": 11, "Anio": 2023, "Porcentaje": "0,7 %"},
    {"Mes": 12, "Anio": 2023, "Porcentaje": "0,0 %"},
    # AÑO 2022
    {"Mes": 1, "Anio": 2022, "Porcentaje": "12,5 %"},
    {"Mes": 2, "Anio": 2022, "Porcentaje": "11,1 %"},
    {"Mes": 3, "Anio": 2022, "Porcentaje": "10,8 %"},
    {"Mes": 4, "Anio": 2022, "Porcentaje": "8,8 %"},
    {"Mes": 5, "Anio": 2022, "Porcentaje": "7,3 %"},
    {"Mes": 6, "Anio": 2022, "Porcentaje": "6,0 %"},
    {"Mes": 7, "Anio": 2022, "Porcentaje": "5,0 %"},
    {"Mes": 8, "Anio": 2022, "Porcentaje": "3,6 %"},
    {"Mes": 9, "Anio": 2022, "Porcentaje": "2,4 %"},
    {"Mes": 10, "Anio": 2022, "Porcentaje": "1,5 %"},
    {"Mes": 11, "Anio": 2022, "Porcentaje": "1,0 %"},
    {"Mes": 12, "Anio": 2022, "Porcentaje": "0,0 %"},
    # AÑO 2020
    {"Mes": 1, "Anio": 2020, "Porcentaje": "2,6 %"},
    {"Mes": 2, "Anio": 2020, "Porcentaje": "2,1 %"},
    {"Mes": 3, "Anio": 2020, "Porcentaje": "1,6 %"},
    {"Mes": 4, "Anio": 2020, "Porcentaje": "1,3 %"},
    {"Mes": 5, "Anio": 2020, "Porcentaje": "1,3 %"},
    {"Mes": 6, "Anio": 2020, "Porcentaje": "1,4 %"},
    {"Mes": 7, "Anio": 2020, "Porcentaje": "1,4 %"},
    {"Mes": 8, "Anio": 2020, "Porcentaje": "1,3 %"},
    {"Mes": 9, "Anio": 2020, "Porcentaje": "1,2 %"},
    {"Mes": 10, "Anio": 2020, "Porcentaje": "0,5 %"},
    {"Mes": 11, "Anio": 2020, "Porcentaje": "-0,1 %"},
    {"Mes": 12, "Anio": 2020, "Porcentaje": "0,0 %"},
]

factores_act = pd.DataFrame(_data_factores)

# ==========================================
# 2. MAPEOS Y UTILIDADES
# ==========================================
MAPA_ABREVIATURAS = {
    1: "ENE", 2: "FEB", 3: "MAR", 4: "ABR", 
    5: "MAY", 6: "JUN", 7: "JUL", 8: "AGO", 
    9: "SEP", 10: "OCT", 11: "NOV", 12: "DIC"
}

MAPA_ABR_INVERSO = {v: k for k, v in MAPA_ABREVIATURAS.items()}

def generar_opciones_mes_pago():
    opciones = ["Sin Asignar"]
    df_sorted = factores_act.sort_values(by=['Anio', 'Mes'], ascending=[False, False])
    for _, row in df_sorted.iterrows():
        mes_abr = MAPA_ABREVIATURAS.get(row['Mes'], "UNK")
        anio = row['Anio']
        opciones.append(f"{mes_abr}-{anio}")
    return opciones

def calcular_mes_pago_inicial(fecha_str):
    try:
        dt = datetime.strptime(fecha_str, "%d-%m-%Y")
        if dt.day == 1 and dt.month == 1:
            mes_pago = 1
            anio_pago = dt.year
        else:
            mes_pago = dt.month + 1
            anio_pago = dt.year
            if mes_pago > 12:
                mes_pago = 1
                anio_pago += 1
        mes_abr = MAPA_ABREVIATURAS.get(mes_pago, "ENE")
        return f"{mes_abr}-{anio_pago}"
    except:
        return "Sin Asignar"

def convertir_porcentaje_a_factor(porcentaje_str):
    try:
        limpio = porcentaje_str.replace('%', '').replace(',', '.').strip()
        valor = float(limpio)
        factor = 1 + (valor / 100)
        # Regla: Factor mínimo 1.0 (Deflación no baja PPM)
        if factor < 1.0: return 1.0
        return round(factor, 3)
    except:
        return None

def recalcular_factor_desde_texto(texto_mes_pago):
    if not texto_mes_pago or texto_mes_pago == "Sin Asignar":
        return None
    try:
        partes = texto_mes_pago.split('-')
        if len(partes) != 2: return None
        
        mes_txt, anio_txt = partes[0], partes[1]
        mes_num = MAPA_ABR_INVERSO.get(mes_txt)
        anio_num = int(anio_txt)
        
        if not mes_num: return None
        
        filtro = (factores_act['Mes'] == mes_num) & (factores_act['Anio'] == anio_num)
        if filtro.any():
            pct_str = factores_act.loc[filtro, 'Porcentaje'].values[0]
            return convertir_porcentaje_a_factor(pct_str)
        return None
    except:
        return None

# ==========================================
# 3. CÁLCULO ESTÁNDAR (SIMPLE)
# ==========================================

def calcular_monto_actualizacion(monto_historico, factor):
    """
    Calcula el ajuste.
    Requerimiento: Calcular (Monto * Factor) y redondear matemáticamente al entero más cercano.
    Luego restar el monto histórico para obtener el ajuste.
    """
    if not factor or factor <= 1 or not monto_historico:
        return 0
    try:
        # Convertir a Decimal usando string para evitar imprecisiones de flotantes
        m = Decimal(str(monto_historico))
        f = Decimal(str(factor))
        
        # Calcular monto total actualizado y aplicar redondeo matemático (0.5 sube)
        monto_actualizado = (m * f).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        
        # El ajuste es la diferencia
        ajuste = monto_actualizado - m
        
        return int(ajuste)
    except:
        return 0

def calcular_ppm_actualizado(monto_historico, actualizacion):
    return (monto_historico or 0) + (actualizacion or 0)
