import streamlit as st
import openai
import datetime

WHITELIST = “parent1@gmail.com parent2@yahoo.com”.split()

FREE_TRIAL_LIMIT = 3
WA_URL = “https://wa.me/573228246703?text=Hola%2C+quiero+registrar+mi+correo+y+obtener+acceso+completo.”

SYSTEM_PROMPT = “ “.join([“Eres”, “el”, “tutor”, “lider”, “de”, “Saber”, “AI”, “Santander,”, “preparacion”, “ICFES”, “2026,”, “Santander”, “Colombia.”, “Reglas:”, “1)”, “Identifica”, “la”, “competencia”, “evaluada.”, “2)”, “Nunca”, “des”, “la”, “respuesta”, “directa,”, “haz”, “primero”, “una”, “pregunta”, “orientadora.”, “3)”, “Tono”, “de”, “docente”, “santandereano:”, “directo,”, “alentador,”, “profesional.”, “4)”, “Si”, “insisten,”, “da”, “una”, “pista”, “adicional”, “no”, “la”, “solucion.”, “5)”, “Celebra”, “avances”, “con”, “frases”, “motivadoras”, “de”, “Bucaramanga.”])

st.set_page_config(page_title=“Saber AI Santander”, layout=“wide”)

st.markdown(”<style>.stApp{background:#f0f4f8}.hdr{background:linear-gradient(135deg,#1a3c6e,#2d6a9f,#f5a623);color:white;padding:1.2rem 2rem;border-radius:12px;margin-bottom:1.5rem}.hdr h1{margin:0;font-size:1.8rem;font-weight:800}.hdr p{margin:.2rem 0 0;opacity:.9}.cu{background:#1a3c6e;color:white;border-radius:18px 18px 4px 18px;padding:.75rem 1.1rem;margin:.4rem 0;max-width:75%;float:right;clear:both}.ca{background:white;color:#1a1a2e;border-radius:18px 18px 18px 4px;padding:.75rem 1.1rem;margin:.4rem 0;max-width:80%;float:left;clear:both;border-left:4px solid #f5a623}.cf{clear:both}.tbadge{background:#fff3cd;border:1px solid #f5a623;border-radius:8px;padding:.4rem .9rem;font-size:.85rem;color:#856404;font-weight:600;display:inline-block;margin-bottom:.8rem}.wa{display:inline-block;background:#25d366;color:white !important;padding:.7rem 1.8rem;border-radius:30px;text-decoration:none !important;font-weight:700}.ok{background:#d4edda;color:#155724;border-radius:8px;padding:.6rem 1rem;font-weight:600;margin-top:.5rem}</style>”, unsafe_allow_html=True)

for key, val in [(“messages”, []), (“trial_count”, 0)]:
if key not in st.session_state:
st.session_state[key] = val

with st.sidebar:
st.markdown(”## Saber AI Santander”)
st.markdown(”—”)
user_email = st.text_input(“Ingresa tu correo registrado”, placeholder=“tucorreo@email.com”)
email_clean = user_email.strip().lower()
access_granted = email_clean in WHITELIST and email_clean != “”
if access_granted:
st.markdown(”<div class='ok'>Acceso completo activo para: <b>” + email_clean + “</b></div>”, unsafe_allow_html=True)
else:
left = max(0, FREE_TRIAL_LIMIT - st.session_state[“trial_count”])
st.markdown(”<div class='tbadge'>Demo gratuito: “ + str(left) + “ mensaje(s) restante(s)</div>”, unsafe_allow_html=True)
st.markdown(”—”)
st.markdown(”**Pruebas disponibles**”)
st.markdown(”- Matematicas”)
st.markdown(”- Lectura Critica”)
st.markdown(”- Ciencias Naturales”)
st.markdown(”- Ingles”)
st.markdown(”- Competencias Ciudadanas”)
st.markdown(”—”)
st.markdown(“ICFES Saber 11 - 26 julio 2026”)
st.markdown(“Bucaramanga, Santander”)

st.markdown(”<div class='hdr'><h1>Saber AI Santander</h1><p>Tu tutor inteligente para el ICFES 2026</p></div>”, unsafe_allow_html=True)

for msg in st.session_state[“messages”]:
if msg[“role”] == “user”:
st.markdown(”<div class='cu'>” + msg[“content”] + “</div><div class='cf'></div>”, unsafe_allow_html=True)
else:
st.markdown(”<div class='ca'>” + msg[“content”] + “</div><div class='cf'></div>”, unsafe_allow_html=True)

trial_exhausted = not access_granted and st.session_state[“trial_count”] >= FREE_TRIAL_LIMIT

if trial_exhausted:
st.error(“Acceso Limitado. Envia $49,000 por Nequi al 3228246703 y registrate con tu email para desbloquear el acceso completo.”)
wa_html = “<div style='text-align:center;margin-top:1rem;'><a href='" + WA_URL + "' target='_blank' class='wa'>Contactar por WhatsApp</a></div>”
st.markdown(wa_html, unsafe_allow_html=True)

if access_granted and len(st.session_state[“messages”]) >= 2:
st.markdown(”—”)
if st.button(“Descargar Plan de Estudio Personalizado”, use_container_width=True):
with st.spinner(“Generando tu plan de 7 dias…”):
try:
client = openai.OpenAI(api_key=st.secrets[“OPENAI_API_KEY”])
hist_lines = []
for m in st.session_state[“messages”]:
lbl = “Estudiante” if m[“role”] == “user” else “Tutor”
hist_lines.append(lbl + “: “ + m[“content”])
history = chr(10).join(hist_lines)
p1 = “Genera un Plan de Estudio de 7 dias para el ICFES 2026.”
p2 = chr(10) + “HISTORIAL:” + chr(10) + history
p3 = chr(10) + “INSTRUCCIONES:”
p4 = chr(10) + “- Identifica areas debiles.”
p5 = chr(10) + “- Dia 1 a Dia 7: tema, competencia, ejercicios, objetivo, consejo.”
p6 = chr(10) + “- Resumen de fortalezas y areas de mejora.”
p7 = chr(10) + “- Tono motivador de docente santandereano. ICFES 26 julio 2026.”
prompt = p1 + p2 + p3 + p4 + p5 + p6 + p7
resp = client.chat.completions.create(model=“gpt-4o-mini”, max_tokens=2000, messages=[{“role”: “user”, “content”: prompt}])
plan = resp.choices[0].message.content
now = datetime.datetime.now().strftime(”%Y-%m-%d %H:%M”)
t1 = “PLAN DE ESTUDIO - ICFES 2026” + chr(10) + “Saber AI Santander” + chr(10)
t2 = “==========================================” + chr(10) + “Generado: “ + now
t3 = chr(10) + “Correo: “ + email_clean
t4 = chr(10) + “Fecha ICFES: 26 julio 2026” + chr(10) + “==========================================” + chr(10) + chr(10)
t5 = plan + chr(10) + chr(10) + “==========================================” + chr(10)
t6 = “Tu puedes, santandereano!” + chr(10) + “Bucaramanga, Santander, Colombia” + chr(10)
txt = t1 + t2 + t3 + t4 + t5 + t6
fname = “plan_ICFES_saber_ai.txt”
st.download_button(label=“Descargar plan .txt”, data=txt, file_name=fname, mime=“text/plain”, use_container_width=True)
except Exception as e:
st.error(“Error al generar el plan: “ + str(e))

chat_allowed = access_granted or st.session_state[“trial_count”] < FREE_TRIAL_LIMIT

if chat_allowed:
if not access_granted:
left = FREE_TRIAL_LIMIT - st.session_state[“trial_count”]
st.markdown(”<div class='tbadge'>Demo: “ + str(left) + “ mensaje(s) gratuito(s)</div>”, unsafe_allow_html=True)
user_input = st.chat_input(“Pregunta sobre ICFES 2026 - Matematicas, Lectura, Ciencias, Ingles, Ciudadanas”)
if user_input:
st.session_state[“messages”].append({“role”: “user”, “content”: user_input})
with st.spinner(“El tutor esta pensando…”):
try:
client = openai.OpenAI(api_key=st.secrets[“OPENAI_API_KEY”])
api_msgs = [{“role”: “system”, “content”: SYSTEM_PROMPT}]
for m in st.session_state[“messages”]:
api_msgs.append({“role”: m[“role”], “content”: m[“content”]})
resp = client.chat.completions.create(model=“gpt-4o-mini”, max_tokens=1000, messages=api_msgs)
reply = resp.choices[0].message.content
except Exception as e:
reply = “Error al conectar: “ + str(e)
st.session_state[“messages”].append({“role”: “assistant”, “content”: reply})
if not access_granted:
st.session_state[“trial_count”] += 1
st.rerun()
else:
st.text_input(””, placeholder=“Adquiere acceso completo para continuar…”, disabled=True, label_visibility=“collapsed”)