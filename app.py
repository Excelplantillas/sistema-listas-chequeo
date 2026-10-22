import streamlit as st
from fpdf import FPDF
import tempfile
import os

# Configuración inicial de la página
st.set_page_config(
    page_title="Sistema de Gestión y Búsqueda",
    page_icon="📋",
    layout="centered"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        color: #1f4e78;
        font-weight: 700;
        margin-bottom: 20px;
    }
    .subtitle {
        text-align: center;
        color: #595959;
        margin-bottom: 30px;
    }
    .stButton>button {
        width: 100%;
        background-color: #2e75b6;
        color: white;
        font-size: 16px;
        font-weight: bold;
        padding: 12px;
        border-radius: 8px;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #1f4e78;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Inicializar estado de autenticación y navegación
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if "menu_actual" not in st.session_state:
    st.session_state.menu_actual = "inicio"

if "form_valido" not in st.session_state:
    st.session_state.form_valido = False

if "pdf_path" not in st.session_state:
    st.session_state.pdf_path = None

if "nombre_archivo_pdf" not in st.session_state:
    st.session_state.nombre_archivo_pdf = "reporte.pdf"

def cambiar_seccion(seccion):
    st.session_state.menu_actual = seccion
    st.session_state.form_valido = False

# --- PANTALLA DE ACCESO (CONTRASEÑA) ---
if not st.session_state.autenticado:
    if os.path.exists("logo.png"):
        col_logo_l, col_logo_r = st.columns([1, 4])
        with col_logo_l:
            st.image("logo.png", width=120)
            
    st.markdown("<h1 class='main-title'>Acceso al Sistema de Control</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Por favor, digite la contraseña para continuar:</p>", unsafe_allow_html=True)
    
    _, col_centro, _ = st.columns([1, 2, 1])
    with col_centro:
        with st.form("form_login"):
            password = st.text_input("Contraseña:", type="password", placeholder="Ingrese la contraseña...")
            btn_login = st.form_submit_button("Ingresar al Sistema")
            
            if btn_login:
                if password == "Archivo123":
                    st.session_state.autenticado = True
                    st.success("¡Acceso concedido!")
                    st.rerun()
                else:
                    st.error("❌ Contraseña incorrecta. Intente nuevamente.")

# --- MENÚ PRINCIPAL (Una vez autenticado) ---
elif st.session_state.menu_actual == "inicio":
    if os.path.exists("logo.png"):
        col_logo, col_espacio = st.columns([1, 4])
        with col_logo:
            st.image("logo.png", width=120)
            
    st.markdown("<h1 class='main-title'>Sistema de Control y Búsqueda</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Seleccione el módulo al que desea ingresar:</p>", unsafe_allow_html=True)
    
    _, col_centro, _ = st.columns([1, 2, 1])
    with col_centro:
        if st.button("📁 BÚSQUEDA DE EXPEDIENTES"):
            cambiar_seccion("expedientes")
            st.rerun()
            
        st.write("")
        if st.button("🏢 BÚSQUEDA DE TRÁMITES EN SEDE"):
            cambiar_seccion("sede")
            st.rerun()
            
        st.write("")
        if st.button("🗄️ BÚSQUEDA DE TRÁMITES EN ARCHIVO"):
            cambiar_seccion("archivo")
            st.rerun()
            
        st.write("")
        if st.button("🔒 Cerrar Sesión"):
            st.session_state.autenticado = False
            st.rerun()

# --- MÓDULO 1: BÚSQUEDA DE EXPEDIENTES (23 Preguntas) ---
elif st.session_state.menu_actual == "expedientes":
    if st.button("⬅ Volver al Menú Principal"):
        cambiar_seccion("inicio")
        st.rerun()
        
    st.markdown("<h2 class='main-title'>Lista de Chequeo - Búsqueda de Expedientes</h2>", unsafe_allow_html=True)
    
    etapas_exp = [
        ("ETAPA 1 - VALIDACIÓN DE DATOS", [
            ("1. Placa verificada en formato correcto", "e1_p1"),
            ("2. Verificación de estado del automotor (Activo u otro)", "e1_p2")
        ]),
        ("ETAPA 2 - CONTROLES DE ARCHIVO", [
            ("3. Inventario físico revisado", "e2_p3"),
            ("4. Registro histórico por placa", "e2_p4"),
            ("5. Registro de préstamos verificado", "e2_p5"),
            ("6. Búsqueda de escaneos recientes", "e2_p6")
        ]),
        ("ETAPA 3 - BÚSQUEDA FÍSICA DIRECTA", [
            ("7. Estantería correcta revisada", "e3_p7"),
            ("8. Expedientes contiguos revisados (Formato Cruz)", "e3_p8")
        ]),
        ("ETAPA 4 - BÚSQUEDA POR VARIACIONES", [
            ("9. Letras y números similares", "e4_p9"),
            ("10. Placas con una letra diferente", "e4_p10"),
            ("11. Placas con un número diferente", "e4_p11"),
            ("12. Placas con cambio letra/número similar (O-0, 1-I, B-8)", "e4_p12"),
            ("13. Rango alfabético inmediato (antes y después)", "e4_p13")
        ]),
        ("ETAPA 5 - BÚSQUEDA POR SEMANA DEL TRÁMITE", [
            ("14. Expedientes archivados por fecha y no por placa", "e5_p14")
        ]),
        ("ETAPA 6 - ENVIADOS EN CONTENEDORES", [
            ("15. Contenedores recibidos a partir de la fecha (2 semanas)", "e6_p15"),
            ("16. Error de digitación del contenedor", "e6_p16"),
            ("17. Expediente en caja equivocada", "e6_p17")
        ]),
        ("ETAPA 7 - BÚSQUEDA POR ANALISTA", [
            ("18. Trámites gestionados por el mismo analista", "e7_p18"),
            ("19. Carpetas físicas del analista", "e7_p19"),
            ("20. Bandejas / archivo temporal del analista", "e7_p20"),
            ("21. Confirmación directa con el analista", "e7_p21")
        ]),
        ("ETAPA 8 - BÚSQUEDA FINAL", [
            ("22. Búsqueda en el rango de la placa", "e8_p22"),
            ("23. Búsqueda en el rango siguiente de la placa", "e8_p23")
        ])
    ]
    
    with st.form("form_expedientes"):
        st.subheader("Información General")
        col_a, col_b = st.columns(2)
        with col_a:
            identificador = st.text_input("Identificador:")
            placa = st.text_input("Placa (Este texto será el nombre del PDF):")
            area = st.text_input("Área solicitante:")
        with col_b:
            expediente_doc = st.text_input("Expediente / Documento:")
            responsable = st.text_input("Responsable de búsqueda:")
            fecha = st.date_input("Fecha:")
            
        st.divider()
        st.subheader("Cuestionario de Verificación (23 Preguntas)")
        
        respuestas = {}
        observaciones = {}
        
        for nombre_etapa, lista_preguntas in etapas_exp:
            st.markdown(f"### **{nombre_etapa}**")
            for texto_pregunta, key in lista_preguntas:
                st.markdown(f"**{texto_pregunta}**")
                respuestas[key] = st.radio("Opción:", ["-- Seleccione --", "Sí", "No"], key=f"r_{key}", label_visibility="collapsed", horizontal=True)
                observaciones[key] = st.text_input(f"Observaciones {key}", key=f"obs_{key}", placeholder="Observaciones opcionales...", label_visibility="collapsed")
                st.write("---")

        submit_btn = st.form_submit_button("Validar y Generar PDF de Expedientes")
        
        if submit_btn:
            if not placa.strip():
                st.error("⚠️ El campo 'Placa' es obligatorio ya que será el nombre del archivo PDF.")
                st.session_state.form_valido = False
            else:
                todas_preguntas = [item for _, lista in etapas_exp for item in lista]
                sin_responder = [p[0] for p, k in zip(todas_preguntas, [i[1] for i in todas_preguntas]) if respuestas[k] == "-- Seleccione --"]
                
                if sin_responder:
                    st.error(f"⚠️ Faltan preguntas por responder. Debes completar las 23 preguntas. (Pendientes: {len(sin_responder)})")
                    st.session_state.form_valido = False
                else:
                    placa_limpia = placa.strip().upper().replace(" ", "_")
                    nombre_pdf = f"{placa_limpia}.pdf"
                    
                    pdf = FPDF(orientation='P', unit='mm', format='A4')
                    pdf.add_page()
                    pdf.set_auto_page_break(auto=True, margin=15)
                    
                    pdf.set_font("Arial", "B", 12)
                    pdf.set_text_color(31, 78, 120)
                    pdf.cell(0, 8, "LISTA DE CHEQUEO - BUSQUEDA DE EXPEDIENTES", 0, 1, "C")
                    pdf.ln(3)
                    
                    pdf.set_font("Arial", "B", 9)
                    pdf.set_text_color(0, 0, 0)
                    pdf.cell(95, 6, f"Identificador: {identificador}", 0, 0)
                    pdf.cell(95, 6, f"Expediente / Documento: {expediente_doc}", 0, 1)
                    pdf.cell(95, 6, f"Placa: {placa.strip().upper()}", 0, 0)
                    pdf.cell(95, 6, f"Responsable de Busqueda: {responsable}", 0, 1)
                    pdf.cell(95, 6, f"Area Solicitante: {area}", 0, 0)
                    pdf.cell(95, 6, f"Fecha: {fecha}", 0, 1)
                    pdf.ln(5)
                    
                    item_contador = 1
                    for nombre_etapa, lista_preguntas in etapas_exp:
                        etapa_limpia = nombre_etapa.encode('latin-1', 'ignore').decode('latin-1')
                        pdf.set_font("Arial", "B", 9)
                        pdf.set_fill_color(220, 230, 242)
                        pdf.cell(190, 6, etapa_limpia, 1, 1, "L", True)
                        
                        pdf.set_font("Arial", "B", 8)
                        pdf.set_fill_color(240, 240, 240)
                        pdf.cell(10, 6, "ITEM", 1, 0, "C", True)
                        pdf.cell(100, 6, "ACTIVIDAD", 1, 0, "C", True)
                        pdf.cell(10, 6, "SI", 1, 0, "C", True)
                        pdf.cell(10, 6, "NO", 1, 0, "C", True)
                        pdf.cell(60, 6, "OBSERVACIONES", 1, 1, "C", True)
                        
                        pdf.set_font("Arial", "", 8)
                        for texto_p, k in lista_preguntas:
                            resp = respuestas[k]
                            obs = observaciones[k] if observaciones[k] else ""
                            
                            marca_si = "X" if resp == "Sí" else ""
                            marca_no = "X" if resp == "No" else ""
                            
                            texto_limpio = texto_p.split(". ", 1)[1] if ". " in texto_p else texto_p
                            texto_limpio = texto_limpio.encode('latin-1', 'ignore').decode('latin-1')
                            obs_limpia = obs.encode('latin-1', 'ignore').decode('latin-1')
                            
                            pdf.cell(10, 6, str(item_contador), 1, 0, "C")
                            pdf.cell(100, 6, texto_limpio, 1, 0, "L")
                            pdf.cell(10, 6, marca_si, 1, 0, "C")
                            pdf.cell(10, 6, marca_no, 1, 0, "C")
                            pdf.cell(60, 6, obs_limpia, 1, 1, "L")
                            
                            item_contador += 1
                        pdf.ln(2)
                    
                    temp_dir = tempfile.gettempdir()
                    pdf_path = os.path.join(temp_dir, nombre_pdf)
                    pdf.output(pdf_path)
                    
                    st.session_state.pdf_path = pdf_path
                    st.session_state.nombre_archivo_pdf = nombre_pdf
                    st.session_state.form_valido = True
                    st.success("¡Validación exitosa! PDF de Expedientes generado correctamente.")

    if st.session_state.form_valido and st.session_state.pdf_path:
        st.divider()
        with open(st.session_state.pdf_path, "rb") as f:
            pdf_bytes = f.read()
        st.download_button(
            label=f"📥 Descargar PDF: {st.session_state.nombre_archivo_pdf}",
            data=pdf_bytes,
            file_name=st.session_state.nombre_archivo_pdf,
            mime="application/pdf"
        )


# --- MÓDULO 2: BÚSQUEDA DE TRÁMITES EN SEDE (15 Preguntas) ---
elif st.session_state.menu_actual == "sede":
    if st.button("⬅ Volver al Menú Principal"):
        cambiar_seccion("inicio")
        st.rerun()
        
    st.markdown("<h2 class='main-title'>Lista de Chequeo - Búsqueda de Trámites en Sede</h2>", unsafe_allow_html=True)
    
    etapas_sede = [
        ("ETAPA 1 - VALIDACIÓN DE DATOS", [
            ("1. Placa verificada en formato correcto", "sede_e1_p1"),
            ("2. Verificación de estado del automotor (Activo u otro que afecte la información física)", "sede_e1_p2")
        ]),
        ("ETAPA 2 - CONTROLES DE ARCHIVO", [
            ("3. Registro histórico por placa", "sede_e2_p3"),
            ("4. Búsqueda de escaneos recientes", "sede_e2_p4")
        ]),
        ("ETAPA 3 - ENVIADOS EN CONTENEDORES (ARCHIVO)", [
            ("5. Contenedores recibido a partir de la fecha del trámite (Contar dos semana)", "sede_e3_p5"),
            ("6. Contenedor pendiente de apertura", "sede_e3_p6"),
            ("7. Error de digitación del contenedor", "sede_e3_p7")
        ]),
        ("ETAPA 4 - BÚSQUEDA POR SEMANA DEL TRÁMITE (SEDE)", [
            ("8. Trámites realizados a partir de la fecha del trámite (Contar dos semana)", "sede_e4_p8"),
            ("9. Remisión al archivo de listado de trámites contando dos semanas a partir de la fecha del trámite para busqueda", "sede_e4_p9"),
            ("10. Error de digitación del contenedor", "sede_e4_p10"),
            ("11. Revisión de planillas de mensajería, confirmar recibido", "sede_e4_p11"),
            ("12. Remisión al archivo de listado de trámites recibidos en mensajería, contando dos semanas a partir de la fecha del trámite para busqueda", "sede_e4_p12")
        ]),
        ("ETAPA 5 - BÚSQUEDA POR ANALISTA", [
            ("13. Trámites gestionados por el mismo analista a partir de la fecha del trámite (Contar dos semana)", "sede_e5_p13"),
            ("14. Documentos físicos del analista", "sede_e5_p14"),
            ("15. Confirmación directa con el analista", "sede_e5_p15")
        ])
    ]
    
    with st.form("form_sede"):
        st.subheader("Información General")
        col_a, col_b = st.columns(2)
        with col_a:
            identificador_sede = st.text_input("Identificador:")
            placa_sede = st.text_input("Placa (Este texto será el nombre del PDF):")
            area_sede = st.text_input("Área solicitante:")
        with col_b:
            expediente_sede = st.text_input("Expediente / Documento:")
            responsable_sede = st.text_input("Responsable de búsqueda:")
            fecha_sede = st.date_input("Fecha:")
            
        st.divider()
        st.subheader("Cuestionario de Verificación - Trámites en Sede (15 Preguntas)")
        
        respuestas_sede = {}
        obs_sede = {}
        
        for nombre_etapa, lista_preguntas in etapas_sede:
            st.markdown(f"### **{nombre_etapa}**")
            for texto_pregunta, key in lista_preguntas:
                st.markdown(f"**{texto_pregunta}**")
                respuestas_sede[key] = st.radio("Opción:", ["-- Seleccione --", "Sí", "No"], key=f"r_{key}", label_visibility="collapsed", horizontal=True)
                obs_sede[key] = st.text_input(f"Observaciones {key}", key=f"obs_{key}", placeholder="Observaciones opcionales...", label_visibility="collapsed")
                st.write("---")

        submit_sede = st.form_submit_button("Validar y Generar PDF de Sede")
        
        if submit_sede:
            if not placa_sede.strip():
                st.error("⚠️ El campo 'Placa' es obligatorio ya que será el nombre del archivo PDF.")
                st.session_state.form_valido = False
            else:
                todas_p_sede = [item for _, lista in etapas_sede for item in lista]
                sin_resp_sede = [p[0] for p, k in zip(todas_p_sede, [i[1] for i in todas_p_sede]) if respuestas_sede[k] == "-- Seleccione --"]
                
                if sin_resp_sede:
                    st.error(f"⚠️ Faltan preguntas por responder. Debes completar las 15 preguntas. (Pendientes: {len(sin_resp_sede)})")
                    st.session_state.form_valido = False
                else:
                    placa_limpia = placa_sede.strip().upper().replace(" ", "_")
                    nombre_pdf = f"{placa_limpia}.pdf"
                    
                    pdf = FPDF(orientation='P', unit='mm', format='A4')
                    pdf.add_page()
                    pdf.set_auto_page_break(auto=True, margin=15)
                    
                    pdf.set_font("Arial", "B", 12)
                    pdf.set_text_color(31, 78, 120)
                    pdf.cell(0, 8, "LISTA DE CHEQUEO - BUSQUEDA DE TRAMITES EN SEDE", 0, 1, "C")
                    pdf.ln(3)
                    
                    pdf.set_font("Arial", "B", 9)
                    pdf.set_text_color(0, 0, 0)
                    pdf.cell(95, 6, f"Identificador: {identificador_sede}", 0, 0)
                    pdf.cell(95, 6, f"Expediente / Documento: {expediente_sede}", 0, 1)
                    pdf.cell(95, 6, f"Placa: {placa_sede.strip().upper()}", 0, 0)
                    pdf.cell(95, 6, f"Responsable de Busqueda: {responsable_sede}", 0, 1)
                    pdf.cell(95, 6, f"Area Solicitante: {area_sede}", 0, 0)
                    pdf.cell(95, 6, f"Fecha: {fecha_sede}", 0, 1)
                    pdf.ln(5)
                    
                    item_contador = 1
                    for nombre_etapa, lista_preguntas in etapas_sede:
                        etapa_limpia = nombre_etapa.encode('latin-1', 'ignore').decode('latin-1')
                        pdf.set_font("Arial", "B", 9)
                        pdf.set_fill_color(220, 230, 242)
                        pdf.cell(190, 6, etapa_limpia, 1, 1, "L", True)
                        
                        pdf.set_font("Arial", "B", 8)
                        pdf.set_fill_color(240, 240, 240)
                        pdf.cell(10, 6, "ITEM", 1, 0, "C", True)
                        pdf.cell(100, 6, "ACTIVIDAD", 1, 0, "C", True)
                        pdf.cell(10, 6, "SI", 1, 0, "C", True)
                        pdf.cell(10, 6, "NO", 1, 0, "C", True)
                        pdf.cell(60, 6, "OBSERVACIONES", 1, 1, "C", True)
                        
                        pdf.set_font("Arial", "", 8)
                        for texto_p, k in lista_preguntas:
                            resp = respuestas_sede[k]
                            obs = obs_sede[k] if obs_sede[k] else ""
                            
                            marca_si = "X" if resp == "Sí" else ""
                            marca_no = "X" if resp == "No" else ""
                            
                            texto_limpio = texto_p.split(". ", 1)[1] if ". " in texto_p else texto_p
                            texto_limpio = texto_limpio.encode('latin-1', 'ignore').decode('latin-1')
                            obs_limpia = obs.encode('latin-1', 'ignore').decode('latin-1')
                            
                            pdf.cell(10, 6, str(item_contador), 1, 0, "C")
                            pdf.cell(100, 6, texto_limpio, 1, 0, "L")
                            pdf.cell(10, 6, marca_si, 1, 0, "C")
                            pdf.cell(10, 6, marca_no, 1, 0, "C")
                            pdf.cell(60, 6, obs_limpia, 1, 1, "L")
                            
                            item_contador += 1
                        pdf.ln(2)
                    
                    temp_dir = tempfile.gettempdir()
                    pdf_path = os.path.join(temp_dir, nombre_pdf)
                    pdf.output(pdf_path)
                    
                    st.session_state.pdf_path = pdf_path
                    st.session_state.nombre_archivo_pdf = nombre_pdf
                    st.session_state.form_valido = True
                    st.success("¡Validación exitosa! PDF de Trámites en Sede generado correctamente.")

    if st.session_state.form_valido and st.session_state.pdf_path:
        st.divider()
        with open(st.session_state.pdf_path, "rb") as f:
            pdf_bytes = f.read()
        st.download_button(
            label=f"📥 Descargar PDF de Sede: {st.session_state.nombre_archivo_pdf}",
            data=pdf_bytes,
            file_name=st.session_state.nombre_archivo_pdf,
            mime="application/pdf"
        )


# --- MÓDULO 3: BÚSQUEDA DE TRÁMITES EN ARCHIVO (14 Preguntas) ---
elif st.session_state.menu_actual == "archivo":
    if st.button("⬅ Volver al Menú Principal"):
        cambiar_seccion("inicio")
        st.rerun()
        
    st.markdown("<h2 class='main-title'>Lista de Chequeo - Búsqueda de Trámites en Archivo</h2>", unsafe_allow_html=True)
    
    etapas_archivo = [
        ("ETAPA 1 - VALIDACIÓN DE DATOS", [
            ("1. Placa verificada en formato correcto", "arch_e1_p1"),
            ("2. Verificación de estado del automotor (Activo u otro que afecte la información física del expediente)", "arch_e1_p2")
        ]),
        ("ETAPA 2 - CONTROLES DE ARCHIVO", [
            ("3. Registro histórico por placa", "arch_e2_p3"),
            ("4. Busqueda de escaneos recientes", "arch_e2_p4")
        ]),
        ("ETAPA 3 - ENVIADOS EN CONTENEDORES (ARCHIVO)", [
            ("5. Contenedores recibido a partir de la fecha del trámite (Contar dos semana)", "arch_e3_p5"),
            ("6. Contenedor pendiente de apertura", "arch_e3_p6"),
            ("7. Error de digitación del contenedor", "arch_e3_p7")
        ]),
        ("ETAPA 4 - BÚSQUEDA POR SEMANA DEL TRÁMITE (SEDE)", [
            ("8. Trámites realizados a partir de la fecha del trámite (Contar dos semana)", "arch_e4_p8"),
            ("9. Revisión de listado de trámites contando dos semanas a partir de la fecha del trámite para busqueda", "arch_e4_p9"),
            ("10. Error de digitación del contenedor", "arch_e4_p10"),
            ("11. Remisión al archivo de listado de trámites recibidos en mensajería, contando dos semanas a partir de la fecha del trámite para busqueda", "arch_e4_p11")
        ]),
        ("ETAPA 5 - BÚSQUEDA POR ANALISTA", [
            ("12. Trámites gestionados por el mismo analista a partir de la fecha del trámite (Contar dos semana)", "arch_e5_p12"),
            ("13. Documentos físicos del analista", "arch_e5_p13"),
            ("14. Confirmación directa con el analista", "arch_e5_p14")
        ])
    ]
    
    with st.form("form_archivo"):
        st.subheader("Información General")
        col_a, col_b = st.columns(2)
        with col_a:
            identificador_arch = st.text_input("Identificador:")
            placa_arch = st.text_input("Placa (Este texto será el nombre del PDF):")
            area_arch = st.text_input("Área solicitante:")
        with col_b:
            expediente_arch = st.text_input("Expediente / Documento:")
            responsable_arch = st.text_input("Responsable de búsqueda:")
            fecha_arch = st.date_input("Fecha:")
            
        st.divider()
        st.subheader("Cuestionario de Verificación - Trámites en Archivo (14 Preguntas)")
        
        respuestas_arch = {}
        obs_arch = {}
        
        for nombre_etapa, lista_preguntas in etapas_archivo:
            st.markdown(f"### **{nombre_etapa}**")
            for texto_pregunta, key in lista_preguntas:
                st.markdown(f"**{texto_pregunta}**")
                respuestas_arch[key] = st.radio("Opción:", ["-- Seleccione --", "Sí", "No"], key=f"r_{key}", label_visibility="collapsed", horizontal=True)
                obs_arch[key] = st.text_input(f"Observaciones {key}", key=f"obs_{key}", placeholder="Observaciones opcionales...", label_visibility="collapsed")
                st.write("---")

        submit_arch = st.form_submit_button("Validar y Generar PDF de Archivo")
        
        if submit_arch:
            if not placa_arch.strip():
                st.error("⚠️ El campo 'Placa' es obligatorio ya que será el nombre del archivo PDF.")
                st.session_state.form_valido = False
            else:
                todas_p_arch = [item for _, lista in etapas_archivo for item in lista]
                sin_resp_arch = [p[0] for p, k in zip(todas_p_arch, [i[1] for i in todas_p_arch]) if respuestas_arch[k] == "-- Seleccione --"]
                
                if sin_resp_arch:
                    st.error(f"⚠️ Faltan preguntas por responder. Debes completar las 14 preguntas. (Pendientes: {len(sin_resp_arch)})")
                    st.session_state.form_valido = False
                else:
                    placa_limpia = placa_arch.strip().upper().replace(" ", "_")
                    nombre_pdf = f"{placa_limpia}.pdf"
                    
                    pdf = FPDF(orientation='P', unit='mm', format='A4')
                    pdf.add_page()
                    pdf.set_auto_page_break(auto=True, margin=15)
                    
                    pdf.set_font("Arial", "B", 12)
                    pdf.set_text_color(31, 78, 120)
                    pdf.cell(0, 8, "LISTA DE CHEQUEO - BUSQUEDA DE TRAMITES EN ARCHIVO", 0, 1, "C")
                    pdf.ln(3)
                    
                    pdf.set_font("Arial", "B", 9)
                    pdf.set_text_color(0, 0, 0)
                    pdf.cell(95, 6, f"Identificador: {identificador_arch}", 0, 0)
                    pdf.cell(95, 6, f"Expediente / Documento: {expediente_arch}", 0, 1)
                    pdf.cell(95, 6, f"Placa: {placa_arch.strip().upper()}", 0, 0)
                    pdf.cell(95, 6, f"Responsable de Busqueda: {responsable_arch}", 0, 1)
                    pdf.cell(95, 6, f"Area Solicitante: {area_arch}", 0, 0)
                    pdf.cell(95, 6, f"Fecha: {fecha_arch}", 0, 1)
                    pdf.ln(5)
                    
                    item_contador = 1
                    for nombre_etapa, lista_preguntas in etapas_archivo:
                        etapa_limpia = nombre_etapa.encode('latin-1', 'ignore').decode('latin-1')
                        pdf.set_font("Arial", "B", 9)
                        pdf.set_fill_color(220, 230, 242)
                        pdf.cell(190, 6, etapa_limpia, 1, 1, "L", True)
                        
                        pdf.set_font("Arial", "B", 8)
                        pdf.set_fill_color(240, 240, 240)
                        pdf.cell(10, 6, "ITEM", 1, 0, "C", True)
                        pdf.cell(100, 6, "ACTIVIDAD", 1, 0, "C", True)
                        pdf.cell(10, 6, "SI", 1, 0, "C", True)
                        pdf.cell(10, 6, "NO", 1, 0, "C", True)
                        pdf.cell(60, 6, "OBSERVACIONES", 1, 1, "C", True)
                        
                        pdf.set_font("Arial", "", 8)
                        for texto_p, k in lista_preguntas:
                            resp = respuestas_arch[k]
                            obs = obs_arch[k] if obs_arch[k] else ""
                            
                            marca_si = "X" if resp == "Sí" else ""
                            marca_no = "X" if resp == "No" else ""
                            
                            texto_limpio = texto_p.split(". ", 1)[1] if ". " in texto_p else texto_p
                            texto_limpio = texto_limpio.encode('latin-1', 'ignore').decode('latin-1')
                            obs_limpia = obs.encode('latin-1', 'ignore').decode('latin-1')
                            
                            pdf.cell(10, 6, str(item_contador), 1, 0, "C")
                            pdf.cell(100, 6, texto_limpio, 1, 0, "L")
                            pdf.cell(10, 6, marca_si, 1, 0, "C")
                            pdf.cell(10, 6, marca_no, 1, 0, "C")
                            pdf.cell(60, 6, obs_limpia, 1, 1, "L")
                            
                            item_contador += 1
                        pdf.ln(2)
                    
                    temp_dir = tempfile.gettempdir()
                    pdf_path = os.path.join(temp_dir, nombre_pdf)
                    pdf.output(pdf_path)
                    
                    st.session_state.pdf_path = pdf_path
                    st.session_state.nombre_archivo_pdf = nombre_pdf
                    st.session_state.form_valido = True
                    st.success("¡Validación exitosa! PDF de Trámites en Archivo generado correctamente.")

    if st.session_state.form_valido and st.session_state.pdf_path:
        st.divider()
        with open(st.session_state.pdf_path, "rb") as f:
            pdf_bytes = f.read()
        st.download_button(
            label=f"📥 Descargar PDF de Archivo: {st.session_state.nombre_archivo_pdf}",
            data=pdf_bytes,
            file_name=st.session_state.nombre_archivo_pdf,
            mime="application/pdf"
        )