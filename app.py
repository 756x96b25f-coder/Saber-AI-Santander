import streamlit as st
import anthropic
import datetime

VALID_CODES = [
‘SAB-A1B2’, ‘SAB-C3D4’, ‘SAB-E5F6’, ‘SAB-G7H8’, ‘SAB-J9K1’,
‘SAB-L2M3’, ‘SAB-N4P5’, ‘SAB-Q6R7’, ‘SAB-S8T9’, ‘SAB-U1V2’,
‘SAB-W3X4’, ‘SAB-Y5Z6’, ‘SAB-A7B8’, ‘SAB-C9D1’, ‘SAB-E2F3’,
‘SAB-G4H5’, ‘SAB-J6K7’, ‘SAB-L8M9’, ‘SAB-N1P2’, ‘SAB-Q3R4’,
‘SAB-S5T6’, ‘SAB-U7V8’, ‘SAB-W9X1’, ‘SAB-Y2Z3’, ‘SAB-A4B5’,
‘SAB-C6D7’, ‘SAB-E8F9’, ‘SAB-G1H2’, ‘SAB-J3K4’, ‘SAB-L5M6’,
‘SAB-N7P8’, ‘SAB-Q9R1’, ‘SAB-S2T3’, ‘SAB-U4V5’, ‘SAB-W6X7’,
‘SAB-Y8Z9’, ‘SAB-A2C3’, ‘SAB-B4D5’, ‘SAB-E6G7’, ‘SAB-F8H9’,
‘SAB-J1L2’, ‘SAB-K3M4’, ‘SAB-N5Q6’, ‘SAB-P7R8’, ‘SAB-S9U1’,
‘SAB-T2V3’, ‘SAB-W4Y5’, ‘SAB-X6Z7’, ‘SAB-A8C9’, ‘SAB-B1D2’,
‘SAB-E3G4’, ‘SAB-F5H6’, ‘SAB-J7L8’, ‘SAB-K9M1’, ‘SAB-N2Q3’,
‘SAB-P4R5’, ‘SAB-S6U7’, ‘SAB-T8V9’, ‘SAB-W1Y2’, ‘SAB-X3Z4’,
‘SAB-A5C6’, ‘SAB-B7D8’, ‘SAB-E9G1’, ‘SAB-F2H3’, ‘SAB-J4L5’,
‘SAB-K6M7’, ‘SAB-N8Q9’, ‘SAB-P1R2’, ‘SAB-S3U4’, ‘SAB-T5V6’,
‘SAB-W7Y8’, ‘SAB-X9Z1’, ‘SAB-A3C4’, ‘SAB-B5D6’, ‘SAB-E7G8’,
‘SAB-F9H1’, ‘SAB-J2L3’, ‘SAB-K4M5’, ‘SAB-N6Q7’, ‘SAB-P8R9’,
‘SAB-S1U2’, ‘SAB-T3V4’, ‘SAB-W5Y6’, ‘SAB-X7Z8’, ‘SAB-A9C1’,
‘SAB-B2D3’, ‘SAB-E4G5’, ‘SAB-F6H7’, ‘SAB-J8L9’, ‘SAB-K1M2’,
‘SAB-N3Q4’, ‘SAB-P5R6’, ‘SAB-S7U8’, ‘SAB-T9V1’, ‘SAB-W2Y3’,
‘SAB-X4Z5’, ‘SAB-A6C7’, ‘SAB-B8D9’, ‘SAB-E1G2’, ‘SAB-F3H4’,
]

VALID_CODES_SET = set(VALID_CODES)
FREE_TRIAL_LIMIT = 3
WHATSAPP_NUMBER = ‘573228246703’
WHATSAPP_MSG = ‘Hola%2C+quiero+adquirir+acceso+completo+a+Saber+AI+Santander.+Adjunto+mi+comprobante.’
WHATSAPP_URL = ‘https://wa.me/’ + WHATSAPP_NUMBER + ‘?text=’ + WHATSAPP_MSG

SYSTEM_PROMPT = (
’Eres el tutor lider de Saber AI Santander, un programa de preparacion para el ICFES 2026 ’
’dirigido a estudiantes de Santander, Colombia. Tu conocimiento esta basado en los cuadernillos ’
’oficiales del ICFES 2026 (Matematicas, Lectura Critica, Ciencias Naturales, Ingles, ’
‘Competencias Ciudadanas).\n\n’
‘Reglas de oro:\n’
‘1. Identifica siempre la competencia evaluada (Interpretacion, Argumentacion, Formulacion, etc.).\n’
’2. NUNCA des la respuesta final directamente. Primero haz una pregunta orientadora que guie ’
‘al estudiante a llegar por si mismo a la conclusion.\n’
‘3. Usa un tono de docente santandereano: directo, alentador, profesional y con calidez regional.\n’
‘4. Si el estudiante insiste en la respuesta, ofrece una pista adicional, no la solucion completa.\n’
‘5. Celebra los avances del estudiante con frases motivadoras propias de Bucaramanga.\n’
‘6. Relaciona los ejercicios con contextos cotidianos de Santander cuando sea pertinente.’
)

st.set_page_config(
page_title=‘Saber AI Santander’,
page_icon=‘🎓’,
layout=‘wide’,
initial_sidebar_state=‘expanded’,
)

CSS = (
‘<style>’
‘.stApp{background-color:#f0f4f8}’
‘.header-banner{background:linear-gradient(135deg,#1a3c6e 0%,#2d6a9f 60%,#f5a623 100%);’
‘color:white;padding:1.2rem 2rem;border-radius:12px;margin-bottom:1.5rem;’
‘box-shadow:0 4px 15px rgba(26,60,110,0.3)}’
‘.header-banner h1{margin:0;font-size:1.8rem;font-weight:800}’
‘.header-banner p{margin:0.2rem 0 0;opacity:0.9;font-size:0.95rem}’
‘.chat-user{background:#1a3c6e;color:white;border-radius:18px 18px 4px 18px;’
‘padding:0.75rem 1.1rem;margin:0.4rem 0;max-width:75%;float:right;clear:both;’
‘box-shadow:0 2px 8px rgba(26,60,110,0.2)}’
‘.chat-assistant{background:white;color:#1a1a2e;border-radius:18px 18px 18px 4px;’
‘padding:0.75rem 1.1rem;margin:0.4rem 0;max-width:80%;float:left;clear:both;’
‘border-left:4px solid #f5a623;box-shadow:0 2px 8px rgba(0,0,0,0.08)}’
‘.clearfix{clear:both}’
‘.trial-badge{background:#fff3cd;border:1px solid #f5a623;border-radius:8px;’
‘padding:0.4rem 0.9rem;font-size:0.85rem;color:#856404;font-weight:600;’
‘display:inline-block;margin-bottom:0.8rem}’
‘.paywall-card{background:linear-gradient(135deg,#1a3c6e,#2d6a9f);color:white;’
‘border-radius:16px;padding:2rem;text-align:center;’
‘box-shadow:0 8px 30px rgba(26,60,110,0.35);margin-top:1rem}’
‘.paywall-card h2{font-size:1.5rem;margin-bottom:0.5rem}’
‘.paywall-card p{opacity:0.92;font-size:1rem;margin-bottom:1rem}’
‘.payment-info{background:rgba(255,255,255,0.15);border-radius:10px;’
‘padding:1rem;margin:1rem 0;font-size:0.95rem}’
‘.payment-info strong{color:#f5a623;font-size:1.1rem}’
‘.wa-button{display:inline-block;background:#25d366;color:white !important;’
‘padding:0.7rem 1.8rem;border-radius:30px;text-decoration:none !important;’
‘font-weight:700;font-size:1rem;box-shadow:0 4px 12px rgba(37,211,102,0.4)}’
‘.code-success{background:#d4edda;color:#155724;border-radius:8px;’
‘padding:0.6rem 1rem;font-weight:600;margin-top:0.5rem}’
‘.code-error{background:#f8d7da;color:#721c24;border-radius:8px;’
‘padding:0.6rem 1rem;font-weight:600;margin-top:0.5rem}’
‘</style>’
)
st.markdown(CSS, unsafe_allow_html=True)

if ‘messages’ not in st.session_state:
st.session_state.messages = []
if ‘trial_count’ not in st.session_state:
st.session_state.trial_count = 0
if ‘access_granted’ not in st.session_state:
st.session_state.access_granted = False
if ‘active_code’ not in st.session_state:
st.session_state.active_code = None
if ‘code_message’ not in st.session_state:
st.session_state.code_message = ‘’
if ‘code_valid’ not in st.session_state:
st.session_state.code_valid = None

params = st.query_params
if not st.session_state.access_granted:
stored_code = params.get(‘code’, None)
if stored_code and stored_code in VALID_CODES_SET:
st.session_state.access_granted = True
st.session_state.active_code = stored_code

with st.sidebar:
st.markdown(’## 🎓 Saber AI Santander’)
st.markdown(’—’)
if st.session_state.access_granted:
st.markdown(
‘<div class="code-success">✅ Acceso completo activo<br>’
‘<small>Codigo: <strong>’ + str(st.session_state.active_code) + ‘</strong></small></div>’,
unsafe_allow_html=True,
)
st.markdown(’—’)
st.markdown(’### 📊 Tu sesion’)
msg_count = len(st.session_state.messages) // 2
st.markdown(‘💬 Mensajes enviados: **’ + str(msg_count) + ’**’)
else:
st.markdown(’**🔑 Tienes codigo de acceso?**’)
code_input = st.text_input(
‘Ingresa tu codigo’,
placeholder=‘SAB-XXXX’,
max_chars=8,
label_visibility=‘collapsed’,
)
if st.button(‘Validar codigo’, use_container_width=True):
cleaned = code_input.strip().upper()
if cleaned in VALID_CODES_SET:
st.session_state.access_granted = True
st.session_state.active_code = cleaned
st.session_state.code_valid = True
st.session_state.code_message = ‘Bienvenido! Codigo ’ + cleaned + ’ activado correctamente.’
st.query_params[‘code’] = cleaned
st.rerun()
else:
st.session_state.code_valid = False
st.session_state.code_message = ‘Codigo invalido. Verifica e intenta de nuevo.’
if st.session_state.code_message:
css_class = ‘code-success’ if st.session_state.code_valid else ‘code-error’
st.markdown(
‘<div class="' + css_class + '">’ + st.session_state.code_message + ‘</div>’,
unsafe_allow_html=True,
)
st.markdown(’—’)
trial_left = max(0, FREE_TRIAL_LIMIT - st.session_state.trial_count)
st.markdown(
‘<div class="trial-badge">🎯 Demo gratuito: ’ + str(trial_left) + ’ mensaje(s) restante(s)</div>’,
unsafe_allow_html=True,
)
st.markdown(’—’)
st.markdown(’**📚 Pruebas disponibles**’)
st.markdown(’- Matematicas\n- Lectura Critica\n- Ciencias Naturales\n- Ingles\n- Competencias Ciudadanas’)
st.markdown(’—’)
st.markdown(’<small>📅 ICFES Saber 11 — 26 de julio de 2026</small>’, unsafe_allow_html=True)
st.markdown(’<small>📍 Bucaramanga, Santander</small>’, unsafe_allow_html=True)

st.markdown(
‘<div class="header-banner">’
‘<h1>🎓 Saber AI Santander</h1>’
‘<p>Tu tutor inteligente para el ICFES 2026 · Basado en los cuadernillos oficiales del ICFES</p>’
‘</div>’,
unsafe_allow_html=True,
)

for msg in st.session_state.messages:
if msg[‘role’] == ‘user’:
st.markdown(
’<div class="chat-user">👤 ’ + msg[‘content’] + ‘</div><div class="clearfix"></div>’,
unsafe_allow_html=True,
)
else:
st.markdown(
’<div class="chat-assistant">🎓 ’ + msg[‘content’] + ‘</div><div class="clearfix"></div>’,
unsafe_allow_html=True,
)

trial_exhausted = (
not st.session_state.access_granted
and st.session_state.trial_count >= FREE_TRIAL_LIMIT
)

if trial_exhausted:
st.markdown(
‘<div class="paywall-card">’
‘<h2>🚀 Has llegado al limite del demo!</h2>’
’<p>Para asegurar tu puesto en la Universidad y dominar el Icfes del ’
‘<strong>26 de Julio</strong>, adquiere el acceso completo.</p>’
‘<div class="payment-info">’
‘💳 Envia <strong>$49,000 COP</strong> por Nequi al numero<br>’
‘<strong style="font-size:1.3rem;">3228246703</strong><br><br>’
‘📲 Luego envia el comprobante por WhatsApp para recibir tu codigo unico.’
‘</div>’
‘</div>’,
unsafe_allow_html=True,
)
st.markdown(
‘<div style="text-align:center;margin-top:1rem;">’
‘<a href="' + WHATSAPP_URL + '" target="_blank" class="wa-button">’
‘💬 Enviar comprobante por WhatsApp</a></div>’,
unsafe_allow_html=True,
)

if st.session_state.access_granted and len(st.session_state.messages) >= 2:
st.markdown(’—’)
if st.button(‘📄 Descargar Plan de Estudio Personalizado’, use_container_width=True):
with st.spinner(‘El tutor esta generando tu plan de 7 dias…’):
try:
client = anthropic.Anthropic()
history_lines = []
for m in st.session_state.messages:
role_label = ‘Estudiante’ if m[‘role’] == ‘user’ else ‘Tutor’
history_lines.append(role_label + ‘: ’ + m[‘content’])
history_text = ‘\n’.join(history_lines)
plan_prompt = (
‘Eres el tutor lider de Saber AI Santander.\n’
‘Analiza el siguiente historial de conversacion de un estudiante ’
‘preparandose para el ICFES 2026 y genera un Plan de Estudio ’
‘Personalizado de 7 dias.\n\n’
‘HISTORIAL:\n’ + history_text + ‘\n\n’
‘INSTRUCCIONES:\n’
‘- Identifica areas y competencias donde el estudiante mostro dificultades.\n’
‘- Crea un plan diario detallado Dia 1 al Dia 7 con:\n’
’  * Tema principal del dia\n’
’  * Competencia ICFES a trabajar\n’
’  * Tipos de ejercicios sugeridos\n’
’  * Objetivo concreto del dia\n’
’  * Consejo motivacional estilo santandereano\n’
‘- Incluye un resumen final de fortalezas y areas de mejora.\n’
‘- Tono calido, profesional, motivador, como docente de Santander.\n’
‘- El ICFES es el 26 de julio de 2026.’
)
response = client.messages.create(
model=‘claude-sonnet-4-20250514’,
max_tokens=2000,
messages=[{‘role’: ‘user’, ‘content’: plan_prompt}],
)
plan_text = response.content[0].text
now = datetime.datetime.now().strftime(’%Y-%m-%d %H:%M’)
file_text = (
‘PLAN DE ESTUDIO PERSONALIZADO - ICFES 2026\n’
‘Saber AI Santander\n’
‘==========================================\n\n’
’Generado el: ’ + now + ‘\n’
’Codigo de acceso: ’ + str(st.session_state.active_code) + ‘\n’
‘Fecha del ICFES: 26 de julio de 2026\n\n’
‘==========================================\n\n’
+ plan_text +
‘\n\n==========================================\n’
‘Tu puedes, santandereano! El esfuerzo de hoy es el logro de manana.\n’
‘Bucaramanga, Santander, Colombia\n’
)
st.download_button(
label=‘Descargar mi plan (.txt)’,
data=file_text,
file_name=‘plan_ICFES_’ + str(st.session_state.active_code) + ‘.txt’,
mime=‘text/plain’,
use_container_width=True,
)
except Exception as e:
st.error(’Error al generar el plan: ’ + str(e))

chat_allowed = (
st.session_state.access_granted
or st.session_state.trial_count < FREE_TRIAL_LIMIT
)

if chat_allowed:
if not st.session_state.access_granted:
trial_left = FREE_TRIAL_LIMIT - st.session_state.trial_count
st.markdown(
‘<div class="trial-badge">🎯 Demo: ’ + str(trial_left) + ’ mensaje(s) gratuito(s) restante(s)</div>’,
unsafe_allow_html=True,
)
user_input = st.chat_input(
‘Escribe tu pregunta sobre el ICFES 2026… (Matematicas, Lectura Critica, Ciencias, Ingles, Ciudadanas)’
)
if user_input:
st.session_state.messages.append({‘role’: ‘user’, ‘content’: user_input})
with st.spinner(‘El tutor esta pensando…’):
try:
client = anthropic.Anthropic()
api_messages = [
{‘role’: m[‘role’], ‘content’: m[‘content’]}
for m in st.session_state.messages
]
response = client.messages.create(
model=‘claude-sonnet-4-20250514’,
max_tokens=1000,
system=SYSTEM_PROMPT,
messages=api_messages,
)
assistant_reply = response.content[0].text
except Exception as e:
assistant_reply = ’Error al conectar con el tutor: ’ + str(e) + ‘. Intenta de nuevo.’
st.session_state.messages.append({‘role’: ‘assistant’, ‘content’: assistant_reply})
if not st.session_state.access_granted:
st.session_state.trial_count += 1
st.rerun()
else:
st.text_input(
‘Chat deshabilitado’,
placeholder=‘🔒 Adquiere acceso completo para continuar estudiando…’,
disabled=True,
label_visibility=‘collapsed’,
)