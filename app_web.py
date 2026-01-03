import streamlit as st
import pandas as pd
from PIL import Image
import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
import io

# =============================================================================
# CONFIGURACIÓN INICIAL
# =============================================================================
st.set_page_config(page_title="Sistema Fiscal", page_icon="📊", layout="wide")

# Estilos CSS Personalizados
st.markdown("""
    <style>
    .stButton>button {
        background-color: #922B21;
        color: white; 
        font-weight: bold;
        border-radius: 5px;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.1rem;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# TABLA ISR
TABLA_DEFAULT = """0.01, 0.00, 1.92
7735.01, 148.51, 6.40
65651.08, 3855.14, 10.88
115375.91, 9265.20, 16.00
134119.42, 12264.16, 17.92
160577.66, 17005.47, 21.36
323862.01, 51883.01, 23.52
510451.01, 95768.74, 30.00
974535.04, 234993.95, 32.00
1299380.05, 338944.34, 34.00
3898140.13, 1222522.76, 35.00"""

# BASE DE DATOS USUARIOS
USERS_DB = {"admin": "1234", "miguel": "smm"}

# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================
def calcular_isr_pf(base, tabla_texto):
    try:
        li, cf, pct = 0.0, 0.0, 0.0
        for linea in tabla_texto.split('\n'):
            datos = linea.split(',')
            if len(datos) < 3: continue
            limite = float(datos[0])
            if base >= limite:
                li, cf, pct = limite, float(datos[1]), float(datos[2])
            else:
                break
        return ((base - li) * (pct / 100)) + cf
    except: return 0.0

def generar_pdf_en_memoria(texto, cliente, autor):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Logo Empresa (logo_smm.png)
    if os.path.exists("logo_smm.png"):
        try:
            logo = ImageReader("logo_smm.png")
            c.drawImage(logo, 50, height - 120, width=120, height=80, mask='auto', preserveAspectRatio=True)
        except: pass

    # Encabezado
    c.setFont("Helvetica-Bold", 14)
    # Limpiamos un poco el nombre para que no quede tan largo en el título si tiene RFC
    titulo_cliente = cliente[:40] + "..." if len(cliente) > 40 else cliente
    c.drawString(200, height - 50, f"REPORTE FISCAL: {titulo_cliente}")
    
    c.setFont("Helvetica", 10)
    c.drawString(450, height - 70, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}")
    
    # Cuerpo
    c.setFont("Courier", 11)
    text_object = c.beginText(50, height - 150)
    for line in texto.split('\n'):
        text_object.textLine(line)
    c.drawText(text_object)
    
    # Pie de página (Desarrollador)
    if os.path.exists("MSM.jpg"):
        try:
            logo_dev = ImageReader("MSM.jpg")
            c.drawImage(logo_dev, width - 80, 20, width=50, height=50, mask='auto', preserveAspectRatio=True)
        except: pass
    
    c.save()
    buffer.seek(0)
    return buffer

# =============================================================================
# LOGIN Y SESIÓN
# =============================================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = ""

def login():
    user = st.session_state.user_input
    pwd = st.session_state.pass_input
    if user in USERS_DB and pwd == USERS_DB[user]:
        st.session_state.logged_in = True
        st.session_state.usuario_actual = user 
    else:
        st.error("Usuario o contraseña incorrectos")

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<h2 style='text-align: center; color: #922B21;'>🔐 Acceso Web</h2>", unsafe_allow_html=True)
        
        if os.path.exists("logo_smm.png"):
            st.image("logo_smm.png", width=200)
        
        st.text_input("Usuario", key="user_input")
        st.text_input("Contraseña", type="password", key="pass_input")
        st.button("Iniciar Sesión", on_click=login, use_container_width=True)
        
        st.markdown("---")
        if os.path.exists("MSM.jpg"):
            st.image("MSM.jpg", width=60)
            st.caption("Desarrollado por DR. MSM")
            
    st.stop()

# =============================================================================
# SISTEMA PRINCIPAL
# =============================================================================

# --- SIDEBAR ---
with st.sidebar:
    if os.path.exists("logo_smm.png"):
        st.image("logo_smm.png", width=180)
        
    st.write(f"**Usuario:** {st.session_state.usuario_actual}")
    st.markdown("---")
    
    # SELECCIÓN DE CLIENTE
    cliente_opcion = st.selectbox("Cliente Actual", ["CLIENTE GENERAL", "NUEVO CLIENTE..."])
    
    # LÓGICA PARA NUEVO CLIENTE (CON RFC)
    if cliente_opcion == "NUEVO CLIENTE...":
        cliente_nombre = st.text_input("Nombre / Razón Social:", placeholder="Ej: Empresa S.A. de C.V.")
        cliente_rfc = st.text_input("RFC:", placeholder="XAXX010101000")
        
        if cliente_nombre:
            if cliente_rfc:
                # Si pone RFC, lo unimos al nombre: "Empresa (RFC)"
                cliente = f"{cliente_nombre} ({cliente_rfc})"
            else:
                cliente = cliente_nombre
        else:
            cliente = "SIN NOMBRE"
    else:
        cliente = cliente_opcion # Usamos "CLIENTE GENERAL"

    mes = st.selectbox("Mes", ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC'])
    regimen = st.selectbox("Régimen", ['RÉGIMEN GENERAL PM', 'RESICO PM', 'PERSONA FÍSICA'])
    
    st.markdown("---")
    if st.button("Cerrar Sesión"):
        st.session_state.logged_in = False
        st.session_state.usuario_actual = ""
        st.rerun()

# --- TÍTULO ---
st.markdown(f"<h1 style='color:#922B21'>SISTEMA FISCAL | {mes}</h1>", unsafe_allow_html=True)

# Confirmación visual del cliente activo
if cliente_opcion == "NUEVO CLIENTE..." and cliente_nombre:
    st.info(f"📁 Trabajando con: **{cliente}**")

# --- PESTAÑAS ---
pestanas = st.tabs(["1. ISR / IVA", "2. Retenciones", "3. Nómina", "4. Concentrado", "5. Anual", "6. Reportes", "Configuración"])

# VARIABLES DE SESIÓN
if 'total_isr' not in st.session_state: st.session_state.total_isr = 0.0
if 'total_iva' not in st.session_state: st.session_state.total_iva = 0.0
if 'total_ret' not in st.session_state: st.session_state.total_ret = 0.0
if 'total_isn' not in st.session_state: st.session_state.total_isn = 0.0
if 'resumen_texto' not in st.session_state: st.session_state.resumen_texto = ""

# -----------------------------------------------------------------------------
# 1. ISR / IVA
# -----------------------------------------------------------------------------
with pestanas[0]:
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("A. ISR Propio")
        ingresos = st.number_input("Ingresos Facturados:", min_value=0.0)
        anticipos = st.number_input("Anticipos Clientes:", min_value=0.0)
        coef = st.number_input("Coeficiente Utilidad:", min_value=0.0, format="%.4f")
        ptu = st.number_input("PTU Pagada:", min_value=0.0)
        perdidas = st.number_input("Pérdidas Fiscales:", min_value=0.0)
        
    with col_b:
        st.subheader("Deducciones y Pagos")
        gastos = st.number_input("Gastos / Deducciones Autorizadas:", min_value=0.0)
        pagos_prov = st.number_input("Pagos Provisionales Anteriores:", min_value=0.0)
        ret_banc = st.number_input("Retención Bancaria:", min_value=0.0)
        ret_otras = st.number_input("Otras Retenciones (10% / 1.25%):", min_value=0.0)

    st.markdown("---")
    st.subheader("B. IVA Propio")
    col_c, col_d = st.columns(2)
    with col_c:
        iva_imp = st.number_input("IVA Importación:", min_value=0.0)
        iva_ret_cte = st.number_input("IVA Retenido por Clientes:", min_value=0.0)
    with col_d:
        iva_fav = st.number_input("IVA a Favor Anterior:", min_value=0.0)
        iva_comp = st.number_input("Compensaciones:", min_value=0.0)

# -----------------------------------------------------------------------------
# 2. RETENCIONES
# -----------------------------------------------------------------------------
with pestanas[1]:
    st.subheader("C. Retenciones a Terceros")
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        r_iva = st.number_input("Retención IVA (Monto):", min_value=0.0)
        r_isr_serv = st.number_input("Retención ISR Serv. Prof.:", min_value=0.0)
    with col_r2:
        r_sueldos = st.number_input("Retención ISR Sueldos:", min_value=0.0)
        r_cedular = st.number_input("Retención Cedular:", min_value=0.0)

# -----------------------------------------------------------------------------
# 3. NÓMINA
# -----------------------------------------------------------------------------
with pestanas[2]:
    st.subheader("D. Nómina e ISN")
    trabajadores = st.number_input("Número de Trabajadores:", min_value=0, step=1)
    
    st.markdown("##### Percepciones")
    c_n1, c_n2 = st.columns(2)
    with c_n1:
        n_sueldos = st.number_input("Sueldos y Salarios:", min_value=0.0)
        n_bono1 = st.number_input("Bono Puntualidad:", min_value=0.0)
        n_bono2 = st.number_input("Bono Asistencia:", min_value=0.0)
    with c_n2:
        n_despensa = st.number_input("Despensa:", min_value=0.0)
        n_extra = st.number_input("Horas Extra / Premios:", min_value=0.0)
        n_otros = st.number_input("Aguinaldo / Prima / Vacaciones:", min_value=0.0)

# -----------------------------------------------------------------------------
# CÁLCULO GLOBAL
# -----------------------------------------------------------------------------
if st.button("🔄 CALCULAR TODO EL SISTEMA", type="primary", use_container_width=True):
    # 1. Nómina
    total_nomina = n_sueldos + n_bono1 + n_bono2 + n_despensa + n_extra + n_otros
    isn_pagar = total_nomina * 0.03
    
    # 2. ISR
    ing_total = ingresos + anticipos
    ret_total_propia = ret_banc + ret_otras
    
    base_isr = 0.0
    isr_causado = 0.0
    
    if "GENERAL" in regimen:
        utilidad = (ing_total * coef)
        base_isr = max(0, utilidad - ptu - perdidas)
        isr_causado = base_isr * 0.30
    elif "RESICO" in regimen:
        base_isr = max(0, ing_total - gastos - total_nomina - ptu - perdidas)
        isr_causado = base_isr * 0.30
    else: # Persona Física
        base_isr = max(0, ing_total - gastos - total_nomina - ptu - perdidas)
        isr_causado = calcular_isr_pf(base_isr, TABLA_DEFAULT)
        
    isr_pagar = max(0, isr_causado - pagos_prov - ret_total_propia)
    
    # 3. IVA
    iva_tras = ing_total * 0.16
    iva_acred = (gastos * 0.16) + iva_imp
    iva_cargo = iva_tras - iva_acred - iva_ret_cte
    iva_pagar = max(0, iva_cargo - iva_fav - iva_comp)
    
    # 4. Retenciones
    total_retenciones = r_iva + r_isr_serv + r_sueldos + r_cedular
    
    # Guardar en sesión
    st.session_state.total_isr = isr_pagar
    st.session_state.total_iva = iva_pagar
    st.session_state.total_ret = total_retenciones
    st.session_state.total_isn = isn_pagar
    
    # Generar Texto Reporte
    st.session_state.resumen_texto = f"""
    REPORTE FISCAL | {cliente} | {mes}
    -------------------------------------------
    1. ISR PROPIO:       ${isr_pagar:,.2f}
    2. IVA PROPIO:       ${iva_pagar:,.2f}
    3. ISN (3%):         ${isn_pagar:,.2f}
    4. RETENCIONES:      ${total_retenciones:,.2f}
    -------------------------------------------
    TOTAL A PAGAR:       ${(isr_pagar + iva_pagar + isn_pagar + total_retenciones):,.2f}
    -------------------------------------------
    Elaboró: {st.session_state.usuario_actual}
    """
    st.success("¡Cálculos actualizados correctamente!")

# -----------------------------------------------------------------------------
# 4. CONCENTRADO
# -----------------------------------------------------------------------------
with pestanas[3]:
    st.subheader("Resumen Ejecutivo")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("ISR A PAGAR", f"${st.session_state.total_isr:,.2f}")
    c2.metric("IVA A PAGAR", f"${st.session_state.total_iva:,.2f}")
    c3.metric("RETENCIONES", f"${st.session_state.total_ret:,.2f}")
    c4.metric("ISN (NÓMINA)", f"${st.session_state.total_isn:,.2f}")
    
    gran_total = st.session_state.total_isr + st.session_state.total_iva + st.session_state.total_ret + st.session_state.total_isn
    st.metric("GRAN TOTAL A PAGAR", f"${gran_total:,.2f}", delta="Mensual")

# -----------------------------------------------------------------------------
# 5. ANUAL
# -----------------------------------------------------------------------------
with pestanas[4]:
    st.subheader("Cálculo Anual Estimado")
    anu_ing = st.number_input("Ingresos Acumulados Anual:", min_value=0.0)
    anu_ded = st.number_input("Deducciones Anuales:", min_value=0.0)
    anu_pagos = st.number_input("Pagos Provisionales Efectuados:", min_value=0.0)
    
    if st.button("Calcular Anual"):
        anu_util = max(0, anu_ing - anu_ded)
        anu_isr = anu_util * 0.30
        anu_neto = max(0, anu_isr - anu_pagos)
        
        st.info(f"Utilidad Fiscal: ${anu_util:,.2f}")
        st.info(f"ISR Causado (30%): ${anu_isr:,.2f}")
        st.error(f"ISR A PAGAR ANUAL: ${anu_neto:,.2f}")

# -----------------------------------------------------------------------------
# 6. REPORTES
# -----------------------------------------------------------------------------
with pestanas[5]:
    st.subheader("Generación de Reporte PDF")
    notas = st.text_area("Notas Adicionales:", height=100)
    texto_final = st.session_state.resumen_texto + f"\nNOTAS: {notas}"
    
    if st.button("📄 Generar PDF"):
        pdf_file = generar_pdf_en_memoria(texto_final, cliente, st.session_state.usuario_actual)
        st.download_button(label="📥 Descargar Reporte PDF",
                           data=pdf_file,
                           file_name=f"Reporte_{cliente}_{mes}.pdf",
                           mime="application/pdf")

# -----------------------------------------------------------------------------
# 7. CONFIGURACIÓN (CON CARGA DE LOGO)
# -----------------------------------------------------------------------------
with pestanas[6]:
    st.subheader("Configuración del Sistema")
    
    # --- SECCIÓN NUEVA: SUBIR LOGO DE EMPRESA ---
    st.markdown("### 🏢 Logo de la Empresa")
    st.info("Sube aquí el logo que aparecerá en el Login y en los Reportes.")
    
    logo_file = st.file_uploader("Cargar imagen (PNG, JPG)", type=['png', 'jpg', 'jpeg'])
    
    if logo_file is not None:
        with open("logo_smm.png", "wb") as f:
            f.write(logo_file.getbuffer())
        st.success("✅ ¡Logo actualizado! Recarga la página para ver los cambios.")
        # Previsualización pequeña (150px)
        st.image(logo_file, width=150, caption="Nuevo Logo")
    
    st.markdown("---")
    st.text_area("Tabla ISR (Editable)", value=TABLA_DEFAULT, height=150)
    
    st.markdown("---")
    
    col_cred1, col_cred2 = st.columns([1, 4])
    with col_cred1:
        if os.path.exists("MSM.jpg"):
            st.image("MSM.jpg", width=120)
    with col_cred2:
        st.markdown("### Desarrollado por:")
        st.markdown("## DR. Miguel Sánchez Morales")
        st.caption("Sistema Fiscal Maestro Versión Web")