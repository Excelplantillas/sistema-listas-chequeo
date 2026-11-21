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

# ============================
# CSS: TEXTO BLANCO FUERTE
# ============================
st.markdown("""
    <style>
    /* Fondo general */
    .stApp {
        background-color: #1e2229 !important;
    }

    /* ===== FORZAR TEXTO BLANCO EN TODA LA APP ===== */
    h1, h2, h3, h4, h5, h6,
    p, span, div, label, strong, em,
    .stMarkdown,
    [data-testid="stMarkdownContainer"],
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] strong,
    [data-testid="stMarkdownContainer"] span,
    [data-testid="stWidgetLabel"],
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] span,
    .stRadio label,
    div[role="radiogroup"] label,
    .stTextInput label,
    .stDateInput label,
    .stTextArea label {
        color: #ffffff !important;
    }

    /* Preguntas y textos secundarios */
    .stMarkdown p,
    [data-testid="stMarkdownContainer"] p {
        color: #f5f5f5 !important;
    }

    /* Placeholders más visibles */
    input::placeholder,
    textarea::placeholder {
        color: #bbbbbb !important;
        opacity: 1 !important;
    }

    /* Formulario oscuro */
    [data-testid="stForm"] {
        background-color: #121212 !important;
        padding: 30px;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6);
        border: 1px solid #2a2a2a;
    }

    /* Títulos personalizados */
    .main-title {
        text-align: center;
        color: #ffffff !important;
        font-weight: 700;
        margin-bottom: 20px;
    }

    .subtitle {
        text-align: center;
        color: #d0d8e0 !important;
        margin-bottom: 30px;
    }

    /* Botones */
    .stButton > button,
    [data-testid="stFormSubmitButton"] button {
        width: 100%;
        background-color: #143f43 !important;
        color: #ffffff !important;
        font-size: 16px;
        font-weight: 700;
        padding: 12px 16px;
        border-radius: 8px;
        border: 1px solid #246b70 !important;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.25);
        transition: all 0.25s ease;
    }

    .stButton > button:hover,
    [data-testid="stFormSubmitButton"] button:hover {
        background-color: #17676b !important;
        border-color: #55d9d1 !important;
        box-shadow: 0 0 12px rgba(52, 220, 210, 0.65);
        transform: translateY(-1px);
    }

    .stButton > button:active,
    [data-testid="stFormSubmitButton"] button:active {
        background-color: #0e3438 !important;
        transform: translateY(0);
    }

    .stButton > button:focus,
    [data-testid="stFormSubmitButton"] button:focus {
        outline: 2px solid #55d9d1;
        outline-offset: 3px;
    }
    </style>
""", unsafe_allow_html=True)

# ============================
# ESTADO INICIAL
# ============================
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
    st.session_state.pdf_path = None


# ============================
# CONTRASEÑA
# ============================
try:
    PASSWORD = st.secrets["APP_PASSWORD"]
except Exception:
    PASSWORD = "Archivo159*"


# ============================
# FUNCIONES AUXILIARES PARA PDF
# ============================
def _limpiar_latin1(texto):
    if not texto:
        return ""
    return str(texto).encode("latin-1", "replace").decode("latin-1")


def _contar_lineas(pdf, texto, ancho_celda, padding=2):
    texto = _limpiar_latin1(texto)
    if not texto:
        return 1
    ancho_util = max(ancho_celda - padding, 1)
    lineas_total = 0
    for parrafo in texto.split("\n"):
        if not parrafo:
            lineas_total += 1
            continue
        palabras = parrafo.split(" ")
        linea_actual = ""
        for palabra in palabras:
            prueba = f"{linea_actual} {palabra}".strip()
            if pdf.get_string_width(prueba) <= ancho_util:
                linea_actual = prueba
            else:
                if linea_actual:
                    lineas_total += 1
                if pdf.get_string_width(palabra) > ancho_util:
                    trozo = ""
                    for ch in palabra:
                        if pdf.get_string_width(trozo + ch) <= ancho_util:
                            trozo += ch
                        else:
                            lineas_total += 1
                            trozo = ch
                    linea_actual = trozo
                else:
                    linea_actual = palabra
        if linea_actual:
            lineas_total += 1
    return max(lineas_total, 1)


# ============================
# FUNCION PARA GENERAR PDF
# ============================
def generar_pdf(
    titulo,
    etapas,
    identificador,
    placa,
    area,
    expediente,
    responsable,
    fecha,
    respuestas,
    observaciones
):
    placa_limpia = placa.strip().upper().replace(" ", "_")
    nombre_pdf = f"{placa_limpia}.pdf"

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Anchos totales = 190 mm
    w_item = 12
    w_act = 96
    w_si = 10
    w_no = 10
    w_obs = 62
    alto_linea = 5.0

    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(31, 78, 120)
    pdf.multi_cell(0, 8, _limpiar_latin1(titulo), 0, "C")
    pdf.ln(3)

    pdf.set_font("Arial", "B", 9)
    pdf.set_text_color(0, 0, 0)

    pdf.cell(95, 6, _limpiar_latin1(f"Identificador: {identificador}"), 0, 0)
    pdf.cell(95, 6, _limpiar_latin1(f"Expediente / Documento: {expediente}"), 0, 1)
    pdf.cell(95, 6, _limpiar_latin1(f"Placa: {placa.strip().upper()}"), 0, 0)
    pdf.cell(95, 6, _limpiar_latin1(f"Responsable de Busqueda: {responsable}"), 0, 1)
    pdf.cell(95, 6, _limpiar_latin1(f"Area Solicitante: {area}"), 0, 0)
    pdf.cell(95, 6, _limpiar_latin1(f"Fecha: {fecha}"), 0, 1)
    pdf.ln(5)

    item_contador = 1

    for nombre_etapa, lista_preguntas in etapas:
        etapa_limpia = _limpiar_latin1(nombre_etapa)

        pdf.set_font("Arial", "B", 9)
        pdf.set_fill_color(220, 230, 242)
        lineas_etapa = _contar_lineas(pdf, etapa_limpia, 190)
        alto_etapa = max(6.0, lineas_etapa * 5.5)
        x_ini = pdf.get_x()
        y_ini = pdf.get_y()
        pdf.rect(x_ini, y_ini, 190, alto_etapa, "DF")
        pdf.multi_cell(190, alto_etapa / lineas_etapa, etapa_limpia, 0, "L")
        pdf.set_xy(x_ini, y_ini + alto_etapa)

        pdf.set_font("Arial", "B", 8)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(w_item, 6, "ITEM", 1, 0, "C", True)
        pdf.cell(w_act, 6, "ACTIVIDAD", 1, 0, "C", True)
        pdf.cell(w_si, 6, "SI", 1, 0, "C", True)
        pdf.cell(w_no, 6, "NO", 1, 0, "C", True)
        pdf.cell(w_obs, 6, "OBSERVACIONES", 1, 1, "C", True)

        pdf.set_font("Arial", "", 8)

        for texto_pregunta, key in lista_preguntas:
            respuesta = respuestas[key]
            observacion = observaciones[key] if observaciones[key] else ""

            marca_si = "X" if respuesta == "Sí" else ""
            marca_no = "X" if respuesta == "No" else ""

            texto_limpio = texto_pregunta.split(". ", 1)[1] if ". " in texto_pregunta else texto_pregunta
            texto_limpio = _limpiar_latin1(texto_limpio)
            observacion_limpia = _limpiar_latin1(observacion)

            lineas_act = _contar_lineas(pdf, texto_limpio, w_act)
            lineas_obs = _contar_lineas(pdf, observacion_limpia, w_obs)
            num_lineas = max(lineas_act, lineas_obs, 1)
            alto_fila = max(6.0, num_lineas * alto_linea)

            if pdf.get_y() + alto_fila > pdf.page_break_trigger:
                pdf.add_page()
                pdf.set_font("Arial", "B", 8)
                pdf.set_fill_color(240, 240, 240)
                pdf.cell(w_item, 6, "ITEM", 1, 0, "C", True)
                pdf.cell(w_act, 6, "ACTIVIDAD", 1, 0, "C", True)
                pdf.cell(w_si, 6, "SI", 1, 0, "C", True)
                pdf.cell(w_no, 6, "NO", 1, 0, "C", True)
                pdf.cell(w_obs, 6, "OBSERVACIONES", 1, 1, "C", True)
                pdf.set_font("Arial", "", 8)

            x0 = pdf.get_x()
            y0 = pdf.get_y()

            pdf.rect(x0, y0, w_item, alto_fila)
            pdf.rect(x0 + w_item, y0, w_act, alto_fila)
            pdf.rect(x0 + w_item + w_act, y0, w_si, alto_fila)
            pdf.rect(x0 + w_item + w_act + w_si, y0, w_no, alto_fila)
            pdf.rect(x0 + w_item + w_act + w_si + w_no, y0, w_obs, alto_fila)

            pdf.set_xy(x0, y0 + (alto_fila - alto_linea) / 2)
            pdf.cell(w_item, alto_linea, str(item_contador), 0, 0, "C")

            pdf.set_xy(x0 + w_item, y0 + 0.5)
            pdf.multi_cell(w_act, alto_linea, texto_limpio, 0, "L")

            y_centro = y0 + (alto_fila - alto_linea) / 2
            pdf.set_xy(x0 + w_item + w_act, y_centro)
            pdf.cell(w_si, alto_linea, marca_si, 0, 0, "C")

            pdf.set_xy(x0 + w_item + w_act + w_si, y_centro)
            pdf.cell(w_no, alto_linea, marca_no, 0, 0, "C")

            pdf.set_xy(x0 + w_item + w_act + w_si + w_no, y0 + 0.5)
            pdf.multi_cell(w_obs, alto_linea, observacion_limpia, 0, "L")

            pdf.set_xy(x0, y0 + alto_fila)
            item_contador += 1

        pdf.ln(2)

    temp_dir = tempfile.gettempdir()
    pdf_path = os.path.join(temp_dir, nombre_pdf)
    pdf.output(pdf_path)

    return pdf_path, nombre_pdf


# ============================
# PANTALLA DE ACCESO
# ============================
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
            password = st.text_input(
                "Contraseña:",
                type="password",
                placeholder="Ingrese la contraseña..."
            )
            btn_login = st.form_submit_button("Ingresar al Sistema")

            if btn_login:
                if password == PASSWORD:
                    st.session_state.autenticado = True
                    st.success("¡Acceso concedido!")
                    st.rerun()
                else:
                    st.error("❌ Contraseña incorrecta. Intente nuevamente.")

# ============================
# MENÚ PRINCIPAL
# ============================
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

# ============================
# MÓDULO 1: EXPEDIENTES
# ============================
elif st.session_state.menu_actual == "expedientes":
    if st.button("⬅ Volver al Menú Principal"):
        cambiar_seccion("inicio")
        st.rerun()

    st.markdown("<h2 class='main-title'>Lista de Chequeo - Búsqueda de Expedientes</h2>", unsafe_allow_html=True)

    etapas_exp = [
        ("ETAPA 1 - VALIDACIÓN DE DATOS", [
            ("1. El formato de la placa se encuentra correcto", "e1_p1"),
            ("2. Verificación de estado del automotor (Activo u otro que afecte la información física del expediente)", "e1_p2")
        ]),
        ("ETAPA 2 - CONTROLES DE ARCHIVO", [
            ("3. Revisión último inventario documental", "e2_p3"),
            ("4. Registro trazabilidad de trámites", "e2_p4"),
            ("5. Registro trazabilidad de préstamos", "e2_p5"),
            ("6. Búsqueda de escaneos recientes", "e2_p6")
        ]),
        ("ETAPA 3 - BÚSQUEDA FÍSICA DIRECTA", [
            ("7. Revisión ubicación física del expediente", "e3_p7"),
            ("8. Expedientes contiguos revisados (En formato Cruz)", "e3_p8")
        ]),
        ("ETAPA 4 - BÚSQUEDA POR VARIACIONES (Obligatorio registrar campo de observaciones con las combinaciones aplicadas)", [
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
            ("15. Contenedores recibidos a partir de la fecha (Contar dos semanas)", "e6_p15"),
            ("16. Error de digitación de la relación recibida por contenedor", "e6_p16")
        ]),
        ("ETAPA 7 - BÚSQUEDA POR ANALISTA", [
            ("17. Trámites gestionados por el mismo analista", "e7_p17"),
            ("18. Carpetas físicas del analista", "e7_p18"),
            ("19. Bandejas / archivo temporal del analista", "e7_p19")
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

        respuestas = {}
        observaciones = {}

        for nombre_etapa, lista_preguntas in etapas_exp:
            st.markdown(f"### **{nombre_etapa}**")

            for texto_pregunta, key in lista_preguntas:
                st.markdown(f"**{texto_pregunta}**")

                respuestas[key] = st.radio(
                    "Opción:",
                    ["-- Seleccione --", "Sí", "No"],
                    key=f"r_{key}",
                    label_visibility="collapsed",
                    horizontal=True
                )

                observaciones[key] = st.text_input(
                    f"Observaciones {key}",
                    key=f"obs_{key}",
                    placeholder="Observaciones opcionales...",
                    label_visibility="collapsed"
                )

                st.write("---")

        submit_btn = st.form_submit_button("Validar y Generar PDF de Expedientes")

        if submit_btn:
            if not placa.strip():
                st.error("⚠️ El campo 'Placa' es obligatorio ya que será el nombre del archivo PDF.")
                st.session_state.form_valido = False
            else:
                todas_preguntas = [item for _, lista in etapas_exp for item in lista]
                sin_responder = [
                    p[0] for p in todas_preguntas
                    if respuestas[p[1]] == "-- Seleccione --"
                ]

                if sin_responder:
                    st.error(
                        f"⚠️ Faltan preguntas por responder. Debes completar las 19 preguntas. "
                        f"(Pendientes: {len(sin_responder)})"
                    )
                    st.session_state.form_valido = False
                else:
                    pdf_path, nombre_pdf = generar_pdf(
                        titulo="LISTA DE CHEQUEO - BUSQUEDA DE EXPEDIENTES",
                        etapas=etapas_exp,
                        identificador=identificador,
                        placa=placa,
                        area=area,
                        expediente=expediente_doc,
                        responsable=responsable,
                        fecha=fecha,
                        respuestas=respuestas,
                        observaciones=observaciones
                    )

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

# ============================
# MÓDULO 2: TRÁMITES EN SEDE
# ============================
elif st.session_state.menu_actual == "sede":
    if st.button("⬅ Volver al Menú Principal"):
        cambiar_seccion("inicio")
        st.rerun()

    st.markdown("<h2 class='main-title'>Lista de Chequeo - Búsqueda de Trámites en Sede</h2>", unsafe_allow_html=True)

    etapas_sede = [
        ("ETAPA 1 - VALIDACIÓN DE DATOS", [
            ("1. El formato de la placa se encuentra correcto", "sede_e1_p1"),
            ("2. Verificación de estado del automotor (Activo u otro que afecte la información física del expediente).", "sede_e1_p2")
        ]),
        ("ETAPA 2 - CONTROLES DE ARCHIVO", [
            ("3. Registro trazabilidad de trámites.", "sede_e2_p3")
        ]),
        ("ETAPA 3 -  BÚSQUEDA POR ANALISTA", [
            ("4. Documentos físicos del analista.", "sede_e3_p4"),
            ("5. Confirmación directa con el analista.", "sede_e3_p5")
        ]),
        ("ETAPA 4 - BÚSQUEDA POR SEMANA DEL TRÁMITE (SEDE)", [
            ("6. Contenedores enviado a partir de la fecha del trámite (Contar dos semana).", "sede_e4_p6"),
            ("7. Contenedor pendiente de apertura.", "sede_e4_p7"),
            ("8. Error de digitación del contenedor.", "sede_e4_p8")
        ]),
        ("ETAPA 5 -  BUSQUEDA POR TRÁMITES GESTIONADOS Y RECIBIDOS", [
            ("9. Trámites gestionados por el mismo analista a partir de la fecha del trámite (Contar dos semana).", "sede_e5_p9"),
            ("10. Remisión a archivo de trámites gestionados por el mismo analista a partir de la fecha del trámite contando dos semanas a partir de la fecha del trámite.", "sede_e5_p10"),
            ("11. Remisión al archivo de listado de trámites de todos los analistas de la sede contando dos semanas a partir de la fecha del trámite para búsqueda.", "sede_e5_p11"),
            ("12. Remisión al archivo de listado de trámites recibidos en mensajería, contando dos semanas a partir de la fecha del trámite para busqueda.", "sede_e5_p12")
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

        respuestas_sede = {}
        obs_sede = {}

        for nombre_etapa, lista_preguntas in etapas_sede:
            st.markdown(f"### **{nombre_etapa}**")

            for texto_pregunta, key in lista_preguntas:
                st.markdown(f"**{texto_pregunta}**")

                respuestas_sede[key] = st.radio(
                    "Opción:",
                    ["-- Seleccione --", "Sí", "No"],
                    key=f"r_{key}",
                    label_visibility="collapsed",
                    horizontal=True
                )

                obs_sede[key] = st.text_input(
                    f"Observaciones {key}",
                    key=f"obs_{key}",
                    placeholder="Observaciones opcionales...",
                    label_visibility="collapsed"
                )

                st.write("---")

        submit_sede = st.form_submit_button("Validar y Generar PDF de Sede")

        if submit_sede:
            if not placa_sede.strip():
                st.error("⚠️ El campo 'Placa' es obligatorio ya que será el nombre del archivo PDF.")
                st.session_state.form_valido = False
            else:
                todas_p_sede = [item for _, lista in etapas_sede for item in lista]
                sin_resp_sede = [
                    p[0] for p in todas_p_sede
                    if respuestas_sede[p[1]] == "-- Seleccione --"
                ]

                if sin_resp_sede:
                    st.error(
                        f"⚠️ Faltan preguntas por responder. Debes completar las 12 preguntas. "
                        f"(Pendientes: {len(sin_resp_sede)})"
                    )
                    st.session_state.form_valido = False
                else:
                    pdf_path, nombre_pdf = generar_pdf(
                        titulo="LISTA DE CHEQUEO - BUSQUEDA DE TRAMITES EN SEDE",
                        etapas=etapas_sede,
                        identificador=identificador_sede,
                        placa=placa_sede,
                        area=area_sede,
                        expediente=expediente_sede,
                        responsable=responsable_sede,
                        fecha=fecha_sede,
                        respuestas=respuestas_sede,
                        observaciones=obs_sede
                    )

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

# ============================
# MÓDULO 3: TRÁMITES EN ARCHIVO
# ============================
elif st.session_state.menu_actual == "archivo":
    if st.button("⬅ Volver al Menú Principal"):
        cambiar_seccion("inicio")
        st.rerun()

    st.markdown("<h2 class='main-title'>Lista de Chequeo - Búsqueda de Trámites en Archivo</h2>", unsafe_allow_html=True)

    etapas_archivo = [
        ("ETAPA 1 - VALIDACIÓN DE DATOS", [
            ("1. El formato de la placa se encuentra correcto", "arch_e1_p1"),
            ("2. Verificación de estado del automotor (Activo u otro que afecte la información física)", "arch_e1_p2")
        ]),
        ("ETAPA 2 - CONTROLES DE ARCHIVO", [
            ("3. Registro histórico por placa.", "arch_e2_p3"),
            ("4. Busqueda de escaneos recientes.", "arch_e2_p4")
        ]),
        ("ETAPA 3 - ENVIADOS EN CONTENEDORES (ARCHIVO)", [
            ("5. Contenedores recibido a partir de la fecha del trámite (Contar dos semana).", "arch_e3_p5"),
            ("6. Contenedor pendiente por revisión (Que llega de la sede).", "arch_e3_p6"),
            ("7. Error de digitación del contenedor.", "arch_e3_p7")
        ]),
        ("ETAPA 4 - BÚSQUEDA POR SEMANA DEL TRÁMITE (SEDE)", [
            ("8. Trámites realizados a partir de la fecha del trámite (Contar dos semana).", "arch_e4_p8"),
            ("9. Revisión de listado de trámites contando dos semanas a partir de la fecha del trámite para busqueda.", "arch_e4_p9")
        ]),
        ("ETAPA 5 - BÚSQUEDA POR ANALISTA", [
            ("10. Trámites gestionados por el mismo analista a partir de la fecha del trámite (Contar dos semana).", "arch_e5_p10"),
            ("11. Documentos físicos del analista.", "arch_e5_p11")
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

        respuestas_arch = {}
        obs_arch = {}

        for nombre_etapa, lista_preguntas in etapas_archivo:
            st.markdown(f"### **{nombre_etapa}**")

            for texto_pregunta, key in lista_preguntas:
                st.markdown(f"**{texto_pregunta}**")

                respuestas_arch[key] = st.radio(
                    "Opción:",
                    ["-- Seleccione --", "Sí", "No"],
                    key=f"r_{key}",
                    label_visibility="collapsed",
                    horizontal=True
                )

                obs_arch[key] = st.text_input(
                    f"Observaciones {key}",
                    key=f"obs_{key}",
                    placeholder="Observaciones opcionales...",
                    label_visibility="collapsed"
                )

                st.write("---")

        submit_arch = st.form_submit_button("Validar y Generar PDF de Archivo")

        if submit_arch:
            if not placa_arch.strip():
                st.error("⚠️ El campo 'Placa' es obligatorio ya que será el nombre del archivo PDF.")
                st.session_state.form_valido = False
            else:
                todas_p_arch = [item for _, lista in etapas_archivo for item in lista]
                sin_resp_arch = [
                    p[0] for p in todas_p_arch
                    if respuestas_arch[p[1]] == "-- Seleccione --"
                ]

                if sin_resp_arch:
                    st.error(
                        f"⚠️ Faltan preguntas por responder. Debes completar las 11 preguntas. "
                        f"(Pendientes: {len(sin_resp_arch)})"
                    )
                    st.session_state.form_valido = False
                else:
                    pdf_path, nombre_pdf = generar_pdf(
                        titulo="LISTA DE CHEQUEO - BUSQUEDA DE TRAMITES EN ARCHIVO",
                        etapas=etapas_archivo,
                        identificador=identificador_arch,
                        placa=placa_arch,
                        area=area_arch,
                        expediente=expediente_arch,
                        responsable=responsable_arch,
                        fecha=fecha_arch,
                        respuestas=respuestas_arch,
                        observaciones=obs_arch
                    )

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
