import streamlit as st
from google import genai
from google.genai import types
import os
import json
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import random

# ==========================================
# ⚙️ CONFIGURACIÓN DEL ADMINISTRADOR
# ==========================================
URL_DE_TU_HOJA = "https://docs.google.com/spreadsheets/d/1XI1QnWKtp2BQUKWQqjsWRThKd6axbEHjfnfqv3AKTNY/edit?gid=0#gid=0"

# --- LISTAS ALEATORIAS ---
DEPARTAMENTOS = ["la taquería", "la carnicería", "la panadería", "la pastelería", "la paletería", "frutas y verduras", "las cajas registradoras"]
PROBLEMAS = [
    "un producto echado a perder o de mala calidad", 
    "un empleado que ignoró al cliente o le contestó mal", 
    "un tiempo de espera excesivamente largo", 
    "un cobro doble en la tarjeta o problema con el cambio", 
    "un pedido que le entregaron completamente equivocado", 
    "un precio en el estante que no coincide con el de la caja"
]

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Examen HEART - La Vaquita", page_icon="📝", layout="centered")

hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """
st.markdown(hide_menu_style, unsafe_allow_html=True)

# --- CONEXIÓN IA ---
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("¡Falta la clave API! Configúrala en los Secrets de Streamlit.")
    st.stop()

client = genai.Client(api_key=api_key)

# --- INSTRUCCIONES DEL SISTEMA ---
def obtener_instrucciones_generador(dificultad):
    return f"""
    Eres un generador de exámenes para gerentes de La Vaquita Meat Market. 
    Genera UNA sola queja de cliente realista en español. No des introducciones. Describe directamente la situación y las palabras exactas que dice el cliente para iniciar la conversación.

    REGLAS:
    1. Pistas de Lenguaje Corporal: SIEMPRE incluye una descripción clara de tu estado físico al inicio (ej. estoy mirando mi reloj frenéticamente, tengo cara de agotamiento).
    2. Dificultad: Si la dificultad es "Difícil", DEBES cruzar la línea usando un insulto o lenguaje denigrante hacia el personal en tu primer mensaje.

    Dificultad EXIGIDA: {dificultad}.
    """

def obtener_instrucciones_actor(dificultad):
    return f"""
    Eres un cliente en La Vaquita Meat Market. Estás siendo atendido por un gerente en un examen de certificación.
    Dificultad de tu actitud: {dificultad}.
    
    REGLAS DE ACTUACIÓN:
    - Responde a lo que dice el gerente de forma conversacional. 
    - Si la dificultad es Difícil y no te establecen límites ante tus insultos, sé más agresivo.
    - Si están en medio del pasillo y el gerente no te reubica, quéjate de que todos los están viendo.
    
    CÓMO TERMINAR (MUY IMPORTANTE):
    El examen debe avanzar. Debes terminar la interacción OBLIGATORIAMENTE si ocurre una de estas tres cosas:
    1. El gerente resolvió tu problema de forma satisfactoria.
    2. El gerente te pidió explícitamente que te retiraras de la tienda (por actitud abusiva).
    3. La conversación ha llegado a 4 o 5 intercambios y no se llega a nada.
    
    CUANDO LA INTERACCIÓN TERMINE por cualquiera de esas 3 razones, escribe tu última frase en personaje y luego, EN UNA NUEVA LÍNEA, escribe EXACTAMENTE esta etiqueta en negritas:
    ### [FIN DE LA SIMULACIÓN]
    """

evaluador_instrucciones = """
Eres un examinador estricto de La Vaquita Meat Market. A continuación recibirás la TRANSCRIPCIÓN COMPLETA de un chat entre un gerente y un cliente.
Evalúa el desempeño del gerente utilizando el método HEART y las políticas de la tienda.

RUBRICA DE EVALUACIÓN:
- H (Hear): ¿Escucharon y dejaron que el cliente se desahogara?
- E (Empathize): ¿Validaron la frustración sin dar la razón absoluta al cliente?
- A (Apologize): ¿Asumieron la responsabilidad en nombre de la empresa?
- R (Resolve & Reubicar): ¿Solucionaron el problema? 
    * Regla de Reubicación: Si el cliente estaba alterado, ¿propusieron moverlo a una zona más tranquila? 
    * Personalización Silenciosa: ¿Adaptaron su solución al lenguaje corporal del cliente (ej. prisa) SIN decir explícitamente "veo que tiene prisa"? (Penaliza si lo señalan explícitamente).
- T (Thank): ¿Agradecieron al cliente al final?
- 🛑 Límites y Respeto: Si el cliente usó insultos en el chat, ¿el gerente estableció un límite profesional firme? Si el cliente siguió agresivo, ¿le pidieron que se retirara? (Penaliza fuertemente si toleraron el abuso).

Debes devolver TU EVALUACIÓN EXCLUSIVAMENTE en el siguiente formato JSON, sin texto adicional:
{
  "calificacion": [Un número estricto del 0 al 100],
  "retroalimentacion": "[Tu análisis detallado de qué hicieron bien y qué les faltó en esta conversación]"
}
"""

# --- GESTIÓN DEL ESTADO ---
if "fase" not in st.session_state:
    st.session_state.fase = "login"
if "nombre" not in st.session_state:
    st.session_state.nombre = ""
if "dificultad" not in st.session_state:
    st.session_state.dificultad = "Fácil"
if "numero_actual" not in st.session_state:
    st.session_state.numero_actual = 1
if "historial_chat" not in st.session_state:
    st.session_state.historial_chat = []
if "evaluaciones" not in st.session_state:
    st.session_state.evaluaciones = []

# --- FUNCIÓN PARA GENERAR ESCENARIO ---
def generar_nuevo_escenario():
    st.session_state.historial_chat = []
    depto = random.choice(DEPARTAMENTOS)
    problema = random.choice(PROBLEMAS)
    prompt_aleatorio = f"Genera el escenario número {st.session_state.numero_actual} de dificultad {st.session_state.dificultad}. El escenario DEBE ocurrir en {depto} y el problema DEBE ser sobre {problema}. Escribe directamente la primera queja del cliente."
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt_aleatorio,
        config=types.GenerateContentConfig(system_instruction=obtener_instrucciones_generador(st.session_state.dificultad))
    )
    st.session_state.historial_chat.append({"role": "model", "content": response.text})

# ==========================================
# INTERFAZ DE LA APLICACIÓN
# ==========================================
st.title("📝 Examen Oficial de Certificación HEART")

# FASE 1: Registro (Solo Administrador)
if st.session_state.fase == "login":
    st.write("Bienvenido al portal de evaluación. El sistema generará **3 escenarios de rol conversacional**.")
    
    st.divider()
    st.subheader("⚙️ Configuración del Administrador")
    st.info("Configura estos datos antes de girar la pantalla hacia el gerente que tomará el examen.")
    
    nombre_input = st.text_input("Ingresa el nombre del gerente a evaluar:")
    dificultad_seleccionada = st.selectbox(
        "Selecciona el nivel de dificultad del examen:",
        ["Fácil", "Medio", "Difícil"]
    )
    
    if st.button("Comenzar Examen"):
        if nombre_input.strip() == "":
            st.warning("Debes ingresar el nombre del gerente.")
        else:
            st.session_state.nombre = nombre_input
            st.session_state.dificultad = dificultad_seleccionada
            with st.spinner("Generando el primer escenario seguro..."):
                generar_nuevo_escenario()
                st.session_state.fase = "examen"
                st.rerun()

# FASE 2: Tomar el Examen (Chat de Rol)
elif st.session_state.fase == "examen":
    st.write(f"👤 **Gerente:** {st.session_state.nombre} | 📝 **Escenario {st.session_state.numero_actual} de 3**")
    st.caption("Responde al cliente. La simulación terminará automáticamente cuando el problema se resuelva o la interacción llegue a su límite.")
    st.divider()
    
    # Mostrar el historial del chat actual
    for msg in st.session_state.historial_chat:
        ui_role = "assistant" if msg["role"] == "model" else "user"
        # Ocultar la etiqueta de fin de simulación visualmente si está presente
        display_text = msg["content"].replace("### [FIN DE LA SIMULACIÓN]", "").strip()
        if display_text:
            with st.chat_message(ui_role):
                st.markdown(display_text)
    
    # Input de chat para el gerente
    user_input = st.chat_input("Escribe tu respuesta al cliente aquí...")
    
    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
        
        st.session_state.historial_chat.append({"role": "user", "content": user_input})
        
        # Formatear el historial para pasarlo a la IA Actor
        formatted_history = [{"role": m["role"], "parts": [{"text": m["content"]}]} for m in st.session_state.historial_chat[:-1]]
        
        actor_chat = client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(system_instruction=obtener_instrucciones_actor(st.session_state.dificultad)),
            history=formatted_history
        )
        
        with st.chat_message("assistant"):
            with st.spinner("El cliente está respondiendo..."):
                response = actor_chat.send_message(user_input)
            
            # Mostrar la respuesta sin la etiqueta técnica
            clean_response = response.text.replace("### [FIN DE LA SIMULACIÓN]", "").strip()
            if clean_response:
                st.markdown(clean_response)
        
        st.session_state.historial_chat.append({"role": "model", "content": response.text})
        
        # VERIFICAR SI LA SIMULACIÓN TERMINÓ
        if "### [FIN DE LA SIMULACIÓN]" in response.text:
            st.info("🛑 El cliente se ha retirado. Evaluando la interacción y preparando el siguiente escenario...")
            
            # Recopilar la transcripción completa
            transcripcion = ""
            for m in st.session_state.historial_chat:
                etiqueta = "Cliente" if m["role"] == "model" else "Gerente"
                transcripcion += f"{etiqueta}: {m['content']}\n\n"
            
            # Llamar al Evaluador
            prompt_evaluacion = f"TRANSCRIPCIÓN DEL CHAT:\n{transcripcion}"
            eval_response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt_evaluacion,
                config=types.GenerateContentConfig(
                    system_instruction=evaluador_instrucciones,
                    temperature=0.1,
                    response_mime_type="application/json"
                )
            )
            
            try:
                resultado_json = json.loads(eval_response.text)
                st.session_state.evaluaciones.append({
                    "escenario": st.session_state.historial_chat[0]["content"],
                    "calificacion": resultado_json.get("calificacion", 0),
                    "retroalimentacion": resultado_json.get("retroalimentacion", ""),
                    "transcripcion": transcripcion
                })
                
                # Avanzar al siguiente escenario
                if st.session_state.numero_actual < 3:
                    st.session_state.numero_actual += 1
                    generar_nuevo_escenario()
                    st.rerun()
                else:
                    st.session_state.fase = "resultados"
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Error técnico al evaluar: {e}")
                st.stop()

# FASE 3: Resultados y Registro en Base de Datos
elif st.session_state.fase == "resultados":
    
    suma_calificaciones = sum(evaluacion["calificacion"] for evaluacion in st.session_state.evaluaciones)
    calificacion_final = round(suma_calificaciones / 3)
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    if "guardado" not in st.session_state:
        try:
            cred_dict = json.loads(st.secrets["google_credentials"])
            scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
            creds = Credentials.from_service_account_info(cred_dict, scopes=scopes)
            gclient = gspread.authorize(creds)
            
            sheet = gclient.open_by_url(URL_DE_TU_HOJA).sheet1
            sheet.append_row([st.session_state.nombre, st.session_state.dificultad, calificacion_final, fecha])
            
            st.session_state.guardado = True
            st.toast("✅ Calificación final registrada en el sistema.")
        except Exception as e:
            st.error(f"Error de base de datos: {e}")

    if calificacion_final >= 85:
        st.balloons()
        st.success("¡EXAMEN APROBADO!")
    else:
        st.error("EXAMEN REPROBADO. Necesitas un promedio de 85% para pasar.")
    
    color_borde = '#28a745' if calificacion_final >= 85 else '#dc3545'
    color_fondo = '#eafaf1' if calificacion_final >= 85 else '#fdeded'
    
    boleta_html = f"""
    <div style="padding: 20px; border: 2px solid {color_borde}; border-radius: 10px; background-color: {color_fondo}; color: black;">
        <h2 style="text-align: center; margin-bottom: 0;">Boleta Oficial La Vaquita</h2>
        <p style="text-align: center; font-size: 14px; margin-top: 0;">{fecha}</p>
        <hr style="border-top: 1px solid black;">
        <p><b>Gerente:</b> {st.session_state.nombre}</p>
        <p><b>Dificultad del Examen:</b> {st.session_state.dificultad}</p>
        <p><b>Calificación Promedio:</b> <span style="font-size: 24px; font-weight: bold; color: {color_borde};">{calificacion_final}%</span></p>
    </div>
    """
    st.markdown(boleta_html, unsafe_allow_html=True)
    
    st.write("---")
    st.header("🔍 Desglose de Resultados (Solo para el Administrador)")
    
    for i, evaluacion in enumerate(st.session_state.evaluaciones):
        with st.expander(f"Ver retroalimentación del Escenario {i+1} (Calificación: {evaluacion['calificacion']}%)", expanded=False):
            st.info(evaluacion["retroalimentacion"])
            st.write("**Transcripción completa del chat:**")
            st.text(evaluacion["transcripcion"].replace("### [FIN DE LA SIMULACIÓN]", ""))
    
    st.divider()
    if st.button("Finalizar y Preparar Nuevo Examen"):
        st.session_state.clear()
        st.rerun()
