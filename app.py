import streamlit as st
import pdfplumber
import re
from openai import OpenAI

st.set_page_config(
    page_title="Saber AI Santander",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .header-banner {
        background: linear-gradient(135deg, #FFCD00 0%, #e6b800 100%);
        padding: 1.2rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        box-shadow: 0 4px 15px rgba(255,205,0,0.4);
    }
    .header-banner h1 {
        color: #1a1a1a;
        margin: 0;
        font-size: 1.9rem;
        font-weight: 800;
    }
    .header-banner p {
        color: #333;
        margin: 0;
        font-size: 0.95rem;
    }
    [data-testid="stSidebar"] {
        background: #00914C !important;
    }
    [data-testid="stSidebar"] * {
        color: #fff !important;
    }
    [data-testid="stSidebar"] .stSelectbox label {
        color: #FFCD00 !important;
        font-weight: 700;
    }
    .stButton > button {
        background-color: #00914C !important;
        color: #fff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        padding: 0.5rem 1.5rem !important;
    }
    .stButton > button:hover {
        background-color: #007a3d !important;
    }
    .pill-critico {
        background: #e74c3c;
        color: #fff;
        border-radius: 20px;
        padding: 4px 14px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
    }
    .pill-mejorar {
        background: #f39c12;
        color: #fff;
        border-radius: 20px;
        padding: 4px 14px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
    }
    .pill-bien {
        background: #00914C;
        color: #fff;
        border-radius: 20px;
        padding: 4px 14px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
    }
    .info-card {
        background: #f0faf5;
        border-left: 5px solid #00914C;
        padding: 1rem 1.2rem;
        border-radius: 8px;
        margin: 0.8rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

for key, default in {
    "messages": [],
    "scores": {},
    "area": "🔢 Matematicas",
    "last_area": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

MODULES = [
    "📊 Diagnostico (Subir Resultados)",
    "🔢 Matematicas",
    "📚 Lectura Critica",
    "🔬 Ciencias Naturales",
    "⚖️ Sociales y Ciudadanas",
    "🇬🇧 Ingles",
    "🧠 Socioemocionales (Nuevo 2026)",
]

AREA_META = {
    "🔢 Matematicas": {
        "competencias": ["Interpretacion y representacion", "Formulacion y ejecucion", "Argumentacion"],
        "tip": "En Matematicas, el ICFES 2026 evalua como aplicas el razonamiento en contextos reales, no solo formulas.",
    },
    "📚 Lectura Critica": {
        "competencias": ["Identificar y ubicar informacion", "Relacionar e interpretar", "Evaluar y reflexionar"],
        "tip": "Lectura Critica mide tu capacidad de analizar textos en tres niveles: local, inferencial y critico.",
    },
    "🔬 Ciencias Naturales": {
        "competencias": ["Indagacion", "Explicacion de fenomenos", "Uso del conocimiento cientifico"],
        "tip": "Ciencias Naturales integra Biologia, Fisica y Quimica. El foco esta en la indagacion cientifica.",
    },
    "⚖️ Sociales y Ciudadanas": {
        "competencias": ["Conocimiento", "Argumentacion", "Multiperspectivismo"],
        "tip": "Sociales evalua pensamiento critico ciudadano: historia, geografia y convivencia.",
    },
    "🇬🇧 Ingles": {
        "competencias": ["Reading", "Listening", "Writing"],
        "tip": "Ingles evalua tu nivel segun el Marco Comun Europeo (A1 a B+). Practica comprension lectora.",
    },
    "🧠 Socioemocionales (Nuevo 2026)": {
        "competencias": ["Procesos emocionales", "Regulacion cognitiva", "Habilidades sociales e interpersonales"],
        "tip": "Nueva seccion 2026! Evalua autorregulacion emocional, empatia y toma responsable de decisiones.",
    },
}

AREA_KEYWORDS = {
    "Matematicas": ["matematicas", "matematica", "math"],
    "Lectura Critica": ["lectura critica", "lectura"],
    "Ciencias Naturales": ["ciencias naturales", "ciencias"],
    "Sociales y Ciudadanas": ["sociales", "ciudadanas"],
    "Ingles": ["ingles", "english"],
    "Global": ["global", "puntaje global", "total"],
}


def classify(score):
    if score < 45:
        return "Prioridad Critica", "pill-critico"
    elif score <= 65:
        return "Por Mejorar", "pill-mejorar"
    else:
        return "Buen Nivel", "pill-bien"


def extract_scores_from_text(text):
    scores = {}
    text_lower = text.lower()
    lines = text_lower.split("\n")
    for area_name, keywords in AREA_KEYWORDS.items():
        for kw in keywords:
            for line in lines:
                if kw in line:
                    numbers = re.findall(r"\b([1-9][0-9]?|100)\b", line)
                    if numbers:
                        for n in numbers:
                            val = int(n)
                            if 0 < val <= 100:
                                scores[area_name] = val
                                break
                if area_name in scores:
                    break
            if area_name in scores:
                break
    return scores


def build_system_prompt(area, scores):
    scores_txt = ""
    if scores:
        lines = ["  - " + k + ": " + str(v) + " (" + classify(v)[0] + ")" for k, v in scores.items()]
        scores_txt = "\nPuntajes ICFES anteriores del estudiante:\n" + "\n".join(lines)

    competencias = ""
    if area in AREA_META:
        comp_list = ", ".join(AREA_META[area]["competencias"])
        competencias = "\nArea actual: " + area + "\nCompetencias evaluadas: " + comp_list

    return (
        "Eres un tutor veterano del ICFES con 20 anos de experiencia en Bucaramanga, Santander, Colombia.\n"
        "Tu mision es preparar a los estudiantes para el Saber 11 del 26 de julio de 2026.\n\n"
        "REGLAS ABSOLUTAS:\n"
        "1. NUNCA des la respuesta directa primero. SIEMPRE haz una pregunta socratica para guiar al estudiante.\n"
        "2. Identifica la competencia ICFES que evalua cada pregunta (ej: Argumentacion, Interpretacion, Indagacion).\n"
        "3. Usa ejemplos con referencias locales de Santander: la industria del calzado en Bucaramanga, "
        "el Canon del Chicamocha, la Metrolinea, el hormiguero, el mute santandereano, "
        "el mercado de Giron, la UIS y la UNAB.\n"
        "4. Tono: animador, directo, profesional. Como un buen profesor bumangues.\n"
        "5. Si el estudiante tiene puntajes bajos (menor a 45), prioriza esas areas con mas enfasis.\n"
        "6. Para el modulo Socioemocionales (nuevo 2026), evalua procesos emocionales, "
        "regulacion cognitiva y habilidades interpersonales.\n"
        "7. Cuando respondas, primero menciona la competencia evaluada en negrita, luego haz tu pregunta guia.\n"
        "8. Maximo 3 parrafos por respuesta para mantenerla concisa y clara.\n"
        + scores_txt
        + competencias
        + "\n\nEjemplo de respuesta correcta:\n"
        '"**Competencia: Argumentacion** -- Buena pregunta! Antes de explicarte, dime: '
        "si vendes zapatos en el barrio Ciudadela Real de Minas y necesitas saber cuanto ganaste en el mes, "
        'que informacion minima necesitarias para calcularlo?"'
    )


# ── SIDEBAR ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🦅 Saber AI Santander")
    st.markdown("---")
    area = st.selectbox("Selecciona tu modulo:", MODULES)
    st.session_state["area"] = area
    st.markdown("---")
    st.markdown("📅 **Examen:** 26 de Julio, 2026")
    st.markdown("📍 **Para estudiantes de Santander**")

    if st.session_state["scores"]:
        st.markdown("---")
        st.markdown("**📈 Mis puntajes ICFES:**")
        for mat, score in st.session_state["scores"].items():
            label, css = classify(score)
            badge = '<span class="' + css + '">' + str(score) + "</span>"
            st.markdown(mat + ": " + badge, unsafe_allow_html=True)

# ── HEADER ───────────────────────────────────────────────────────────────────

st.markdown(
    """
    <div class="header-banner">
        <div style="font-size:3rem">🦅</div>
        <div>
            <h1>Saber AI Santander</h1>
            <p>Tu tutor virtual para el Saber 11 &middot; Bucaramanga &amp; Santander &middot; Examen: 26 Jul 2026</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── MODULE: DIAGNOSTICO ───────────────────────────────────────────────────────

if area == "📊 Diagnostico (Subir Resultados)":
    st.subheader("📊 Analizador de Resultados ICFES")
    st.markdown(
        '<div class="info-card">Sube el PDF con tus resultados ICFES anteriores. '
        "El tutor analizara tus puntajes y personalizara las sesiones de estudio.</div>",
        unsafe_allow_html=True,
    )

    uploaded = st.file_uploader("Selecciona tu PDF de resultados ICFES", type=["pdf"])

    if uploaded:
        with st.spinner("Leyendo tu PDF... un momento 🦅"):
            try:
                full_text = ""
                with pdfplumber.open(uploaded) as pdf:
                    for page in pdf.pages:
                        t = page.extract_text()
                        if t:
                            full_text += t + "\n"

                scores = extract_scores_from_text(full_text)

                if scores:
                    st.session_state["scores"] = scores
                    st.success("Puntajes detectados exitosamente!")

                    cols = st.columns(len(scores))
                    for i, (mat, score) in enumerate(scores.items()):
                        label, css = classify(score)
                        with cols[i]:
                            st.markdown(
                                "<div style='text-align:center'>"
                                "<div style='font-size:2rem;font-weight:800;color:#00914C'>"
                                + str(score)
                                + "</div>"
                                "<div style='font-size:0.8rem;font-weight:700'>"
                                + mat
                                + "</div>"
                                '<span class="'
                                + css
                                + '">'
                                + label
                                + "</span>"
                                "</div>",
                                unsafe_allow_html=True,
                            )

                    st.markdown("---")
                    st.markdown("### Plan de Estudio Recomendado")
                    for mat, score in scores.items():
                        label, _ = classify(score)
                        if score < 45:
                            st.error("🔴 **" + mat + "** (" + str(score) + " pts): " + label + " -- Dedica minimo 2 horas diarias aqui.")
                        elif score <= 65:
                            st.warning("🟡 **" + mat + "** (" + str(score) + " pts): " + label + " -- Practica ejercicios intermedios.")
                        else:
                            st.success("🟢 **" + mat + "** (" + str(score) + " pts): " + label + " -- Mantén el ritmo con repasos semanales.")

                    st.info("Selecciona un modulo en la barra lateral para comenzar a practicar con el tutor.")

                else:
                    st.warning(
                        "No se encontraron puntajes numericos en el PDF. "
                        "Asegurate de subir el reporte oficial del ICFES. "
                        "Puedes ingresar tus puntajes manualmente abajo."
                    )

            except Exception as e:
                st.error("Error al leer el PDF: " + str(e))

    with st.expander("Ingresar puntajes manualmente"):
        manual_scores = {}
        areas_list = ["Matematicas", "Lectura Critica", "Ciencias Naturales", "Sociales y Ciudadanas", "Ingles"]
        c1, c2 = st.columns(2)
        for i, a in enumerate(areas_list):
            col = c1 if i % 2 == 0 else c2
            val = col.number_input(a, min_value=0, max_value=100, value=50, key="manual_" + a)
            manual_scores[a] = val
        if st.button("Guardar puntajes"):
            st.session_state["scores"] = manual_scores
            st.success("Puntajes guardados! Selecciona un modulo para comenzar.")

# ── MODULE: TUTOR CHAT ────────────────────────────────────────────────────────

else:
    meta = AREA_META.get(area, {})

    st.subheader(area)

    if meta:
        comp_str = " - ".join(meta["competencias"])
        st.markdown(
            '<div class="info-card"><b>Competencias evaluadas:</b> '
            + comp_str
            + "<br><small>"
            + meta["tip"]
            + "</small></div>",
            unsafe_allow_html=True,
        )

    if st.session_state.get("last_area") != area:
        st.session_state["messages"] = []
        st.session_state["last_area"] = area

        score_note = ""
        if st.session_state["scores"]:
            area_key = area.split(" ", 1)[-1].strip()
            for k, v in st.session_state["scores"].items():
                if k.lower() in area_key.lower() or area_key.lower() in k.lower():
                    label, _ = classify(v)
                    score_note = " Veo que en esta area obtuviste **" + str(v) + " puntos** (" + label + ")."
                    break

        greeting = (
            "Bienvenido, futuro profesional santandereano! 🦅"
            + score_note
            + " Estamos en **"
            + area
            + "** y hoy vamos a trabajar duro como los artesanos del calzado en el barrio Trigal. "
            "Cuentame: que tema o pregunta del ICFES te esta generando mas dificultad?"
        )
        st.session_state["messages"].append({"role": "assistant", "content": greeting})

    for msg in st.session_state["messages"]:
        avatar = "🦅" if msg["role"] == "assistant" else "🎓"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Preguntame sobre " + area.split(" ", 1)[-1] + "..."):
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🎓"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🦅"):
            with st.spinner("El tutor esta pensando..."):
                try:
                    system_prompt = build_system_prompt(area, st.session_state["scores"])
                    api_messages = [{"role": "system", "content": system_prompt}]
                    for m in st.session_state["messages"]:
                        api_messages.append({"role": m["role"], "content": m["content"]})

                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=api_messages,
                        max_tokens=600,
                        temperature=0.7,
                    )
                    reply = response.choices[0].message.content
                except Exception as e:
                    reply = (
                        "Hubo un problema de conexion con el tutor: "
                        + str(e)
                        + ". Verifica tu API key en los Secrets de Streamlit."
                    )

                st.markdown(reply)
                st.session_state["messages"].append({"role": "assistant", "content": reply})

    if meta and len(st.session_state["messages"]) <= 1:
        st.markdown("---")
        st.markdown("**Inicio rapido -- Elige un tema:**")
        cols = st.columns(len(meta["competencias"]))
        for i, comp in enumerate(meta["competencias"]):
            if cols[i].button(comp, key="quick_" + str(i)):
                msg = "Quiero practicar la competencia de **" + comp + "** para el ICFES."
                st.session_state["messages"].append({"role": "user", "content": msg})
                st.rerun()

# ── FOOTER ────────────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown(
    "<center style='color:#888;font-size:0.8rem'>"
    "🦅 Saber AI Santander -- Basado en los cuadernillos ICFES 2026 oficiales -- "
    "Hecho con amor para los estudiantes de Bucaramanga y Santander"
    "</center>",
    unsafe_allow_html=True,
)
