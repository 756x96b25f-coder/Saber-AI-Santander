import streamlit as st
import openai
import datetime

VALID_CODES = set("SAB-A1B2 SAB-C3D4 SAB-E5F6 SAB-G7H8 SAB-J9K1 SAB-L2M3 SAB-N4P5 SAB-Q6R7 SAB-S8T9 SAB-U1V2 SAB-W3X4 SAB-Y5Z6 SAB-A7B8 SAB-C9D1 SAB-E2F3 SAB-G4H5 SAB-J6K7 SAB-L8M9 SAB-N1P2 SAB-Q3R4 SAB-S5T6 SAB-U7V8 SAB-W9X1 SAB-Y2Z3 SAB-A4B5 SAB-C6D7 SAB-E8F9 SAB-G1H2 SAB-J3K4 SAB-L5M6 SAB-N7P8 SAB-Q9R1 SAB-S2T3 SAB-U4V5 SAB-W6X7 SAB-Y8Z9 SAB-A2C3 SAB-B4D5 SAB-E6G7 SAB-F8H9 SAB-J1L2 SAB-K3M4 SAB-N5Q6 SAB-P7R8 SAB-S9U1 SAB-T2V3 SAB-W4Y5 SAB-X6Z7 SAB-A8C9 SAB-B1D2 SAB-E3G4 SAB-F5H6 SAB-J7L8 SAB-K9M1 SAB-N2Q3 SAB-P4R5 SAB-S6U7 SAB-T8V9 SAB-W1Y2 SAB-X3Z4 SAB-A5C6 SAB-B7D8 SAB-E9G1 SAB-F2H3 SAB-J4L5 SAB-K6M7 SAB-N8Q9 SAB-P1R2 SAB-S3U4 SAB-T5V6 SAB-W7Y8 SAB-X9Z1 SAB-A3C4 SAB-B5D6 SAB-E7G8 SAB-F9H1 SAB-J2L3 SAB-K4M5 SAB-N6Q7 SAB-P8R9 SAB-S1U2 SAB-T3V4 SAB-W5Y6 SAB-X7Z8 SAB-A9C1 SAB-B2D3 SAB-E4G5 SAB-F6H7 SAB-J8L9 SAB-K1M2 SAB-N3Q4 SAB-P5R6 SAB-S7U8 SAB-T9V1 SAB-W2Y3 SAB-X4Z5 SAB-A6C7 SAB-B8D9 SAB-E1G2 SAB-F3H4".split())

FREE_TRIAL_LIMIT = 3
WA_URL = "https://wa.me/573228246703?text=Hola%2C+quiero+acceso+completo.+Adjunto+comprobante."

SYSTEM_PROMPT = ’ ’.join([‘Eres’, ‘el’, ‘tutor’, ‘lider’, ‘de’, ‘Saber’, ‘AI’, ‘Santander,’, ‘preparacion’, ‘ICFES’, ‘2026,’, ‘Santander’, ‘Colombia.’, ‘Reglas:’, ‘1)’, ‘Identifica’, ‘la’, ‘competencia’, ‘evaluada.’, ‘2)’, ‘Nunca’, ‘des’, ‘la’, ‘respuesta’, ‘directa,’, ‘haz’, ‘primero’, ‘una’, ‘pregunta’, ‘orientadora.’, ‘3)’, ‘Tono’, ‘de’, ‘docente’, ‘santandereano:’, ‘directo,’, ‘alentador,’, ‘profesional.’, ‘4)’, ‘Si’, ‘insisten,’, ‘da’, ‘una’, ‘pista’, ‘adicional’, ‘no’, ‘la’, ‘solucion.’, ‘5)’, ‘Celebra’, ‘avances’, ‘con’, ‘frases’, ‘motivadoras’, ‘de’, ‘Bucaramanga.’])

st.set_page_config(page_title=‘Saber AI Santander’, layout=‘wide’)

st.markdown(’<style>.stApp{background:#f0f4f8}.hdr{background:linear-gradient(135deg,#1a3c6e,#2d6a9f,#f5a623);color:white;padding:1.2rem 2rem;border-radius:12px;margin-bottom:1.5rem}.hdr h1{margin:0;font-size:1.8rem;font-weight:800}.hdr p{margin:.2rem 0 0;opacity:.9}.cu{background:#1a3c6e;color:white;border-radius:18px 18px 4px 18px;padding:.75rem 1.1rem;margin:.4rem 0;max-width:75%;float:right;clear:both}.ca{background:white;color:#1a1a2e;border-radius:18px 18px 18px 4px;padding:.75rem 1.1rem;margin:.4rem 0;max-width:80%;float:left;clear:both;border-left:4px solid #f5a623}.cf{clear:both}.tbadge{background:#fff3cd;border:1px solid #f5a623;border-radius:8px;padding:.4rem .9rem;font-size:.85rem;color:#856404;font-weight:600;display:inline-block;margin-bottom:.8rem}.pw{background:linear-gradient(135deg,#1a3c6e,#2d6a9f);color:white;border-radius:16px;padding:2rem;text-align:center;margin-top:1rem}.pw h2{font-size:1.5rem;margin-bottom:.5rem}.pw p{opacity:.92;font-size:1rem;margin-bottom:1rem}.pi{background:rgba(255,255,255,.15);border-radius:10px;padding:1rem;margin:1rem 0}.pi strong{color:#f5a623;font-size:1.1rem}.wa{display:inline-block;background:#25d366;color:white !important;padding:.7rem 1.8rem;border-radius:30px;text-decoration:none !important;font-weight:700}.ok{background:#d4edda;color:#155724;border-radius:8px;padding:.6rem 1rem;font-weight:600;margin-top:.5rem}.er{background:#f8d7da;color:#721c24;border-radius:8px;padding:.6rem 1rem;font-weight:600;margin-top:.5rem}</style>’, unsafe_allow_html=True)

for key, val in [(‘messages’, []), (‘trial_count’, 0), (‘access_granted’, False), (‘active_code’, None), (‘code_msg’, ‘’), (‘code_ok’, None)]:
if key not in st.session_state:
st.session_state[key] = val

params = st.query_params
if not st.session_state.access_granted:
stored = params.get(‘code’, None)
if stored and stored in VALID_CODES:
st.session_state.access_granted = True
st.session_state.active_code = stored

with st.sidebar:
st.markdown(’## Saber AI Santander’)
st.markdown(’—’)
if st.session_state.access_granted:
active = str(st.session_state.active_code)
st.markdown(’<div class="ok">Acceso completo activo<br><small>Codigo: <b>’ + active + ‘</b></small></div>’, unsafe_allow_html=True)
st.markdown(’—’)
st.markdown(‘Mensajes enviados: **’ + str(len(st.session_state.messages) // 2) + ’**’)
else:
st.markdown(’**Tienes codigo de acceso?**’)
code_input = st.text_input(‘Codigo’, placeholder=‘SAB-XXXX’, max_chars=8, label_visibility=‘collapsed’)
if st.button(‘Validar codigo’, use_container_width=True):
cleaned = code_input.strip().upper()
if cleaned in VALID_CODES:
st.session_state.access_granted = True
st.session_state.active_code = cleaned
st.session_state.code_ok = True
st.session_state.code_msg = ‘Bienvenido! Codigo ’ + cleaned + ’ activado.’
st.query_params[‘code’] = cleaned
st.rerun()
else:
st.session_state.code_ok = False
st.session_state.code_msg = ‘Codigo invalido. Verifica e intenta de nuevo.’
if st.session_state.code_msg:
css_cls = ‘ok’ if st.session_state.code_ok else ‘er’
st.markdown(’<div class="' + css_cls + '">’ + st.session_state.code_msg + ‘</div>’, unsafe_allow_html=True)
st.markdown(’—’)
left = max(0, FREE_TRIAL_LIMIT - st.session_state.trial_count)
st.markdown(’<div class="tbadge">Demo gratuito: ’ + str(left) + ’ mensaje(s) restante(s)</div>’, unsafe_allow_html=True)
st.markdown(’—’)
st.markdown(’**Pruebas disponibles**’)
st.markdown(’- Matematicas\n- Lectura Critica\n- Ciencias Naturales\n- Ingles\n- Competencias Ciudadanas’)
st.markdown(’—’)
st.markdown(‘ICFES Saber 11 - 26 de julio de 2026’)
st.markdown(‘Bucaramanga, Santander’)

st.markdown(’<div class="hdr"><h1>Saber AI Santander</h1><p>Tu tutor inteligente para el ICFES 2026 - Basado en los cuadernillos oficiales</p></div>’, unsafe_allow_html=True)

for msg in st.session_state.messages:
if msg[‘role’] == ‘user’:
st.markdown(’<div class="cu">’ + msg[‘content’] + ‘</div><div class="cf"></div>’, unsafe_allow_html=True)
else:
st.markdown(’<div class="ca">’ + msg[‘content’] + ‘</div><div class="cf"></div>’, unsafe_allow_html=True)

trial_exhausted = not st.session_state.access_granted and st.session_state.trial_count >= FREE_TRIAL_LIMIT

if trial_exhausted:
st.markdown(’<div class="pw"><h2>Has llegado al limite del demo!</h2><p>Para asegurar tu puesto en la Universidad y dominar el Icfes del <strong>26 de Julio</strong>, adquiere el acceso completo.</p><div class="pi">Envia <strong>$49,000 COP</strong> por Nequi al numero<br><strong style="font-size:1.3rem;">3228246703</strong><br><br>Luego envia el comprobante por WhatsApp para recibir tu codigo unico.</div></div>’, unsafe_allow_html=True)
st.markdown(’<div style="text-align:center;margin-top:1rem;"><a href="' + WA_URL + '" target="_blank" class="wa">Enviar comprobante por WhatsApp</a></div>’, unsafe_allow_html=True)

if st.session_state.access_granted and len(st.session_state.messages) >= 2:
st.markdown(’—’)
if st.button(‘Descargar Plan de Estudio Personalizado’, use_container_width=True):
with st.spinner(‘Generando tu plan de 7 dias…’):
try:
client = openai.OpenAI(api_key=st.secrets[‘OPENAI_API_KEY’])
hist_lines = []
for m in st.session_state.messages:
lbl = ‘Estudiante’ if m[‘role’] == ‘user’ else ‘Tutor’
hist_lines.append(lbl + ‘: ’ + m[‘content’])
history = ‘\n’.join(hist_lines)
prompt = ‘Genera un Plan de Estudio de 7 dias para el ICFES 2026.\n\nHISTORIAL:\n’ + history + ‘\n\nINSTRUCCIONES:\n- Identifica areas debiles.\n- Dia 1 a Dia 7: tema, competencia, ejercicios, objetivo, consejo santandereano.\n- Resumen fortalezas y mejoras.\n- Tono motivador santandereano.\n- ICFES 26 julio 2026.’
resp = client.chat.completions.create(model=‘gpt-4o-mini’, max_tokens=2000, messages=[{‘role’: ‘user’, ‘content’: prompt}])
plan = resp.choices[0].message.content
now = datetime.datetime.now().strftime(’%Y-%m-%d %H:%M’)
txt = ’PLAN DE ESTUDIO PERSONALIZADO - ICFES 2026\nSaber AI Santander\n==========================================\nGenerado: ’ + now + ’\nCodigo: ’ + str(st.session_state.active_code) + ‘\nFecha ICFES: 26 julio 2026\n==========================================\n\n’ + plan + ‘\n\n==========================================\nTu puedes, santandereano!\nBucaramanga, Santander, Colombia\n’
st.download_button(label=‘Descargar plan (.txt)’, data=txt, file_name=‘plan_ICFES_’ + str(st.session_state.active_code) + ‘.txt’, mime=‘text/plain’, use_container_width=True)
except Exception as e:
st.error(’Error al generar el plan: ’ + str(e))

chat_allowed = st.session_state.access_granted or st.session_state.trial_count < FREE_TRIAL_LIMIT

if chat_allowed:
if not st.session_state.access_granted:
left = FREE_TRIAL_LIMIT - st.session_state.trial_count
st.markdown(’<div class="tbadge">Demo: ’ + str(left) + ’ mensaje(s) gratuito(s)</div>’, unsafe_allow_html=True)
user_input = st.chat_input(‘Escribe tu pregunta ICFES 2026 - Matematicas, Lectura Critica, Ciencias, Ingles, Ciudadanas’)
if user_input:
st.session_state.messages.append({‘role’: ‘user’, ‘content’: user_input})
with st.spinner(‘El tutor esta pensando…’):
try:
client = openai.OpenAI(api_key=st.secrets[‘OPENAI_API_KEY’])
api_msgs = [{‘role’: ‘system’, ‘content’: SYSTEM_PROMPT}]
for m in st.session_state.messages:
api_msgs.append({‘role’: m[‘role’], ‘content’: m[‘content’]})
resp = client.chat.completions.create(model=‘gpt-4o-mini’, max_tokens=1000, messages=api_msgs)
reply = resp.choices[0].message.content
except Exception as e:
reply = ‘Error al conectar: ’ + str(e)
st.session_state.messages.append({‘role’: ‘assistant’, ‘content’: reply})
if not st.session_state.access_granted:
st.session_state.trial_count += 1
st.rerun()
else:
st.text_input(’’, placeholder=‘Adquiere acceso completo para continuar…’, disabled=True, label_visibility=‘collapsed’)